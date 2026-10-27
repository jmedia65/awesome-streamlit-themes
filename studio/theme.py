"""Pure Python theme resolution, validation, and advisory contrast checks."""

from copy import deepcopy
from functools import lru_cache
import re

from studio.catalog import PRESETS, ROOT, get_preset, load_theme

# Preserve every original preset value, including Cyberpunk's 0.2rem.
RADIUS_OPTIONS = ("0.125rem", "0.2rem", "0.25rem", "0.375rem", "0.5rem", "0.75rem", "1rem")
FONT_CHOICES = {"IBMPlexSans": "IBM Plex Sans", "Inter": "Inter", "Lora": "Lora"}
CODE_FONT_CHOICES = {"IBMPlexMono": "IBM Plex Mono", "SourceCodePro": "Source Code Pro", "JetBrainsMono": "JetBrains Mono"}
EDITABLE_PRESETS = ("healthcare", "financial", "dark-mode")
COLORS = {"primaryColor", "backgroundColor", "secondaryBackgroundColor", "textColor", "linkColor", "borderColor", "codeBackgroundColor"}
FONTS = {"font", "headingFont", "codeFont"}
APPEARANCE_FIELDS = COLORS | FONTS | {"baseRadius", "buttonRadius", "showWidgetBorder", "sidebar"}
SHARED_FIELDS = {"base", "fontFaces", "showSidebarBorder"}


class ThemeError(ValueError):
    """An actionable invalid choice or missing export dependency."""


def control_defaults(slug):
    source = load_theme(slug)
    return {"accent": source["primaryColor"], "background": source["backgroundColor"],
            "radius": source["baseRadius"], "body_font": source["font"],
            "sidebar_background": source["sidebar"]["backgroundColor"]}


def _face_key(face):
    return (face.get("family"), face.get("url"), face.get("style", "normal"), face.get("weight"))


@lru_cache(maxsize=1)
def _font_inventory():
    """Private, read-only inventory of declarations from canonical presets."""
    inventory = {}
    for preset in PRESETS:
        for face in load_theme(preset.slug)["fontFaces"]:
            relative = face["url"].removeprefix("app/")
            inventory.setdefault(_face_key(face), (deepcopy(face), preset.slug, relative))
    return inventory


def font_asset(face, root=ROOT):
    try:
        _, slug, relative = _font_inventory()[_face_key(face)]
    except (KeyError, TypeError):
        raise ThemeError("Unsupported font declaration. Choose a bundled font.") from None
    path = root / slug / relative
    if not path.is_file():
        raise ThemeError(f"Missing font asset: {path.name}. Restore the file before exporting.")
    return path


def resolve_theme(slug, values):
    theme = load_theme(slug)
    theme.update(base=get_preset(slug).appearance, primaryColor=values["accent"],
                 backgroundColor=values["background"], baseRadius=values["radius"])
    theme["sidebar"]["backgroundColor"] = values["sidebar_background"]
    # This slice edits body and heading typography together; code font is retained.
    theme["font"] = theme["headingFont"] = values["body_font"]
    families = {theme[key] for key in FONTS}
    theme["fontFaces"] = [deepcopy(face) for face, _, _ in _font_inventory().values() if face["family"] in families]
    validate_theme(theme)
    return theme


