"""Controlled, isolated HTML approximation of supported theme settings."""

import base64
from copy import deepcopy
from html import escape
import re

from studio.catalog import get_preset, load_theme
from studio.theme import RADIUS_OPTIONS, font_asset, validate_theme


def render_preview(slug: str, primary: str, background: str, radius: str, view: str, theme_override=None) -> str:
    # Values are CSS literals only after validation. No visitor markup or URLs.
    if not all(re.fullmatch(r"#[0-9a-fA-F]{6}", color) for color in (primary, background)):
        raise ValueError("Use a six-digit hex color.")
    if radius not in RADIUS_OPTIONS:
        raise ValueError("Choose a supported radius.")
    theme = deepcopy(theme_override) if theme_override is not None else load_theme(slug)
    preset = get_preset(slug)
    theme.setdefault("base", preset.appearance)
    theme.update(primaryColor=primary, backgroundColor=background, baseRadius=radius)
    validate_theme(theme)
    sidebar = {**theme, **theme.get("sidebar", {})}
    widget_border = theme['borderColor'] if theme['showWidgetBorder'] else 'transparent'
    sidebar_border = '1px' if theme.get('showSidebarBorder', True) else '0'
    font_css = []
    # Inline trusted font bytes keeps the preview independent of static routes.
    for face in theme["fontFaces"]:
        if face["weight"] not in (400, 700):
            continue
        data = font_asset(face).read_bytes()
        encoded = base64.b64encode(data).decode("ascii")
        font_css.append(f"@font-face{{font-family:'{face['family']}';font-style:normal;"
                        f"font-weight:{face['weight']};src:url(data:font/ttf;base64,{encoded})}}")
    if view == "Components":
        content = """
        <div class="eyebrow">WORKSPACE / NEW REPORT</div>
        <h1>Make room for good work.</h1><p class="muted">A few everyday components, in your theme.</p>
        <section class="card"><h2>Create a report</h2><div class="form-grid">
        <label>Report name<input value="Monthly overview" readonly></label>
        <label>Workspace<select aria-label="Workspace"><option>Product team</option></select></label>
        </div><label class="check"><input type="checkbox" checked> Include a comparison with last month</label>
        <div class="actions"><button class="primary">Create report</button><button>Cancel</button></div></section>
        <section class="card"><h2>A little code, beautifully set</h2>
        <pre><code>import streamlit as st\n\nst.title("Made for your next idea.")</code></pre></section>
        <p><a href="#reporting-guide">View reporting guide</a></p>
        <p class="muted" id="reporting-guide">Preview controls illustrate appearance. They do not submit data.</p>
        """
    else:
        content = """
        <div class="topline"><div class="eyebrow">WORKSPACE / OVERVIEW</div><span class="period">Last 30 days</span></div>
        <h1>A clearer view of your work.</h1><p class="muted">Your team's progress, at a glance.</p>
        <div class="metrics"><section class="card"><span>Total revenue</span><strong>$48,620</strong><small>↑ 12.8% this month</small></section>
        <section class="card"><span>Active projects</span><strong>24</strong><small>↑ 4 this month</small></section>
        <section class="card"><span>Completion rate</span><strong>94.2%</strong><small>↑ 3.1% this month</small></section></div>
        <section class="card"><div class="topline"><h2>Revenue over time</h2><span class="muted">Weekly</span></div>
        <div class="chart" role="img" aria-label="Illustrative revenue bar chart, rising from week 1 to week 8">
        <i style="height:35%"></i><i style="height:48%"></i><i style="height:42%"></i><i style="height:62%"></i>
        <i style="height:54%"></i><i style="height:77%"></i><i style="height:68%"></i><i style="height:93%"></i></div>
        <div class="axis"><span>Week 1</span><span>Week 8</span></div></section>
        <section class="card"><div class="topline"><h2>Recent projects</h2><button class="primary">New project</button></div>
        <table><thead><tr><th>Project</th><th>Owner</th><th>Status</th></tr></thead><tbody>
        <tr><td>Website refresh</td><td>Alex Kim</td><td><span class="badge">In progress</span></td></tr>
        <tr><td>Customer research</td><td>Sam Rivera</td><td>Complete</td></tr>
        </tbody></table></section>
        """
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1"><style>
    {''.join(font_css)}
    :root{{--accent:{primary};--bg:{background};--surface:{theme['secondaryBackgroundColor']};
    --text:{theme['textColor']};--border:{theme['borderColor']};--radius:{radius};
    --button-radius:{theme.get('buttonRadius', radius)}}}
    *{{box-sizing:border-box}}body{{margin:0;color:var(--text);background:var(--bg);font:14px '{theme['font']}',sans-serif}}
    .app{{display:grid;grid-template-columns:148px minmax(0,1fr);min-height:640px}}
    aside{{padding:25px 15px;color:{sidebar['textColor']};background:{sidebar['backgroundColor']};border-right:{sidebar_border} solid var(--border)}}
    .brand{{font-weight:700;font-size:17px;letter-spacing:-.6px;margin:0 0 35px}}
    .brand b{{color:var(--accent)}}nav div{{padding:10px 11px;margin:5px 0;border-radius:var(--radius);font-size:12px}}
    nav .active{{background:{sidebar['secondaryBackgroundColor']};border:1px solid var(--border);font-weight:600}}
    .aside-note{{font-size:10px;line-height:1.5;margin-top:195px;opacity:.6}}
    main{{padding:28px;min-width:0}}h1,h2{{font-family:'{theme['headingFont']}',serif}}
    h1{{font-size:25px;line-height:1.2;letter-spacing:-.7px;margin:22px 0 8px}}
    h2{{font-size:13px;margin:0 0 12px}}p{{line-height:1.6}}.muted{{opacity:.65;font-size:12px}}
    .eyebrow{{font-size:9px;letter-spacing:1.2px;opacity:.6;font-weight:600}}
    .period{{font-size:10px;padding:6px 9px;border:1px solid var(--border);border-radius:var(--radius)}}
    .topline{{display:flex;align-items:center;justify-content:space-between;gap:8px}}.topline h2{{margin:0}}
    .metrics{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:22px 0 15px}}
    .card{{border:1px solid var(--border);border-radius:var(--radius);padding:17px;margin-bottom:14px;background:var(--bg)}}
    .metrics .card{{margin:0;padding:15px 12px}}.metrics span{{font-size:10px;opacity:.7}}
    strong{{display:block;font-size:25px;letter-spacing:-1px;margin:8px 0}}small{{font-size:9px;opacity:.7}}
    .chart{{height:115px;display:flex;align-items:end;gap:12px;padding-top:15px;border-bottom:1px solid var(--border);margin-top:8px}}
    .chart i{{flex:1;display:block;background:var(--accent);border-radius:4px 4px 0 0;opacity:.85}}
    .chart i:nth-child(even){{opacity:.5}}.axis{{display:flex;justify-content:space-between;font-size:9px;opacity:.6;margin-top:8px}}
    button,input,select{{font:inherit;color:inherit;border:1px solid var(--border);background:var(--bg);border-radius:var(--radius);padding:8px 11px}}
    button{{font-size:10px;border-radius:var(--button-radius)}}.primary{{background:var(--accent);color:white;border-color:var(--accent)}}
    a{{color:{theme['linkColor']}}}input,select{{background:var(--surface);border-color:{widget_border}}}
    table{{border-collapse:collapse;width:100%;font-size:10px;text-align:left;margin-top:15px}}
    th,td{{padding:12px 2px;border-bottom:1px solid var(--border)}}th{{font-weight:500;opacity:.6}}
    tr:last-child td{{border:0}}.badge{{background:var(--surface);padding:5px;border-radius:var(--radius)}}
    .form-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0}}label{{font-size:11px;display:block}}
    input:not([type=checkbox]),select{{display:block;width:100%;margin-top:8px}}.check{{margin:20px 0}}
    .actions{{display:flex;gap:8px}}pre{{background:{theme['codeBackgroundColor']};padding:16px;overflow:auto;font:11px '{theme['codeFont']}',monospace}}
    @media(max-width:650px){{.app{{grid-template-columns:1fr}}aside{{padding:16px;border-right:0;border-bottom:{sidebar_border} solid var(--border)}}
    .brand{{margin:0 0 12px}}nav{{display:flex;gap:6px}}nav div{{margin:0;padding:7px}}nav div:last-child,.aside-note{{display:none}}
    main{{padding:20px 16px}}h1{{font-size:23px}}.metrics{{gap:6px}}.metrics .card{{padding:12px 8px}}
    strong{{font-size:22px}}.form-grid{{grid-template-columns:1fr}}.period{{display:none}}}}
    </style></head><body><div class="app"><aside><div class="brand"><b>◈</b> northstar</div>
    <nav aria-label="Sample app navigation"><div class="active">Overview</div><div>Projects</div><div>Reports</div><div>Settings</div></nav>
    <p class="aside-note">SAMPLE APPLICATION<br>{escape(preset.name)} theme</p></aside><main>{content}</main></div></body></html>"""
