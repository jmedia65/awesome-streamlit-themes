"""Per-session theme design, isolated preview, and portable exports."""

import streamlit as st

from studio.catalog import PRESETS, get_preset, load_theme
from studio.export import export_package
from studio.preview import render_preview
from studio.theme import (RADIUS_OPTIONS, ThemeError, contrast_advisories, draft_changes,
                          draft_theme, font_choices, preset_draft)

st.set_page_config(page_title="Theme Studio · Awesome Streamlit Themes", page_icon="◈", layout="wide")

# Fixed shell polish only; no CSS is derived from visitor edits.
st.html("""<style>
.stMainBlockContainer{max-width:1420px;padding-top:2rem;padding-bottom:2rem}
h1{letter-spacing:-1.5px;font-weight:650!important;font-size:2.65rem!important;line-height:1.12!important}
h2{letter-spacing:-.6px;font-size:1.45rem!important}h3{font-size:1.05rem!important}
.st-key-controls{background:#f8fafc}.st-key-preview_frame{padding:0!important;overflow:hidden}
/* Streamlit 1.66.1: replace only the single HEX field's visible caption.
   Keep the native input/label association and RGB/HSL captions intact. */
[data-testid="stColorPickerPopover"] .flexbox-fix > div:only-child > div:has(> input) > label{
font-size:0!important;text-transform:none!important}
[data-testid="stColorPickerPopover"] .flexbox-fix > div:only-child > div:has(> input) > label::after{
content:" Press Esc to confirm";font-size:11px;line-height:11px}
@media(max-width:700px){.stMainBlockContainer{padding:1.4rem 1rem}h1{font-size:2rem!important}}
</style>""")

CONTROL_FIELDS = {
    "accent": ("primaryColor",), "background": ("backgroundColor",),
    "surface": ("secondaryBackgroundColor",), "text": ("textColor",),
    "link": ("linkColor",), "border": ("borderColor",), "code_background": ("codeBackgroundColor",),
    "radius": ("baseRadius",), "button_radius": ("buttonRadius",), "widget_border": ("showWidgetBorder",),
    "sidebar_custom": ("sidebar_custom",), "sidebar_background": ("sidebar", "backgroundColor"),
    "sidebar_surface": ("sidebar", "secondaryBackgroundColor"), "sidebar_text": ("sidebar", "textColor"),
}
FONT_FIELDS = {"body_font": "font", "heading_font": "headingFont", "code_font": "codeFont"}

if "preset" not in st.session_state:
    st.session_state.preset = "healthcare"
if "workspace" not in st.session_state:
    st.session_state.workspace = "All 10 themes"
if "draft" not in st.session_state:
    st.session_state.draft = preset_draft(st.session_state.preset)
    # Keep valid edits from a running Stage 2 session during this local upgrade.
    old = st.session_state.get("concept_values", {})
    variant = st.session_state.draft["variants"][st.session_state.draft["appearance"]]
    for key in ("accent", "background", "radius"):
        if key in old:
            variant[CONTROL_FIELDS[key][0]] = old[key]
    if st.session_state.preset == "healthcare" and old:
        st.session_state.draft["fonts"].update(font=old["body_font"], headingFont=old["body_font"])
        variant["sidebar"]["backgroundColor"] = old["sidebar_background"]


def hydrate_controls(force=False):
    """Sync widgets from durable session data after mode changes and cleanup."""
    draft = st.session_state.draft
    context = (st.session_state.preset, draft["appearance"], st.session_state.workspace)
    force = force or st.session_state.get("controls_for") != context
    variant = draft["variants"][draft["appearance"]]
    for widget, path in CONTROL_FIELDS.items():
        if force or widget not in st.session_state:
            st.session_state[widget] = variant[path[0]] if len(path) == 1 else variant[path[0]][path[1]]
    for widget, field in FONT_FIELDS.items():
        if force or widget not in st.session_state:
            st.session_state[widget] = draft["fonts"][field]
    for widget, value in (("edit_appearance", draft["appearance"]), ("export_scope", draft["output"]),
                          ("sidebar_border", draft["showSidebarBorder"]), ("preset_picker", st.session_state.preset)):
        if force or widget not in st.session_state:
            st.session_state[widget] = value
    st.session_state.controls_for = context


def reset_controls():
    st.session_state.draft = preset_draft(st.session_state.preset)
    st.session_state.preview_source = "Current edits"
    st.session_state.pending_preset = None
    hydrate_controls(force=True)


def apply_preset(slug):
    st.session_state.preset = slug
    st.session_state.workspace = "Studio"
    reset_controls()


def choose_preset(slug):
    current = st.session_state.preset
    if slug == current:
        st.session_state.workspace = "Studio"
    elif draft_changes(current, st.session_state.draft):
        st.session_state.pending_preset = slug
        st.session_state.preset_picker = current
    else:
        apply_preset(slug)


