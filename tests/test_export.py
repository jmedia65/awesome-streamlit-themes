"""Healthcare vertical slice: semantic config, complete assets, and failures."""

from copy import deepcopy
from io import BytesIO
import shutil
import subprocess
import sys
import tomllib
import zipfile

import pytest
from streamlit import config
from streamlit.testing.v1 import AppTest

from studio.catalog import ROOT
from studio.export import config_bytes, export_package
from studio.theme import ThemeError, control_defaults, contrast_advisories, contrast_ratio, draft_theme, paired_proof, resolve_theme, validate_theme


def edited_theme():
    values = control_defaults("healthcare")
    values.update(accent="#176b4e", background="#f5faf7", radius="1rem",
                  body_font="Lora", sidebar_background="#e0ede5")
    return resolve_theme("healthcare", values)


def test_preset_and_edited_packages_roundtrip_without_dangling_assets():
    for theme in (resolve_theme("healthcare", control_defaults("healthcare")), edited_theme()):
        shown, package = export_package(theme)
        assert config_bytes(theme) == shown
        assert export_package(theme) == (shown, package)
        document = tomllib.loads(shown.decode())
        assert document["theme"] == theme
        assert document["server"]["enableStaticServing"] is True
        with zipfile.ZipFile(BytesIO(package)) as archive:
            assert archive.read(".streamlit/config.toml") == shown
            assert all(not name.startswith("/") and ".." not in name.split("/") for name in archive.namelist())
            referenced = {face["url"].removeprefix("app/") for face in theme["fontFaces"]}
            assert {name for name in archive.namelist() if name.startswith("static/")} == referenced
            for face in theme["fontFaces"]:
                assert archive.getinfo(face["url"].removeprefix("app/")).file_size > 1000
                assert archive.read(f"licenses/OFL-{face['family'].lower()}.txt")
                assert archive.read(f"licenses/original-{face['family']}.txt")
            assert archive.read("LICENSE") and archive.read("licenses/FONT_NOTICES.md")
            assert b"Restart" in archive.read("README.md")


def test_changed_font_omits_unreferenced_original_font_files():
    theme = edited_theme()
    assert {f["family"] for f in theme["fontFaces"]} == {"Lora", "IBMPlexMono"}
    assert theme["font"] == theme["headingFont"] == "Lora"
    assert theme["sidebar"]["backgroundColor"] == "#e0ede5"
    assert theme["base"] == "light"


@pytest.mark.parametrize("key,value", [("primaryColor", "red"), ("backgroundColor", "#gggggg"),
    ("baseRadius", "9rem"), ("font", "unregistered"), ("showSidebarBorder", "true"),
    ("unrecognized", True)])
def test_invalid_values_stop_export(key, value):
    theme = edited_theme()
    theme[key] = value
    with pytest.raises(ThemeError):
        export_package(theme)


def test_font_path_cannot_reference_unregistered_files():
    theme = edited_theme()
    theme["fontFaces"][0]["url"] = "app/static/../../.streamlit/secrets.toml"
    with pytest.raises(ThemeError):
        export_package(theme)


@pytest.mark.parametrize("missing", ["healthcare/static/IBMPlexMono-Regular.ttf", "licenses/fonts/OFL-ibmplexmono.txt"])
def test_missing_asset_or_license_prevents_package(tmp_path, missing):
    # Supply only expected roots, then remove a required dependency.
    for name in ("healthcare", "editorial", "licenses"):
        shutil.copytree(ROOT / name, tmp_path / name)
    shutil.copyfile(ROOT / "LICENSE", tmp_path / "LICENSE")
    (tmp_path / missing).unlink()
    with pytest.raises(ThemeError, match="Missing"):
        export_package(edited_theme(), root=tmp_path)


