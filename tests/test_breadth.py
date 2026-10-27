"""Representative breadth: real palettes, paired output, and session journeys."""

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

from studio.catalog import ROOT, get_preset, load_theme
from studio.export import config_bytes, export_package
from studio.theme import (EDITABLE_PRESETS, ThemeError, contrast_advisories, draft_changes,
                          draft_theme, preset_draft, validate_theme)


def editor(slug="healthcare"):
    app = AppTest.from_file(str(ROOT / "studio/streamlit_app.py"), default_timeout=20).run()
    app.button(key=f"choose_{slug}").click().run()
    assert not app.exception
    return app


def set_mode(app, mode):
    segment(app, "edit_appearance").set_value(mode).run()


def segment(app, key):
    return next(element for element in app.get("segmented_control") if element.key == key)


@pytest.mark.parametrize("slug", EDITABLE_PRESETS)
def test_three_defaults_preserve_original_identity_and_have_distinct_counterparts(slug):
    draft = preset_draft(slug)
    theme = draft_theme(draft)
    original = load_theme(slug)
    for key in ("primaryColor", "backgroundColor", "secondaryBackgroundColor", "textColor",
                "font", "headingFont", "codeFont", "baseRadius", "showWidgetBorder", "showSidebarBorder"):
        assert theme[key] == original[key]
    assert not draft_changes(slug, draft)
    assert theme["base"] == get_preset(slug).appearance
    opposite = "light" if theme["base"] == "dark" else "dark"
    counterpart = draft_theme(draft, appearance=opposite, output="single")
    assert counterpart["base"] == opposite
    assert counterpart["backgroundColor"] != theme["backgroundColor"]
    assert counterpart["sidebar"]["backgroundColor"] != theme["sidebar"]["backgroundColor"]
    assert not [warning for warning in contrast_advisories(counterpart) if "text contrast" in warning]
    draft["variants"][opposite]["backgroundColor"] = "#ffffff"
    assert preset_draft(slug)["variants"][opposite]["backgroundColor"] != "#ffffff"


@pytest.mark.parametrize("slug", EDITABLE_PRESETS)
def test_paired_custom_palettes_sidebar_fonts_and_sections_are_real_runtime_keys(slug):
    draft = preset_draft(slug)
    draft["output"] = "paired"
    draft["fonts"].update(font="Inter", headingFont="Lora", codeFont="JetBrainsMono")
    draft["showSidebarBorder"] = False
    draft["variants"]["light"].update(primaryColor="#176b4e", backgroundColor="#f5faf7",
                                      buttonRadius="1rem", showWidgetBorder=False)
    draft["variants"]["dark"].update(primaryColor="#4b369e", backgroundColor="#101824")
    draft["variants"]["light"]["sidebar"].update(backgroundColor="#e0ede5", textColor="#193b2c")
    draft["variants"]["dark"]["sidebar"].update(backgroundColor="#1d2940", textColor="#f4f6ff")
    theme = draft_theme(draft)
    data, package = export_package(theme)
    assert data == config_bytes(theme)
    assert export_package(theme) == (data, package)
    parsed = tomllib.loads(data.decode())["theme"]
    assert parsed["light"]["primaryColor"] == "#176b4e"
    assert parsed["dark"]["primaryColor"] == "#4b369e"
    assert parsed["light"]["sidebar"]["backgroundColor"] == "#e0ede5"
    assert parsed["dark"]["sidebar"]["textColor"] == "#f4f6ff"
    assert parsed["headingFont"] == "Lora" and parsed["showSidebarBorder"] is False
    assert parsed["light"]["buttonRadius"] == "1rem" and parsed["light"]["showWidgetBorder"] is False
    assert {face["family"] for face in parsed["fontFaces"]} == {"Inter", "Lora", "JetBrainsMono"}
    for mode in ("light", "dark"):
        assert not ({"base", "fontFaces", "showSidebarBorder", "font", "headingFont", "codeFont"} & parsed[mode].keys())
    options = config.get_config_options()
    def check(section, path):
        for key, value in section.items():
            if isinstance(value, dict):
                check(value, f"{path}.{key}")
            else:
                assert f"{path}.{key}" in options
    check(parsed, "theme")
    with zipfile.ZipFile(BytesIO(package)) as archive:
        assert archive.read(".streamlit/config.toml") == data
        assert {name for name in archive.namelist() if name.startswith("static/")} == {
            face["url"].removeprefix("app/") for face in parsed["fontFaces"]}
        for family in {face["family"] for face in parsed["fontFaces"]}:
            assert archive.read(f"licenses/OFL-{family.lower()}.txt")
            assert archive.read(f"licenses/original-{family}.txt")


