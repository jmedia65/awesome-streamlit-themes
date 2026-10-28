"""Finished all-ten experience and portable packages from relocated assets."""

from io import BytesIO
import tomllib
import zipfile

import pytest
from streamlit.testing.v1 import AppTest

from studio.catalog import PRESETS, ROOT, load_theme
from studio.export import config_bytes, export_package
from studio.theme import contrast_advisories, draft_theme, font_asset, preset_draft


@pytest.mark.parametrize("preset", PRESETS, ids=lambda p:p.slug)
@pytest.mark.parametrize("scope", ["light", "dark", "paired"])
def test_every_default_output_is_complete_and_has_no_default_text_warning(preset, scope):
    draft = preset_draft(preset.slug)
    theme = draft_theme(draft, output="paired") if scope == "paired" else draft_theme(draft, appearance=scope)
    if scope == "paired":
        for mode in ("light", "dark"):
            assert not contrast_advisories(draft_theme(draft, appearance=mode))
    else:
        assert theme["base"] == scope
        assert not contrast_advisories(theme)
    data, package = export_package(theme)
    assert data == config_bytes(theme)
    assert tomllib.loads(data.decode())["theme"] == theme
    original = load_theme(preset.slug)
    for field in ("font", "headingFont", "codeFont"):
        assert theme[field] == original[field]
    with zipfile.ZipFile(BytesIO(package)) as archive:
        assert archive.read(".streamlit/config.toml") == data
        expected = {face["url"].removeprefix("app/") for face in theme["fontFaces"]}
        assert {name for name in archive.namelist() if name.startswith("static/")} == expected
        for face in theme["fontFaces"]:
            assert archive.read(face["url"].removeprefix("app/")) == font_asset(face).read_bytes()
            assert archive.read(f"licenses/OFL-{face['family'].lower()}.txt")
            assert archive.read(f"licenses/original-{face['family']}.txt")
        assert archive.read("LICENSE") and archive.read("licenses/FONT_NOTICES.md")


@pytest.mark.parametrize("preset", PRESETS, ids=lambda p:p.slug)
def test_every_gallery_card_opens_a_finished_no_edit_export(preset):
    app = AppTest.from_file(str(ROOT / "studio/streamlit_app.py"), default_timeout=20).run()
    app.button(key=f"choose_{preset.slug}").click().run()
    assert not app.exception and not app.error and not app.warning
    assert len(app.get("download_button")) == 1
    original = load_theme(preset.slug)
    for widget, field in (("body_font", "font"), ("heading_font", "headingFont"), ("code_font", "codeFont")):
        assert app.selectbox(key=widget).value == original[field]
        assert len(app.selectbox(key=widget).options) <= 4
    parsed = tomllib.loads(app.code[0].value)["theme"]
    assert parsed["base"] == preset.appearance
    assert parsed["font"] == original["font"]
    app.radio(key="export_scope").set_value("paired").run()
    assert set(tomllib.loads(app.code[0].value)["theme"]) >= {"light", "dark", "fontFaces"}
    assert not app.exception and len(app.get("download_button")) == 1