def store_control(widget, appearance):
    path = CONTROL_FIELDS[widget]
    draft = st.session_state.draft
    variant = draft["variants"][appearance]
    if len(path) == 1:
        variant[path[0]] = st.session_state[widget]
    else:
        variant[path[0]][path[1]] = st.session_state[widget]


def store_font(widget):
    st.session_state.draft["fonts"][FONT_FIELDS[widget]] = st.session_state[widget]


def store_choice(widget, field):
    st.session_state.draft[field] = st.session_state[widget]
    # Rehydrate in the script after all callbacks finish. A pending color edit
    # and a mode change may arrive together; both must keep their original mode.


def color_controls(fields, disabled=False):
    with st.container(horizontal=True, wrap=True, gap="medium"):
        for key, label in fields:
            with st.container(width=104, gap="xsmall"):
                value = st.color_picker(label, key=key, disabled=disabled, on_change=store_control, args=(key, mode))
                st.caption(value.upper())


hydrate_controls()
selected = get_preset(st.session_state.preset)
draft = st.session_state.draft
mode = draft["appearance"]
variant = draft["variants"][mode]
changes = draft_changes(selected.slug, draft)

with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="distribute"):
    st.markdown("**◈ &nbsp; THEME STUDIO**", width="content")
    st.link_button("Star on GitHub ↗", "https://github.com/jmedia65/awesome-streamlit-themes", type="tertiary")

st.title("Your app. A better first impression.")
st.markdown("Start with a considered theme. Make it yours. Bring it to your next Streamlit app.")
st.segmented_control("Workspace", ["Studio", "All 10 themes"], key="workspace", required=True, label_visibility="collapsed")

pending = st.session_state.get("pending_preset")
if pending:
    with st.container(border=True):
        st.warning(f"You have unsaved changes to {selected.name}. Switching to {get_preset(pending).name} replaces them, including both appearances. Download first if you want to keep them.")
        with st.container(horizontal=True):
            st.button("Discard edits and switch", key="discard_switch", type="primary", on_click=apply_preset, args=(pending,))
            st.button("Keep editing", key="cancel_switch", on_click=lambda: st.session_state.update(pending_preset=None))

if st.session_state.workspace == "All 10 themes":
    st.subheader("A starting point for every kind of app.")
    st.caption("Ten original themes, shown in the Studio’s approximate preview.")
    for offset in range(0, len(PRESETS), 3):
        columns = st.columns(3, gap="medium")
        for column, preset in zip(columns, PRESETS[offset:offset + 3]):
            with column, st.container(border=True):
                if preset.gallery_image.is_file():
                    st.image(str(preset.gallery_image), width="stretch", output_format="PNG",
                             alt=f"{preset.name} Dashboard in the Studio’s approximate preview")
                else:
                    st.caption("Preview image unavailable. You can still use this theme.")
                st.markdown(f"### {preset.name}")
                st.caption(preset.description)
                st.button("Selected · Open studio" if preset == selected else "Use this theme →",
                          key=f"choose_{preset.slug}", width="stretch",
                          type="primary" if preset == selected else "secondary",
                          on_click=choose_preset, args=(preset.slug,))
