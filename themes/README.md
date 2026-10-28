# Original themes and standalone demos

The [Theme Studio](../README.md) is the main application: choose a starting theme, customize it, and download a complete package.

This collection contains the ten original configurations, bundled fonts, screenshots and standalone Streamlit demos. The Studio reads these canonical assets; it does not keep a second copy of the presets. The standalone demos retain their original design and code. Studio palettes may include small contrast refinements and curated light/dark counterparts.

| Theme | Original appearance | Original typography |
|---|---|---|
| [Healthcare](healthcare/) | Light | IBM Plex Sans / IBM Plex Mono |
| [Financial](financial/) | Light | Inter / Source Code Pro |
| [Dark Mode Developer](dark-mode/) | Dark | Inter / JetBrains Mono |
| [Editorial](editorial/) | Light | Lora / Playfair Display |
| [SaaS / Startup](saas-startup/) | Light | DM Sans / Fira Code |
| [Bootstrap](bootstrap/) | Light | Inter / JetBrains Mono |
| [Tailwind](tailwind/) | Light | Inter / JetBrains Mono |
| [Material Design](material-design/) | Light | Roboto / Roboto Mono |
| [Cyberpunk](cyberpunk/) | Dark | Orbitron / Source Code Pro |
| [Toddler Friendly](toddler/) | Light | Comic Neue / Fredoka |

## Run an original demo

From the repository root, in a separate virtual environment:

```bash
python3.13 -m venv .venv-legacy
source .venv-legacy/bin/activate
python -m pip install -r themes/requirements-legacy.txt
cd themes/healthcare
streamlit run streamlit_app.py
```

On Windows, use `.venv-legacy\Scripts\Activate.ps1` to activate the environment. Replace `healthcare` with another folder from the table. Run from inside the chosen theme directory so Streamlit finds its configuration and fonts. These original demos also receive smoke checks on the Studio's current target runtime; they retain the historical dependency manifest for reproduction.

## Use an original theme manually

Copy the chosen theme's `.streamlit/config.toml` and `static/` files into your app's project root. Keep the applicable font licenses and notices from [third-party notices](../THIRD_PARTY_NOTICES.md). Back up an existing configuration before replacing it, run Streamlit from that project directory, and restart after configuration/font changes.

For a customized, self-contained package with the required notices included, use the Studio instead.

## Exact pre-Studio repository

[Browse the original repository snapshot](https://github.com/jmedia65/awesome-streamlit-themes/tree/6e6fcfe3464103924301834b64ccae925d49ed60). To run that exact version after cloning, check out that commit before following its historical README. Root-level theme paths changed intentionally when the Studio became the primary product.

Original source/configuration/font/license contents are preserved. Documentation paths were updated for this layout. See [LICENSE](../LICENSE) and [third-party notices](../THIRD_PARTY_NOTICES.md).
