# Awesome Streamlit Theme Studio — preview

Browse ten original themes and try an isolated visual preview. Healthcare, Financial and Dark Mode Developer support the complete customize-and-export flow. The other seven retain concept previews while representative breadth is under review.

## Run locally

From the repository root, using Python 3.13:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r studio/requirements.txt
.venv/bin/python -m studio
```

Open http://localhost:8501. The launcher prepares the fixed shell's font assets from the original Financial theme and uses the Studio's own config directory. Generated files stay in ignored `studio/static/`; the ten canonical theme folders remain unchanged. The original demos retain their separate root `requirements.txt` and run instructions.

Tested runtime: **Streamlit 1.66.1 / Python 3.13.12**. This is an exact tested target, not a promise of compatibility with every release. Configuration is validated and serialized with `tomli-w`.

## Try the Studio

1. Start in **All 10 themes**, then choose Healthcare (or another original theme) to open the Studio. The fixed shell uses Financial.
2. Adjust Accent or Canvas. That is all you need for a quick variation; the other controls stay collapsed.
3. Choose **This appearance** for one design or **Light + dark** for a switchable pair. **Edit appearance** changes which palette you are working on; each keeps its own colors. The original appearance comes from the repository; its counterpart is a curated Studio starting point.
4. Optionally open **Typography & shape**, **Sidebar**, or **Advanced**. There are three bundled body/heading font choices and three code font choices. Typography and the sidebar divider are shared across appearances. Colors, corners and widget borders belong to the appearance you are editing.
5. Switch Dashboard / Components, or compare **Current edits** with **Preset defaults**. Comparing does not replace your edits or change the download. Reset restores the whole preset, including both appearances.
6. Browse **All 10 themes** and choose another preset. If you have changes, choose **Keep editing** or explicitly discard them before switching.

The preview is an HTML/CSS approximation of built-in Streamlit elements. Native widgets, chart palettes, sizes and responsive behavior may differ. It is not a second running Streamlit app. Your original preset screenshots and demos are preserved.

## Export and install

For Healthcare, Financial or Dark Mode Developer, use **Download package**. The ZIP contains `.streamlit/config.toml`, only the referenced font files, applicable licenses/notices, and installation steps. **Configuration & installation** provides the exact same TOML with a native copy button. Use the complete ZIP to install the fonts.

Unzip into your app's project root, keeping `.streamlit/`, `static/`, and `licenses/` together. Back up an existing config before replacing it. Run Streamlit from that directory and restart after font/config changes. For a paired export, open your app's menu at the top right and choose **Light** or **Dark**. A single export includes only the appearance selected in the Studio.

The sidebar's custom canvas, surface and text colors are explicit. Turning off **Customize sidebar colors** makes them match the main appearance exactly; your custom values are retained if you turn it back on. Other sidebar settings inherit from that appearance. Shared font declarations are written once, with per-mode values in valid light/dark tables.

Missing assets or notices block downloads. Contrast advisories flag common text/background combinations; they do not certify accessibility and do not block otherwise valid exports. Your choices last for the current session; there is no account or durable save.

For native rendering checks, copy `studio/sample_app.py` into a separate project after installing an exported package, then run `streamlit run sample_app.py` from that project's root. The sample uses native widgets and synthetic data without custom CSS.

## Development checks

```bash
.venv/bin/python -m pip install -r studio/requirements-dev.txt
.venv/bin/python scripts/audit_baseline.py
.venv/bin/python -m pytest -q
```

See [third-party notices](../THIRD_PARTY_NOTICES.md) for preserved licensing.
