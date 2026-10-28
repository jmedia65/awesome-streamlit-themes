"""Gallery, original preview controls, and shell preservation regressions."""

import hashlib

import pytest
from streamlit.testing.v1 import AppTest

from studio.catalog import PRESETS, ROOT, load_theme
from studio.preview import render_preview


def concept():
    app = AppTest.from_file(str(ROOT / "studio/streamlit_app.py"), default_timeout=20).run()
    app.get("segmented_control")[0].set_value("Studio").run()
    return app


def test_new_visitor_opens_gallery_with_ten_original_presets():
    app = AppTest.from_file(str(ROOT / "studio/streamlit_app.py"), default_timeout=20).run()
    assert app.get("segmented_control")[0].value == "All 10 themes"
    assert len(app.button) == 10
    assert not app.exception


def test_edit_browse_restore_reset_and_shell_preservation():
    shell = ROOT / "studio/.streamlit/config.toml"
    before = hashlib.sha256(shell.read_bytes()).hexdigest()
    app = concept()
    app.color_picker(key="accent").set_value("#e05231").run()
    app.select_slider[0].set_value("1rem").run()
    app.get("segmented_control")[0].set_value("All 10 themes").run()
    assert len(app.button) == 10
    app.get("segmented_control")[0].set_value("Studio").run()
    assert app.color_picker(key="accent").value == "#e05231"
    assert app.select_slider[0].value == "1rem"
    app.button[0].click().run()
    assert app.color_picker(key="accent").value == "#0066cc"
    assert app.select_slider[0].value == "0.25rem"
    assert not app.exception
    assert hashlib.sha256(shell.read_bytes()).hexdigest() == before


def test_gallery_choice_syncs_controls_and_new_visitor_is_independent():
    app = concept()
    app.get("segmented_control")[0].set_value("All 10 themes").run()
    app.button(key="choose_dark-mode").click().run()
    assert app.selectbox(key="preset_picker").value == "dark-mode"
    assert app.color_picker(key="accent").value == "#9333ea"
    assert app.selectbox(key="body_font").value == "Inter"
    assert concept().selectbox(key="preset_picker").value == "healthcare"
    assert not app.exception


@pytest.mark.parametrize("preset", PRESETS, ids=lambda p: p.slug)
def test_dropdown_switch_synchronizes_frontend_then_radius_keeps_palette(preset):
    app = concept()
    if preset.slug == "healthcare":
        app.selectbox(key="preset_picker").select("financial").run()
    app.color_picker(key="accent").set_value("#e05231").run()
    app.selectbox(key="preset_picker").select(preset.slug).run()
    assert app.button(key="discard_switch")
    app.button(key="discard_switch").click().run()
    source = load_theme(preset.slug)
    accent = "#9333ea" if preset.slug == "dark-mode" else source["primaryColor"]
    assert not app.exception
    assert app.color_picker(key="accent").value == accent
    assert app.color_picker(key="background").value == source["backgroundColor"]
    # Backend values alone missed the browser desynchronization regression.
    assert app.color_picker(key="accent").proto.set_value
    assert app.color_picker(key="background").proto.set_value
    assert app.select_slider[0].value == source["baseRadius"]
    app.select_slider[0].set_value("1rem").run()
    assert app.select_slider[0].value == "1rem"
    assert app.color_picker(key="accent").value == accent
    assert app.color_picker(key="background").value == source["backgroundColor"]
    app.button[0].click().run()
    assert app.select_slider[0].value == source["baseRadius"]
    assert app.color_picker(key="accent").proto.set_value


@pytest.mark.parametrize("color,radius", [("red;}</style><script>alert(1)</script>", "0.5rem"),
                                         ("#0066cc", "1rem;position:fixed")])
def test_preview_rejects_nonliteral_css(color, radius):
    with pytest.raises(ValueError):
        render_preview("healthcare", color, "#fafbfc", radius, "Dashboard")