def validate_theme(theme):
    if not isinstance(theme, dict):
        raise ThemeError("Theme must be a table.")
    paired = "light" in theme or "dark" in theme
    if paired and not all(isinstance(theme.get(mode), dict) for mode in ("light", "dark")):
        raise ThemeError("Paired exports require both light and dark tables.")
    if paired and "base" in theme:
        raise ThemeError("Paired exports use light and dark tables instead of a single base.")
    declarations = theme.get("fontFaces")
    if not isinstance(declarations, list) or not declarations:
        raise ThemeError("Bundled font declarations are required.")
    for face in declarations:
        if (not isinstance(face, dict) or set(face) - {"family", "url", "style", "weight"}
                or not all(isinstance(face.get(key), str) for key in ("family", "url"))
                or type(face.get("weight")) is not int
                or not isinstance(face.get("style", "normal"), str)
                or _face_key(face) not in _font_inventory()):
            raise ThemeError("Unsupported font declaration. Choose a bundled font.")
    families = {face["family"] for face in declarations}

    def validate_section(section, name, shared=False, sidebar=False):
        if not isinstance(section, dict):
            raise ThemeError(f"{name} must be a table.")
        allowed = APPEARANCE_FIELDS | (SHARED_FIELDS | {"light", "dark"} if shared else set())
        if sidebar:
            allowed -= {"sidebar"}
        for key, value in section.items():
            if key not in allowed:
                raise ThemeError(f"{key} is not supported in [{name}].")
            if key in COLORS and (not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value)):
                raise ThemeError(f"{key}: enter a six-digit hex color, such as #0066CC.")
            if key in FONTS and (not isinstance(value, str) or value not in families):
                raise ThemeError(f"{key}: choose a declared bundled font.")
            if key in {"baseRadius", "buttonRadius"} and value not in RADIUS_OPTIONS:
                raise ThemeError("Choose a supported corner radius.")
            if key in {"showWidgetBorder", "showSidebarBorder"} and type(value) is not bool:
                raise ThemeError(f"{key} must be true or false.")
            if key == "base" and (not isinstance(value, str) or value not in {"light", "dark"}):
                raise ThemeError("Appearance must be light or dark.")
            if key == "sidebar":
                validate_section(value, f"{name}.sidebar", sidebar=True)
        if not sidebar and (not shared or not paired):
            for key in ("primaryColor", "backgroundColor", "secondaryBackgroundColor", "textColor"):
                if key not in section:
                    raise ThemeError(f"{key} is required in [{name}].")

    validate_section(theme, "theme", shared=True)
    if paired:
        for mode in ("light", "dark"):
            validate_section(theme[mode], f"theme.{mode}")
    elif "base" not in theme:
        raise ThemeError("Single-appearance exports require an explicit base.")
    for key in FONTS:
        if key not in theme:
            raise ThemeError(f"{key} is required in [theme].")


def paired_proof(light):
    """A small curated structure proof, not the full paired-mode editor."""
    shared = {key: deepcopy(value) for key, value in light.items() if key in FONTS | {"fontFaces", "showSidebarBorder", "showWidgetBorder", "baseRadius"}}
    shared["light"] = {key: deepcopy(value) for key, value in light.items() if key in COLORS | {"sidebar"}}
    shared["dark"] = {
        "primaryColor": "#60a5fa", "backgroundColor": "#0b1220",
        "secondaryBackgroundColor": "#182233", "textColor": "#e5edf7",
        "linkColor": "#93c5fd", "borderColor": "#334155", "codeBackgroundColor": "#121c2c",
        "sidebar": {"backgroundColor": "#101b2c", "secondaryBackgroundColor": "#1a2940"},
    }
    validate_theme(shared)
    return shared


def contrast_ratio(foreground, background):
    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
        return sum(v * weight for v, weight in zip(linear, (.2126, .7152, .0722)))
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + .05) / (dark + .05)


def contrast_advisories(theme):
    warnings = []
    sidebar = {**theme, **theme.get("sidebar", {})}
    pairs = [("Canvas text", theme["textColor"], theme["backgroundColor"]),
             ("Widget text", theme["textColor"], theme["secondaryBackgroundColor"]),
             ("Code text", theme["textColor"], theme["codeBackgroundColor"]),
             ("Sidebar text", sidebar["textColor"], sidebar["backgroundColor"]),
             ("Links", theme["linkColor"], theme["backgroundColor"]),
             ("Primary button text", "#ffffff", theme["primaryColor"])]
    for label, foreground, background in pairs:
        ratio = contrast_ratio(foreground, background)
        if ratio < 4.5:
            warnings.append(f"{label} contrast is {ratio:.1f}:1. Consider a lighter or darker color (4.5:1 reference for normal text).")
    return warnings


# Deliberately designed counterparts, not inversions or another preset's palette.
# The original appearance still comes directly from its canonical TOML.
COUNTERPARTS = {
    "healthcare": {
        "primaryColor": "#2563eb", "backgroundColor": "#0b1523",
        "secondaryBackgroundColor": "#172638", "textColor": "#e5edf5",
        "linkColor": "#93c5fd", "borderColor": "#3c5066", "codeBackgroundColor": "#132131",
        "sidebar": {"backgroundColor": "#101e2e", "secondaryBackgroundColor": "#203449", "textColor": "#e5edf5"}},
    "financial": {
        "primaryColor": "#4663a8", "backgroundColor": "#0d1424",
        "secondaryBackgroundColor": "#1a263b", "textColor": "#eef2fa",
        "linkColor": "#a7bfff", "borderColor": "#394b69", "codeBackgroundColor": "#152036",
        "sidebar": {"backgroundColor": "#131f34", "secondaryBackgroundColor": "#243550", "textColor": "#eef2fa"}},
    "dark-mode": {
        "primaryColor": "#7e22ce", "backgroundColor": "#faf9fc",
        "secondaryBackgroundColor": "#f0edf5", "textColor": "#242033",
        "linkColor": "#6b21a8", "borderColor": "#d3cbdc", "codeBackgroundColor": "#ece8f2",
        "sidebar": {"backgroundColor": "#f2eef8", "secondaryBackgroundColor": "#e7e0f1", "textColor": "#242033"}},
}


