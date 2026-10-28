# Studio development and installation

The [main README](../README.md) introduces the product. All ten starting themes support the same editor, single/paired exports and complete font packages. This page adds development and installation details.

## Run locally

From the repository root, using Python 3.13:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m studio
```

Open http://localhost:8501. The launcher prepares the fixed shell's font assets from the original Financial theme and uses the Studio's own config directory. Generated files stay in ignored `studio/static/`; canonical assets live under `themes/`. Original demos retain `themes/requirements-legacy.txt` and their own [collection instructions](../themes/README.md).

Tested runtime: **Streamlit 1.66.1 / Python 3.13.12**. This is an exact tested target, not a promise of compatibility with every release. Configuration is validated and serialized with `tomli-w`.

## Try the Studio

1. Start in **All 10 themes**, then choose Healthcare (or another original theme) to open the Studio. The fixed shell uses Financial.
2. Adjust Accent or Canvas. That is all you need for a quick variation; the other controls stay collapsed.
3. Choose **Only light** / **Only dark** for the selected design or **Light + dark** for a switchable pair. **Edit appearance** changes which palette you are working on; each keeps its own colors. The original appearance comes from the repository, with small contrast refinements for readability; each counterpart is a Studio starting point. Historical demos remain untouched.
4. Optionally open **Typography & shape**, **Sidebar**, or **Advanced**. Each font picker offers the theme’s own font and a few bundled alternatives. Typography and the sidebar divider are shared across appearances. Colors, corners and widget borders belong to the appearance you are editing.
5. Switch Dashboard / Components, or compare **Current edits** with **Preset defaults**. Comparing does not replace your edits or change the download. Reset restores the whole preset, including both appearances.
6. Browse **All 10 themes** and choose another preset. If you have changes, choose **Keep editing** or explicitly discard them before switching.

The preview is an HTML/CSS approximation of built-in Streamlit elements. Native widgets, chart palettes, sizes and responsive behavior may differ. It is not a second running Streamlit app. Your original preset screenshots and demos are preserved.

## Export and install

For any of the ten themes, use **Download package**. The ZIP contains `.streamlit/config.toml`, only the referenced font files, applicable licenses/notices, and installation steps. **Configuration & installation** provides the exact same TOML with a native copy button. Use the complete ZIP to install the fonts.

Unzip into your app's project root, keeping `.streamlit/`, `static/`, and `licenses/` together. Back up an existing config before replacing it. Run Streamlit from that directory and restart after font/config changes. For a paired export, open your app's menu at the top right and choose **Light** or **Dark**. A single export includes only the appearance selected in the Studio.

The sidebar's custom canvas, surface and text colors are explicit. Turning off **Customize sidebar colors** makes them match the main appearance exactly; your custom values are retained if you turn it back on. Other sidebar settings inherit from that appearance. Shared font declarations are written once, with per-mode values in valid light/dark tables.

Missing assets or notices block downloads. Contrast advisories flag common text/background combinations; they do not certify accessibility and do not block otherwise valid exports. Your choices last for the current session; there is no account or durable save.

For native rendering checks, copy `studio/sample_app.py` into a separate project after installing an exported package, then run `streamlit run sample_app.py` from that project's root. The sample uses native widgets and synthetic data without custom CSS.

## Managed hosting

The deployment target is a single DigitalOcean App Platform **Python web service** using its managed buildpack. Keep the source directory at the repository root (`/`): the Studio needs the sibling `themes/` and `licenses/` directories. Root `requirements.txt` supplies dependencies; `runtime.txt` pins the tested Python version. Leave the custom build command empty so the buildpack installs dependencies normally.

Set the HTTP port to **8080** and the run command to:

```bash
python -m studio --server.address=0.0.0.0 --server.port=8080
```

Use `/_stcore/health` for the HTTP health check. One instance is sufficient for the initial deployment; no database, worker, persistent disk or separate frontend is required. No Dockerfile or Docker tooling is needed. Keep automatic deployment off while reviewing the initial hosted candidate. Deploy only after approving the provider's current pricing and the exact source revision.

Streamlit session state is held in memory. Restarts, redeploys or a new session may lose unsaved edits. The health endpoint confirms the server is running; verify the actual editor, WebSocket connection, downloads and memory usage on the host before release.

The website exposes the Studio, its displayed media/downloads and the public font assets in `studio/static/`. It does not expose a directory browser or arbitrary repository files. Unknown URLs may display the Studio shell rather than return a file. The full source, READMEs and original collection remain publicly available on GitHub.

See DigitalOcean's [Python buildpack](https://docs.digitalocean.com/products/app-platform/reference/buildpacks/python/), [pricing](https://docs.digitalocean.com/products/app-platform/details/pricing/) and [deployment/rollback instructions](https://docs.digitalocean.com/products/app-platform/how-to/manage-deployments/).

## Development checks

```bash
.venv/bin/python -m pip install -r studio/requirements-dev.txt
.venv/bin/python scripts/audit_baseline.py
.venv/bin/python -m pytest -q
```

See [third-party notices](../THIRD_PARTY_NOTICES.md) for preserved licensing.