def test_sidebar_matching_is_explicit_and_custom_values_are_recoverable():
    draft = preset_draft("financial")
    variant = draft["variants"]["light"]
    custom = deepcopy(variant["sidebar"])
    variant["sidebar_custom"] = False
    variant["textColor"] = "#123456"
    theme = draft_theme(draft)
    assert theme["sidebar"] == {"backgroundColor": theme["backgroundColor"],
                                "secondaryBackgroundColor": theme["secondaryBackgroundColor"], "textColor": "#123456"}
    assert variant["sidebar"] == custom
    variant["sidebar_custom"] = True
    assert draft_theme(draft)["sidebar"] == custom


@pytest.mark.parametrize("field,value", [("buttonRadius", "2rem"), ("showWidgetBorder", "false"),
                                        ("linkColor", "url(secret)"), ("textColor", "red")])
def test_advanced_invalid_values_stop_export(field, value):
    draft = preset_draft("financial")
    draft["variants"]["light"][field] = value
    with pytest.raises(ThemeError):
        export_package(draft_theme(draft))


def test_paired_missing_variant_and_illegal_shared_fields_are_rejected():
    draft = preset_draft("healthcare")
    draft["output"] = "paired"
    del draft["variants"]["dark"]
    with pytest.raises(ThemeError, match="dark palette"):
        draft_theme(draft)
    paired = draft_theme(preset_draft("healthcare"), output="paired")
    paired["base"] = "light"
    with pytest.raises(ThemeError, match="single base"):
        validate_theme(paired)
    del paired["base"]
    paired["light"]["fontFaces"] = paired["fontFaces"]
    with pytest.raises(ThemeError, match="not supported"):
        validate_theme(paired)


def test_mode_switch_comparison_browsing_and_reset_preserve_or_restore_all_controls():
    app = editor("financial")
    app.radio(key="export_scope").set_value("paired").run()
    app.color_picker(key="accent").set_value("#176b4e").run()
    app.selectbox(key="heading_font").select("Lora").run()
    app.selectbox(key="code_font").select("JetBrainsMono").run()
    app.color_picker(key="link").set_value("#176b4e").run()
    app.checkbox(key="widget_border").uncheck().run()
    app.checkbox(key="sidebar_border").uncheck().run()
    app.color_picker(key="sidebar_background").set_value("#e0ede5").run()
    set_mode(app, "dark")
    app.color_picker(key="accent").set_value("#4b369e").run()
    app.color_picker(key="sidebar_background").set_value("#1d2940").run()
    paired = app.code[0].value
    segment(app, "preview_source").set_value("Preset defaults").run()
    assert app.code[0].value == paired
    segment(app, "workspace").set_value("All 10 themes").run()
    app.button(key="choose_financial").click().run()
    assert app.code[0].value == paired
    set_mode(app, "light")
    assert app.color_picker(key="accent").value == "#176b4e"
    assert app.color_picker(key="accent").proto.set_value
    assert app.color_picker(key="sidebar_background").value == "#e0ede5"
    assert app.selectbox(key="body_font").value == "Inter"
    assert app.selectbox(key="heading_font").value == "Lora"
    assert app.checkbox(key="widget_border").value is False
    assert app.code[0].value == paired
    app.button[0].click().run()
    assert not app.exception
    assert app.radio(key="export_scope").value == "single"
    assert app.color_picker(key="accent").value == "#1e3a8a"
    assert app.selectbox(key="heading_font").value == "Inter"
    assert app.checkbox(key="widget_border").value is True
    assert not draft_changes("financial", app.session_state.draft)


