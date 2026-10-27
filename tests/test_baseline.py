"""Focused baseline checks against the real source assets and target runtime."""

import subprocess
import sys
import tomllib

import pytest
from streamlit import config
from streamlit.testing.v1 import AppTest

from studio.catalog import PRESETS, ROOT, load_theme


@pytest.mark.parametrize("preset", PRESETS, ids=lambda p: p.slug)
def test_original_config_and_assets(preset):
    options = config.get_config_options()
    data = tomllib.loads((preset.directory / ".streamlit/config.toml").read_text())
    assert preset.image.is_file()
    for key in data["theme"]:
        if key == "sidebar":
            for sidebar_key in data["theme"][key]:
                assert f"theme.sidebar.{sidebar_key}" in options
        else:
            assert f"theme.{key}" in options
    for face in data["theme"]["fontFaces"]:
        assert (preset.directory / face["url"].removeprefix("app/")).is_file()
    assert data["server"]["enableStaticServing"] is True


@pytest.mark.parametrize("preset", PRESETS, ids=lambda p: p.slug)
def test_original_demo_home_runs(preset):
    # A fresh process avoids leaking module/config/session state between demos.
    code = """from streamlit.testing.v1 import AppTest
app=AppTest.from_file('streamlit_app.py', default_timeout=30).run()
assert not app.exception, [e.message for e in app.exception]
assert app.title[0].value == 'Streamlit element explorer'
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=preset.directory,
                            capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stderr


def test_catalog_returns_fresh_state():
    first = load_theme("healthcare")
    first["sidebar"]["backgroundColor"] = "#000000"
    assert load_theme("healthcare")["sidebar"]["backgroundColor"] == "#f1f4f7"


def test_paired_section_boundaries_and_writer():
    import tomli_w
    options = config.get_config_options()
    for shared in ("base", "fontFaces", "baseFontSize", "baseFontWeight", "showSidebarBorder"):
        assert f"theme.{shared}" in options
        assert f"theme.light.{shared}" not in options
        assert f"theme.dark.{shared}" not in options
    sample = {"theme": {"fontFaces": [{"family": "Test", "url": "app/static/test.ttf", "weight": 400}],
                        "light": {"primaryColor": "#0066cc", "sidebar": {"backgroundColor": "#fafafa"}},
                        "dark": {"primaryColor": "#a855f7", "sidebar": {"backgroundColor": "#161b22"}}}}
    text = tomli_w.dumps(sample)
    assert tomllib.loads(text) == sample
    assert tomli_w.dumps(sample) == text