def test_paired_structure_and_shared_only_fields_match_actual_runtime():
    paired = paired_proof(edited_theme())
    document = tomllib.loads(config_bytes(paired).decode())
    assert document["theme"]["light"]["primaryColor"] != document["theme"]["dark"]["primaryColor"]
    assert "fontFaces" in document["theme"]
    assert "fontFaces" not in document["theme"]["light"]
    assert "showSidebarBorder" not in document["theme"]["dark"]
    options = config.get_config_options()
    def check(section, prefix):
        for key, value in section.items():
            if isinstance(value, dict):
                check(value, f"{prefix}.{key}")
            else:
                assert f"{prefix}.{key}" in options
    check(document["theme"], "theme")
    invalid = deepcopy(paired)
    invalid["dark"]["showSidebarBorder"] = True
    with pytest.raises(ThemeError, match="not supported"):
        validate_theme(invalid)
    assert export_package(paired)[1]


def test_contrast_advisory_is_specific_and_does_not_block_valid_export():
    assert contrast_ratio("#ffffff", "#000000") == 21
    theme = edited_theme()
    theme["backgroundColor"] = theme["textColor"]
    warnings = contrast_advisories(theme)
    assert any("Canvas" in warning and "1.0:1" in warning for warning in warnings)
    assert config_bytes(theme)


def test_healthcare_font_sidebar_reruns_and_reset():
    app = AppTest.from_file(str(ROOT / "studio/streamlit_app.py"), default_timeout=20).run()
    app.button(key="choose_healthcare").click().run()
    app.selectbox(key="body_font").select("Lora").run()
    app.color_picker(key="sidebar_background").set_value("#e0ede5").run()
    app.select_slider[0].set_value("1rem").run()
    assert not app.exception
    assert 'font = "Lora"' in app.code[0].value
    assert 'backgroundColor = "#e0ede5"' in app.code[0].value
    assert 'headingFont = "IBMPlexSans"' in app.code[0].value
    assert app.code[0].value.encode("utf-8") == config_bytes(draft_theme(app.session_state.draft))
    app.button[0].click().run()
    assert app.selectbox(key="body_font").value == "IBMPlexSans"
    assert app.color_picker(key="sidebar_background").value == "#f1f4f7"
    assert app.select_slider[0].value == "0.25rem"


def test_missing_dependency_disables_the_ui_download(monkeypatch):
    def missing(*args, **kwargs):
        raise ThemeError("Missing font asset: IBMPlexSans-Regular.ttf. Export was stopped.")
    monkeypatch.setattr("studio.export.export_package", missing)
    app = AppTest.from_file(str(ROOT / "studio/streamlit_app.py"), default_timeout=20).run()
    app.button(key="choose_healthcare").click().run()
    assert not app.exception
    assert any("Missing font asset" in error.value for error in app.error)
    assert not app.get("download_button")


def test_low_contrast_is_an_advisory_in_the_ui_not_an_export_failure():
    app = AppTest.from_file(str(ROOT / "studio/streamlit_app.py"), default_timeout=20).run()
    app.button(key="choose_healthcare").click().run()
    app.color_picker(key="background").set_value("#2c3e50").run()
    assert any("Canvas text contrast is 1.0:1" in warning.value for warning in app.warning)
    assert len(app.get("download_button")) == 1
    assert not app.exception


@pytest.mark.parametrize("paired", [False, True], ids=["single", "paired"])
def test_export_installs_and_runs_in_an_independent_native_app(tmp_path, paired):
    theme = paired_proof(edited_theme()) if paired else edited_theme()
    _, package = export_package(theme)
    with zipfile.ZipFile(BytesIO(package)) as archive:
        archive.extractall(tmp_path)
    shutil.copyfile(ROOT / "studio/sample_app.py", tmp_path / "sample_app.py")
    code = """from streamlit.testing.v1 import AppTest
from streamlit import config
app=AppTest.from_file('sample_app.py',default_timeout=30).run()
assert not app.exception, [e.message for e in app.exception]
assert config.get_option('theme.font') == 'Lora'
assert config.get_option('server.enableStaticServing') is True
assert any(title.value == 'A clearer view of your work.' for title in app.title)
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=tmp_path,
                            capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stderr