@pytest.mark.parametrize("via_gallery", [False, True])
def test_dirty_switch_requires_choice_and_cancel_preserves_both_appearances(via_gallery):
    app = editor()
    app.color_picker(key="accent").set_value("#176b4e").run()
    set_mode(app, "dark")
    app.color_picker(key="accent").set_value("#4b369e").run()
    before = deepcopy(app.session_state.draft)
    if via_gallery:
        segment(app, "workspace").set_value("All 10 themes").run()
        app.button(key="choose_dark-mode").click().run()
    else:
        app.selectbox(key="preset_picker").select("dark-mode").run()
    assert app.session_state.preset == "healthcare"
    assert app.session_state.draft == before
    assert any("unsaved changes" in warning.value for warning in app.warning)
    app.button(key="cancel_switch").click().run()
    assert app.session_state.draft == before
    if via_gallery:
        app.button(key="choose_dark-mode").click().run()
    else:
        assert app.selectbox(key="preset_picker").value == "healthcare"
        app.selectbox(key="preset_picker").select("dark-mode").run()
    app.button(key="discard_switch").click().run()
    assert app.session_state.preset == "dark-mode"
    assert app.color_picker(key="accent").value == "#a855f7"
    assert not app.exception


def test_paired_warnings_include_hidden_mode_and_visitors_are_independent():
    app = editor()
    app.radio(key="export_scope").set_value("paired").run()
    app.color_picker(key="background").set_value("#2c3e50").run()
    set_mode(app, "dark")
    assert any("Light · Canvas text contrast is 1.0:1" in warning.value for warning in app.warning)
    assert app.get("download_button")
    other = editor("dark-mode")
    assert other.radio(key="export_scope").value == "single"
    assert other.color_picker(key="accent").value == "#a855f7"
    assert app.color_picker(key="accent").value == "#2563eb"


def test_color_and_mode_events_in_one_rerun_keep_the_color_in_its_rendered_mode():
    app = editor("financial")
    app.color_picker(key="sidebar_background").set_value("#e0ede5")
    segment(app, "edit_appearance").set_value("dark")
    app.run()
    assert app.session_state.draft["variants"]["light"]["sidebar"]["backgroundColor"] == "#e0ede5"
    assert app.color_picker(key="sidebar_background").value == "#131f34"
    set_mode(app, "light")
    assert app.color_picker(key="sidebar_background").value == "#e0ede5"


@pytest.mark.parametrize("slug", EDITABLE_PRESETS)
@pytest.mark.parametrize("paired", [False, True], ids=["single", "paired"])
def test_representative_packages_install_in_separate_native_processes(tmp_path, slug, paired):
    draft = preset_draft(slug)
    draft["output"] = "paired" if paired else "single"
    draft["fonts"]["headingFont"] = "Lora"
    _, package = export_package(draft_theme(draft))
    with zipfile.ZipFile(BytesIO(package)) as archive:
        archive.extractall(tmp_path)
    shutil.copyfile(ROOT / "studio/sample_app.py", tmp_path / "sample_app.py")
    code = '''from streamlit.testing.v1 import AppTest
from streamlit import config
import tomllib
app=AppTest.from_file('sample_app.py',default_timeout=30).run()
assert not app.exception, [e.message for e in app.exception]
assert config.get_option('theme.headingFont')=='Lora'
assert config.get_option('server.enableStaticServing') is True
theme=tomllib.load(open('.streamlit/config.toml','rb'))['theme']
for mode in ('light','dark'):
    if mode in theme:
        assert config.get_option(f'theme.{mode}.primaryColor')==theme[mode]['primaryColor']
        assert config.get_option(f'theme.{mode}.sidebar.backgroundColor')==theme[mode]['sidebar']['backgroundColor']
assert any(title.value=='A clearer view of your work.' for title in app.title)
'''
    result = subprocess.run([sys.executable, "-c", code], cwd=tmp_path, capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stderr