def preset_draft(slug):
    """Fresh session data; palettes vary by mode and typography is shared."""
    source = load_theme(slug)
    mode = get_preset(slug).appearance
    variant = {key: deepcopy(value) for key, value in source.items()
               if key in COLORS | {"baseRadius", "showWidgetBorder", "sidebar"}}
    variant["buttonRadius"] = source["baseRadius"]
    variant["sidebar"].setdefault("textColor", source["textColor"])
    variant["sidebar_custom"] = True
    variants = {mode: variant}
    if slug in EDITABLE_PRESETS:
        opposite = "dark" if mode == "light" else "light"
        variants[opposite] = {**deepcopy(variant), **deepcopy(COUNTERPARTS[slug])}
    return {"variants": variants, "fonts": {key: source[key] for key in sorted(FONTS)},
            "showSidebarBorder": source["showSidebarBorder"], "appearance": mode, "output": "single"}


def draft_theme(draft, *, appearance=None, output=None):
    """Materialize explicit sidebars; never depend on Streamlit's color swap."""
    output = output or draft["output"]
    appearance = appearance or draft["appearance"]
    if output not in {"single", "paired"} or appearance not in {"light", "dark"}:
        raise ThemeError("Choose a single appearance or a light/dark pair.")
    fonts = draft["fonts"]
    if (set(fonts) != FONTS or fonts["font"] not in FONT_CHOICES
            or fonts["headingFont"] not in FONT_CHOICES or fonts["codeFont"] not in CODE_FONT_CHOICES):
        raise ThemeError("Choose a supported bundled body, heading and code font.")
    families = set(fonts.values())
    theme = {**fonts, "showSidebarBorder": draft["showSidebarBorder"],
             "fontFaces": [deepcopy(face) for face, _, _ in _font_inventory().values() if face["family"] in families]}

    def variant(mode):
        if mode not in draft["variants"]:
            raise ThemeError(f"A {mode} palette is required for this export.")
        result = deepcopy(draft["variants"][mode])
        custom = result.pop("sidebar_custom")
        if type(custom) is not bool:
            raise ThemeError("Choose whether to customize sidebar colors.")
        if not custom:
            result["sidebar"] = {key: result[key] for key in ("backgroundColor", "secondaryBackgroundColor", "textColor")}
        return result

    if output == "paired":
        theme.update(light=variant("light"), dark=variant("dark"))
    else:
        theme.update(variant(appearance), base=appearance)
    validate_theme(theme)
    return theme


def draft_changes(slug, draft):
    """Readable differences, including edits in the currently hidden mode."""
    original = preset_draft(slug)
    changes = []

    labels = {"variants": "", "light": "Light", "dark": "Dark", "fonts": "Typography",
              "font": "Body font", "headingFont": "Heading font", "codeFont": "Code font",
              "primaryColor": "Accent", "backgroundColor": "Canvas", "secondaryBackgroundColor": "Surface",
              "textColor": "Text", "linkColor": "Links", "borderColor": "Borders", "codeBackgroundColor": "Code canvas",
              "baseRadius": "Corner radius", "buttonRadius": "Button radius", "showWidgetBorder": "Widget borders",
              "sidebar": "Sidebar", "sidebar_custom": "Custom sidebar colors", "showSidebarBorder": "Sidebar divider",
              "appearance": "Active appearance", "output": "Download format"}

    def compare(before, after, prefix=()):
        for key, value in before.items():
            path = (*prefix, key)
            if isinstance(value, dict):
                compare(value, after[key], path)
            elif value != after[key]:
                label = " · ".join(labels.get(part, part) for part in path if labels.get(part, part))
                changes.append({"Setting": label, "Preset": str(value), "Current": str(after[key])})

    # Selecting which half of a pair to edit does not change the package.
    if draft["output"] == "paired":
        original["appearance"] = draft["appearance"]
    compare(original, draft)
    return changes