else:
    controls, canvas = st.columns([1, 2.4], gap="large", vertical_alignment="top")
    with controls:
        with st.container(border=True, key="controls", gap="xsmall"):
            st.markdown("### 01 · Make it yours")
            st.selectbox("Starting theme", [p.slug for p in PRESETS],
                         format_func=lambda slug: get_preset(slug).name, key="preset_picker",
                         on_change=lambda: choose_preset(st.session_state.preset_picker))
            st.caption(selected.description)
            st.caption(f"{len(changes)} setting{'s' if len(changes) != 1 else ''} changed · session only" if changes else "Preset defaults · ready to try")
            st.radio("Include in your download:", ["single", "paired"], key="export_scope", horizontal=True,
                     format_func=lambda value: f"Only {mode}" if value == "single" else "Light + dark",
                     on_change=store_choice, args=("export_scope", "output"))
            st.segmented_control("Edit appearance", ["light", "dark"], key="edit_appearance", required=True,
                                 format_func=str.capitalize, on_change=store_choice, args=("edit_appearance", "appearance"))
            st.caption("Light and dark have separate colors.")
            st.markdown("**Colors**")
            color_controls([("accent", "Accent"), ("background", "Canvas")])
            with st.expander("Typography & shape"):
                st.caption("Fonts apply to both appearances and the sidebar.")
                for key, label, options in (("heading_font", "Heading font", font_choices(selected.slug, "headingFont")),
                                            ("body_font", "Body font", font_choices(selected.slug, "font")),
                                            ("code_font", "Code font", font_choices(selected.slug, "codeFont"))):
                    st.selectbox(label, list(options), key=key, format_func=options.get,
                                 on_change=store_font, args=(key,))
                st.select_slider("Corner radius", options=RADIUS_OPTIONS, key="radius", on_change=store_control, args=("radius", mode))
                st.select_slider("Button radius", options=RADIUS_OPTIONS, key="button_radius", on_change=store_control, args=("button_radius", mode))
            with st.expander("Sidebar"):
                st.checkbox("Customize sidebar colors", key="sidebar_custom", on_change=store_control, args=("sidebar_custom", mode))
                st.caption("Custom colors affect this appearance only. Turn off to match the main canvas, surface and text exactly; your custom values are kept.")
                color_controls([("sidebar_background", "Sidebar canvas"), ("sidebar_surface", "Sidebar surface"),
                                ("sidebar_text", "Sidebar text")], disabled=not variant["sidebar_custom"])
                st.caption("Accent, links, borders and fonts inherit the main appearance.")
            with st.expander("Advanced"):
                color_controls([("text", "Text"), ("link", "Links"), ("border", "Borders"),
                                ("surface", "Surface"), ("code_background", "Code canvas")])
                st.checkbox("Show widget borders", key="widget_border", on_change=store_control, args=("widget_border", mode))
                st.checkbox("Show sidebar divider · both appearances", key="sidebar_border", on_change=store_choice,
                            args=("sidebar_border", "showSidebarBorder"))
            st.button("Reset to preset", on_click=reset_controls, type="tertiary", width="stretch")
            if changes:
                with st.expander("Changes from preset"):
                    st.dataframe(changes, hide_index=True)

    working_theme = None
    export_data = None
    try:
        working_theme = draft_theme(draft)
        export_data = export_package(working_theme)
    except (ThemeError, OSError) as error:
        st.error(str(error) if isinstance(error, ThemeError) else "A required asset is unavailable. Export was stopped.")
    with canvas:
        with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
            st.markdown("### 02 · See it in context")
            view = st.segmented_control("Preview example", ["Dashboard", "Components"], key="preview_view",
                                        default="Dashboard", required=True, label_visibility="collapsed")
        st.session_state.setdefault("preview_source", "Current edits")
        source = st.segmented_control("Compare with preset", ["Current edits", "Preset defaults"], key="preview_source",
                                      required=True, label_visibility="collapsed")
        st.caption(f"{selected.name} · {mode.capitalize()} appearance · {source} · Approximate preview")
        if source == "Preset defaults":
            st.caption("Showing the starting palette for this appearance. Your edits and download are unchanged.")
        with st.container(border=True, key="preview_frame"):
            try:
                preview_draft = preset_draft(selected.slug) if source == "Preset defaults" else draft
                preview_theme = draft_theme(preview_draft, appearance=mode, output="single")
                st.iframe(render_preview(selected.slug, preview_theme["primaryColor"], preview_theme["backgroundColor"],
                                         preview_theme["baseRadius"], view, preview_theme),
                          height="content", alt=f"Approximate {selected.name} {mode} {view.lower()} preview")
            except (ThemeError, OSError) as error:
                st.error(str(error) if isinstance(error, ThemeError) else "A preview font is unavailable. Restore the asset and try again.")
        st.caption("HTML/CSS approximation of built-in Streamlit elements. Native widgets, charts, sizing and responsive behavior may differ.")
        if working_theme:
            modes = ("light", "dark") if draft["output"] == "paired" else (mode,)
            for appearance in modes:
                for advisory in contrast_advisories(draft_theme(draft, appearance=appearance, output="single")):
                    st.warning(f"{appearance.capitalize()} · {advisory}")
            st.caption("Contrast checks are guidance for common text/background pairs, not accessibility certification.")

    with st.container(border=True, horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
        st.markdown("**03 · Take it to your app** &nbsp; — &nbsp; Configuration, fonts, licenses, and installation steps.")
        if export_data:
            suffix = "light-dark" if draft["output"] == "paired" else mode
            st.download_button("Download package ↓", export_data[1], file_name=f"{selected.slug}-{suffix}-theme.zip",
                               mime="application/zip", type="primary", on_click="ignore")
        else:
            st.button("Download package ↓", disabled=True, type="primary")
    if export_data:
        with st.expander("Configuration & installation"):
            includes = "Light + dark · switch appearances in your app’s menu" if draft["output"] == "paired" else f"Single {mode} appearance"
            st.caption(f"Streamlit 1.66.1 · {includes}. The copy button copies this exact package configuration.")
            st.code(export_data[0].decode("utf-8"), language="toml", height=260)
            st.markdown("Unzip into your project root, keeping `.streamlit/config.toml`, `static/`, and `licenses/` together. "
                        "Back up an existing config before replacing it. Run Streamlit from that directory and restart after font/config changes. "
                        "The configuration references bundled fonts; use the complete ZIP for installation.")

st.divider()
with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
    st.caption("Awesome Streamlit Themes · by [Max Braglia](https://maxbraglia.com/). Your edits last for this session; refreshing or leaving may lose them. Download to keep your theme.")
    st.markdown("[Source & credits](https://github.com/jmedia65/awesome-streamlit-themes) &nbsp; · &nbsp; "
                "[Feedback](https://github.com/jmedia65/awesome-streamlit-themes/issues)")
