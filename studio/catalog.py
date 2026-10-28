"""Read-only catalog. Original theme directories remain the source of truth."""

from dataclasses import dataclass
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
THEMES = ROOT / "themes"


@dataclass(frozen=True)
class Preset:
    slug: str
    name: str
    description: str
    appearance: str = "light"
    image_name: str | None = None

    @property
    def directory(self) -> Path:
        return THEMES / self.slug

    @property
    def image(self) -> Path:
        return self.directory / (self.image_name or f"{self.slug}.png")

    @property
    def gallery_image(self) -> Path:
        return ROOT / "studio/assets/previews" / f"{self.slug}.webp"


PRESETS = (
    Preset("healthcare", "Healthcare", "Calm blue. Clear, clinical typography."),
    Preset("financial", "Financial", "Deep navy for considered decisions."),
    Preset("dark-mode", "Dark Mode Developer", "A familiar home for developer tools.", "dark", "dark-mode-dev.png"),
    Preset("editorial", "Editorial", "Expressive serif type. A publishing sensibility."),
    Preset("saas-startup", "SaaS / Startup", "Confident purple with softer corners."),
    Preset("bootstrap", "Bootstrap", "Classic blue. Instantly familiar."),
    Preset("tailwind", "Tailwind", "Crisp slate tones and modern spacing."),
    Preset("material-design", "Material Design", "A clean, systematic visual language."),
    Preset("cyberpunk", "Cyberpunk", "Neon accents after dark.", "dark"),
    Preset("toddler", "Toddler Friendly", "Warm colors with a playful personality."),
)


def get_preset(slug: str) -> Preset:
    return next(p for p in PRESETS if p.slug == slug)


def load_theme(slug: str) -> dict:
    """Return a fresh dict every time, safe for visitor-local edits."""
    with (get_preset(slug).directory / ".streamlit/config.toml").open("rb") as handle:
        return tomllib.load(handle)["theme"]
