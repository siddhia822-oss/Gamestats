from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

st.set_page_config(
    page_title="GAMESTATS // Performance Intelligence",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

THEME_GROUPS = {
    "GAME WORLDS": [
        ("Los Santos / GTA V", "#D7A46B", "#9B8BC4", "#6EBAB1", "#101014", "#19191F", "#37313A", "#B5ADB8", "#E7E1E8", "LOS SANTOS", "AFTER HOURS • PERFORMANCE DIVISION", "OWN THE NIGHT. READ THE NUMBERS."),
        ("Protocol / VALORANT", "#D95765", "#D88A91", "#8FC7C0", "#101216", "#191D23", "#353A43", "#AEB6C0", "#E7E9ED", "PROTOCOL", "TACTICAL ANALYTICS • COMPETITIVE DIVISION", "STAY SHARP. PLAY WITH INTENT."),
        ("Counter-Strike 2", "#D6A15B", "#79A9D5", "#C3C8CE", "#101216", "#1A1D22", "#373C43", "#AEB4BC", "#E6E8EA", "COUNTER-STRIKE", "TACTICAL OPS • ROUND-BY-ROUND INTELLIGENCE", "CLEAR ANGLES. CLEAN EXECUTION."),
        ("Night City / Cyberpunk", "#D7C95D", "#C47BAE", "#6CBCC4", "#111018", "#1C1924", "#3C3548", "#B7B0C3", "#EAE6EF", "NIGHT CITY", "EDGERUNNER SYSTEMS • NEON PERFORMANCE", "NO RULES. JUST RAW PERFORMANCE."),
        ("The Outlands / Apex", "#D8755D", "#D5A16C", "#78B8AE", "#131112", "#20191B", "#443438", "#BBAEAE", "#EEE5E3", "THE OUTLANDS", "LEGEND PERFORMANCE • DROP ZONE INTELLIGENCE", "DROP IN. ADAPT FAST. FINISH STRONG."),
        ("Overworld / Minecraft", "#85B86A", "#77A9C9", "#C5A77D", "#101510", "#1A211B", "#354438", "#AEBBAF", "#E4EAE3", "THE OVERWORLD", "SURVIVAL MODE • BUILD YOUR ADVANTAGE", "MINE THE DATA. BUILD YOUR EDGE."),
        ("The Lands Between / Elden Ring", "#B99A63", "#8B9C85", "#C5B9A0", "#12120F", "#1D1C17", "#3D392E", "#B5B0A3", "#E7E2D7", "THE LANDS BETWEEN", "ANCIENT SYSTEMS • PRECISION & PATIENCE", "ENDURE THE GRIND. MASTER THE BUILD."),
        ("Red Dead / Frontier", "#B97955", "#C5A47B", "#81958B", "#151210", "#211B17", "#46382E", "#B9ADA2", "#E8DFD5", "THE FRONTIER", "FRONTIER INTELLIGENCE • EST. 1899", "TAKE THE LONG ROAD. KNOW YOUR NUMBERS."),
    ],
    "NEON & SCI-FI": [
        ("Neon Noir", "#B69BD4", "#79A9D0", "#7FC4B8", "#101018", "#1A1A25", "#383747", "#B1B0C1", "#E7E5EF", "NEON NOIR", "NIGHT SHIFT • DIGITAL INTELLIGENCE", "FIND SIGNAL IN THE NOISE."),
        ("Synthwave Dusk", "#C18DBB", "#D4A078", "#7AAFC0", "#15121B", "#211B29", "#44384B", "#B8AEBF", "#E9E2EB", "SYNTHWAVE", "AFTER DARK • ANALOG FUTURE", "CHASE THE HORIZON."),
        ("Arctic Cyber", "#8EBCCB", "#A5A9D2", "#7CBDB0", "#0F151A", "#182128", "#34434D", "#AABAC4", "#E3EBEF", "ARCTIC CYBER", "COLD SYSTEMS • CLEAR SIGNAL", "COOL HEAD. CLEAN DATA."),
        ("Plasma Core", "#C88DA4", "#8FA7D1", "#83BDB3", "#131217", "#1E1C25", "#3D3546", "#B6AFBF", "#E9E5ED", "PLASMA CORE", "ENERGY SYSTEMS • CORE MONITORING", "CONTROL THE OUTPUT."),
        ("Deep Space", "#9AA8D5", "#7EB8C2", "#C2A7C8", "#0D121A", "#161D28", "#303D4D", "#A8B4C5", "#E2E8F1", "DEEP SPACE", "ORBITAL SYSTEMS • LONG-RANGE INTEL", "EXPLORE THE UNKNOWN."),
        ("Holographic", "#9CBDBA", "#B4A3D0", "#D0B5A0", "#101518", "#1A2226", "#354247", "#AEBABD", "#E5EAEB", "HOLOGRAPHIC", "SPECTRAL UI • MULTI-LAYER ANALYTICS", "SEE EVERY ANGLE."),
        ("Circuit Garden", "#8DB69A", "#88AFC4", "#C2B48A", "#101613", "#1A211D", "#34453B", "#AEBBB2", "#E3EAE5", "CIRCUIT GARDEN", "BIO-DIGITAL SYSTEMS • GREEN SIGNAL", "GROW YOUR ADVANTAGE."),
        ("Quantum Blue", "#83AFCB", "#9B9DCE", "#8FC2B7", "#0F141A", "#18212A", "#33434F", "#A9B8C5", "#E2E9EF", "QUANTUM BLUE", "QUANTUM SYSTEMS • PRECISION COMPUTING", "THINK BEYOND THE FRAME."),
    ],
    "EARTH & LUXE": [
        ("Moss & Stone", "#9DAF86", "#BBA98B", "#7FA69A", "#121511", "#1C211B", "#3B4337", "#B1B8AA", "#E4E8DF", "MOSS & STONE", "FIELD NOTES • QUIET PERFORMANCE", "GROUNDED. FOCUSED. READY."),
        ("Sandstone", "#C3A27E", "#A9B6A0", "#C28C78", "#171512", "#24201B", "#494035", "#BDB2A4", "#E9E1D7", "SANDSTONE", "DESERT STUDIO • WARM MINIMALISM", "MAKE EVERY MOVE COUNT."),
        ("Forest Retreat", "#88A88A", "#B9A982", "#7CA6A0", "#101612", "#1A211B", "#34453A", "#ACB9AF", "#E0E8E1", "FOREST RETREAT", "CANOPY SYSTEMS • CALM BY DESIGN", "BREATHE. ANALYZE. IMPROVE."),
        ("Terracotta Studio", "#C18770", "#D0B08A", "#8EAAA0", "#171311", "#241D19", "#493830", "#BBAEA4", "#E8DFD8", "TERRACOTTA", "CLAY STUDIO • HUMAN-CENTRED ANALYTICS", "CRAFT YOUR EDGE."),
        ("Olive & Brass", "#A7A77A", "#C0A16D", "#89A69A", "#151610", "#22231A", "#454536", "#B9B9A8", "#E7E6DA", "OLIVE & BRASS", "PRIVATE COLLECTION • REFINED PERFORMANCE", "SUBTLE BY DESIGN. STRONG BY NATURE."),
        ("Midnight Walnut", "#B38A6C", "#9EAAA5", "#C1B08A", "#151210", "#221B17", "#45372D", "#B7AAA0", "#E6DDD5", "MIDNIGHT WALNUT", "DARK WOOD • WARM PRECISION", "LET THE DETAILS SPEAK."),
        ("Desert Dusk", "#C39782", "#B2A2B9", "#9BAF9C", "#171416", "#231E21", "#45373E", "#BBAFB7", "#E8E0E5", "DESERT DUSK", "DUSK COLLECTION • SOFT CONTRAST", "A QUIETER KIND OF POWER."),
        ("Slate & Sage", "#91AAA0", "#B0A995", "#7FA3B1", "#111615", "#1B2220", "#35423D", "#ACB8B3", "#E1E8E4", "SLATE & SAGE", "MODERN HERITAGE • BALANCED SYSTEMS", "STAY STEADY. PLAY SMART."),
    ],
    "STUDIO & MINIMAL": [
        ("Obsidian", "#A6B2C4", "#8FA7B7", "#B7A6C8", "#101216", "#191D23", "#343A43", "#AEB6C0", "#E5E8EC", "OBSIDIAN", "MONOCHROME SYSTEMS • CLEAN SIGNAL", "LESS NOISE. MORE INSIGHT."),
        ("Graphite", "#A8B0B9", "#8CA7B5", "#C2B8A8", "#121416", "#1C2023", "#383E43", "#B1B7BC", "#E5E7E9", "GRAPHITE", "PRECISION STUDIO • PERFORMANCE DESIGN", "BUILT AROUND THE ESSENTIALS."),
        ("Ivory & Ink", "#C5BBA8", "#98A9B8", "#B5A2B8", "#171715", "#24231F", "#47443D", "#C0BDB4", "#EBE8E0", "IVORY & INK", "EDITORIAL SYSTEMS • QUIET LUXURY", "CLARITY IS A COMPETITIVE EDGE."),
        ("Midnight Blue", "#7FA8C7", "#9AA9C9", "#8ABBB8", "#0F141B", "#18212B", "#334251", "#A9B8C5", "#E2E9F0", "MIDNIGHT BLUE", "BLUE HOUR • FOCUSED PERFORMANCE", "STAY CALM UNDER LOAD."),
        ("Burgundy Velvet", "#B98291", "#C1A17E", "#8CA9A1", "#171215", "#241B20", "#47363F", "#BDAEB5", "#E9E0E4", "BURGUNDY VELVET", "ATELIER SERIES • ELEVATED DARK MODE", "QUIET CONFIDENCE. CLEAR RESULTS."),
        ("Espresso", "#B89478", "#A9B2A2", "#C0A0A0", "#151311", "#221D19", "#453A31", "#B8ADA4", "#E6DED6", "ESPRESSO", "COFFEEHOUSE EDITION • WARM FOCUS", "TAKE YOUR TIME. FIND THE PATTERN."),
        ("Moonstone", "#A5B9C2", "#B6A9C9", "#C1BCA8", "#111619", "#1C2428", "#36454A", "#B1BEC2", "#E3EAEC", "MOONSTONE", "LUNAR STUDIO • SOFT-LIGHT INTERFACE", "A CLEARER VIEW OF PERFORMANCE."),
        ("Coastal Mist", "#8FB7B5", "#A4B6C8", "#C4B49A", "#101617", "#1A2223", "#354445", "#AEBBBA", "#E2E9E8", "COASTAL MIST", "COASTAL STUDIO • OPEN AND UNCLUTTERED", "KEEP THE SIGNAL CLEAR."),
    ],
}


def build_theme(group, item):
    name, accent, accent2, accent3, bg, panel, line, muted, text_color, short_name, tag, hero_line = item
    return {
        "group": group, "accent": accent, "accent2": accent2, "accent3": accent3,
        "bg": bg, "panel": panel, "line": line, "muted": muted, "text": text_color,
        "name": short_name, "tag": tag,
        "gradient": f"linear-gradient(120deg, {accent}22, {accent2}16 52%, {accent3}0D)",
        "plot_colors": [accent, accent2, accent3, "#C58F8F"], "hero_line": hero_line,
    }

THEMES = {item[0]: build_theme(group, item) for group, items in THEME_GROUPS.items() for item in items}

with st.sidebar:
    st.markdown("<div class='side-brand'>GS<span>//</span></div>", unsafe_allow_html=True)
    st.markdown("### GAMESTATS")
    st.caption("Performance Intelligence")
    theme_group = st.selectbox("THEME COLLECTION", list(THEME_GROUPS.keys()), index=0, help="Browse curated visual collections.")
    group_theme_names = [item[0] for item in THEME_GROUPS[theme_group]]
    theme_name = st.selectbox("✦ CHOOSE YOUR THEME", group_theme_names, index=0, help="Choose a complete visual palette.")
    theme_mode = st.radio(
        "THEME BEHAVIOUR",
        ["Palette only", "Full experience"],
        index=1,
        help="Palette only changes colours. Full experience also changes typography, panel shapes, spacing, and interface details.",
    )
    T = THEMES[theme_name]
    # The Full experience mode gives each collection its own visual language, not just a new accent colour.
    STYLE_PROFILES = {
        "GAME WORLDS": {"display": "Rajdhani", "body": "Barlow", "mono": "IBM Plex Mono", "radius": "10px", "tracking": "-0.035em", "shadow": "0 14px 34px rgba(0,0,0,.18)"},
        "NEON & SCI-FI": {"display": "Space Grotesk", "body": "Space Grotesk", "mono": "DM Mono", "radius": "15px", "tracking": "-0.055em", "shadow": "0 0 28px {accent}12"},
        "EARTH & LUXE": {"display": "Manrope", "body": "Manrope", "mono": "IBM Plex Mono", "radius": "18px", "tracking": "-0.045em", "shadow": "0 12px 32px rgba(0,0,0,.14)"},
        "STUDIO & MINIMAL": {"display": "Inter", "body": "Inter", "mono": "IBM Plex Mono", "radius": "12px", "tracking": "-0.04em", "shadow": "0 8px 24px rgba(0,0,0,.10)"},
    }
    if theme_mode == "Full experience":
        style = STYLE_PROFILES[theme_group]
    else:
        style = {"display": "Space Grotesk", "body": "Space Grotesk", "mono": "DM Mono", "radius": "14px", "tracking": "-0.045em", "shadow": "none"}
    st.caption(f"{len(THEMES)} themes · {theme_group.title()} · {theme_mode}")
    st.divider()
    menu_head, menu_help = st.columns([0.82, 0.18], vertical_alignment="center")
    menu_head.markdown("#### COMMAND MENU")
    with menu_help.popover("?", help="What does each section do?", use_container_width=True):
        st.markdown("### Command menu guide")
        st.caption("What each section shows, how it works, and why it matters.")
        st.markdown("""
**01 · Command Center**  
**What:** A quick overview of the currently selected dataset: average FPS, KDA, win rate, score, session count and hardware readings.  
**How it works:** Recalculates the KPIs, charts and short observations from your active filters.  
**Why use it:** Get the main performance picture in seconds and spot patterns worth investigating.

---
**02 · Player Rankings**  
**What:** A leaderboard ranked by score, KDA, FPS, kills, win rate or wins, plus a two-player comparison.  
**How it works:** Aggregates the visible records per player and sorts them by the metric you choose.  
**Why use it:** Compare players fairly using the same dataset and see where each player stands.

---
**03 · Hardware Lab**  
**What:** FPS distributions, CPU/GPU utilisation, GPU temperature and related hardware records.  
**How it works:** Visualises hardware metrics already present in the CSV; it does not read sensors from your computer.  
**Why use it:** Explore performance variation and possible relationships between frame rate and recorded hardware metrics.

---
**04 · Intel & Correlations**  
**What:** A correlation heatmap and metric relationships, including associations with FPS.  
**How it works:** Calculates Pearson correlations for numeric columns in the filtered data.  
**Why use it:** Discover variables that move together. Correlation is descriptive and does not prove cause and effect.

---
**05 · Data Explorer**  
**What:** Searchable rows, dataset size, missing-cell counts, column types, validation checks and CSV exports.  
**How it works:** Searches the current filtered records and lets you download the visible data or a missing-value report.  
**Why use it:** Verify what the dashboard is analysing and inspect or export the underlying records.

---
**Shared controls**  
**Theme collection / theme:** Change the visual identity. **Palette only** changes colours; **Full experience** also changes font pairing and interface styling.  
**Data intake:** Upload another CSV. **Filters:** Narrow all relevant analysis by game, mode and player.
        """)
    page = st.radio(
        "COMMAND MENU",
        ["Command Center", "Player Rankings", "Hardware Lab", "Intel & Correlations", "Data Explorer"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("#### DATA INTAKE")
    uploaded = st.file_uploader("Drop a CSV dataset", type=["csv"], help="Use a CSV with columns such as Player, FPS_Avg, Score, CPU_Usage and GPU_Usage.")
    st.caption("Default source: game_stats.csv (shared project dataset)")
    st.markdown(f"<div class='side-status'><span class='status-dot'></span> SYSTEM READY <span class='side-version'>BUILD 06.0</span></div>", unsafe_allow_html=True)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=DM+Mono:wght@400;500&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {{
 --bg:{T['bg']}; --panel:{T['panel']}; --line:{T['line']}; --muted:{T['muted']};
 --text:{T['text']}; --accent:{T['accent']}; --accent2:{T['accent2']}; --accent3:{T['accent3']};
 --font-body:'{style['body']}',sans-serif; --font-display:'{style['display']}',sans-serif; --font-mono:'{style['mono']}',monospace;
 --radius:{style['radius']}; --tracking:{style['tracking']}; --card-shadow:{style['shadow'].replace('{accent}', T['accent'])};
}}
html, body, [class*="css"] {{ font-family:var(--font-body); }}
.stApp {{ background:radial-gradient(ellipse at 80% -10%, {T['accent']}13, transparent 34%), var(--bg); color:var(--text); }}
[data-testid="stHeader"] {{ background:rgba(8,11,16,.78); }}
[data-testid="stSidebar"] {{ background:#090C12; border-right:1px solid var(--line); }}
[data-testid="stSidebar"] * {{ color:#D4D9E1; }}
.block-container {{ max-width:1500px; padding-top:1.5rem; padding-bottom:3rem; }}
h1,h2,h3,h4 {{ font-family:var(--font-display); letter-spacing:var(--tracking); color:var(--text); }}
p, label, .stCaption {{ color:var(--muted); }}
[data-testid="stMetric"] {{ background:linear-gradient(145deg, {T['panel']}, {T['bg']}); border:1px solid var(--line); padding:17px 18px; border-radius:var(--radius); min-height:118px; box-shadow:var(--card-shadow); transition:transform .24s cubic-bezier(.2,.7,.2,1),border-color .24s ease,box-shadow .24s ease; }}
[data-testid="stMetric"]:hover {{ transform:translateY(-2px) scale(1.003); border-color:color-mix(in srgb,var(--accent) 42%,var(--line)); box-shadow:0 10px 28px rgba(0,0,0,.13); }}
[data-testid="stMetricLabel"] {{ color:var(--muted); font-size:.78rem; letter-spacing:.07em; text-transform:uppercase; }}
[data-testid="stMetricValue"] {{ color:var(--text); font-family:var(--font-display); font-size:1.75rem; font-weight:700; letter-spacing:var(--tracking); }}
[data-testid="stMetricDelta"] {{ font-size:.76rem; }}
[data-testid="stPlotlyChart"] {{ border:1px solid var(--line); border-radius:var(--radius); padding:7px; background:color-mix(in srgb,var(--panel) 68%,transparent); box-shadow:var(--card-shadow); transition:border-color .24s ease,transform .24s cubic-bezier(.2,.7,.2,1),box-shadow .24s ease; }}
[data-testid="stPlotlyChart"]:hover {{ border-color:color-mix(in srgb,var(--accent) 34%,var(--line)); transform:translateY(-1px); box-shadow:0 10px 28px rgba(0,0,0,.10); }}
[data-testid="stDataFrame"] {{ border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
.stButton>button, .stDownloadButton>button {{ border-radius:var(--radius); border:1px solid color-mix(in srgb,var(--accent) 70%,var(--line)); background:color-mix(in srgb, var(--accent) 22%, var(--panel)); color:var(--text); font-family:var(--font-body); font-weight:650; transition:transform .2s ease,background .2s ease,border-color .2s ease; }}
.stButton>button:hover, .stDownloadButton>button:hover {{ transform:translateY(-1px); border-color:var(--accent2); background:color-mix(in srgb,var(--accent) 30%,var(--panel)); color:var(--text); }}
[data-testid="stFileUploader"] {{ border:1px dashed var(--line); border-radius:14px; background:#0D1219; padding:8px; }}
hr {{ border-color:var(--line); }}
.side-brand {{ font-family:var(--font-display); font-size:2.2rem; font-weight:800; letter-spacing:-.1em; color:var(--text); }}
.side-brand span {{ color:var(--accent); }}
.side-status {{ border:1px solid var(--line); background:#10151D; border-radius:9px; padding:9px 10px; color:var(--muted); font-size:.69rem; letter-spacing:.08em; }}
.status-dot {{ display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--accent3); margin-right:7px; box-shadow:0 0 5px color-mix(in srgb, var(--accent3) 55%, transparent); }}
.side-version {{ float:right; opacity:.65; }}
[data-testid="stSelectbox"] label p {{ font-size:.72rem; letter-spacing:.09em; text-transform:uppercase; font-weight:650; }}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {{ border-color:var(--line); border-radius:10px; background:#12171E; }}
.stMarkdown, .stText, .stCaption {{ line-height:1.55; }}
::selection {{ background:var(--accent); color:#101319; }}
.eyebrow {{ font-family:var(--font-mono); color:var(--accent); font-size:.70rem; letter-spacing:.15em; text-transform:uppercase; }}
.hero {{ position:relative; overflow:hidden; border:1px solid var(--line); border-radius:22px; padding:28px 30px; background:{T['gradient']}; margin-bottom:18px; }}
.hero:after {{ content:'GS'; position:absolute; right:25px; top:-38px; font-size:12rem; font-weight:700; letter-spacing:-.13em; color:rgba(255,255,255,.025); pointer-events:none; }}
.hero-title {{ font-size:clamp(2rem,3.8vw,3.35rem); line-height:1.04; font-family:var(--font-display); font-weight:700; letter-spacing:var(--tracking); color:var(--text); max-width:800px; text-wrap:balance; }}
.hero-title span {{ color:var(--accent); }}
.hero-sub {{ color:var(--muted); margin-top:12px; font-size:.94rem; line-height:1.65; max-width:650px; }}
.chip {{ display:inline-block; padding:6px 10px; border:1px solid var(--line); border-radius:999px; color:var(--text); background:rgba(9,12,18,.42); font-family:var(--font-mono); font-size:.67rem; letter-spacing:.04em; margin:15px 6px 0 0; }}
.section-head {{ display:flex; align-items:end; justify-content:space-between; gap:12px; margin:20px 0 10px; }}
.section-title {{ color:var(--text); font-size:1.22rem; font-weight:700; letter-spacing:-.04em; }}
.section-note {{ color:var(--muted); font-size:.8rem; margin-top:3px; }}
.panel {{ border:1px solid var(--line); background:linear-gradient(145deg, {T['panel']}, {T['bg']}); border-radius:var(--radius); padding:17px 18px; box-shadow:var(--card-shadow); }}
.panel-label {{ color:var(--muted); font-family:var(--font-mono); text-transform:uppercase; letter-spacing:.1em; font-size:.68rem; }}
.panel-value {{ color:var(--text); font-size:1.45rem; font-weight:650; letter-spacing:-.025em; margin-top:8px; overflow-wrap:anywhere; }}
.panel-note {{ color:var(--accent); font-size:.77rem; margin-top:5px; }}
div[data-testid="stRadio"] label p {{ font-weight:500; }}
/* Quiet, accessible navigation feedback: a soft tint and tiny shift, never a loud glow. */
[data-testid="stRadio"] label {{ border-radius:9px; padding:5px 8px; margin:1px 0; transition:background-color .20s ease,border-color .20s ease,transform .20s ease; border:1px solid transparent; }}
[data-testid="stRadio"] label:hover {{ background:color-mix(in srgb,var(--accent) 8%,transparent); border-color:color-mix(in srgb,var(--accent) 22%,transparent); transform:translateX(2px); }}
[data-testid="stRadio"] label:has(input:checked) {{ background:color-mix(in srgb,var(--accent) 11%,transparent); border-color:color-mix(in srgb,var(--accent) 30%,var(--line)); }}
[data-testid="stPopover"] button {{ min-height:2rem; min-width:2rem; border-radius:999px; border:1px solid var(--line); background:color-mix(in srgb,var(--panel) 88%,transparent); color:var(--text); transition:background-color .2s ease,border-color .2s ease,transform .2s ease; }}
[data-testid="stPopover"] button:hover {{ border-color:var(--accent); background:color-mix(in srgb,var(--accent) 12%,var(--panel)); transform:translateY(-1px); }}
[data-testid="stExpander"] {{ border-color:var(--line); border-radius:var(--radius); }}
@keyframes gs-enter {{ 0% {{ opacity:0; transform:translateY(4px) scale(.997); }} 100% {{ opacity:1; transform:translateY(0) scale(1); }} }}
.hero {{ animation:gs-enter .38s cubic-bezier(.2,.7,.2,1) both; }}
[data-testid="stMetric"], [data-testid="stPlotlyChart"], .panel {{ animation:gs-enter .28s cubic-bezier(.2,.7,.2,1) both; }}
@media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation:none !important; transition:none !important; scroll-behavior:auto !important; transform:none !important; }} }}
footer {{ visibility:hidden; }}
#MainMenu {{ visibility:hidden; }}
</style>
""", unsafe_allow_html=True)

def locate_default_csv():
    # Use the single project dataset shared with GameStats_Backend.ipynb.
    # game_stats.csv is the canonical repository filename; the other names
    # are fallbacks for older copies of the project.
    candidates = [
        ROOT / "game_stats.csv",
        ROOT / "game_stats(2).csv",
        DATA_DIR / "game_stats.csv",
        DATA_DIR / "game_stats(2).csv",
        ROOT / "gta5_cleaned_data.csv",
        DATA_DIR / "gta5_cleaned_data.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    # Case-insensitive fallback, including files accidentally left at the repository root.
    for folder in (DATA_DIR, ROOT):
        if folder.exists():
            for path in folder.glob("*.csv"):
                name = path.name.lower()
                if "cleaned" in name and "data" in name:
                    return path
            for path in folder.glob("*.csv"):
                if "game_stats" in path.name.lower():
                    return path
    return None

@st.cache_data(show_spinner=False)
def read_csv_bytes(file_bytes):
    return pd.read_csv(io.BytesIO(file_bytes))

@st.cache_data(show_spinner=False)
def read_csv_path(path_string, modified_time):
    return pd.read_csv(path_string)

def prepare_data(frame):
    df = frame.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in ["Player", "Game", "Game_Mode", "FPS_Category"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
    numeric = [
        "Kills", "Deaths", "Assists", "Wins", "Matches", "Playtime_Hours",
        "FPS_Avg", "FPS_Min", "CPU_Usage", "GPU_Usage", "RAM_Usage_GB",
        "GPU_Temp", "Score", "KDA", "Win_Rate",
    ]
    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if {"Kills", "Deaths", "Assists"}.issubset(df.columns):
        calculated = (df["Kills"] + df["Assists"]) / df["Deaths"].replace(0, np.nan)
        if "KDA" not in df.columns:
            df["KDA"] = calculated
        else:
            df["KDA"] = df["KDA"].fillna(calculated)
    if {"Wins", "Matches"}.issubset(df.columns):
        calculated = df["Wins"] / df["Matches"].replace(0, np.nan) * 100
        if "Win_Rate" not in df.columns:
            df["Win_Rate"] = calculated
        else:
            df["Win_Rate"] = df["Win_Rate"].fillna(calculated)
    return df

def fmt(value, digits=1):
    try:
        return "—" if pd.isna(value) else f"{value:,.{digits}f}"
    except (TypeError, ValueError):
        return "—"

def section(title, note=""):
    st.markdown(f"<div class='section-head'><div><div class='section-title'>{title}</div><div class='section-note'>{note}</div></div></div>", unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family=f"{style['body']}, sans-serif", color=T["muted"]),
    margin=dict(l=20, r=20, t=38, b=18),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor=T["line"], zerolinecolor=T["line"]),
    yaxis=dict(gridcolor=T["line"], zerolinecolor=T["line"]),
)
def polish(fig, height=330):
    fig.update_layout(**PLOT_LAYOUT, height=height)
    fig.update_xaxes(showline=False, ticks="outside")
    fig.update_yaxes(showline=False, ticks="outside")
    return fig

try:
    if uploaded is not None:
        original = read_csv_bytes(uploaded.getvalue())
        source = f"UPLOAD / {uploaded.name}"
    else:
        default_path = locate_default_csv()
        if default_path is None:
            original = pd.DataFrame()
            source = "NO DATASET"
        else:
            original = read_csv_path(str(default_path), default_path.stat().st_mtime)
            source = f"PROJECT / {default_path.name}"
    df = prepare_data(original)
except Exception as exc:
    st.error(f"Could not read this dataset: {exc}")
    st.info("Check that the uploaded file is a valid CSV and try again.")
    st.stop()

hero_words = T["hero_line"].rsplit(" ", 1)
st.markdown(f"""
<div class="eyebrow">GAMESTATS / {T['name']} DIVISION</div>
<div class="hero">
  <div class="hero-title">{hero_words[0]} <span>{hero_words[1]}</span></div>
  <div class="hero-sub">A unified command centre for player performance, frame rates, and hardware behaviour. Explore the numbers. Find the edge.</div>
  <div><span class="chip">{T['tag']}</span><span class="chip">DATASET / {len(df):,} ROWS</span><span class="chip">{source}</span></div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.error("No dataset found yet.")
    st.markdown("Place **`game_stats.csv`** in the project root (next to `app.py`) or inside `data/`. The app can also load `game_stats(2).csv` and older dataset filenames, or you can upload a CSV using the sidebar.")
    st.stop()

required = ["Player", "Game_Mode", "FPS_Avg", "Score"]
missing = [col for col in required if col not in df.columns]
if missing:
    st.warning("Some dashboard features may be unavailable because these columns are missing: " + ", ".join(missing))

with st.sidebar:
    st.markdown("#### FILTERS")
    games = sorted(df["Game"].dropna().astype(str).unique()) if "Game" in df else []
    modes = sorted(df["Game_Mode"].dropna().astype(str).unique()) if "Game_Mode" in df else []
    players = sorted(df["Player"].dropna().astype(str).unique()) if "Player" in df else []
    selected_games = st.multiselect("Game", games, default=games) if games else []
    selected_modes = st.multiselect("Game mode", modes, default=modes) if modes else []
    selected_players = st.multiselect("Player", players, default=players) if players else []
    if st.button("↺ Reset filters", use_container_width=True):
        st.rerun()

filtered = df.copy()
if "Game" in filtered and games:
    filtered = filtered[filtered["Game"].astype(str).isin(selected_games)]
if "Game_Mode" in filtered and modes:
    filtered = filtered[filtered["Game_Mode"].astype(str).isin(selected_modes)]
if "Player" in filtered and players:
    filtered = filtered[filtered["Player"].astype(str).isin(selected_players)]

if filtered.empty:
    st.warning("No rows match the current filters. Reset filters or select at least one option.")
    st.stop()

fps = filtered["FPS_Avg"].mean() if "FPS_Avg" in filtered else np.nan
kda = filtered["KDA"].mean() if "KDA" in filtered else np.nan
win_rate = filtered["Win_Rate"].mean() if "Win_Rate" in filtered else np.nan
score = filtered["Score"].mean() if "Score" in filtered else np.nan
gpu = filtered["GPU_Usage"].mean() if "GPU_Usage" in filtered else np.nan
temp = filtered["GPU_Temp"].mean() if "GPU_Temp" in filtered else np.nan
players_count = filtered["Player"].nunique() if "Player" in filtered else 0

if page == "Command Center":
    section("Command overview", "A live read on the sessions in your current selection.")
    cols = st.columns(4)
    cols[0].metric("AVERAGE FPS", fmt(fps), help="Average FPS across the selected sessions.")
    cols[1].metric("AVERAGE KDA", fmt(kda, 2))
    cols[2].metric("WIN RATE", f"{fmt(win_rate)}%" if not pd.isna(win_rate) else "—")
    cols[3].metric("AVERAGE SCORE", fmt(score, 0))
    cols = st.columns(4)
    cols[0].metric("SESSIONS", f"{len(filtered):,}")
    cols[1].metric("PLAYERS", f"{players_count:,}")
    cols[2].metric("GPU LOAD", f"{fmt(gpu)}%" if not pd.isna(gpu) else "—")
    cols[3].metric("GPU TEMP", f"{fmt(temp)} °C" if not pd.isna(temp) else "—")

    # Explainable, data-grounded observations (not AI claims or causal conclusions).
    insight_bits = []
    if {"Player", "Score"}.issubset(filtered.columns) and not filtered.empty:
        player_means = filtered.groupby("Player")["Score"].mean().dropna().sort_values(ascending=False)
        if not player_means.empty:
            insight_bits.append(f"**Top average score:** {player_means.index[0]} ({player_means.iloc[0]:,.1f}).")
    if {"Game_Mode", "Win_Rate"}.issubset(filtered.columns):
        mode_rates = filtered.groupby("Game_Mode")["Win_Rate"].mean().dropna().sort_values(ascending=False)
        if not mode_rates.empty:
            insight_bits.append(f"**Highest average win rate by mode:** {mode_rates.index[0]} ({mode_rates.iloc[0]:.1f}%).")
    if {"FPS_Avg", "GPU_Usage"}.issubset(filtered.columns) and filtered["FPS_Avg"].notna().sum() > 1 and filtered["GPU_Usage"].notna().sum() > 1:
        association = filtered[["FPS_Avg", "GPU_Usage"]].corr().iloc[0, 1]
        if pd.notna(association):
            strength = "stronger" if abs(association) >= .6 else "moderate" if abs(association) >= .3 else "weak"
            direction = "positive" if association > 0 else "negative" if association < 0 else "near-zero"
            insight_bits.append(f"**FPS / GPU-load association:** {direction} (Pearson r = {association:.2f}; {strength}). This is descriptive, not causal.")
    if insight_bits:
        section("Signal briefing", "Quick observations generated from the currently filtered records.")
        st.markdown("\n".join([f"- {item}" for item in insight_bits]))

    left, right = st.columns([1.25, 1])
    with left:
        section("FPS by game mode", "Which modes are running at the highest average frame rate?")
        if {"Game_Mode", "FPS_Avg"}.issubset(filtered.columns):
            chart = filtered.groupby("Game_Mode", as_index=False)["FPS_Avg"].mean().sort_values("FPS_Avg")
            fig = px.bar(chart, x="FPS_Avg", y="Game_Mode", orientation="h", text_auto=".1f",
                         color="Game_Mode", color_discrete_sequence=T["plot_colors"])
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(xaxis_title="Average FPS", yaxis_title="", showlegend=False)
            st.plotly_chart(polish(fig, 350), use_container_width=True)
        else:
            st.info("This chart needs Game_Mode and FPS_Avg columns.")
    with right:
        section("CPU vs GPU load", "Average utilization in the selected sessions.")
        util = [{"Component": label, "Usage": filtered[col].mean()} for col, label in [("CPU_Usage", "CPU"), ("GPU_Usage", "GPU")] if col in filtered]
        if util:
            fig = px.bar(pd.DataFrame(util), x="Component", y="Usage", text="Usage",
                         color="Component", color_discrete_sequence=[T["accent"], T["accent3"]])
            fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig.update_layout(yaxis_title="Utilization (%)", yaxis_range=[0, 110], showlegend=False)
            st.plotly_chart(polish(fig, 350), use_container_width=True)
        else:
            st.info("No CPU/GPU usage columns found.")

    left, right = st.columns([1.1, 1])
    with left:
        section("Score × frame rate", "Explore how score and FPS appear together.")
        if {"FPS_Avg", "Score"}.issubset(filtered.columns):
            color = "Game_Mode" if "Game_Mode" in filtered else None
            fig = px.scatter(filtered, x="FPS_Avg", y="Score", color=color,
                             color_discrete_sequence=T["plot_colors"], opacity=.82,
                             hover_data=[c for c in ["Player", "Game", "Game_Mode", "Kills", "Deaths"] if c in filtered])
            fig.update_traces(marker=dict(size=9, line=dict(width=0)))
            fig.update_layout(xaxis_title="Average FPS", yaxis_title="Score", legend_title="")
            st.plotly_chart(polish(fig, 340), use_container_width=True)
        else:
            st.info("This chart needs FPS_Avg and Score columns.")
    with right:
        section("Top sessions", "Highest scoring sessions in this selection.")
        if "Score" in filtered:
            top = filtered.nlargest(6, "Score")
            cols = [c for c in ["Player", "Game_Mode", "Score", "FPS_Avg", "KDA"] if c in top]
            st.dataframe(top[cols].reset_index(drop=True), use_container_width=True, hide_index=True)
            st.download_button("↓ Export filtered sessions", filtered.to_csv(index=False).encode("utf-8"), "gamestats_filtered.csv")

elif page == "Player Rankings":
    section("Player rankings", "Pick a metric and see who leads the lobby.")
    if "Player" not in filtered:
        st.warning("This dataset needs a Player column.")
    else:
        rank_options = [c for c in ["Score", "KDA", "FPS_Avg", "Kills", "Win_Rate", "Wins"] if c in filtered]
        if rank_options:
            rank_by = st.selectbox("RANK PLAYERS BY", rank_options, index=0)
            with st.expander("⚔️ Compare two players", expanded=False):
                available_players = sorted(filtered["Player"].dropna().astype(str).unique())
                if len(available_players) >= 2:
                    ca, cb = st.columns(2)
                    player_a = ca.selectbox("PLAYER A", available_players, index=0, key="compare_player_a")
                    player_b = cb.selectbox("PLAYER B", available_players, index=1, key="compare_player_b")
                    compare_metrics = [c for c in ["Score", "KDA", "FPS_Avg", "Win_Rate", "Kills", "Deaths", "Assists"] if c in filtered]
                    comparison = filtered[filtered["Player"].astype(str).isin([player_a, player_b])].groupby("Player")[compare_metrics].mean().reindex([player_a, player_b])
                    st.dataframe(comparison.round(2), use_container_width=True)
                    if len(compare_metrics) >= 2:
                        compare_long = comparison.reset_index().melt(id_vars="Player", var_name="Metric", value_name="Average")
                        fig = px.bar(compare_long, x="Metric", y="Average", color="Player", barmode="group", color_discrete_sequence=T["plot_colors"])
                        fig.update_layout(xaxis_title="Metric", yaxis_title="Average value", legend_title="Player")
                        st.plotly_chart(polish(fig, 320), use_container_width=True)
                else:
                    st.info("Select at least two players in the sidebar to compare them.")
            agg = {c: "mean" for c in ["Score", "KDA", "FPS_Avg", "Win_Rate", "GPU_Usage"] if c in filtered}
            for c in ["Kills", "Deaths", "Assists", "Wins", "Matches"]:
                if c in filtered:
                    agg[c] = "sum"
            board = filtered.groupby("Player", as_index=False).agg(agg) if agg else filtered[["Player"]].drop_duplicates()
            board = board.sort_values(rank_by, ascending=False, na_position="last").reset_index(drop=True)
            board.insert(0, "Rank", np.arange(1, len(board) + 1))
            podium = st.columns(min(3, len(board)))
            for idx, col in enumerate(podium):
                row = board.iloc[idx]
                with col:
                    st.markdown(f"<div class='panel'><div class='panel-label'>RANK / 0{idx+1}</div><div class='panel-value'>{row['Player']}</div><div class='panel-note'>{rank_by.replace('_',' ')} · {fmt(row[rank_by],2)}</div></div>", unsafe_allow_html=True)
            st.write("")
            st.dataframe(board.round(2), use_container_width=True, hide_index=True)
            st.download_button("↓ Download leaderboard", board.to_csv(index=False).encode("utf-8"), "gamestats_leaderboard.csv")
            chart_data = board.head(15).sort_values(rank_by, ascending=True)
            fig = px.bar(chart_data, x=rank_by, y="Player", orientation="h", text_auto=".2s",
                         color=rank_by, color_continuous_scale=[T["panel"], T["accent"]])
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(xaxis_title=rank_by.replace("_", " "), yaxis_title="", coloraxis_showscale=False)
            st.plotly_chart(polish(fig, max(360, len(chart_data)*28)), use_container_width=True)
        else:
            st.info("No ranking metric columns were found.")

elif page == "Hardware Lab":
    section("Hardware performance lab", "Dataset-based hardware readings, not live sensors from this computer.")
    cols = st.columns(4)
    cols[0].metric("AVG FPS", fmt(fps))
    cols[1].metric("MIN FPS", fmt(filtered["FPS_Min"].mean()) if "FPS_Min" in filtered else "—")
    cols[2].metric("CPU LOAD", f"{fmt(filtered['CPU_Usage'].mean())}%" if "CPU_Usage" in filtered else "—")
    cols[3].metric("GPU TEMP", f"{fmt(temp)} °C" if not pd.isna(temp) else "—")
    left, right = st.columns(2)
    with left:
        section("FPS distribution", "How the session frame rates are spread.")
        if "FPS_Avg" in filtered:
            fig = px.histogram(filtered, x="FPS_Avg", nbins=24, marginal="box", color_discrete_sequence=[T["accent"]])
            fig.update_layout(xaxis_title="Average FPS", yaxis_title="Sessions")
            st.plotly_chart(polish(fig, 350), use_container_width=True)
    with right:
        section("GPU temperature", "Distribution of recorded GPU temperatures.")
        if "GPU_Temp" in filtered:
            fig = px.histogram(filtered, x="GPU_Temp", nbins=20, color_discrete_sequence=[T["accent2"]])
            fig.update_layout(xaxis_title="GPU temperature (°C)", yaxis_title="Sessions")
            st.plotly_chart(polish(fig, 350), use_container_width=True)
    left, right = st.columns(2)
    with left:
        section("Utilization vs FPS", "Compare recorded utilization against frame rate.")
        usage_cols = [c for c in ["CPU_Usage", "GPU_Usage"] if c in filtered]
        if usage_cols and "FPS_Avg" in filtered:
            melted = filtered.melt(id_vars=["FPS_Avg"], value_vars=usage_cols, var_name="Component", value_name="Usage")
            fig = px.scatter(melted, x="Usage", y="FPS_Avg", color="Component", color_discrete_sequence=[T["accent"], T["accent3"]], opacity=.72)
            fig.update_layout(xaxis_title="Utilization (%)", yaxis_title="Average FPS", legend_title="")
            st.plotly_chart(polish(fig, 330), use_container_width=True)
    with right:
        section("Hardware records", "A preview of the selected session records.")
        cols = [c for c in ["Player", "Game_Mode", "FPS_Avg", "FPS_Min", "CPU_Usage", "GPU_Usage", "RAM_Usage_GB", "GPU_Temp"] if c in filtered]
        st.dataframe(filtered[cols].head(30), use_container_width=True, hide_index=True)
    st.caption("Note: these are readings in the supplied CSV. GameStats does not currently collect live PC sensor data.")

elif page == "Intel & Correlations":
    section("Intel & correlations", "Statistical relationships are descriptive, not proof of cause and effect.")
    numeric = filtered.select_dtypes(include="number")
    if numeric.shape[1] >= 2:
        corr = numeric.corr(method="pearson")
        fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                        color_continuous_scale=[T["accent2"], T["panel"], T["accent"]],
                        zmin=-1, zmax=1, origin="lower")
        fig.update_layout(coloraxis_colorbar_title="Pearson r")
        st.plotly_chart(polish(fig, max(430, 31*len(corr.columns))), use_container_width=True)
        if "FPS_Avg" in corr.columns:
            pairs = corr["FPS_Avg"].drop(labels=["FPS_Avg"], errors="ignore").dropna().sort_values()
            if len(pairs):
                left, right = st.columns(2)
                with left:
                    st.markdown(f"<div class='panel'><div class='panel-label'>MOST NEGATIVE ASSOCIATION WITH FPS</div><div class='panel-value'>{pairs.index[0]}</div><div class='panel-note'>Pearson r = {pairs.iloc[0]:.2f}</div></div>", unsafe_allow_html=True)
                with right:
                    st.markdown(f"<div class='panel'><div class='panel-label'>MOST POSITIVE ASSOCIATION WITH FPS</div><div class='panel-value'>{pairs.index[-1]}</div><div class='panel-note'>Pearson r = {pairs.iloc[-1]:.2f}</div></div>", unsafe_allow_html=True)
        st.download_button("↓ Download correlation matrix", corr.to_csv().encode("utf-8"), "gamestats_correlation.csv")
    else:
        st.info("At least two numeric columns are required for correlations.")
    if {"Game_Mode", "Score"}.issubset(filtered.columns):
        section("Score by game mode", "Average score for each selected mode.")
        by_mode = filtered.groupby("Game_Mode", as_index=False)["Score"].mean().sort_values("Score", ascending=False)
        fig = px.bar(by_mode, x="Game_Mode", y="Score", text_auto=".0f", color="Game_Mode", color_discrete_sequence=T["plot_colors"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(polish(fig, 310), use_container_width=True)

elif page == "Data Explorer":
    section("Dataset explorer", "Search, inspect, and export the records behind the dashboard.")
    a, b, c = st.columns(3)
    a.metric("ROWS", f"{len(filtered):,}")
    b.metric("COLUMNS", f"{len(filtered.columns):,}")
    c.metric("MISSING CELLS", f"{int(filtered.isna().sum().sum()):,}")
    search = st.text_input("SEARCH TEXT", placeholder="Search a player, game, or mode...")
    view = filtered.copy()
    if search:
        text_cols = view.select_dtypes(include=["object", "string"]).columns
        mask = pd.Series(False, index=view.index)
        for col in text_cols:
            mask |= view[col].astype(str).str.contains(search, case=False, na=False)
        view = view[mask]
    st.dataframe(view, use_container_width=True, hide_index=True, height=470)
    left, right = st.columns(2)
    left.download_button("↓ Download visible rows", view.to_csv(index=False).encode("utf-8"), "gamestats_visible_rows.csv", use_container_width=True)
    right.download_button("↓ Download missing-value report", filtered.isna().sum().rename("Missing_Values").to_csv().encode("utf-8"), "gamestats_missing_values.csv", use_container_width=True)
    with st.expander("Column types & data quality"):
        info = pd.DataFrame({
            "Column": filtered.columns,
            "Data type": [str(filtered[c].dtype) for c in filtered.columns],
            "Missing values": [int(filtered[c].isna().sum()) for c in filtered.columns],
            "Unique values": [int(filtered[c].nunique(dropna=True)) for c in filtered.columns],
        })
        st.dataframe(info, use_container_width=True, hide_index=True)
        st.markdown("**Quick validation checks**")
        checks = []
        for col, low, high, label in [("FPS_Avg", 0, None, "FPS should not be negative"), ("Win_Rate", 0, 100, "Win rate should be between 0 and 100%"), ("CPU_Usage", 0, 100, "CPU usage should be between 0 and 100%"), ("GPU_Usage", 0, 100, "GPU usage should be between 0 and 100%"), ("GPU_Temp", -20, 150, "GPU temperature outside a broad plausible range")]:
            if col in filtered:
                series = filtered[col].dropna()
                bad = int(((series < low) | (series > high if high is not None else False)).sum())
                checks.append({"Check": label, "Column": col, "Flagged rows": bad, "Status": "Review" if bad else "OK"})
        if checks:
            st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)
            st.caption("These are broad sanity checks. Flagged values are not automatically changed or deleted.")

st.divider()
st.markdown(
    f"<div class='eyebrow'>GAMESTATS / {T['name']} // BUILT FOR THE NEXT SESSION</div>",
    unsafe_allow_html=True,
)
st.caption("Built with Python • Pandas • Streamlit • Plotly | Dataset may contain synthetic/sample records. Not a live hardware sensor.")
