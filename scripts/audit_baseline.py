"""Audit original assets and the installed target schema; never modify demos.

Run from the repository root: .venv/bin/python scripts/audit_baseline.py
"""

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import tomllib

from fontTools.ttLib import TTFont
import streamlit
from streamlit import config

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from studio.catalog import PRESETS  # noqa: E402


def flatten(data, prefix=""):
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from flatten(value, name)
        else:
            yield name, value


def audit():
    options = config.get_config_options()
    rows = []
    fonts = defaultdict(lambda: {"copyright": set(), "license": set(), "files": []})
    for preset in PRESETS:
        with (preset.directory / ".streamlit/config.toml").open("rb") as handle:
            data = tomllib.load(handle)
        missing, invalid = [], []
        for face in data["theme"]["fontFaces"]:
            path = preset.directory / face["url"].removeprefix("app/")
            if not path.is_file():
                missing.append(face["url"])
                continue
            try:
                with TTFont(path) as font:
                    for record in font["name"].names:
                        if record.nameID == 0:
                            fonts[face["family"]]["copyright"].add(record.toUnicode())
                        if record.nameID == 13:
                            fonts[face["family"]]["license"].add(record.toUnicode())
                fonts[face["family"]]["files"].append({
                    "path": str(path.relative_to(ROOT)),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                })
            except Exception as exc:
                invalid.append(f"{path.name}: {type(exc).__name__}")
        rows.append({
            "preset": preset.slug, "appearance": preset.appearance,
            "explicit_legacy_base": data["theme"].get("base"),
            "font_faces": len(data["theme"]["fontFaces"]),
            "licenses": [p.name for p in sorted(preset.directory.glob("static/*.txt"))],
            "thumbnail": str(preset.image.relative_to(ROOT)),
            "missing_fonts": missing, "invalid_fonts": invalid,
            "unknown_keys": [key for key, _ in flatten(data) if key not in options],
        })
    return {"streamlit": streamlit.__version__, "presets": rows,
            "fonts": {key: {k: sorted(v) if isinstance(v, set) else v for k, v in value.items()}
                      for key, value in sorted(fonts.items())}}


if __name__ == "__main__":
    result = audit()
    output = ROOT / ".local/audit"
    output.mkdir(parents=True, exist_ok=True)
    (output / "baseline.json").write_text(json.dumps(result, indent=2) + "\n")
    errors = [p for p in result["presets"] if p["missing_fonts"] or p["invalid_fonts"] or p["unknown_keys"]]
    print(f"Streamlit {result['streamlit']}: {len(result['presets'])} presets, "
          f"{sum(p['font_faces'] for p in result['presets'])} font faces, "
          f"{len(result['fonts'])} font families, {len(errors)} failures.")
    sys.exit(bool(errors))
