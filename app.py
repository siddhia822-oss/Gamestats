from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -------------------- Page setup --------------------
st.set_page_config(
    page_title="GameStats | Performance Lab",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

# -------------------- Premium dark styling --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root { --bg:#080b10; --panel:#10151d; --line:#222b37; --muted:#8995a7; --text:#edf3fa; --lime:#c8ff4d; --cyan:#50e3e0; }
html, body, [class*="css"] { font-family:'Space Grotesk', sans-serif; }
.stApp { background: radial-gradient(ellipse at 75% -10%, rgba(77,111,50,.15), transparent 35%), #080b10; color:var(--text); }
[data-testid="stHeader"] { background:rgba(8,11,16,.88); }
[data-testid="stSidebar"] { background:#0b0f15; border-right:1px solid #202733; }
[data-testid="stSidebar"] * { color:#dce5ef; }
.block-container { padding-top:1.65rem; padding-bottom:3rem; max-width:1500px; }
h1,h2,h3 { letter-spacing:-.04em; }
h1 { font-weight:700; }
p, label, .stCaption { color:#a7b2c2; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#131a23,#0d1219); border:1px solid #26313e; padding:18px 18px 14px; border-radius:16px; min-height:130px; }
div[data-testid="stMetricLabel"] { color:#9aa8b9; font-size:.82rem; }
div[data-testid="stMetricValue"] { color:#f1f6fc; font-size:1.9rem; font-weight:700; }
div[data-testid="stMetricDelta"] { font-size:.75rem; }
div[data-testid="stPlotlyChart"] { background:#0d1219; border:1px solid #202a36; border-radius:16px; padding:8px; }
div[data-testid="stDataFrame"] { border:1px solid #222b37; border-radius:12px; overflow:hidden; }
.stButton > button, .stDownloadButton > button { border-radius:10px; border:1px solid #b9f544; background:#c8ff4d; color:#10150a; font-weight:700; }
.stButton > button:hover, .stDownloadButton > button:hover { background:#d8ff83; border-color:#d8ff83; color:#10150a; }
div[data-testid="stFileUploader"] { border:1px dashed #354454; border-radius:14px; background:#0d1219; padding:8px; }
hr { border-color:#222b37; }
.gs-eyebrow { color:#c8ff4d; text-transform:uppercase; letter-spacing:.19em; font-size:.72rem; font-weight:700; }
.gs-hero { padding:24px 26px; border:1px solid #283443; border-radius:20px; background:linear-gradient(115deg,rgba(200,255,77,.09),rgba(80,227,224,.035) 55%,rgba(17,24,34,.7)); margin-bottom:20px; }
.gs-hero-title { font-size:2.4rem; font-weight:700; letter-spacing:-.065em; line-height:1.05; color:#f1f6fc; }
.gs-hero-sub { color:#9ba9ba; margin-top:10px; font-size:.95rem; }
.gs-chip { display:inline-block; padding:5px 9px; border:1px solid #33414f; border-radius:999px; color:#c8ff4d; font-size:.72rem; margin-right:5px; background:#111922; }
.gs-section { margin-top:16px; margin-bottom:8px; }
.gs-section-title { color:#f0f5fa; font-weight:700; font-size:1.25rem; letter-spacing:-.035em; }
.gs-section-note { color:#7f8da0; font-size:.83rem; margin-top:3px; }
.gs-card { border:1px solid #26313e; background:linear-gradient(145deg,#121922,#0c1118); border-radius:16px; padding:16px 18px; }
.gs-card-label { color:#8796a9; font-size:.78rem; text-transform:uppercase; letter-spacing:.09em; }
.gs-card-value { color:#eaf1f8; font-size:1.55rem; font-weight:700; margin-top:7px; }
.gs-card-note { color:#c8ff4d; font-size:.78rem; margin-top:5px; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk, sans-serif", color="#b9c4d2"),
    margin=dict(l=20, r=20, t=45, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="#202a36", zerolinecolor="#202a36"),
    yaxis=dict(gridcolor="#202a36", zerolinecolor="#202a36"),
)

def polish(fig, height=330):
    fig.update_layout(**PLOT_LAYOUT, height=height)
    fig.update_xaxes(showline=False, ticks="outside")
    fig.update_yaxes(showline=False, ticks="outside")
    return fig

@st.cache_data
def read_csv_bytes(file_bytes):
    return pd.read_csv(io.BytesIO(file_bytes))

def load_default_data():
    cleaned = DATA_DIR / "gta5_cleaned_data.csv"
    raw = DATA_DIR / "game_stats.csv"
    path = cleaned if cleaned.exists() else raw
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

def prepare_data(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for c in ["Player", "Game", "Game_Mode"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.strip()
    numeric = [
        "Kills", "Deaths", "Assists", "Wins", "Matches", "Playtime_Hours",
        "FPS_Avg", "FPS_Min", "CPU_Usage", "GPU_Usage", "RAM_Usage_GB",
        "GPU_Temp", "Score", "KDA", "Win_Rate"
    ]
    for c in numeric:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if {"Kills", "Deaths", "Assists"}.issubset(df.columns):
        if "KDA" not in df.columns:
            df["KDA"] = (df["Kills"] + df["Assists"]) / df["Deaths"].replace(0, np.nan)
        else:
            df["KDA"] = df["KDA"].fillna(
                (df["Kills"] + df["Assists"]) / df["Deaths"].replace(0, np.nan)
            )
    if {"Wins", "Matches"}.issubset(df.columns):
        calculated = df["Wins"] / df["Matches"].replace(0, np.nan) * 100
        if "Win_Rate" not in df.columns:
            df["Win_Rate"] = calculated
        else:
            df["Win_Rate"] = df["Win_Rate"].fillna(calculated)
    return df

def fmt_num(value, digits=1):
    try:
        if pd.isna(value):
            return "—"
        return f"{value:,.{digits}f}"
    except (TypeError, ValueError):
        return "—"

# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown('<div class="gs-eyebrow">GAMESTATS / LAB 01</div>', unsafe_allow_html=True)
    st.markdown("## 🎮 GameStats")
    st.caption("Gaming performance intelligence")
    st.divider()
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Player leaderboard", "Hardware lab", "Insights", "Data explorer"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("### DATA SOURCE")
    uploaded = st.file_uploader(
        "Upload a CSV dataset",
        type=["csv"],
        help="Your file should contain columns such as Player, Game, FPS_Avg, Score, CPU_Usage and GPU_Usage.",
    )
    st.caption("Default dataset: GTA 5 • 300 recorded sample sessions")
    st.divider()
    st.markdown('<span class="gs-chip">PYTHON</span><span class="gs-chip">PANDAS</span><span class="gs-chip">PLOTLY</span>', unsafe_allow_html=True)
    st.caption("GameStats · Performance Lab")

# -------------------- Data --------------------
try:
    if uploaded is not None:
        raw_df = read_csv_bytes(uploaded.getvalue())
        source_label = f"Uploaded: {uploaded.name}"
    else:
        raw_df = load_default_data()
        source_label = "Project dataset"
    df = prepare_data(raw_df)
except Exception as exc:
    st.error(f"We couldn't read this CSV: {exc}")
    st.stop()

if df.empty:
    st.warning("No dataset found. Put gta5_cleaned_data.csv in the project's data folder or upload a CSV in the sidebar.")
    st.stop()

required = ["Player", "Game_Mode", "FPS_Avg", "Score"]
missing_required = [c for c in required if c not in df.columns]
if missing_required:
    st.warning("This dataset is missing some dashboard columns: " + ", ".join(missing_required) + ". Some charts may be unavailable.")

# Filters
with st.sidebar:
    st.markdown("### FILTERS")
    games = sorted(df["Game"].dropna().astype(str).unique().tolist()) if "Game" in df else []
    modes = sorted(df["Game_Mode"].dropna().astype(str).unique().tolist()) if "Game_Mode" in df else []
    selected_games = st.multiselect("Game", games, default=games)
    selected_modes = st.multiselect("Game mode", modes, default=modes)
    players = sorted(df["Player"].dropna().astype(str).unique().tolist()) if "Player" in df else []
    selected_players = st.multiselect("Players", players, default=players)
    if st.button("Reset filters", use_container_width=True):
        st.rerun()

filtered = df.copy()
if "Game" in filtered and selected_games:
    filtered = filtered[filtered["Game"].astype(str).isin(selected_games)]
if "Game_Mode" in filtered and selected_modes:
    filtered = filtered[filtered["Game_Mode"].astype(str).isin(selected_modes)]
if "Player" in filtered and selected_players:
    filtered = filtered[filtered["Player"].astype(str).isin(selected_players)]

# -------------------- Shared header --------------------
st.markdown('<div class="gs-eyebrow">PLAYER + HARDWARE ANALYTICS</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="gs-hero">
  <div class="gs-hero-title">Performance, <span style="color:#c8ff4d">decoded.</span></div>
  <div class="gs-hero-sub">One command centre for player stats, frame rates and hardware behaviour.</div>
  <div style="margin-top:16px">
    <span class="gs-chip">● LIVE FILTERS</span>
    <span class="gs-chip">DATASET: {len(filtered):,} SESSIONS</span>
    <span class="gs-chip">{source_label.upper()}</span>
  </div>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No rows match the current filters. Change the filters in the sidebar.")
    st.stop()

# Compute key metrics from filtered data
avg_fps = filtered["FPS_Avg"].mean() if "FPS_Avg" in filtered else np.nan
avg_score = filtered["Score"].mean() if "Score" in filtered else np.nan
avg_kda = filtered["KDA"].mean() if "KDA" in filtered else np.nan
win_rate = filtered["Win_Rate"].mean() if "Win_Rate" in filtered else np.nan
avg_gpu = filtered["GPU_Usage"].mean() if "GPU_Usage" in filtered else np.nan
avg_temp = filtered["GPU_Temp"].mean() if "GPU_Temp" in filtered else np.nan
player_count = filtered["Player"].nunique() if "Player" in filtered else 0
game_count = filtered["Game"].nunique() if "Game" in filtered else 0

# -------------------- Overview --------------------
if page == "Overview":
    st.markdown('<div class="gs-section"><div class="gs-section-title">Command overview</div><div class="gs-section-note">A quick read on the selected sessions.</div></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AVG. FPS", fmt_num(avg_fps, 1), help="Mean average FPS across the selected rows.")
    m2.metric("AVG. KDA", fmt_num(avg_kda, 2), help="Mean of session-level KDA values.")
    m3.metric("WIN RATE", f"{fmt_num(win_rate, 1)}%" if not pd.isna(win_rate) else "—")
    m4.metric("AVG. SCORE", fmt_num(avg_score, 0))
    m5, m6, m7, m8 = st.columns(4)
    m5.metric("SESSIONS", f"{len(filtered):,}")
    m6.metric("PLAYERS", f"{player_count:,}")
    m7.metric("GPU UTILIZATION", f"{fmt_num(avg_gpu, 1)}%" if not pd.isna(avg_gpu) else "—")
    m8.metric("GPU TEMPERATURE", f"{fmt_num(avg_temp, 1)} °C" if not pd.isna(avg_temp) else "—")

    left, right = st.columns([1.45, 1])
    with left:
        st.markdown('<div class="gs-section"><div class="gs-section-title">FPS by game mode</div><div class="gs-section-note">Average frame rate across the selected modes.</div></div>', unsafe_allow_html=True)
        if {"Game_Mode", "FPS_Avg"}.issubset(filtered.columns):
            mode_fps = filtered.groupby("Game_Mode", as_index=False)["FPS_Avg"].mean().sort_values("FPS_Avg", ascending=True)
            fig = px.bar(mode_fps, x="FPS_Avg", y="Game_Mode", orientation="h", text_auto=".1f")
            fig.update_traces(marker_color="#c8ff4d", textfont_color="#eaf1f8", textposition="outside", cliponaxis=False)
            fig.update_layout(xaxis_title="Average FPS", yaxis_title="", showlegend=False)
            st.plotly_chart(polish(fig, 340), use_container_width=True)
        else:
            st.info("FPS_Avg and Game_Mode columns are needed for this chart.")
    with right:
        st.markdown('<div class="gs-section"><div class="gs-section-title">CPU vs GPU load</div><div class="gs-section-note">Average utilization for selected sessions.</div></div>', unsafe_allow_html=True)
        util_rows = []
        for col, label in [("CPU_Usage", "CPU"), ("GPU_Usage", "GPU")]:
            if col in filtered:
                util_rows.append({"Component": label, "Usage": filtered[col].mean()})
        if util_rows:
            u = pd.DataFrame(util_rows)
            fig = go.Figure(go.Bar(
                x=u["Component"], y=u["Usage"],
                marker_color=["#50e3e0", "#c8ff4d"],
                text=[f"{x:.1f}%" for x in u["Usage"]], textposition="outside"
            ))
            fig.update_layout(yaxis_title="Usage (%)", yaxis_range=[0, 110], showlegend=False)
            st.plotly_chart(polish(fig, 340), use_container_width=True)
        else:
            st.info("CPU_Usage and GPU_Usage columns are needed for this chart.")

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="gs-section"><div class="gs-section-title">Score vs frame rate</div><div class="gs-section-note">Explore whether high FPS appears alongside higher scores.</div></div>', unsafe_allow_html=True)
        if {"FPS_Avg", "Score"}.issubset(filtered.columns):
            color_col = "Game_Mode" if "Game_Mode" in filtered else None
            fig = px.scatter(filtered, x="FPS_Avg", y="Score", color=color_col, opacity=.78,
                             color_discrete_sequence=["#c8ff4d", "#50e3e0", "#b49aff", "#ff9b70"],
                             hover_data=[c for c in ["Player", "Game_Mode", "Kills", "Deaths"] if c in filtered])
            fig.update_traces(marker=dict(size=8, line=dict(width=0)))
            fig.update_layout(xaxis_title="Average FPS", yaxis_title="Score", legend_title="")
            st.plotly_chart(polish(fig, 330), use_container_width=True)
        else:
            st.info("FPS_Avg and Score columns are needed for this chart.")
    with right:
        st.markdown('<div class="gs-section"><div class="gs-section-title">Top sessions</div><div class="gs-section-note">Highest-scoring rows in the current selection.</div></div>', unsafe_allow_html=True)
        if "Score" in filtered:
            top = filtered.nlargest(5, "Score")
            show_cols = [c for c in ["Player", "Game_Mode", "Score", "FPS_Avg", "KDA"] if c in top]
            st.dataframe(top[show_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
        st.download_button("↓  Export filtered data", filtered.to_csv(index=False).encode("utf-8"), "gamestats_filtered.csv", "text/csv", use_container_width=True)

# -------------------- Player leaderboard --------------------
elif page == "Player leaderboard":
    st.markdown('<div class="gs-section"><div class="gs-section-title">Player rankings</div><div class="gs-section-note">Rank by total impact, score, KDA or FPS.</div></div>', unsafe_allow_html=True)
    if "Player" not in filtered:
        st.warning("The dataset needs a Player column.")
    else:
        rank_by_options = [c for c in ["Score", "KDA", "FPS_Avg", "Kills", "Win_Rate"] if c in filtered]
        rank_by = st.selectbox("Rank players by", rank_by_options, index=0 if "Score" in rank_by_options else 0)
        agg = {c: "mean" for c in ["Score", "KDA", "FPS_Avg", "Win_Rate", "GPU_Usage"] if c in filtered}
        for c in ["Kills", "Deaths", "Assists", "Wins", "Matches"]:
            if c in filtered:
                agg[c] = "sum"
        if agg:
            lb = filtered.groupby("Player", as_index=False).agg(agg)
            lb = lb.sort_values(rank_by, ascending=False, na_position="last").reset_index(drop=True)
            lb.insert(0, "Rank", np.arange(1, len(lb) + 1))
            top3 = st.columns(3)
            for i, col in enumerate(top3):
                if i < len(lb):
                    row = lb.iloc[i]
                    col.markdown(f"""<div class="gs-card"><div class="gs-card-label">RANK #{i+1}</div><div class="gs-card-value">{row['Player']}</div><div class="gs-card-note">{rank_by.replace('_',' ')} · {fmt_num(row[rank_by], 2)}</div></div>""", unsafe_allow_html=True)
            st.write("")
            st.dataframe(lb.round(2), use_container_width=True, hide_index=True)
            st.download_button("↓  Download leaderboard", lb.to_csv(index=False).encode("utf-8"), "gamestats_leaderboard.csv", "text/csv")
            if {"Player", rank_by}.issubset(lb.columns):
                chart_data = lb.head(12).sort_values(rank_by, ascending=True)
                fig = px.bar(chart_data, x=rank_by, y="Player", orientation="h", text_auto=".2s")
                fig.update_traces(marker_color="#c8ff4d", textposition="outside", cliponaxis=False)
                fig.update_layout(xaxis_title=rank_by.replace("_", " "), yaxis_title="")
                st.plotly_chart(polish(fig, max(330, len(chart_data)*30)), use_container_width=True)

# -------------------- Hardware lab --------------------
elif page == "Hardware lab":
    st.markdown('<div class="gs-section"><div class="gs-section-title">Hardware performance lab</div><div class="gs-section-note">Read the selected session metrics; thresholds are configurable indicators, not hardware diagnoses.</div></div>', unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("AVG. FPS", fmt_num(avg_fps, 1))
    h2.metric("MIN. FPS", fmt_num(filtered["FPS_Min"].mean(), 1) if "FPS_Min" in filtered else "—")
    h3.metric("CPU LOAD", f"{fmt_num(avg_gpu if False else filtered['CPU_Usage'].mean(), 1)}%" if "CPU_Usage" in filtered else "—")
    h4.metric("GPU TEMP", f"{fmt_num(avg_temp, 1)} °C" if not pd.isna(avg_temp) else "—")
    left, right = st.columns(2)
    with left:
        st.markdown("#### FPS distribution")
        if "FPS_Avg" in filtered:
            fig = px.histogram(filtered, x="FPS_Avg", nbins=22, marginal="box")
            fig.update_traces(marker_color="#50e3e0", opacity=.85)
            fig.update_layout(xaxis_title="Average FPS", yaxis_title="Sessions")
            st.plotly_chart(polish(fig, 350), use_container_width=True)
    with right:
        st.markdown("#### GPU temperature distribution")
        if "GPU_Temp" in filtered:
            fig = px.histogram(filtered, x="GPU_Temp", nbins=18)
            fig.update_traces(marker_color="#ff9b70", opacity=.85)
            fig.update_layout(xaxis_title="GPU temperature (°C)", yaxis_title="Sessions")
            st.plotly_chart(polish(fig, 350), use_container_width=True)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Utilization vs FPS")
        cols = [c for c in ["CPU_Usage", "GPU_Usage"] if c in filtered]
        if cols and "FPS_Avg" in filtered:
            melted = filtered.melt(id_vars=["FPS_Avg"], value_vars=cols, var_name="Component", value_name="Usage")
            fig = px.scatter(melted, x="Usage", y="FPS_Avg", color="Component",
                             color_discrete_map={"CPU_Usage":"#50e3e0","GPU_Usage":"#c8ff4d"}, opacity=.65)
            fig.update_layout(xaxis_title="Utilization (%)", yaxis_title="Average FPS", legend_title="")
            st.plotly_chart(polish(fig, 330), use_container_width=True)
    with right:
        st.markdown("#### Hardware session records")
        cols = [c for c in ["Player", "Game_Mode", "FPS_Avg", "FPS_Min", "CPU_Usage", "GPU_Usage", "RAM_Usage_GB", "GPU_Temp"] if c in filtered]
        st.dataframe(filtered[cols].head(30), use_container_width=True, hide_index=True)
    st.caption("Temperatures and utilization are taken from the supplied dataset. This dashboard does not read live PC sensors.")

# -------------------- Insights --------------------
elif page == "Insights":
    st.markdown('<div class="gs-section"><div class="gs-section-title">Insights & correlations</div><div class="gs-section-note">Statistical relationships are descriptive and do not prove cause and effect.</div></div>', unsafe_allow_html=True)
    numeric = filtered.select_dtypes(include="number")
    if numeric.shape[1] >= 2:
        corr = numeric.corr(method="pearson")
        fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                        color_continuous_scale=["#ff9278", "#151d27", "#c8ff4d"],
                        zmin=-1, zmax=1, origin="lower")
        fig.update_layout(coloraxis_colorbar_title="Pearson r")
        st.plotly_chart(polish(fig, max(430, 32*len(corr.columns))), use_container_width=True)
        preferred = [c for c in ["FPS_Avg", "Score", "Kills", "Deaths", "CPU_Usage", "GPU_Usage", "GPU_Temp"] if c in corr]
        if "FPS_Avg" in corr:
            st.markdown("#### What moves with FPS?")
            pairs = corr["FPS_Avg"].drop(labels=["FPS_Avg"], errors="ignore").loc[preferred[1:] if len(preferred)>1 else corr.index].dropna().sort_values()
            if len(pairs):
                strongest = pairs.iloc[-1]
                weakest = pairs.iloc[0]
                a,b = st.columns(2)
                a.markdown(f"""<div class="gs-card"><div class="gs-card-label">STRONGEST POSITIVE PAIR WITH FPS</div><div class="gs-card-value">{pairs.index[-1]}</div><div class="gs-card-note">Pearson r = {strongest:.2f}</div></div>""", unsafe_allow_html=True)
                b.markdown(f"""<div class="gs-card"><div class="gs-card-label">MOST NEGATIVE PAIR WITH FPS</div><div class="gs-card-value">{pairs.index[0]}</div><div class="gs-card-note">Pearson r = {weakest:.2f}</div></div>""", unsafe_allow_html=True)
        st.download_button("↓  Download correlation matrix", corr.to_csv().encode("utf-8"), "gamestats_correlation.csv", "text/csv")
    else:
        st.info("At least two numeric columns are needed to calculate correlations.")
    if "Game_Mode" in filtered and "Score" in filtered:
        st.markdown("#### Score by game mode")
        gm = filtered.groupby("Game_Mode", as_index=False)["Score"].mean().sort_values("Score", ascending=False)
        fig = px.bar(gm, x="Game_Mode", y="Score", text_auto=".0f")
        fig.update_traces(marker_color="#b49aff", textposition="outside")
        st.plotly_chart(polish(fig, 300), use_container_width=True)

# -------------------- Data explorer --------------------
elif page == "Data explorer":
    st.markdown('<div class="gs-section"><div class="gs-section-title">Dataset explorer</div><div class="gs-section-note">Inspect, search and export the rows behind the visuals.</div></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.metric("Rows", f"{len(filtered):,}")
    b.metric("Columns", f"{len(filtered.columns):,}")
    c.metric("Missing cells", f"{int(filtered.isna().sum().sum()):,}")
    search = st.text_input("Search across text columns", placeholder="Type a player or game mode...")
    view = filtered.copy()
    if search:
        text_cols = view.select_dtypes(include=["object", "string"]).columns
        mask = pd.Series(False, index=view.index)
        for col in text_cols:
            mask |= view[col].astype(str).str.contains(search, case=False, na=False)
        view = view[mask]
    st.dataframe(view, use_container_width=True, hide_index=True, height=480)
    left, right = st.columns(2)
    left.download_button("↓  Download visible rows", view.to_csv(index=False).encode("utf-8"), "gamestats_visible_rows.csv", "text/csv", use_container_width=True)
    right.download_button("↓  Download missing-value report", filtered.isna().sum().rename("Missing_Values").to_csv().encode("utf-8"), "gamestats_missing_values.csv", "text/csv", use_container_width=True)
    with st.expander("Column types and data quality"):
        info_df = pd.DataFrame({
            "Column": filtered.columns,
            "Data type": [str(filtered[c].dtype) for c in filtered.columns],
            "Missing values": [int(filtered[c].isna().sum()) for c in filtered.columns],
            "Unique values": [int(filtered[c].nunique(dropna=True)) for c in filtered.columns],
        })
        st.dataframe(info_df, use_container_width=True, hide_index=True)

st.divider()
st.markdown(
    '<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:#718096;font-size:.78rem"><span>GAMESTATS / PERFORMANCE LAB</span><span>Built with Python · Pandas · Streamlit · Plotly</span><span>Sample data may be synthetic</span></div>',
    unsafe_allow_html=True
)
