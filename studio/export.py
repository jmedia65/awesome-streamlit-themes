"""Deterministic config and complete asset packages from validated theme data."""

from io import BytesIO
import tomllib
import zipfile

import tomli_w

from studio.catalog import ROOT
from studio.theme import ThemeError, font_asset, validate_theme

TARGET = "1.66.1"


def config_bytes(theme):
    validate_theme(theme)
    document = {"server": {"enableStaticServing": True}, "theme": theme}
    text = f"# Theme Studio — tested with Streamlit {TARGET}\n" + tomli_w.dumps(document)
    # st.code's native copy action strips surrounding newlines. Match those
    # exact bytes in the package; TOML does not require a final newline.
    data = text.rstrip("\n").encode("utf-8")
    if tomllib.loads(data.decode("utf-8")) != document:
        raise ThemeError("Configuration did not round-trip. Export was stopped.")
    return data


INSTALL = """# Install your Streamlit theme

Tested with Streamlit 1.66.1 and Python 3.13.

1. Unzip this package into your app's project directory. Merge files carefully;
   back up an existing .streamlit/config.toml before replacing it.
2. Keep .streamlit/config.toml, static/, and licenses/ together at project root.
3. From that directory run: streamlit run your_app.py
4. Restart the server after changing font declarations or configuration.

The app/static/ URLs in config.toml map to the included static/ folder.
Static serving is enabled. You do not need to clone the Theme Studio repository.
For a paired theme, open the app menu (top right) and choose Light or Dark.

The Studio preview is approximate. Native widgets, font scaling, charts and
responsive behavior can differ. Review the result in your own app.

Fonts remain under their included SIL Open Font Licenses. Original font notices,
actual binary copyright metadata and the repository's MIT notice are included.
Source: https://github.com/jmedia65/awesome-streamlit-themes
"""


def export_package(theme, root=ROOT):
    """Return the exact displayed TOML bytes and its self-contained ZIP."""
    data = config_bytes(theme)
    files = {".streamlit/config.toml": data, "README.md": INSTALL.encode("utf-8")}

    def include(destination, source):
        if not source.is_file():
            raise ThemeError(f"Missing required asset or notice: {source.name}. Export was stopped.")
        content = source.read_bytes()
        if destination in files and files[destination] != content:
            raise ThemeError("Conflicting font assets. Export was stopped.")
        files[destination] = content

    for face in theme["fontFaces"]:
        path = font_asset(face, root)
        include("static/" + path.name, path)
        family = face["family"]
        include(f"licenses/OFL-{family.lower()}.txt", root / "licenses/fonts" / f"OFL-{family.lower()}.txt")
        include(f"licenses/original-{family}.txt", path.parent / f"OFL-{family}.txt")
    include("licenses/FONT_NOTICES.md", root / "licenses/FONT_NOTICES.md")
    include("LICENSE", root / "LICENSE")
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return data, stream.getvalue()
