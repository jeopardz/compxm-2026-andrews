"""
Comp-XM 2026 Andrews Simulator — Streamlit UI (Capsim-styled)

Run with:
    streamlit run F:/Claude CODE/CAPSIM/sim/app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from sim.data.r0_seed import build_r0_state
from sim.data_models import (
    GameState, RoundDecision, ProductDecision, FinanceDecision,
    HRDecision, TQMDecision,
)
from sim.engines.round_engine import advance_round
from sim.engines.customer_score import net_score
from sim.reports.inquirer import full_inquirer
from sim.engines.bsc import compute_round_bsc, compute_cumulative_bsc
from sim.board_queries import get_round_queries, grade_round
from sim.engines.tqm import INITIATIVE_NAMES, recommended_initiatives_for_round

SAVE_PATH = Path(__file__).parent / "save_state.json"

st.set_page_config(
    page_title="Comp-XM® 2026 — Andrews",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CAPSIM-STYLE CSS (extensive theming)
# ============================================================

CAPSIM_CSS = """
<style>
    /* Color tokens — Capsim navy/white/gold */
    :root {
        --capsim-navy: #1a365d;
        --capsim-navy-dark: #0f2440;
        --capsim-navy-light: #2c5282;
        --capsim-gold: #d69e2e;
        --capsim-gold-dark: #b7791f;
        --capsim-red: #c53030;
        --capsim-green: #2f855a;
        --capsim-bg: #f7fafc;
        --capsim-border: #cbd5e0;
        --capsim-text: #2d3748;
        --capsim-text-muted: #718096;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
    .block-container { padding-top: 0.5rem; padding-bottom: 1rem; max-width: 1400px; }

    /* Base */
    .stApp { background-color: var(--capsim-bg); color: var(--capsim-text); }

    /* === COMP-XM HEADER BAR === */
    .compxm-header {
        background: linear-gradient(135deg, var(--capsim-navy) 0%, var(--capsim-navy-dark) 100%);
        color: white;
        padding: 12px 24px;
        margin: -10px -10px 16px -10px;
        border-bottom: 4px solid var(--capsim-gold);
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Segoe UI', Arial, sans-serif;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .compxm-logo {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .compxm-logo .reg { font-size: 12px; vertical-align: super; }
    .compxm-logo .sub {
        font-size: 12px; font-weight: 400; color: #cbd5e0; margin-left: 8px;
        letter-spacing: 1px;
    }
    .compxm-round-badge {
        background: var(--capsim-gold);
        color: var(--capsim-navy-dark);
        padding: 4px 14px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 0.5px;
    }
    .compxm-tagline {
        font-size: 11px; color: #cbd5e0; text-align: right;
    }

    /* === NAV TABS === */
    div[data-baseweb="tab-list"] {
        background-color: white;
        border-bottom: 2px solid var(--capsim-navy);
        gap: 0;
        margin-bottom: 16px;
    }
    button[data-baseweb="tab"] {
        background-color: #edf2f7;
        color: var(--capsim-navy);
        border-radius: 0;
        border-right: 1px solid var(--capsim-border);
        padding: 8px 16px !important;
        font-weight: 600;
        font-size: 13px;
        margin: 0 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--capsim-navy);
        color: white;
        border-bottom: 2px solid var(--capsim-gold);
    }

    /* === HEADINGS === */
    h1 { color: var(--capsim-navy); font-weight: 700; }
    h2 { color: var(--capsim-navy); border-bottom: 2px solid var(--capsim-gold); padding-bottom: 4px; font-weight: 700; font-size: 1.4rem; }
    h3 { color: var(--capsim-navy); font-weight: 600; font-size: 1.15rem; }

    /* === SECTION CARD === */
    .capsim-section {
        background: white;
        border: 1px solid var(--capsim-border);
        border-top: 3px solid var(--capsim-navy);
        padding: 14px 18px;
        margin: 8px 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .capsim-section-title {
        color: var(--capsim-navy);
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid var(--capsim-border);
        padding-bottom: 6px;
        margin-bottom: 10px;
    }

    /* === KPI CARDS (mimics Capsim metric tiles) === */
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; }
    .kpi-card {
        background: white; border: 1px solid var(--capsim-border);
        padding: 10px 12px; border-left: 3px solid var(--capsim-navy);
    }
    .kpi-card.up { border-left-color: var(--capsim-green); }
    .kpi-card.down { border-left-color: var(--capsim-red); }
    .kpi-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--capsim-text-muted); font-weight: 600; }
    .kpi-value { font-size: 18px; font-weight: 700; color: var(--capsim-navy); margin: 2px 0; }
    .kpi-delta { font-size: 11px; color: var(--capsim-text-muted); }
    .kpi-delta.up { color: var(--capsim-green); }
    .kpi-delta.down { color: var(--capsim-red); }

    /* === DATA TABLES (Capsim spreadsheet style) === */
    .stDataFrame, .stTable { font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; }
    .stDataFrame [data-testid="stDataFrameResizable"] table thead th {
        background-color: var(--capsim-navy) !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 11px !important;
        letter-spacing: 0.5px;
    }
    .stDataFrame [data-testid="stDataFrameResizable"] table tbody tr:nth-child(even) {
        background-color: var(--capsim-bg);
    }
    .stDataFrame [data-testid="stDataFrameResizable"] table tbody td {
        padding: 4px 8px !important;
        border-color: var(--capsim-border) !important;
    }

    /* === BUTTONS === */
    .stButton button {
        background-color: var(--capsim-navy);
        color: white;
        border: none;
        border-radius: 2px;
        padding: 6px 16px;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stButton button:hover { background-color: var(--capsim-navy-light); transform: none; }
    .stButton button[kind="primary"] {
        background-color: var(--capsim-gold);
        color: var(--capsim-navy-dark);
    }
    .stButton button[kind="primary"]:hover { background-color: var(--capsim-gold-dark); }

    /* === FORM INPUTS === */
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border: 1px solid var(--capsim-border) !important;
        border-radius: 2px !important;
        font-family: 'Consolas', monospace !important;
        font-size: 13px !important;
    }
    .stNumberInput input:focus { border-color: var(--capsim-navy) !important; box-shadow: 0 0 0 1px var(--capsim-navy) !important; }
    .stSlider [data-baseweb="slider"] > div > div > div { background-color: var(--capsim-navy) !important; }

    /* === EXPANDERS === */
    .streamlit-expanderHeader {
        background-color: var(--capsim-navy) !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 12px !important;
        letter-spacing: 0.5px;
        padding: 6px 12px !important;
        border-radius: 0 !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid var(--capsim-border) !important;
        margin-bottom: 8px;
    }

    /* === NEWSPAPER-STYLE INQUIRER === */
    .inq-paper {
        background: white;
        border: 2px solid var(--capsim-navy);
        padding: 20px 28px;
        font-family: 'Georgia', 'Times New Roman', serif;
        max-width: 100%;
        margin: 16px 0;
    }
    .inq-masthead {
        text-align: center;
        border-bottom: 3px double var(--capsim-navy);
        padding-bottom: 12px;
        margin-bottom: 18px;
    }
    .inq-masthead h1 {
        font-family: 'Georgia', serif !important;
        font-size: 38px !important;
        margin: 0;
        letter-spacing: 4px;
        color: var(--capsim-navy);
    }
    .inq-masthead .subtitle {
        font-size: 13px;
        color: var(--capsim-text-muted);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 4px;
    }
    .inq-section-head {
        background: var(--capsim-navy);
        color: white;
        padding: 6px 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 13px;
        font-family: 'Segoe UI', Arial, sans-serif;
        margin: 16px 0 8px 0;
    }
    .inq-page-marker {
        text-align: right;
        font-size: 11px;
        color: var(--capsim-text-muted);
        font-style: italic;
        margin-top: 8px;
        border-top: 1px solid var(--capsim-border);
        padding-top: 4px;
    }

    /* Annual Report classic style */
    .annual-report {
        background: white;
        border: 1px solid var(--capsim-border);
        padding: 20px;
        font-family: 'Times New Roman', serif;
    }
    .annual-report h2, .annual-report h3 { font-family: 'Times New Roman', serif; }
    .annual-report table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Consolas', monospace;
        font-size: 12px;
        margin: 8px 0;
    }
    .annual-report table th {
        background: var(--capsim-navy);
        color: white;
        padding: 4px 8px;
        text-align: left;
    }
    .annual-report table td {
        padding: 3px 8px;
        border-bottom: 1px solid var(--capsim-border);
    }
    .annual-report table tr.total {
        font-weight: 700;
        border-top: 2px solid var(--capsim-navy);
        background: var(--capsim-bg);
    }

    /* Module navigation (left side of decision pages) */
    .module-nav {
        background: var(--capsim-navy);
        color: white;
        padding: 0;
        margin: 8px 0;
    }
    .module-nav-item {
        display: block;
        padding: 8px 14px;
        border-bottom: 1px solid var(--capsim-navy-light);
        color: white;
        text-decoration: none;
        font-size: 13px;
        font-weight: 600;
    }
    .module-nav-item:hover { background: var(--capsim-navy-light); }
    .module-nav-item.active { background: var(--capsim-gold); color: var(--capsim-navy-dark); }

    /* Footer */
    .compxm-footer {
        text-align: center;
        font-size: 10px;
        color: var(--capsim-text-muted);
        margin-top: 20px;
        padding-top: 8px;
        border-top: 1px solid var(--capsim-border);
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Pill / Tag */
    .pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .pill-thrift { background: #fef5e7; color: #b7791f; }
    .pill-core { background: #e6fffa; color: #234e52; }
    .pill-nano { background: #ebf8ff; color: #2b6cb0; }
    .pill-elite { background: #fed7e2; color: #9b2c2c; }
    .pill-good { background: #c6f6d5; color: #22543d; }
    .pill-warn { background: #feebc8; color: #7b341e; }
    .pill-bad { background: #fed7d7; color: #742a2a; }

    /* Streamlit metric override */
    div[data-testid="stMetric"] {
        background: white; border: 1px solid var(--capsim-border);
        border-left: 3px solid var(--capsim-navy);
        padding: 8px 12px;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--capsim-text-muted) !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px !important;
        color: var(--capsim-navy) !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 11px !important;
    }
</style>
"""

st.markdown(CAPSIM_CSS, unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    loaded_pending = None
    if "game_state" not in st.session_state:
        loaded = None
        if SAVE_PATH.exists():
            try:
                with open(SAVE_PATH, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                loaded = GameState.model_validate(payload["game_state"])
                st.session_state.bsc_history = payload.get("bsc_history", [])
                st.session_state.board_results = payload.get("board_results", {})
                # Load pending_decisions if present and matches current round
                pd_payload = payload.get("pending_decisions")
                if pd_payload:
                    pd = RoundDecision.model_validate(pd_payload)
                    if pd.round_num == loaded.round_num + 1:
                        loaded_pending = pd
            except Exception as e:
                st.warning(f"Save file corrupt — starting fresh. ({e})")
                loaded = None
        st.session_state.game_state = loaded or build_r0_state()
    if "bsc_history" not in st.session_state:
        st.session_state.bsc_history = []
    if "board_results" not in st.session_state:
        st.session_state.board_results = {}
    if "pending_decisions" not in st.session_state:
        st.session_state.pending_decisions = loaded_pending
    if "prev_state_snapshot" not in st.session_state:
        st.session_state.prev_state_snapshot = None


def save_state():
    """Save via JSON (avoids pickle issues with Streamlit hot-reload).
    Also persists pending_decisions so R&D/Mkt/etc inputs survive reload."""
    payload = {
        "game_state": st.session_state.game_state.model_dump(),
        "bsc_history": st.session_state.bsc_history,
        "board_results": {str(k): v for k, v in st.session_state.board_results.items()},
        "pending_decisions": (st.session_state.pending_decisions.model_dump()
                              if st.session_state.pending_decisions else None),
    }
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)


def autosave():
    """Save silently after every input change (called from on_change handlers)."""
    try:
        save_state()
    except Exception:
        pass  # don't crash UI on save errors


def reset_state():
    st.session_state.game_state = build_r0_state()
    st.session_state.bsc_history = []
    st.session_state.board_results = {}
    st.session_state.pending_decisions = None
    st.session_state.prev_state_snapshot = None
    if SAVE_PATH.exists():
        SAVE_PATH.unlink()


init_state()
state = st.session_state.game_state
andrews = state.get_company("Andrews")


# ============================================================
# HEADER (Capsim-style)
# ============================================================

st.markdown(f"""
<div class="compxm-header">
    <div class="compxm-logo">
        COMP-XM<span class="reg">®</span> INQUIRER
        <span class="sub">2026 EXAM • ANDREWS CORPORATION</span>
    </div>
    <div>
        <span class="compxm-round-badge">ROUND {state.round_num} / 4</span>
        <span style="margin-left:12px; font-size:12px;">DEC 31, {state.year}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# TOP NAVIGATION TABS (mimics Capsim's top bar)
# ============================================================

tab_dash, tab_rd, tab_mkt, tab_prod, tab_fin, tab_hr, tab_tqm, tab_inq, tab_icr, tab_bsc, tab_bq, tab_hist = st.tabs([
    "🏠 Dashboard",
    "⚗ R&D",
    "📢 Marketing",
    "🏭 Production",
    "💰 Finance",
    "👥 HR",
    "🎯 TQM",
    "📰 Inquirer",
    "📋 Industry Conditions",
    "📊 Scorecard",
    "❓ Board Queries",
    "📈 History",
])


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def fmt_money(x, in_k=False):
    """Format as $X.XM or $X,XXXK."""
    if x is None:
        return "—"
    if in_k:
        return f"${x:,.0f}K"
    if abs(x) >= 1e6:
        return f"${x/1e6:,.1f}M"
    if abs(x) >= 1e3:
        return f"${x/1e3:,.0f}K"
    return f"${x:,.2f}"


def fmt_pct(x):
    if x is None:
        return "—"
    return f"{x*100:.1f}%"


def kpi_card(label, value, delta=None, direction=None):
    """Render a Capsim-style KPI card."""
    dir_class = direction or ""
    delta_html = ""
    if delta is not None:
        delta_class = "up" if (direction == "up") else ("down" if direction == "down" else "")
        delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>'
    st.markdown(f"""
    <div class="kpi-card {dir_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def seg_pill(seg_name):
    cls = {"Thrift": "pill-thrift", "Core": "pill-core", "Nano": "pill-nano", "Elite": "pill-elite"}.get(seg_name, "")
    return f'<span class="pill {cls}">{seg_name}</span>'


def ensure_pending():
    if (st.session_state.pending_decisions is None
            or st.session_state.pending_decisions.round_num != state.round_num + 1):
        # Pre-populate HR from current state so it persists if user doesn't open HR tab
        st.session_state.pending_decisions = RoundDecision(
            round_num=state.round_num + 1,
            products=[ProductDecision(
                product_name=p.name,
                price=p.price,
                promo_budget=p.promo_budget,
                sales_budget=p.sales_budget,
                production_schedule=int(p.capacity_first_shift * 1.5),
            ) for p in andrews.products],
            hr=HRDecision(
                recruit_spend=andrews.hr.recruit_spend or 2500,
                training_hours=andrews.hr.training_hours or 40,
            ),
        )
    return st.session_state.pending_decisions


# ============================================================
# TAB: DASHBOARD
# ============================================================

with tab_dash:
    # Comp-XM Inquirer-style front-page banner
    st.markdown(f"""
    <div class="inq-paper">
        <div class="inq-masthead">
            <h1>COMP-XM&reg; INQUIRER</h1>
            <div class="subtitle">Round {state.round_num} Report • Dec 31, {state.year} • Andrews Corp View</div>
        </div>
    """, unsafe_allow_html=True)

    # Selected Financial Statistics table (mimics R0 Inquirer Page 1)
    st.markdown('<div class="inq-section-head">Selected Financial Statistics</div>', unsafe_allow_html=True)

    fin_df = pd.DataFrame({
        "Company": [c.name for c in state.companies],
        "Sales": [fmt_money(c.sales_last) for c in state.companies],
        "EBIT": [fmt_money(c.ebit_last) for c in state.companies],
        "Profits": [fmt_money(c.profit_last) for c in state.companies],
        "Cum Profit": [fmt_money(c.cumulative_profit) for c in state.companies],
        "ROS": [fmt_pct(c.ros) for c in state.companies],
        "Asset Turnover": [f"{c.asset_turnover:.2f}" for c in state.companies],
        "ROA": [fmt_pct(c.roa) for c in state.companies],
        "ROE": [fmt_pct(c.roe) for c in state.companies],
        "Leverage": [f"{c.leverage:.2f}" for c in state.companies],
        "Emergency Loan": [fmt_money(c.emergency_loan) if c.emergency_loan > 0 else "$0" for c in state.companies],
    })
    st.dataframe(fin_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="inq-page-marker">Page 1 — Front Page</div></div>', unsafe_allow_html=True)

    # KPI strip — Andrews focus
    st.markdown('<div class="capsim-section"><div class="capsim-section-title">Andrews Snapshot</div>', unsafe_allow_html=True)

    cols = st.columns(8)
    delta_stock = andrews.stock_price - 95.38
    delta_dir = "up" if delta_stock >= 0 else "down"
    with cols[0]: kpi_card("Stock", f"${andrews.stock_price:.2f}", f"{'+' if delta_stock >= 0 else ''}${delta_stock:.2f} vs R0", delta_dir)
    with cols[1]: kpi_card("Market Cap", fmt_money(andrews.market_cap))
    with cols[2]: kpi_card("Cash", fmt_money(andrews.cash))
    with cols[3]: kpi_card("Profit", fmt_money(andrews.profit_last))
    with cols[4]: kpi_card("Cum Profit", fmt_money(andrews.cumulative_profit))
    with cols[5]: kpi_card("ROS", fmt_pct(andrews.ros))
    with cols[6]: kpi_card("ROE", fmt_pct(andrews.roe))
    with cols[7]: kpi_card("S&P", andrews.sp_rating)
    st.markdown('</div>', unsafe_allow_html=True)

    # Perceptual Map (the most visually distinctive Comp-XM element)
    col_map, col_pos = st.columns([3, 2])
    with col_map:
        st.markdown('<div class="capsim-section"><div class="capsim-section-title">Perceptual Map — Current + Drift Trajectory</div>', unsafe_allow_html=True)

        show_drift = st.checkbox("📍 Show segment ideal drift trajectory (R0 → R4)",
                                  value=True, key="show_drift",
                                  help="Dotted line + ghost markers show where each segment's ideal spot will be over the next 4 years")

        fig = go.Figure()
        import math

        # Draw rough-cut + fine-cut circles for each segment (current position only)
        for seg in state.segments:
            theta = list(range(0, 361, 5))
            xs = [seg.center_pfmn + 4.0 * math.cos(math.radians(t)) for t in theta]
            ys = [seg.center_size + 4.0 * math.sin(math.radians(t)) for t in theta]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                      line=dict(color="rgba(26, 54, 93, 0.15)", width=1, dash="dot"),
                                      showlegend=False, hoverinfo="skip"))
            xs2 = [seg.ideal_pfmn + 2.5 * math.cos(math.radians(t)) for t in theta]
            ys2 = [seg.ideal_size + 2.5 * math.sin(math.radians(t)) for t in theta]
            fig.add_trace(go.Scatter(x=xs2, y=ys2, mode="lines",
                                      line=dict(color="rgba(214, 158, 46, 0.3)", width=1),
                                      showlegend=False, hoverinfo="skip"))
            # Current ideal spot marker (round number = state.round_num)
            fig.add_trace(go.Scatter(x=[seg.ideal_pfmn], y=[seg.ideal_size],
                                      mode="markers+text",
                                      marker=dict(size=16, color="rgba(214, 158, 46, 0.9)", symbol="x",
                                                  line=dict(color="#1a365d", width=2)),
                                      text=[f"<b>{seg.name}</b><br>R{state.round_num}"],
                                      textposition="bottom center",
                                      textfont=dict(color="#1a365d", size=10),
                                      showlegend=False, hoverinfo="text",
                                      hovertext=f"{seg.name} R{state.round_num} ideal ({seg.ideal_pfmn:.1f}, {seg.ideal_size:.1f})"))

        # Drift trajectory: ghost markers + connecting line for future rounds
        if show_drift:
            rounds_remaining = 4 - state.round_num
            seg_colors_drift = {"Thrift": "#b7791f", "Core": "#234e52", "Nano": "#2b6cb0", "Elite": "#9b2c2c"}
            for seg in state.segments:
                drift_pfmn = [seg.ideal_pfmn]
                drift_size = [seg.ideal_size]
                drift_labels = [f"R{state.round_num}"]
                for r in range(1, rounds_remaining + 1):
                    future_pfmn = seg.ideal_pfmn + seg.drift_pfmn * r
                    future_size = seg.ideal_size + seg.drift_size * r
                    drift_pfmn.append(future_pfmn)
                    drift_size.append(future_size)
                    drift_labels.append(f"R{state.round_num + r}")

                seg_color = seg_colors_drift.get(seg.name, "#718096")
                # Connecting line (dotted arrow effect)
                fig.add_trace(go.Scatter(
                    x=drift_pfmn, y=drift_size, mode="lines+markers+text",
                    line=dict(color=seg_color, width=1.5, dash="dot"),
                    marker=dict(size=[16] + [8]*(len(drift_pfmn)-1),
                                color=[seg_color] + [f"rgba({int(seg_color[1:3],16)}, {int(seg_color[3:5],16)}, {int(seg_color[5:7],16)}, 0.4)" for _ in range(len(drift_pfmn)-1)],
                                symbol="x"),
                    text=drift_labels,
                    textposition="top right",
                    textfont=dict(color=seg_color, size=9),
                    showlegend=False, hoverinfo="text",
                    hovertext=[f"{seg.name} {lbl}: ({p:.1f}, {s:.1f})" for lbl, p, s in zip(drift_labels, drift_pfmn, drift_size)],
                ))
                # Add arrow annotation at endpoint
                if len(drift_pfmn) >= 2:
                    fig.add_annotation(
                        x=drift_pfmn[-1], y=drift_size[-1],
                        ax=drift_pfmn[-2], ay=drift_size[-2],
                        xref="x", yref="y", axref="x", ayref="y",
                        showarrow=True, arrowhead=2, arrowsize=1.2,
                        arrowwidth=1.5, arrowcolor=seg_color, opacity=0.7,
                    )

        # Products
        company_colors = {"Andrews": "#1a365d", "Baldwin": "#9b2c2c", "Chester": "#2c7a7b", "Digby": "#744210"}
        company_symbols = {"Andrews": "circle", "Baldwin": "square", "Chester": "triangle-up", "Digby": "diamond"}
        for c in state.companies:
            xs = [p.pfmn for p in c.products]
            ys = [p.size for p in c.products]
            labels = [p.name for p in c.products]
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="markers+text",
                marker=dict(size=14, color=company_colors[c.name], symbol=company_symbols[c.name],
                            line=dict(color="white", width=1)),
                text=labels, textposition="top center",
                textfont=dict(color=company_colors[c.name], size=11, family="Arial Black"),
                name=c.name,
                hovertemplate="<b>%{text}</b><br>Pfmn: %{x:.1f}<br>Size: %{y:.1f}<extra></extra>",
            ))

        fig.update_layout(
            xaxis=dict(range=[0, 20], title="<b>Performance →</b>", gridcolor="#e2e8f0",
                       showgrid=True, zeroline=False),
            yaxis=dict(range=[0, 20], title="<b>← Size (smaller = better)</b>", gridcolor="#e2e8f0",
                       showgrid=True, zeroline=False, autorange="reversed"),
            height=520,
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(t=20, b=40, l=60, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("⊕ Dashed circles = segment rough-cut • ◯ Gold ring = fine-cut zone • ⨯ = ideal spot • Dotted arrows = drift trajectory to R4")

        # Drift summary table
        with st.expander("📊 Segment Drift Forecast Table (R0 → R4)"):
            drift_rows = []
            for seg in state.segments:
                row = {"Segment": seg.name, f"R{state.round_num} (now)": f"({seg.ideal_pfmn:.1f}, {seg.ideal_size:.1f})"}
                for r in range(1, 4 - state.round_num + 1):
                    fp = seg.ideal_pfmn + seg.drift_pfmn * r
                    fs = seg.ideal_size + seg.drift_size * r
                    row[f"R{state.round_num + r}"] = f"({fp:.1f}, {fs:.1f})"
                row["Drift/yr"] = f"({seg.drift_pfmn:+.1f}, {seg.drift_size:+.1f})"
                drift_rows.append(row)
            st.dataframe(pd.DataFrame(drift_rows), use_container_width=True, hide_index=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_pos:
        st.markdown('<div class="capsim-section"><div class="capsim-section-title">Andrews Products</div>', unsafe_allow_html=True)
        for p in andrews.products:
            seg = state.get_segment(p.primary_segment)
            health = "good" if p.age <= seg.ideal_age + 1 else ("warn" if p.age <= seg.ideal_age + 2.5 else "bad")
            st.markdown(f"""
            <div style="border-left: 3px solid #1a365d; padding: 6px 10px; margin: 6px 0; background: white; border: 1px solid #cbd5e0;">
                <b style="color: #1a365d; font-size: 14px;">{p.name}</b> {seg_pill(p.primary_segment)}
                <span class="pill pill-{health}" style="float:right;">age {p.age:.1f}</span>
                <div style="font-size: 11px; color: #718096; margin-top: 4px;">
                    Pos ({p.pfmn:.1f}, {p.size:.1f}) | MTBF {p.mtbf:,} | ${p.price:.2f} | Cap {p.capacity_first_shift}
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Stocks & Bonds (Inquirer Page 2)
    st.markdown(f"""
    <div class="inq-paper">
        <div class="inq-section-head">Stocks & Bonds Summary — Page 2</div>
    """, unsafe_allow_html=True)

    col_st, col_bd = st.columns(2)
    with col_st:
        st.markdown("**Stock Market**")
        stock_df = pd.DataFrame([{
            "Co": c.name,
            "Close$": f"${c.stock_price:.2f}",
            "Shares": f"{c.shares_outstanding:,}",
            "MktCap": fmt_money(c.market_cap),
            "BV/Sh": f"${c.book_value_per_share:.2f}",
            "EPS": f"${c.eps:.2f}",
            "Div": f"${c.dividend_per_share:.2f}",
            "P/E": f"{c.stock_price/max(0.01,c.eps):.1f}" if c.eps > 0 else "—",
        } for c in state.companies])
        st.dataframe(stock_df, use_container_width=True, hide_index=True)

    with col_bd:
        st.markdown(f"**Bond Market** — Next Prime Rate {state.prime_interest_rate*100:.1f}%")
        bond_rows = []
        for c in state.companies:
            for b in c.bonds:
                bond_rows.append({
                    "Co": c.name,
                    "Series": b.series,
                    "Face": fmt_money(b.face_value),
                    "Yield": f"{b.yield_to_maturity*100:.1f}%",
                    "Close": f"${b.market_close:.2f}",
                    "Rating": c.sp_rating,
                })
        st.dataframe(pd.DataFrame(bond_rows), use_container_width=True, hide_index=True, height=300)

    st.markdown('<div class="inq-page-marker">Page 2 — Stocks & Bonds</div></div>', unsafe_allow_html=True)


# ============================================================
# TAB: R&D
# ============================================================

with tab_rd:
    st.markdown('<div class="capsim-section-title">Research & Development — Round {} Decisions</div>'.format(state.round_num + 1), unsafe_allow_html=True)
    pending = ensure_pending()

    st.caption("Capsim rules: Age halves at revise completion. Project duration ≈ 60 days + 180×distance. Cost ≈ $1M base + position move + MTBF change. Round starts Jan 1; products age +1yr automatically if no revise completes.")

    from datetime import date, timedelta
    from math import sqrt

    # Round start date for projecting completion
    round_start = date(state.year + 1, 1, 1)
    round_end = date(state.year + 1, 12, 31)

    # Spreadsheet-like grid (mimics Capsim R&D spreadsheet) — 11 columns
    col_widths = [1.2, 0.7, 0.7, 0.8, 0.7, 0.7, 0.7, 0.8, 1.3, 0.9, 1.0]
    cols_header = st.columns(col_widths)
    headers = ["Product", "Cur Pfmn", "Cur Size", "Cur MTBF", "Cur Age", "→ Pfmn", "→ Size", "→ MTBF", "Revision Date", "New Age", "Est. Cost"]
    for i, h in enumerate(headers):
        with cols_header[i]:
            st.markdown(f"<div style='background:#1a365d; color:white; padding:6px 4px; font-size:10px; font-weight:700; text-align:center; letter-spacing:0.3px;'>{h}</div>", unsafe_allow_html=True)

    for i, p in enumerate(andrews.products):
        seg = state.get_segment(p.primary_segment)
        future_pfmn = seg.center_pfmn + seg.drift_pfmn + seg.ideal_offset_pfmn
        future_size = seg.center_size + seg.drift_size + seg.ideal_offset_size

        # Compute smart default (used only if pending has no saved value)
        ideal_dist = sqrt((future_pfmn - p.pfmn)**2 + (future_size - p.size)**2)
        tqm_factor_default = 1 + andrews.tqm.rd_cycle_time_reduction
        max_reachable_dist = (270 / 180) / tqm_factor_default if tqm_factor_default > 0 else (270/180)
        if ideal_dist > max_reachable_dist and ideal_dist > 0:
            scale = max_reachable_dist / ideal_dist
            smart_p = round(p.pfmn + (future_pfmn - p.pfmn) * scale, 1)
            smart_s = round(p.size + (future_size - p.size) * scale, 1)
        else:
            smart_p = round(future_pfmn, 1)
            smart_s = round(future_size, 1)
        smart_m = min(seg.mtbf_max, p.mtbf + 1000)

        # READ FROM PENDING FIRST — preserve user inputs across refresh
        saved_p = pending.products[i].new_pfmn
        saved_s = pending.products[i].new_size
        saved_m = pending.products[i].new_mtbf
        default_p = saved_p if saved_p is not None else smart_p
        default_s = saved_s if saved_s is not None else smart_s
        default_m = saved_m if saved_m is not None else smart_m

        cols_row = st.columns(col_widths)
        with cols_row[0]:
            st.markdown(f"<div style='padding-top:8px;'><b>{p.name}</b> {seg_pill(p.primary_segment)}</div>", unsafe_allow_html=True)
        with cols_row[1]: st.text_input(f"_curp{i}", f"{p.pfmn:.1f}", disabled=True, label_visibility="collapsed", key=f"rd_curp_{i}")
        with cols_row[2]: st.text_input(f"_curs{i}", f"{p.size:.1f}", disabled=True, label_visibility="collapsed", key=f"rd_curs_{i}")
        with cols_row[3]: st.text_input(f"_curm{i}", f"{p.mtbf:,}", disabled=True, label_visibility="collapsed", key=f"rd_curm_{i}")
        with cols_row[4]: st.text_input(f"_cura{i}", f"{p.age:.1f}", disabled=True, label_visibility="collapsed", key=f"rd_cura_{i}")
        with cols_row[5]:
            new_p = st.number_input("_p", min_value=0.0, max_value=20.0, value=default_p,
                                     step=0.1, label_visibility="collapsed", key=f"rd_newp_{i}",
                                     help=f"R1 ideal: {future_pfmn:.1f} (dist {ideal_dist:.2f}). Smart default = reachable target.")
        with cols_row[6]:
            new_s = st.number_input("_s", min_value=0.0, max_value=20.0, value=default_s,
                                     step=0.1, label_visibility="collapsed", key=f"rd_news_{i}",
                                     help=f"R1 ideal: {future_size:.1f}")
        with cols_row[7]:
            new_m = st.number_input("_m", min_value=10000, max_value=27000,
                                     value=default_m, step=500,
                                     label_visibility="collapsed", key=f"rd_newm_{i}")

        # Calculate revision projection
        is_revising = abs(new_p - p.pfmn) > 0.01 or abs(new_s - p.size) > 0.01 or new_m != p.mtbf
        dist = sqrt((new_p - p.pfmn)**2 + (new_s - p.size)**2)
        # Apply TQM R&D cycle reduction (rd_cycle_time_reduction is NEGATIVE, e.g., -0.40)
        # So tqm_factor = 1 + reduction gives <1 (shorter days) when TQM invested
        tqm_factor = 1 + andrews.tqm.rd_cycle_time_reduction
        days = int((60 + dist * 180) * tqm_factor)
        cost = 1_000_000 + dist * 500_000 + abs(new_m - p.mtbf) / 1000 * 5000

        if is_revising:
            completion_date = round_start + timedelta(days=days)
            # If completes within the year, new age = (old_age + months_to_complete/12) / 2 + months_after_complete/12
            if completion_date <= round_end:
                months_to_complete = days / 30.44
                months_after = max(0, (round_end - completion_date).days / 30.44)
                age_at_completion = p.age + months_to_complete / 12
                new_age = age_at_completion / 2 + months_after / 12
                rev_label = completion_date.strftime("%b %d, %Y")
                age_label = f"{new_age:.2f}"
                age_color = "#2f855a"   # green = good (refreshed)
            else:
                # Project spills into next year — won't apply this round
                rev_label = f"⚠ {completion_date.strftime('%b %Y')}"
                age_label = f"{p.age + 1.0:.2f}"  # ages naturally
                age_color = "#c53030"   # red = won't help this year
        else:
            # No revise → age +1
            rev_label = "(no revise)"
            age_label = f"{p.age + 1.0:.2f}"
            age_color = "#718096"       # gray = neutral

        with cols_row[8]:
            st.markdown(f"<div style='padding-top:6px; font-size:11px; font-family:monospace;'>{rev_label}</div>", unsafe_allow_html=True)
        with cols_row[9]:
            st.markdown(f"<div style='padding-top:6px; font-size:13px; font-weight:700; color:{age_color}; font-family:monospace;'>{age_label}</div>", unsafe_allow_html=True)
        with cols_row[10]:
            cost_label = fmt_money(cost) if is_revising else "—"
            days_label = f"~{days}d" if is_revising else ""
            st.markdown(f"<div style='padding-top:6px; font-size:12px;'><b>{cost_label}</b><br><span style='color:#718096;'>{days_label}</span></div>", unsafe_allow_html=True)

        # Update pending
        pending.products[i].new_pfmn = new_p if abs(new_p - p.pfmn) > 0.01 else None
        pending.products[i].new_size = new_s if abs(new_s - p.size) > 0.01 else None
        pending.products[i].new_mtbf = new_m if new_m != p.mtbf else None

    st.session_state.pending_decisions = pending
    autosave()

    # Legend
    st.markdown("""
    <div style='font-size:11px; color:#718096; padding:6px 12px; background:#edf2f7; border-left:3px solid #d69e2e; margin-top:8px;'>
        <b>New Age color:</b>
        <span style='color:#2f855a;'>● green</span> = revise completes this year (age halves) •
        <span style='color:#c53030;'>● red</span> = project too long, spills to next year (won't apply) •
        <span style='color:#718096;'>● gray</span> = no revise (age +1)
    </div>
    """, unsafe_allow_html=True)

    # Segment drift forecast — matches Industry Conditions Report convention
    # Table A: Centers per round  +  Table B: Ideal Offsets (constant)
    st.markdown('<div class="capsim-section-title" style="margin-top:20px;">📍 Segment Centers per Round (Industry Conditions Report Table 2)</div>', unsafe_allow_html=True)
    st.caption("Segment **centers** drift each year by the rates below. Customer **ideal spot** = Center + Ideal Offset (offset is constant — see Table B).")

    center_rows = []
    for seg in state.segments:
        row = {
            "Segment": seg.name,
            f"R{state.round_num} (now)": f"({seg.center_pfmn:.1f}, {seg.center_size:.1f})",
        }
        for r_ahead in range(1, 5 - state.round_num):
            cp = seg.center_pfmn + seg.drift_pfmn * r_ahead
            cs = seg.center_size + seg.drift_size * r_ahead
            row[f"R{state.round_num + r_ahead}"] = f"({cp:.1f}, {cs:.1f})"
        row["Drift/year"] = f"({seg.drift_pfmn:+.1f}, {seg.drift_size:+.1f})"
        center_rows.append(row)
    st.dataframe(pd.DataFrame(center_rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="capsim-section-title" style="margin-top:16px;">📍 Ideal Spot Offsets (Industry Conditions Report Table 3 — Constant)</div>', unsafe_allow_html=True)
    st.caption("These offsets do NOT change between rounds. Customers prefer products at (Center + Offset).")

    offset_rows = []
    for seg in state.segments:
        ideal_now_p = seg.center_pfmn + seg.ideal_offset_pfmn
        ideal_now_s = seg.center_size + seg.ideal_offset_size
        offset_rows.append({
            "Segment": seg.name,
            "Ideal Offset (Pfmn, Size)": f"({seg.ideal_offset_pfmn:+.1f}, {seg.ideal_offset_size:+.1f})",
            f"Resulting Ideal R{state.round_num}": f"({ideal_now_p:.1f}, {ideal_now_s:.1f})",
            "Why": {
                "Thrift": "Center = Ideal (no offset)",
                "Core": "Slight bias toward faster + smaller",
                "Nano": "Strong bias toward smaller (size matters more than perf)",
                "Elite": "Strong bias toward faster (perf matters more than size)",
            }.get(seg.name, "—"),
        })
    st.dataframe(pd.DataFrame(offset_rows), use_container_width=True, hide_index=True)

    st.markdown("""
    <div style='font-size:11px; color:#4a5568; padding:8px 12px; background:#fef5e7; border-left:3px solid #d69e2e; margin-top:8px;'>
        <b>🧮 To calculate ideal spot at any future round:</b><br>
        <code style='background:white; padding:2px 6px;'>Ideal(Rn) = Center(Rn) + Offset</code><br>
        Example: Nano R3 ideal = (Center R3) + (+0.8, −1.1). Aim R&D projects to land HERE next round.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# TAB: MARKETING
# ============================================================

with tab_mkt:
    st.markdown('<div class="capsim-section-title">Marketing — Round {} Decisions</div>'.format(state.round_num + 1), unsafe_allow_html=True)
    pending = ensure_pending()

    st.caption("Promo: $1.4M maintain / $2M grow / $3M cap • Sales: $3M/product or $4.5M combined / segment")

    # Headers: now 8 cols (added Forecast)
    col_widths_mkt = [1.0, 0.7, 0.9, 1.1, 1.1, 1.0, 0.8, 0.8]
    cols_h = st.columns(col_widths_mkt)
    for i, h in enumerate(["Product", "Seg", "Price ($)", "Promo ($M)", "Sales ($M)", "Forecast (000s)", "Aware", "Access"]):
        with cols_h[i]:
            st.markdown(f"<div style='background:#1a365d; color:white; padding:6px; font-size:11px; font-weight:700; text-align:center;'>{h}</div>", unsafe_allow_html=True)

    for i, p in enumerate(andrews.products):
        seg = state.get_segment(p.primary_segment)

        # READ FROM PENDING FIRST — preserve user inputs across refresh
        saved_price = pending.products[i].price
        saved_promo = pending.products[i].promo_budget
        saved_sales = pending.products[i].sales_budget
        saved_forecast = pending.products[i].forecast
        default_price = saved_price if saved_price is not None else float(p.price)
        default_promo_m = (saved_promo / 1_000_000) if saved_promo is not None else (p.promo_budget / 1_000_000)
        default_sales_m = (saved_sales / 1_000_000) if saved_sales is not None else (p.sales_budget / 1_000_000)
        # Default Forecast = Pessimistic per Playbook methodology
        # = R0_sold × (1 + growth) × 0.90  (apply segment growth, then 10% safety margin)
        forecast_base = int(max(p.units_sold_last, 100) * (1 + seg.growth_rate))
        pessimistic_forecast = int(forecast_base * 0.90)
        optimistic_forecast = int(forecast_base * 1.15)
        default_forecast = saved_forecast if saved_forecast is not None else pessimistic_forecast

        cols_r = st.columns(col_widths_mkt)
        with cols_r[0]: st.markdown(f"<div style='padding-top:8px;'><b>{p.name}</b></div>", unsafe_allow_html=True)
        with cols_r[1]: st.markdown(f"<div style='padding-top:6px;'>{seg_pill(p.primary_segment)}</div>", unsafe_allow_html=True)
        with cols_r[2]:
            new_price = st.number_input("_pr", min_value=0.0, max_value=100.0, value=default_price,
                                         step=0.50, format="%.2f", label_visibility="collapsed",
                                         key=f"mkt_price_{i}",
                                         help=f"Seg range ${seg.price_min}-${seg.price_max}")
        with cols_r[3]:
            new_promo_m = st.number_input("_pm", min_value=0.0, max_value=5.0,
                                           value=default_promo_m, step=0.1, format="%.1f",
                                           label_visibility="collapsed", key=f"mkt_promo_{i}",
                                           help="In $M. $1.4M maintain / $2M grow / $3M cap")
            new_promo = int(new_promo_m * 1_000_000)
        with cols_r[4]:
            new_sales_m = st.number_input("_sl", min_value=0.0, max_value=5.0,
                                           value=default_sales_m, step=0.1, format="%.1f",
                                           label_visibility="collapsed", key=f"mkt_sales_{i}",
                                           help="In $M. $3M solo / $4.5M combined")
            new_sales = int(new_sales_m * 1_000_000)
        with cols_r[5]:
            new_forecast = st.number_input("_fc", min_value=0, max_value=10000,
                                            value=default_forecast, step=50, format="%d",
                                            label_visibility="collapsed", key=f"mkt_fc_{i}",
                                            help=(f"Playbook methodology:\n"
                                                   f"• R0 sold: {p.units_sold_last:,}\n"
                                                   f"• × Growth ({seg.growth_rate*100:.0f}%): {forecast_base:,} = Base\n"
                                                   f"• Pessimistic (× 0.90): {pessimistic_forecast:,} ← recommended for Forecast field\n"
                                                   f"• Optimistic (× 1.15): {optimistic_forecast:,} ← recommended for Production"))
        with cols_r[6]:
            st.markdown(f"<div style='padding-top:6px; font-family:monospace;'>{p.awareness*100:.0f}%</div>", unsafe_allow_html=True)
        with cols_r[7]:
            st.markdown(f"<div style='padding-top:6px; font-family:monospace;'>{p.accessibility.get(p.primary_segment, 0)*100:.0f}%</div>", unsafe_allow_html=True)

        pending.products[i].price = new_price
        pending.products[i].promo_budget = new_promo
        pending.products[i].sales_budget = new_sales
        pending.products[i].forecast = new_forecast

    st.session_state.pending_decisions = pending
    autosave()

    # Total marketing budget summary
    total_promo = sum(pd.promo_budget or 0 for pd in pending.products)
    total_sales = sum(pd.sales_budget or 0 for pd in pending.products)
    st.markdown(f"""
    <div style='background:#edf2f7; padding:10px; margin-top:12px; border-left:3px solid #d69e2e;'>
        <b>Total Round Marketing:</b> Promo {fmt_money(total_promo)} + Sales {fmt_money(total_sales)} = <b>{fmt_money(total_promo + total_sales)}</b>
    </div>
    """, unsafe_allow_html=True)

    # === PLAYBOOK RECOMMENDED FORECAST TABLE ===
    st.markdown('<div class="capsim-section-title" style="margin-top:16px;">📚 Playbook Recommended Forecasts (Pessimistic + Optimistic)</div>', unsafe_allow_html=True)
    st.caption("Strategy: ใส่ **Pessimistic** ใน Forecast field (BSC accuracy safe) • ใส่ **Optimistic** ใน Production Schedule (no stockout)")
    rec_rows = []
    for p in andrews.products:
        seg = state.get_segment(p.primary_segment)
        base = int(max(p.units_sold_last, 100) * (1 + seg.growth_rate))
        rec_rows.append({
            "Product": p.name,
            "R0 Sold": f"{p.units_sold_last:,}",
            "Segment Growth": f"{seg.growth_rate*100:.0f}%",
            "Base (R0 × growth)": f"{base:,}",
            "Pessimistic (90%) → Forecast": f"{int(base * 0.90):,}",
            "Optimistic (115%) → Production": f"{int(base * 1.15):,}",
        })
    st.dataframe(pd.DataFrame(rec_rows), use_container_width=True, hide_index=True)
    st.caption("💡 If you revise + reduce price + run TQM/QFD, ADD +5-10% bonus before splitting into Pessimistic/Optimistic.")


# ============================================================
# TAB: PRODUCTION
# ============================================================

with tab_prod:
    st.markdown('<div class="capsim-section-title">Production — Round {} Decisions</div>'.format(state.round_num + 1), unsafe_allow_html=True)
    pending = ensure_pending()

    st.caption("Capacity in 000s units. 1 shift = 100% util, 2 shifts = 200% max. Automation 1-10 ($4/unit/level).")

    cols_h = st.columns([1.2, 0.9, 1, 1, 1.2, 1.2, 1, 1.2])
    for i, h in enumerate(["Product", "Seg", "Inv", "Capacity", "Production Sched", "New Automation", "Cap Δ (±000)", "Plant Cost"]):
        with cols_h[i]:
            st.markdown(f"<div style='background:#1a365d; color:white; padding:6px; font-size:11px; font-weight:700; text-align:center;'>{h}</div>", unsafe_allow_html=True)

    from sim.engines.production import plant_value, capacity_purchase_cost, automation_upgrade_cost, capacity_sell_value

    total_capex = 0
    for i, p in enumerate(andrews.products):
        cols_r = st.columns([1.2, 0.9, 1, 1, 1.2, 1.2, 1, 1.2])
        with cols_r[0]: st.markdown(f"<div style='padding-top:8px;'><b>{p.name}</b></div>", unsafe_allow_html=True)
        with cols_r[1]: st.markdown(f"<div style='padding-top:6px;'>{seg_pill(p.primary_segment)}</div>", unsafe_allow_html=True)
        with cols_r[2]: st.markdown(f"<div style='padding-top:6px; font-family:monospace;'>{p.inventory:,}</div>", unsafe_allow_html=True)
        with cols_r[3]: st.markdown(f"<div style='padding-top:6px; font-family:monospace;'>{p.capacity_first_shift:,}</div>", unsafe_allow_html=True)
        # READ FROM PENDING FIRST
        saved_prod = pending.products[i].production_schedule
        saved_auto = pending.products[i].new_automation
        saved_cap = pending.products[i].capacity_change
        # Smart default for production: use Forecast × 1.1 buffer if set, else 1.5 × cap
        forecast = pending.products[i].forecast
        default_prod = (saved_prod if saved_prod is not None
                         else (int(forecast * 1.1) if forecast else int(p.capacity_first_shift * 1.5)))
        default_prod = min(default_prod, p.capacity_first_shift * 2)
        default_auto = saved_auto if saved_auto is not None else float(p.automation)
        default_cap = saved_cap if saved_cap else 0

        with cols_r[4]:
            new_prod = st.number_input("_pd", min_value=0, max_value=p.capacity_first_shift * 2,
                                        value=default_prod, step=50,
                                        format="%d", label_visibility="collapsed", key=f"pd_prod_{i}",
                                        help=f"In 000s units. Max 2×cap = {p.capacity_first_shift*2:,}. Forecast × 1.1 buffer recommended.")
        with cols_r[5]:
            new_auto = st.number_input("_au", min_value=1.0, max_value=10.0, value=default_auto,
                                        step=0.5, format="%.1f",
                                        label_visibility="collapsed", key=f"pd_auto_{i}")
        with cols_r[6]:
            cap_change = st.number_input("_cc", min_value=-500, max_value=500, value=default_cap, step=50,
                                          format="%d", label_visibility="collapsed", key=f"pd_cap_{i}",
                                          help="In 000s units. +buy / -sell")
        # Cost calc — MATCH engine: capacity bought at OLD auto, then automation upgrade
        # applies to FULL effective capacity (current + bought capacity, after sell)
        effective_cap = p.capacity_first_shift + (cap_change if cap_change else 0)
        effective_cap = max(0, effective_cap)
        # Engine uses OLD auto for cap purchase (line 99: p.automation), so we mirror
        if cap_change > 0:
            cap_cost = capacity_purchase_cost(cap_change, p.automation)  # OLD auto
        elif cap_change < 0:
            cap_cost = -capacity_sell_value(min(-cap_change, p.capacity_first_shift), p.automation)
        else:
            cap_cost = 0
        # Automation upgrade applies to effective capacity
        auto_cost = automation_upgrade_cost(effective_cap, p.automation, new_auto) if new_auto > p.automation else 0
        total = auto_cost + cap_cost
        total_capex += total
        with cols_r[7]:
            # Show with explicit + or - sign so user sees proceeds clearly
            if total < 0:
                # Net inflow (rare — only if sell proceeds > automation cost)
                display = f"<span style='color:#2f855a;'>+{fmt_money(abs(total))}</span>"
            elif cap_change < 0 and auto_cost > 0:
                # Split: auto cost + sell proceeds
                display = (f"<b>{fmt_money(total)}</b> net<br>"
                          f"<span style='color:#718096; font-size:10px;'>= {fmt_money(auto_cost)} auto - {fmt_money(-cap_cost)} sell</span>")
            elif cap_change < 0:
                # Pure sell — net proceeds
                display = f"<span style='color:#2f855a;'>+{fmt_money(-cap_cost)} proceeds</span>"
            else:
                display = fmt_money(total)
            st.markdown(f"<div style='padding-top:6px; font-size:12px;'>{display}</div>", unsafe_allow_html=True)

        pending.products[i].production_schedule = new_prod
        pending.products[i].new_automation = new_auto if abs(new_auto - p.automation) > 0.01 else None
        pending.products[i].capacity_change = cap_change

    st.session_state.pending_decisions = pending
    autosave()

    st.markdown(f"""
    <div style='background:#edf2f7; padding:10px; margin-top:12px; border-left:3px solid #d69e2e;'>
        <b>Total Capex this round:</b> {fmt_money(total_capex)}
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # SCHEDULE SUMMARY — Forecast vs Production vs Utilization
    # ============================================================
    from sim.engines.production import labor_cost_factor as _lcf, SECOND_SHIFT_LABOR_MULTIPLIER, INVENTORY_CARRY_PCT
    st.markdown('<div class="capsim-section-title" style="margin-top:20px;">📋 Schedule Summary (Forecast → Production → Utilization)</div>', unsafe_allow_html=True)
    sched_rows = []
    for i, p in enumerate(andrews.products):
        fc = pending.products[i].forecast or 0
        prod_sched = pending.products[i].production_schedule or 0
        # EFFECTIVE capacity after sell/buy (cap_change applied)
        cap_change_i = pending.products[i].capacity_change or 0
        effective_cap = max(0, p.capacity_first_shift + cap_change_i)
        # Production after adj = min(scheduled, 2× effective cap)
        prod_actual = min(prod_sched, int(effective_cap * 2))
        # Utilization on EFFECTIVE capacity
        util = (prod_actual / effective_cap * 100) if effective_cap > 0 else 0
        # 2nd shift split based on EFFECTIVE capacity
        first_shift_units = min(prod_actual, effective_cap)
        second_shift_units = max(0, prod_actual - effective_cap)
        second_pct = (second_shift_units / prod_actual * 100) if prod_actual > 0 else 0

        sched_rows.append({
            "Product": p.name,
            "Forecast (000s)": f"{fc:,}",
            "Inventory": f"{p.inventory:,}",
            "Cap (effective)": f"{effective_cap:,}" + (f" ({cap_change_i:+d})" if cap_change_i else ""),
            "Prod Sched": f"{prod_sched:,}",
            "1st Shift": f"{first_shift_units:,}",
            "2nd Shift": f"{second_shift_units:,}",
            "Util %": f"{util:.0f}%",
            "2nd Shift %": f"{second_pct:.0f}%",
        })
    st.dataframe(pd.DataFrame(sched_rows), use_container_width=True, hide_index=True)
    st.caption("💡 Util % uses EFFECTIVE capacity (after cap sell/buy). 100-150% = sweet spot. >150% = 2nd shift (+50% labor). <100% = wasted.")

    # ============================================================
    # MARGINS — Per-unit costs and contribution
    # ============================================================
    st.markdown('<div class="capsim-section-title" style="margin-top:16px;">📊 Margins (Per-Unit Cost Breakdown)</div>', unsafe_allow_html=True)
    pi = andrews.hr.productivity_index
    tqm_mat = andrews.tqm.material_cost_reduction
    tqm_lab = andrews.tqm.labor_cost_reduction

    margin_rows = []
    for i, p in enumerate(andrews.products):
        # Effective labor (with HR + TQM)
        eff_labor = p.labor_cost / max(0.5, pi) * (1 + tqm_lab)
        # Use EFFECTIVE capacity (after cap_change)
        cap_change_i = pending.products[i].capacity_change or 0
        effective_cap = max(0, p.capacity_first_shift + cap_change_i)
        prod_sched = pending.products[i].production_schedule or 0
        if prod_sched > effective_cap:
            second_units = prod_sched - effective_cap
            blended_labor = (effective_cap * eff_labor + second_units * eff_labor * SECOND_SHIFT_LABOR_MULTIPLIER) / prod_sched
        else:
            blended_labor = eff_labor
        eff_material = p.material_cost * (1 + tqm_mat)
        carry_per_unit = (p.material_cost + p.labor_cost) * INVENTORY_CARRY_PCT  # rough
        total_var = blended_labor + eff_material
        cm_pct = ((p.price - total_var) / p.price * 100) if p.price > 0 else 0
        margin_rows.append({
            "Product": p.name,
            "Price": f"${p.price:.2f}",
            "Labor/Unit": f"${blended_labor:.2f}",
            "Material/Unit": f"${eff_material:.2f}",
            "Total Variable": f"${total_var:.2f}",
            "Contribution Margin %": f"{cm_pct:.1f}%",
        })
    st.dataframe(pd.DataFrame(margin_rows), use_container_width=True, hide_index=True)
    st.caption(f"Includes HR Productivity Index ({pi:.3f}) and TQM Material/Labor reductions ({tqm_mat*100:.1f}% / {tqm_lab*100:.1f}%).")

    # ============================================================
    # WORKFORCE SUMMARY
    # ============================================================
    st.markdown('<div class="capsim-section-title" style="margin-top:16px;">👥 Workforce Summary</div>', unsafe_allow_html=True)
    # Estimate needed employees from scheduled production
    total_prod = sum((pd.production_schedule or 0) for pd in pending.products)
    needed = max(50, int(total_prod * 0.144))
    current = andrews.hr.workforce_complement
    new_hires = max(0, needed - int(current * (1 - andrews.hr.turnover_rate)))
    separated = int(current * andrews.hr.turnover_rate)
    first_shift_needed = int(sum(p.capacity_first_shift for p in andrews.products) * 0.144)
    second_shift_needed = max(0, needed - first_shift_needed)

    wf_cols = st.columns(4)
    with wf_cols[0]:
        kpi_card("Last Year Complement", f"{current:,}")
        kpi_card("New Employees", f"{new_hires:,}")
    with wf_cols[1]:
        kpi_card("Needed This Year", f"{needed:,}")
        kpi_card("Separated", f"{separated:,}", f"turnover {andrews.hr.turnover_rate*100:.1f}%")
    with wf_cols[2]:
        kpi_card("1st Shift Needed", f"{first_shift_needed:,}")
        kpi_card("Productivity Index", f"{andrews.hr.productivity_index:.3f}")
    with wf_cols[3]:
        kpi_card("2nd Shift Needed", f"{second_shift_needed:,}")
        kpi_card("Turnover Rate", f"{andrews.hr.turnover_rate*100:.1f}%")


# ============================================================
# TAB: FINANCE
# ============================================================

with tab_fin:
    st.markdown('<div class="capsim-section-title">Finance — Round {} Decisions</div>'.format(state.round_num + 1), unsafe_allow_html=True)
    pending = ensure_pending()

    col_bnd, col_stk = st.columns(2)

    with col_bnd:
        st.markdown("##### Bond Portfolio")
        bond_df = pd.DataFrame([{
            "Series": b.series,
            "Face": fmt_money(b.face_value),
            "Coupon": f"{b.coupon_rate*100:.1f}%",
            "Due": b.year_due,
            "Close$": f"${b.market_close:.2f}",
        } for b in andrews.bonds])
        st.dataframe(bond_df, use_container_width=True, hide_index=True)

        retire_options = [b.series for b in andrews.bonds]
        saved_retire = pending.finance.retire_bond_early or []
        retire_default = [s for s in saved_retire if s in retire_options] if saved_retire else \
                          [b.series for b in andrews.bonds if b.year_due <= state.year + 2]
        retire_selected = st.multiselect(
            "Retire bonds early (1.5% fee)",
            retire_options,
            default=retire_default,
            help="Recommended: retire 13.5S2027 to save interest before maturity",
        )
        saved_issue_bond = pending.finance.issue_bond
        new_bond_m = st.number_input("Issue new bond ($M)", min_value=0.0, max_value=50.0,
                                      value=saved_issue_bond / 1_000_000, step=0.5, format="%.1f",
                                      help="In $M. 5% brokerage fee. Rate = current LT + 1.4%")
        new_bond = int(new_bond_m * 1_000_000)

    with col_stk:
        st.markdown("##### Stock & Dividend")
        st.write(f"Current price: **${andrews.stock_price:.2f}** • Shares out: {andrews.shares_outstanding:,} • Book value/share: ${andrews.book_value_per_share:.2f}")
        saved_div = pending.finance.dividend_per_share
        default_div = saved_div if saved_div else float(andrews.dividend_per_share or 6.50)
        dividend = st.number_input("Dividend per share ($)", min_value=0.0, max_value=20.0,
                                    value=default_div, step=0.25,
                                    format="%.2f",
                                    help=f"Cash out = {andrews.shares_outstanding:,} shares × dividend")
        st.caption(f"Estimated dividend total: {fmt_money(dividend * andrews.shares_outstanding)}")

        saved_issue_stk = pending.finance.issue_stock
        issue_stk_m = st.number_input("Issue stock ($M)", min_value=0.0, max_value=50.0,
                                       value=saved_issue_stk / 1_000_000, step=0.5, format="%.1f",
                                       help="In $M. $500K fee. Dilutes shares.")
        issue_stk = int(issue_stk_m * 1_000_000)

        saved_buyback = pending.finance.buyback_stock
        buyback_stk_m = st.number_input("Buyback stock ($M)", min_value=0.0, max_value=20.0,
                                         value=saved_buyback / 1_000_000, step=0.5, format="%.1f",
                                         help="In $M. At current market price")
        buyback_stk = int(buyback_stk_m * 1_000_000)

    # Policy Lag (AR/AP days)
    st.markdown("##### 📅 Policy Lag (Accounts Receivable / Payable Days)")
    col_ar, col_ap = st.columns(2)
    with col_ar:
        ar_lag = st.slider("Accounts Receivable Lag (days)", min_value=0, max_value=140,
                            value=pending.finance.accounts_receivable_lag or 30, step=15,
                            help="Days customers take to pay. Lower = cash collected faster. 30 = standard.")
    with col_ap:
        ap_lag = st.slider("Accounts Payable Lag (days)", min_value=0, max_value=140,
                            value=pending.finance.accounts_payable_lag or 30, step=15,
                            help="Days you take to pay suppliers. Higher = cash kept longer. 30 = standard.")

    pending.finance = FinanceDecision(
        retire_bond_early=retire_selected,
        issue_bond=new_bond,
        issue_stock=issue_stk,
        buyback_stock=buyback_stk,
        dividend_per_share=dividend,
        accounts_receivable_lag=ar_lag,
        accounts_payable_lag=ap_lag,
    )
    st.session_state.pending_decisions = pending
    autosave()

    # === CASH FLOW SUMMARY (right-side panel-like) ===
    st.divider()
    cf_col, lb_col = st.columns([3, 2])
    with cf_col:
        st.markdown('<div class="capsim-section-title">💵 Projected Cash Flow Summary</div>', unsafe_allow_html=True)
        # Compute projected components
        starting_cash = andrews.cash
        # Operating: profit + depreciation - delta_AR - delta_Inv + delta_AP  (approximate using last round)
        from sim.engines.production import annual_depreciation
        depreciation = sum(annual_depreciation(p) for p in andrews.products)
        proj_operating = andrews.profit_last + depreciation
        # Investing: capex (capacity buy + automation upgrade)
        from sim.engines.production import capacity_purchase_cost, automation_upgrade_cost
        proj_investing = 0
        for pd_ in pending.products:
            prod = next(pp for pp in andrews.products if pp.name == pd_.product_name)
            if pd_.new_automation and pd_.new_automation > prod.automation:
                proj_investing -= automation_upgrade_cost(prod.capacity_first_shift, prod.automation, pd_.new_automation)
            if pd_.capacity_change and pd_.capacity_change > 0:
                proj_investing -= capacity_purchase_cost(pd_.capacity_change, pd_.new_automation or prod.automation)
        # Financing: dividend + bond issue/retire + stock issue/buyback - current_debt change
        div_total = dividend * andrews.shares_outstanding
        bond_issued = new_bond * (1 - 0.05)  # net after fee
        bond_retired = sum(b.face_value * (b.market_close/100 + 0.015) for b in andrews.bonds if b.series in retire_selected)
        repay_current = andrews.current_debt
        proj_financing = bond_issued + issue_stk * (1 - 500_000/max(1, issue_stk) if issue_stk > 0 else 0) \
                          - buyback_stk - div_total - bond_retired - repay_current
        closing_cash = starting_cash + proj_operating + proj_investing + proj_financing

        cf_rows = pd.DataFrame([
            {"Item": "Starting Cash Position (Jan 1)", "Amount": fmt_money(starting_cash)},
            {"Item": "Cash from Operating (profit + depr)", "Amount": fmt_money(proj_operating)},
            {"Item": "Cash from Investing (capex)", "Amount": fmt_money(proj_investing)},
            {"Item": "Cash from Financing", "Amount": fmt_money(proj_financing)},
            {"Item": "Closing Cash Position (Dec 31)", "Amount": fmt_money(closing_cash)},
        ])
        st.dataframe(cf_rows, use_container_width=True, hide_index=True)
        st.caption("⚠️ Approximate. Real round may differ based on actual sales + AR/AP changes.")

    with lb_col:
        st.markdown('<div class="capsim-section-title">🥧 Liabilities & Owner\'s Equity</div>', unsafe_allow_html=True)
        ap_val = andrews.accounts_payable
        cd_val = andrews.current_debt
        ltd_val = sum(b.face_value for b in andrews.bonds)
        cs_val = andrews.common_stock
        re_val = andrews.retained_earnings
        labels = ["Accounts Payable", "Current Debt", "Long-Term Debt", "Common Stock", "Retained Earnings"]
        values = [ap_val, cd_val, ltd_val, cs_val, re_val]
        colors = ["#2caffe", "#544fc5", "#00e272", "#fe6a35", "#6b8abc"]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors), hole=0.4)])
        fig.update_layout(height=300, margin=dict(t=10, b=10), showlegend=True,
                          legend=dict(orientation="v", x=1.05, y=0.5))
        st.plotly_chart(fig, use_container_width=True)

    # Outstanding Bonds detail
    st.markdown('<div class="capsim-section-title">📜 Outstanding Bonds</div>', unsafe_allow_html=True)
    outst_bonds = pd.DataFrame([{
        "Series": b.series,
        "Face Amount": fmt_money(b.face_value),
        "Current Yield": f"{b.yield_to_maturity*100:.1f}%",
        "Closing Price": f"${b.market_close:.2f}",
        "Year Due": b.year_due,
        "Status": "⚠ Matures next round!" if b.year_due <= state.year + 1 else "ok"
    } for b in andrews.bonds])
    st.dataframe(outst_bonds, use_container_width=True, hide_index=True)


# ============================================================
# TAB: HR
# ============================================================

with tab_hr:
    st.markdown('<div class="capsim-section-title">Human Resources — Round {} Decisions</div>'.format(state.round_num + 1), unsafe_allow_html=True)
    pending = ensure_pending()

    st.caption("OLD Comp-XM HR module: Recruit Spend ($0-$5K) + Training Hours (0-80hr × $20). Workforce Complement set on Production page.")

    # READ FROM PENDING FIRST
    default_recruit = int(pending.hr.recruit_spend) if pending.hr.recruit_spend else 2500
    default_training = pending.hr.training_hours if pending.hr.training_hours else 40

    col_r, col_t = st.columns(2)
    with col_r:
        recruit = st.slider("Recruit Spend ($/employee above auto $1,000)",
                             min_value=0, max_value=5000, value=default_recruit, step=500,
                             help="$0 = basic hires, $5000 = best talent")
        st.caption(f"× {andrews.hr.workforce_complement} employees = {fmt_money(recruit * andrews.hr.workforce_complement)}/yr (incl auto $1K)")
    with col_t:
        training = st.slider("Training Hours (hrs/employee/yr × $20)",
                              min_value=0, max_value=80, value=default_training, step=10,
                              help="Up to 80hr × $20 = $1,600/employee/yr")
        st.caption(f"× {andrews.hr.workforce_complement} employees = {fmt_money(training * 20 * andrews.hr.workforce_complement)}/yr")

    pi_new = 1.0 + 0.09 * (recruit/5000) + 0.09 * (training/80)
    turnover_new = 0.10 - 0.05 * (training/80)
    # Use ACTUAL new_hires estimate (matches engine), not magic 200
    from sim.engines.hr import employees_needed as _emp_needed
    # Estimate new hires from scheduled production
    total_prod_for_hr = sum((pdec.production_schedule or 0) for pdec in pending.products) or 1
    needed_emp = max(50, int(total_prod_for_hr * 0.144))
    est_separated = int(andrews.hr.workforce_complement * turnover_new)
    est_new_hires = max(0, needed_emp - (andrews.hr.workforce_complement - est_separated))
    hr_admin_cost = training * 20 * needed_emp + (recruit + 1000) * est_new_hires

    pending.hr = HRDecision(recruit_spend=recruit, training_hours=training)
    st.session_state.pending_decisions = pending
    autosave()

    # === HR IMPACTS PANELS (Yearly + Cumulative) ===
    st.divider()
    imp_col1, imp_col2 = st.columns(2)
    with imp_col1:
        st.markdown('<div class="capsim-section-title">📅 Yearly Impacts (this round\'s decision)</div>', unsafe_allow_html=True)
        pi_delta = pi_new - andrews.hr.productivity_index
        turnover_delta = turnover_new - andrews.hr.turnover_rate
        yi_df = pd.DataFrame([
            {"Metric": "Productivity Index", "Change": f"{pi_delta:+.3f}", "New Value": f"{pi_new:.3f}"},
            {"Metric": "Turnover Rate", "Change": f"{turnover_delta*100:+.1f}%", "New Value": f"{turnover_new*100:.1f}%"},
            {"Metric": "Recruiting Cost", "Change": "—", "New Value": fmt_money((recruit + 1000) * 200)},
            {"Metric": "Training Cost", "Change": "—", "New Value": fmt_money(training * 20 * andrews.hr.workforce_complement)},
            {"Metric": "Total HR Admin", "Change": "—", "New Value": fmt_money(hr_admin_cost)},
        ])
        st.dataframe(yi_df, use_container_width=True, hide_index=True)

    with imp_col2:
        st.markdown('<div class="capsim-section-title">📈 Cumulative HR State</div>', unsafe_allow_html=True)
        ci_df = pd.DataFrame([
            {"Metric": "Workforce Complement", "Value": f"{andrews.hr.workforce_complement:,}"},
            {"Metric": "1st Shift", "Value": f"{andrews.hr.first_shift_complement:,}"},
            {"Metric": "2nd Shift", "Value": f"{andrews.hr.second_shift_complement:,}"},
            {"Metric": "Productivity Index (current)", "Value": f"{andrews.hr.productivity_index:.3f}"},
            {"Metric": "Turnover Rate (current)", "Value": f"{andrews.hr.turnover_rate*100:.1f}%"},
            {"Metric": "Total HR Admin Cost (last yr)", "Value": fmt_money(andrews.hr.total_hr_admin_cost)},
        ])
        st.dataframe(ci_df, use_container_width=True, hide_index=True)


# ============================================================
# TAB: TQM
# ============================================================

with tab_tqm:
    st.markdown('<div class="capsim-section-title">Total Quality Management — Round {} Decisions</div>'.format(state.round_num + 1), unsafe_allow_html=True)
    pending = ensure_pending()

    st.caption("10 initiatives, $0-$2M per round each, $4M cumulative cap per initiative. S-curve response.")

    rec = recommended_initiatives_for_round(state.round_num + 1)
    if rec:
        st.info(f"💡 **Recommended for R{state.round_num + 1}**: " +
                ", ".join(f"{n}: {fmt_money(v)}" for n, v in rec.items()))

    tqm_decisions = {}
    cols = st.columns(2)
    saved_tqm = pending.tqm.initiatives or {}
    for idx, name in enumerate(INITIATIVE_NAMES):
        with cols[idx % 2]:
            cumulative = andrews.tqm.cumulative_spend.get(name, 0)
            # READ FROM PENDING FIRST, then recommended default
            saved_amt = saved_tqm.get(name)
            default_amt = saved_amt if saved_amt is not None else rec.get(name, 0)
            spend_m = st.slider(f"{name} — cumulative: {fmt_money(cumulative)} / $4M cap",
                                min_value=0.0, max_value=2.0,
                                value=default_amt / 1_000_000, step=0.1,
                                format="$%.1fM", key=f"tqm_{name}")
            spend = int(spend_m * 1_000_000)
            if spend > 0:
                tqm_decisions[name] = spend

    total_tqm = sum(tqm_decisions.values())
    st.markdown(f"""
    <div style='background:#edf2f7; padding:10px; margin-top:12px; border-left:3px solid #d69e2e;'>
        <b>Total TQM this round:</b> {fmt_money(total_tqm)}
    </div>
    """, unsafe_allow_html=True)

    pending.tqm = TQMDecision(initiatives=tqm_decisions)
    st.session_state.pending_decisions = pending
    autosave()

    # === TQM IMPACTS PANELS (Yearly + Cumulative) ===
    st.divider()
    from sim.engines.tqm import TQM_IMPACTS, s_curve_factor

    imp_col1, imp_col2 = st.columns(2)
    with imp_col1:
        st.markdown('<div class="capsim-section-title">📅 Yearly Impacts (this round\'s spend → projected)</div>', unsafe_allow_html=True)
        # Simulate what cumulative impacts will be AFTER applying this round's decisions
        proj_cumulative = {name: andrews.tqm.cumulative_spend.get(name, 0) + tqm_decisions.get(name, 0)
                           for name in INITIATIVE_NAMES}
        proj_mat = proj_lab = proj_rd = proj_adm = proj_dem = 0.0
        for name, impacts in TQM_IMPACTS.items():
            factor = s_curve_factor(proj_cumulative.get(name, 0))
            proj_mat += impacts["material"] * factor
            proj_lab += impacts["labor"] * factor
            proj_rd += impacts["rd_cycle"] * factor
            proj_adm += impacts["admin"] * factor
            proj_dem += impacts["demand"] * factor
        cur_mat = andrews.tqm.material_cost_reduction
        cur_lab = andrews.tqm.labor_cost_reduction
        cur_rd = andrews.tqm.rd_cycle_time_reduction
        cur_adm = andrews.tqm.admin_cost_reduction
        cur_dem = andrews.tqm.demand_increase
        yi_df = pd.DataFrame([
            {"Metric": "Material Cost", "Current": f"{cur_mat*100:.1f}%", "After This Round": f"{proj_mat*100:.1f}%", "Δ": f"{(proj_mat-cur_mat)*100:+.1f}%"},
            {"Metric": "Labor Cost", "Current": f"{cur_lab*100:.1f}%", "After This Round": f"{proj_lab*100:.1f}%", "Δ": f"{(proj_lab-cur_lab)*100:+.1f}%"},
            {"Metric": "R&D Cycle Time", "Current": f"{cur_rd*100:.1f}%", "After This Round": f"{proj_rd*100:.1f}%", "Δ": f"{(proj_rd-cur_rd)*100:+.1f}%"},
            {"Metric": "Admin Cost", "Current": f"{cur_adm*100:.1f}%", "After This Round": f"{proj_adm*100:.1f}%", "Δ": f"{(proj_adm-cur_adm)*100:+.1f}%"},
            {"Metric": "Demand Increase", "Current": f"+{cur_dem*100:.1f}%", "After This Round": f"+{proj_dem*100:.1f}%", "Δ": f"{(proj_dem-cur_dem)*100:+.1f}%"},
            {"Metric": "Total Round Spend", "Current": "—", "After This Round": fmt_money(total_tqm), "Δ": "—"},
        ])
        st.dataframe(yi_df, use_container_width=True, hide_index=True)

    with imp_col2:
        st.markdown('<div class="capsim-section-title">📈 Cumulative Impacts (all rounds to date)</div>', unsafe_allow_html=True)
        ci_df = pd.DataFrame([
            {"Metric": "Material Cost Reduction", "Value": f"{cur_mat*100:.1f}%", "Max": "-11.8%"},
            {"Metric": "Labor Cost Reduction", "Value": f"{cur_lab*100:.1f}%", "Max": "-14.0%"},
            {"Metric": "R&D Cycle Time Reduction", "Value": f"{cur_rd*100:.1f}%", "Max": "-40.0%"},
            {"Metric": "Admin Cost Reduction", "Value": f"{cur_adm*100:.1f}%", "Max": "-60.0%"},
            {"Metric": "Demand Increase", "Value": f"+{cur_dem*100:.1f}%", "Max": "+14.4%"},
            {"Metric": "Total Cumulative Spend", "Value": fmt_money(andrews.tqm.total_expenditures), "Max": "—"},
        ])
        st.dataframe(ci_df, use_container_width=True, hide_index=True)

    st.divider()

    # The big ADVANCE ROUND button
    advance_col1, advance_col2, advance_col3 = st.columns([1, 2, 1])
    with advance_col2:
        if st.button(f"🚀 SUBMIT ALL DECISIONS & ADVANCE TO R{state.round_num + 1}", type="primary", use_container_width=True):
            if state.round_num >= 4:
                st.error("Game already at R4. Reset to play again.")
            else:
                with st.spinner(f"Simulating Round {state.round_num + 1}..."):
                    prev_state = state.model_copy(deep=True)
                    st.session_state.prev_state_snapshot = prev_state
                    result = advance_round(state, pending, prev_state=prev_state)
                    st.session_state.bsc_history.append(result["bsc"])
                    st.session_state.pending_decisions = None
                    save_state()
                st.success(f"Round {result['round_num']} complete! BSC: {result['bsc']['total']:.1f}")
                st.balloons()
                st.rerun()


# ============================================================
# TAB: INQUIRER (single long scrollable page, mimics real Capstone Courier)
# ============================================================

with tab_inq:
    inq = full_inquirer(state)
    fp_data = inq["front_page"]["data"]
    company_colors = {"Andrews": "#1a365d", "Baldwin": "#9b2c2c", "Chester": "#2c7a7b", "Digby": "#744210"}

    # ---------- HEADER + TABLE OF CONTENTS ----------
    st.markdown(f"""
    <div class="inq-paper" id="inq-top">
        <div class="inq-masthead">
            <h1>COMP-XM&reg; INQUIRER</h1>
            <div class="subtitle">Round {state.round_num} • Dec 31, {state.year} • Industry Report</div>
        </div>
        <h3 style="color:#1a365d; font-family:Georgia,serif; margin-bottom:8px;">Contents</h3>
        <hr style="border-top:2px solid #1a365d; margin:8px 0 12px 0;">
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:8px 24px; font-family:Georgia,serif;">
            <div><b>Section 1</b> <a href="#sec-1-front" style="color:#1a365d;">Front Page</a></div>
            <div><b>Section 5</b> <a href="#sec-5-thrift" style="color:#1a365d;">Thrift Segment Analysis</a></div>
            <div><b>Section 9</b> <a href="#sec-9-market" style="color:#1a365d;">Market Share</a></div>
            <div><b>Section 2</b> <a href="#sec-2-stocks" style="color:#1a365d;">Stock &amp; Bonds</a></div>
            <div><b>Section 6</b> <a href="#sec-6-core" style="color:#1a365d;">Core Segment Analysis</a></div>
            <div><b>Section 10</b> <a href="#sec-10-pmap" style="color:#1a365d;">Perceptual Map</a></div>
            <div><b>Section 3</b> <a href="#sec-3-fin" style="color:#1a365d;">Financial Summary</a></div>
            <div><b>Section 7</b> <a href="#sec-7-nano" style="color:#1a365d;">Nano Segment Analysis</a></div>
            <div><b>Section 11</b> <a href="#sec-11-custom" style="color:#1a365d;">HR &amp; TQM Modules</a></div>
            <div><b>Section 4</b> <a href="#sec-4-prod" style="color:#1a365d;">Production Analysis</a></div>
            <div><b>Section 8</b> <a href="#sec-8-elite" style="color:#1a365d;">Elite Segment Analysis</a></div>
            <div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ====== SECTION 1: FRONT PAGE ======
    st.markdown(f"""
    <div class="inq-paper" id="sec-1-front">
        <h2 style="display:flex; justify-content:space-between; align-items:center; color:#1a365d;">
            <span>Front Page</span>
            <span style="font-size:13px; color:#718096;">Round {state.round_num} Dec. 31, {state.year} &nbsp;&nbsp; CompXM-Andrews</span>
        </h2><hr>
    """, unsafe_allow_html=True)

    # Selected Financial Statistics — exact row order from real Capstone
    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">SELECTED FINANCIAL STATISTICS</div>', unsafe_allow_html=True)
    metric_rows = [
        ("ROS", lambda c: f"{c.ros*100:.1f}%"),
        ("Asset Turnover", lambda c: f"{c.asset_turnover:.2f}"),
        ("ROA", lambda c: f"{c.roa*100:.1f}%"),
        ("Leverage", lambda c: f"{c.leverage:.2f}"),
        ("ROE", lambda c: f"{c.roe*100:.1f}%"),
        ("Sales", lambda c: fmt_money(c.sales_last)),
        ("EBIT", lambda c: fmt_money(c.ebit_last)),
        ("Profit", lambda c: fmt_money(c.profit_last)),
        ("Cumulative Profit", lambda c: fmt_money(c.cumulative_profit)),
        ("SG&A / Sales", lambda c: f"{c.sga_last / max(1,c.sales_last)*100:.1f}%"),
        ("Contribution Margin", lambda c: f"{c.contribution_margin_last / max(1,c.sales_last)*100:.1f}%"),
        ("Emergency Loan", lambda c: fmt_money(c.emergency_loan) if c.emergency_loan > 0 else "$0"),
    ]
    sfs_data = {"Category": [m[0] for m in metric_rows]}
    for c in state.companies:
        sfs_data[c.name] = [fn(c) for _, fn in metric_rows]
    # Average column (where numeric)
    def _avg(metric_name):
        vals = []
        for c in state.companies:
            try:
                if metric_name == "ROS": vals.append(c.ros)
                elif metric_name == "Asset Turnover": vals.append(c.asset_turnover)
                elif metric_name == "ROA": vals.append(c.roa)
                elif metric_name == "Leverage": vals.append(c.leverage)
                elif metric_name == "ROE": vals.append(c.roe)
                elif metric_name == "Sales": vals.append(c.sales_last)
                elif metric_name == "EBIT": vals.append(c.ebit_last)
                elif metric_name == "Profit": vals.append(c.profit_last)
                elif metric_name == "Cumulative Profit": vals.append(c.cumulative_profit)
                elif metric_name == "SG&A / Sales": vals.append(c.sga_last / max(1,c.sales_last))
                elif metric_name == "Contribution Margin": vals.append(c.contribution_margin_last / max(1,c.sales_last))
                elif metric_name == "Emergency Loan": vals.append(c.emergency_loan)
            except Exception: pass
        return sum(vals)/len(vals) if vals else 0
    avg_col = []
    for name, _ in metric_rows:
        a = _avg(name)
        if "%" in name or name in ("ROS", "ROA", "ROE", "SG&A / Sales", "Contribution Margin"):
            avg_col.append(f"{a*100:.1f}%")
        elif name in ("Asset Turnover", "Leverage"):
            avg_col.append(f"{a:.2f}")
        else:
            avg_col.append(fmt_money(a))
    sfs_data["Average"] = avg_col
    st.dataframe(pd.DataFrame(sfs_data), use_container_width=True, hide_index=True)

    # Percent of Sales + Market Share charts
    col_ps, col_ms = st.columns(2)
    with col_ps:
        st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">PERCENT OF SALES</div>', unsafe_allow_html=True)
        ps_data = []
        for c in state.companies:
            sales = max(1, c.sales_last)
            var_cost = c.sales_last - c.contribution_margin_last
            depr = c.sales_last * 0.04  # approx
            sga = c.sga_last
            profit = c.profit_last
            other = max(0, sales - var_cost - depr - sga - profit)
            ps_data.append({
                "Company": c.name,
                "Var Costs": var_cost/sales*100,
                "Depreciation": depr/sales*100,
                "SG&A": sga/sales*100,
                "Other": other/sales*100,
                "Profit": profit/sales*100,
            })
        ps_df = pd.DataFrame(ps_data).set_index("Company")
        fig = px.bar(ps_df, orientation="v", barmode="stack",
                     color_discrete_sequence=["#2caffe", "#544fc5", "#00e272", "#fe6a35", "#6b8abc"])
        fig.update_layout(height=300, margin=dict(t=20, b=20), yaxis_title="% of Sales",
                          plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)
    with col_ms:
        st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">MARKET SHARE</div>', unsafe_allow_html=True)
        ms_data = inq["market_share"]
        totals = [(c.name, ms_data[c.name]["Total"]) for c in state.companies]
        fig = go.Figure(data=[go.Pie(
            labels=[t[0] for t in totals], values=[t[1] for t in totals],
            marker=dict(colors=[company_colors[t[0]] for t in totals]),
            hole=0.4, textposition="auto", textinfo="label+percent",
        )])
        fig.update_layout(height=300, margin=dict(t=20, b=20),
                          paper_bgcolor="white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Page 1</div></div>', unsafe_allow_html=True)

    # ====== SECTION 2: STOCK & BONDS ======
    st.markdown(f"""
    <div class="inq-paper" id="sec-2-stocks">
        <h2 style="display:flex; justify-content:space-between; align-items:center; color:#1a365d;">
            <span>Stock &amp; Bonds</span>
            <span style="font-size:13px; color:#718096;">Round {state.round_num} Dec. 31, {state.year}</span>
        </h2><hr>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">STOCK MARKET SUMMARY</div>', unsafe_allow_html=True)
    stock_df = pd.DataFrame([{
        "Company": c.name, "Close$": f"${c.stock_price:.2f}",
        "Change": "—",  # historical change not tracked yet
        "Shares": f"{c.shares_outstanding:,}",
        "MarketCap": fmt_money(c.market_cap),
        "Book Value/Sh": f"${c.book_value_per_share:.2f}",
        "EPS": f"${c.eps:.2f}",
        "Dividend": f"${c.dividend_per_share:.2f}",
        "Yield": f"{c.dividend_per_share/max(0.01,c.stock_price)*100:.1f}%" if c.stock_price > 0 else "0%",
        "P/E": f"{c.stock_price/max(0.01,c.eps):.1f}" if c.eps > 0 else "—",
    } for c in state.companies])
    st.dataframe(stock_df, use_container_width=True, hide_index=True)

    # Stock price chart (history if available)
    if state.history:
        hist_df = pd.DataFrame(state.history)
        fig = px.line(hist_df, x="round", y="andrews_stock", markers=True,
                       title="Andrews Stock Price Trend",
                       color_discrete_sequence=[company_colors["Andrews"]])
        fig.update_layout(height=260, margin=dict(t=40, b=20), plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">BOND MARKET SUMMARY</div>', unsafe_allow_html=True)
    bond_rows = []
    for c in state.companies:
        for b in c.bonds:
            bond_rows.append({
                "Company": c.name, "Series#": b.series,
                "Face": fmt_money(b.face_value),
                "Yield": f"{b.yield_to_maturity*100:.1f}%",
                "Close$": f"${b.market_close:.2f}",
                "S&P": c.sp_rating,
            })
    st.dataframe(pd.DataFrame(bond_rows), use_container_width=True, hide_index=True, height=300)
    st.markdown(f"<p style='font-style:italic; margin:8px 0;'>Next Year's Prime Rate: <b>{state.prime_interest_rate*100:.1f}%</b></p>", unsafe_allow_html=True)

    st.markdown('<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Page 2</div></div>', unsafe_allow_html=True)

    # ====== SECTION 3: FINANCIAL SUMMARY ======
    st.markdown(f"""
    <div class="inq-paper" id="sec-3-fin">
        <h2 style="display:flex; justify-content:space-between; align-items:center; color:#1a365d;">
            <span>Financial Summary</span>
            <span style="font-size:13px; color:#718096;">Round {state.round_num} Dec. 31, {state.year}</span>
        </h2><hr>
    """, unsafe_allow_html=True)

    fs_table = inq["financial_summary"]
    # Cash Flow Statement (subset of approximations)
    cf_rows = [
        ("Net Income", "Net_Profit"),
        ("Sales", "Sales"),
        ("Variable Costs", "Variable_Costs"),
        ("Contribution Margin", "Contribution_Margin"),
        ("SG&A", "SGA"),
        ("EBIT", "EBIT"),
    ]
    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">CASH FLOW + INCOME SURVEY</div>', unsafe_allow_html=True)
    cf_df = pd.DataFrame({"Category": [r[0] for r in cf_rows], **{
        c.name: [fmt_money(fs_table[c.name][r[1]]) for r in cf_rows] for c in state.companies
    }})
    st.dataframe(cf_df, use_container_width=True, hide_index=True)

    bs_rows = [
        ("Cash", "Cash"), ("Accounts Receivable", "AR"), ("Inventory", "Inventory"),
        ("Plant (Net)", "Plant_Net"), ("Total Assets", "Total_Assets"),
        ("Accounts Payable", "AP"), ("Current Debt", "Current_Debt"), ("Long Term Debt", "LT_Debt"),
        ("Common Stock", "Common_Stock"), ("Retained Earnings", "Retained_Earnings"),
        ("Total Equity", "Total_Equity"),
    ]
    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">BALANCE SHEET SURVEY</div>', unsafe_allow_html=True)
    bs_df = pd.DataFrame({"Category": [r[0] for r in bs_rows], **{
        c.name: [fmt_money(fs_table[c.name][r[1]]) for r in bs_rows] for c in state.companies
    }})
    st.dataframe(bs_df, use_container_width=True, hide_index=True)

    st.markdown('<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Page 3</div></div>', unsafe_allow_html=True)

    # ====== SECTION 4: PRODUCTION ANALYSIS ======
    st.markdown(f"""
    <div class="inq-paper" id="sec-4-prod">
        <h2 style="display:flex; justify-content:space-between; align-items:center; color:#1a365d;">
            <span>Production Analysis</span>
            <span style="font-size:13px; color:#718096;">Round {state.round_num} Dec. 31, {state.year}</span>
        </h2><hr>
    """, unsafe_allow_html=True)

    # Production vs Capacity (per company total)
    pvc_rows = []
    for c in state.companies:
        total_cap = sum(p.capacity_first_shift for p in c.products)
        total_prod = sum(p.units_produced_last for p in c.products)
        pvc_rows.append({"Company": c.name, "Capacity (1k)": total_cap, "Production (1k)": total_prod})
    pvc_df = pd.DataFrame(pvc_rows)
    fig = px.bar(pvc_df, x="Company", y=["Capacity (1k)", "Production (1k)"],
                  barmode="group", title="Production vs Capacity",
                  color_discrete_sequence=["#cbd5e0", "#1a365d"])
    fig.update_layout(height=260, margin=dict(t=40, b=20), plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

    # Plant Information table (matches Capsim 17-col format)
    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">PLANT INFORMATION</div>', unsafe_allow_html=True)
    prod_df = pd.DataFrame(inq["production_analysis"])
    prod_df["2nd Shift OT"] = "—"
    prod_df["Contrib Mgn %"] = "—"
    prod_df["Util%"] = prod_df["Utilization_Pct"].round(0).astype(int).astype(str) + "%"
    plant_cols = ["Company", "Name", "Segment", "Units_Sold", "Inventory",
                   "Revision_Date", "Age", "MTBF", "Pfmn", "Size",
                   "Price", "Material_Cost", "Labor_Cost", "Contrib Mgn %",
                   "2nd Shift OT", "Automation", "Capacity_Next", "Util%"]
    st.dataframe(prod_df[plant_cols], use_container_width=True, hide_index=True)

    st.markdown('<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Page 4</div></div>', unsafe_allow_html=True)

    # ====== SECTIONS 5-8: SEGMENT ANALYSIS (4-quadrant layout) ======
    segment_page_map = {"Thrift": ("5-thrift", 5), "Core": ("6-core", 6),
                         "Nano": ("7-nano", 7), "Elite": ("8-elite", 8)}
    for seg_name, (anchor, page_num) in segment_page_map.items():
        seg_data = inq["segments"][seg_name]
        seg_obj = state.get_segment(seg_name)

        st.markdown(f"""
        <div class="inq-paper" id="sec-{anchor}">
            <h2 style="display:flex; justify-content:space-between; align-items:center; color:#1a365d;">
                <span>{seg_name} Segment Analysis</span>
                <span style="font-size:13px; color:#718096;">Round {state.round_num} Dec. 31, {state.year}</span>
            </h2><hr>
        """, unsafe_allow_html=True)

        # 4-quadrant layout: TL Stats+Criteria | TR Access bars + Perceptual + Mkt share
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f'<h3 style="color:#1a365d;">{seg_name} Statistics</h3>', unsafe_allow_html=True)
            stats_df = pd.DataFrame([
                {"Metric": f"{state.year} Total Market Size", "Value": f"{seg_data['industry_demand']:,} units"},
                {"Metric": f"{state.year} Total Units Sold", "Value": f"{seg_data['industry_sold']:,} units"},
                {"Metric": "Segment % of Total Industry", "Value": f"{seg_data['industry_demand'] / sum(state.industry_unit_demand.values()) * 100:.1f}%"},
                {"Metric": f"{state.year + 1} Demand Growth Rate", "Value": seg_data['next_growth']},
            ])
            st.dataframe(stats_df, use_container_width=True, hide_index=True)

            st.markdown(f'<h3 style="color:#1a365d;">{seg_name} Customer Buying Criteria</h3>', unsafe_allow_html=True)
            # Build BC table with CENTER + OFFSET shown clearly (per user feedback)
            bc = seg_data["buying_criteria"]
            criteria_df = pd.DataFrame([
                {"Criterion": "Price", "Expectations": f"${bc['Price']['range'][0]:.2f}-${bc['Price']['range'][1]:.2f}", "Importance": bc['Price']['weight']},
                {"Criterion": "Age", "Expectations": f"Ideal {bc['Age']['ideal']:.1f} years", "Importance": bc['Age']['weight']},
                {"Criterion": "MTBF (Reliability)", "Expectations": f"{bc['MTBF']['range'][0]:,}-{bc['MTBF']['range'][1]:,}", "Importance": bc['MTBF']['weight']},
                {"Criterion": "Position (Ideal Spot)", "Expectations": f"Pfmn {seg_obj.ideal_pfmn:.1f} Size {seg_obj.ideal_size:.1f}", "Importance": bc['Position']['weight']},
            ])
            st.dataframe(criteria_df, use_container_width=True, hide_index=True)
            st.caption(f"📍 **Segment Center** ({seg_obj.center_pfmn:.1f}, {seg_obj.center_size:.1f}) + **Ideal Offset** ({seg_obj.ideal_offset_pfmn:+.1f}, {seg_obj.ideal_offset_size:+.1f}) = Ideal Position above. Center drifts by ({seg_obj.drift_pfmn:+.1f}, {seg_obj.drift_size:+.1f}) per year.")

        with col_r:
            st.markdown(f'<h3 style="color:#1a365d;">Accessibility — {seg_name}</h3>', unsafe_allow_html=True)
            access_data = []
            for c in state.companies:
                segment_products = [p for p in c.products if p.primary_segment == seg_name]
                if segment_products:
                    avg_access = sum(p.accessibility.get(seg_name, 0) for p in segment_products) / len(segment_products)
                    access_data.append({"Company": c.name, "Accessibility %": avg_access * 100})
                else:
                    access_data.append({"Company": c.name, "Accessibility %": 0})
            access_df = pd.DataFrame(access_data)
            fig = px.bar(access_df, y="Company", x="Accessibility %", orientation="h",
                         color="Company", color_discrete_map=company_colors,
                         range_x=[0, 100])
            fig.update_layout(height=200, margin=dict(t=10, b=10, l=10, r=10),
                              plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Per-segment perceptual map (focus on this segment)
            st.markdown(f'<h3 style="color:#1a365d;">Perceptual Map — {seg_name}</h3>', unsafe_allow_html=True)
            import math as _m
            fig = go.Figure()
            # Ideal spot circle (fine-cut)
            theta = list(range(0, 361, 5))
            xs = [seg_obj.ideal_pfmn + 2.5 * _m.cos(_m.radians(t)) for t in theta]
            ys = [seg_obj.ideal_size + 2.5 * _m.sin(_m.radians(t)) for t in theta]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                      line=dict(color="rgba(214, 158, 46, 0.5)", width=2),
                                      showlegend=False, hoverinfo="skip"))
            # Ideal spot marker
            fig.add_trace(go.Scatter(x=[seg_obj.ideal_pfmn], y=[seg_obj.ideal_size],
                                      mode="markers", marker=dict(size=12, color="#d69e2e", symbol="x"),
                                      name="Ideal", showlegend=False))
            # All products
            for c in state.companies:
                xs = [p.pfmn for p in c.products]
                ys = [p.size for p in c.products]
                labels = [p.name for p in c.products]
                fig.add_trace(go.Scatter(
                    x=xs, y=ys, mode="markers+text",
                    marker=dict(size=10, color=company_colors[c.name]),
                    text=labels, textposition="top center",
                    textfont=dict(color=company_colors[c.name], size=9),
                    name=c.name, showlegend=False,
                ))
            fig.update_layout(
                xaxis=dict(range=[max(0, seg_obj.ideal_pfmn-5), min(20, seg_obj.ideal_pfmn+5)], title="Performance"),
                yaxis=dict(range=[max(0, seg_obj.ideal_size-5), min(20, seg_obj.ideal_size+5)], title="Size", autorange="reversed"),
                height=250, plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=10, b=30, l=40, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Top Products table (15 columns matching real Capstone)
        st.markdown(f'<h3 style="color:#1a365d; margin-top:12px;">Top Products in {seg_name}</h3>', unsafe_allow_html=True)
        tp_df = pd.DataFrame(seg_data["top_products"])
        if not tp_df.empty:
            tp_display = pd.DataFrame({
                "Name": tp_df["Name"],
                "Co.": tp_df["Company"],
                "Market Share %": tp_df["Market_Share_Pct"].round(1),
                "Units Sold (000s)": tp_df["Units_Sold"].apply(lambda x: f"{x:,}"),
                "Stock Out": tp_df["Stock_Out"],
                "Rev Date": tp_df["Revision_Date"],
                "Age": tp_df["Age"].round(2),
                "Pfmn": tp_df["Pfmn"],
                "Size": tp_df["Size"],
                "Price": tp_df["Price"].apply(lambda x: f"${x:.2f}"),
                "MTBF": tp_df["MTBF"].apply(lambda x: f"{x:,}"),
                "Promo$": tp_df["Promo"].apply(fmt_money),
                "Aware%": (tp_df["Awareness"] * 100).round(0).astype(int).astype(str) + "%",
                "Sales$": tp_df["Sales"].apply(fmt_money),
                "Access%": (tp_df["Accessibility"] * 100).round(0).astype(int).astype(str) + "%",
                "Cust Survey": tp_df["Cust_Score"].round(1),
            })
            st.dataframe(tp_display, use_container_width=True, hide_index=True)

        st.markdown(f'<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Page {page_num}</div></div>', unsafe_allow_html=True)

    # ====== SECTION 9: MARKET SHARE ======
    st.markdown(f"""
    <div class="inq-paper" id="sec-9-market">
        <h2 style="display:flex; justify-content:space-between; align-items:center; color:#1a365d;">
            <span>Market Share Report</span>
            <span style="font-size:13px; color:#718096;">Round {state.round_num} Dec. 31, {state.year}</span>
        </h2><hr>
    """, unsafe_allow_html=True)

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown('<div style="font-weight:700; color:#1a365d; padding:4px 0;">UNITS SOLD VS. DEMAND</div>', unsafe_allow_html=True)
        usd_data = []
        for seg in state.segments:
            usd_data.append({
                "Segment": seg.name,
                "Demand": state.industry_unit_demand.get(seg.name, 0),
                "Sold": state.industry_unit_sold.get(seg.name, 0),
            })
        usd_df = pd.DataFrame(usd_data)
        fig = px.bar(usd_df, x="Segment", y=["Demand", "Sold"], barmode="group",
                     color_discrete_sequence=["#cbd5e0", "#1a365d"])
        fig.update_layout(height=280, margin=dict(t=20, b=20), plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    with col_c2:
        st.markdown('<div style="font-weight:700; color:#1a365d; padding:4px 0;">MARKET SHARE BY SEGMENT</div>', unsafe_allow_html=True)
        ms_data = inq["market_share"]
        ms_seg_data = []
        for cname in [c.name for c in state.companies]:
            for seg in ["Thrift", "Core", "Nano", "Elite"]:
                ms_seg_data.append({"Company": cname, "Segment": seg, "Units": ms_data[cname][seg]})
        ms_seg_df = pd.DataFrame(ms_seg_data)
        fig = px.bar(ms_seg_df, x="Segment", y="Units", color="Company", barmode="group",
                     color_discrete_map=company_colors)
        fig.update_layout(height=280, margin=dict(t=20, b=20), plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">ACTUAL MARKET SHARE IN UNITS</div>', unsafe_allow_html=True)
    ms_table_data = {"Segment": ["Thrift", "Core", "Nano", "Elite", "Total"]}
    for cname in [c.name for c in state.companies]:
        col = [ms_data[cname][s] for s in ["Thrift", "Core", "Nano", "Elite"]]
        col.append(sum(col))
        ms_table_data[cname] = [f"{x:,}" for x in col]
    st.dataframe(pd.DataFrame(ms_table_data), use_container_width=True, hide_index=True)

    st.markdown('<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Page 9</div></div>', unsafe_allow_html=True)

    # ====== SECTION 10: PERCEPTUAL MAP (industry-wide) ======
    st.markdown(f"""
    <div class="inq-paper" id="sec-10-pmap">
        <h2 style="display:flex; justify-content:space-between; align-items:center; color:#1a365d;">
            <span>Perceptual Map</span>
            <span style="font-size:13px; color:#718096;">Round {state.round_num} Dec. 31, {state.year}</span>
        </h2><hr>
    """, unsafe_allow_html=True)

    import math as _m
    fig = go.Figure()
    # All 4 segments' rough-cut + fine-cut circles
    for seg in state.segments:
        theta = list(range(0, 361, 5))
        xs = [seg.center_pfmn + 4.0 * _m.cos(_m.radians(t)) for t in theta]
        ys = [seg.center_size + 4.0 * _m.sin(_m.radians(t)) for t in theta]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                  line=dict(color="rgba(26, 54, 93, 0.15)", width=1, dash="dot"),
                                  showlegend=False, hoverinfo="skip"))
        xs2 = [seg.ideal_pfmn + 2.5 * _m.cos(_m.radians(t)) for t in theta]
        ys2 = [seg.ideal_size + 2.5 * _m.sin(_m.radians(t)) for t in theta]
        fig.add_trace(go.Scatter(x=xs2, y=ys2, mode="lines",
                                  line=dict(color="rgba(214, 158, 46, 0.3)", width=1),
                                  showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=[seg.ideal_pfmn], y=[seg.ideal_size],
                                  mode="markers+text", marker=dict(size=14, color="#d69e2e", symbol="x"),
                                  text=[f"<b>{seg.name}</b>"], textposition="bottom center",
                                  textfont=dict(color="#1a365d", size=11),
                                  showlegend=False, hoverinfo="skip"))
    for c in state.companies:
        xs = [p.pfmn for p in c.products]
        ys = [p.size for p in c.products]
        labels = [p.name for p in c.products]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers+text",
            marker=dict(size=14, color=company_colors[c.name],
                        line=dict(color="white", width=1)),
            text=labels, textposition="top center",
            textfont=dict(color=company_colors[c.name], size=11, family="Arial Black"),
            name=c.name,
        ))
    fig.update_layout(
        xaxis=dict(range=[0, 20], title="<b>Performance →</b>", gridcolor="#e2e8f0"),
        yaxis=dict(range=[0, 20], title="<b>Size</b>", gridcolor="#e2e8f0", autorange="reversed"),
        height=500, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=20, b=40, l=60, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 4 per-company tables (one row of 4)
    cols = st.columns(4)
    for idx, c in enumerate(state.companies):
        with cols[idx]:
            st.markdown(f"<div style='font-weight:700; color:{company_colors[c.name]}; text-align:center; padding:4px;'>{c.name}</div>", unsafe_allow_html=True)
            ct_df = pd.DataFrame([{"Name": p.name, "Pfmn": p.pfmn, "Size": p.size,
                                     "Revised": p.revision_date} for p in c.products])
            st.dataframe(ct_df, use_container_width=True, hide_index=True)

    st.markdown('<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Page 10</div></div>', unsafe_allow_html=True)

    # ====== SECTION 11: HR & TQM CUSTOM MODULES ======
    st.markdown(f"""
    <div class="inq-paper" id="sec-11-custom">
        <h2 style="display:flex; justify-content:space-between; align-items:center; color:#1a365d;">
            <span>HR &amp; TQM Custom Modules</span>
            <span style="font-size:13px; color:#718096;">Round {state.round_num} Dec. 31, {state.year}</span>
        </h2><hr>
    """, unsafe_allow_html=True)

    # Workforce Summary
    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">WORKFORCE SUMMARY</div>', unsafe_allow_html=True)
    wf_metrics = [
        ("Workforce Complement", lambda c: f"{c.hr.workforce_complement:,}"),
        ("1st Shift", lambda c: f"{c.hr.first_shift_complement:,}"),
        ("2nd Shift", lambda c: f"{c.hr.second_shift_complement:,}"),
        ("Overtime %", lambda c: f"{c.hr.overtime_pct*100:.1f}%"),
        ("Turnover Rate", lambda c: f"{c.hr.turnover_rate*100:.1f}%"),
        ("New Employees", lambda c: f"{c.hr.new_employees:,}"),
        ("Separated Employees", lambda c: f"{c.hr.separated_employees:,}"),
        ("Productivity Index", lambda c: f"{c.hr.productivity_index:.3f}"),
        ("Recruit Spend", lambda c: f"${c.hr.recruit_spend:.0f}"),
        ("Training Hours", lambda c: f"{c.hr.training_hours} hrs"),
        ("Total HR Admin Cost", lambda c: fmt_money(c.hr.total_hr_admin_cost)),
    ]
    wf_df = pd.DataFrame({"Category": [m[0] for m in wf_metrics], **{
        c.name: [fn(c) for _, fn in wf_metrics] for c in state.companies
    }})
    st.dataframe(wf_df, use_container_width=True, hide_index=True)

    # TQM Decisions + Impacts
    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">TOTAL QUALITY MANAGEMENT</div>', unsafe_allow_html=True)
    tqm_initiatives = INITIATIVE_NAMES
    tqm_rows = []
    for init in tqm_initiatives:
        tqm_rows.append({"Initiative ($ this round)": init, **{
            c.name: fmt_money(c.tqm.spend_this_round.get(init, 0)) for c in state.companies
        }})
    tqm_rows.append({"Initiative ($ this round)": "**TOTAL ROUND SPEND**", **{
        c.name: fmt_money(sum(c.tqm.spend_this_round.values())) for c in state.companies
    }})
    st.dataframe(pd.DataFrame(tqm_rows), use_container_width=True, hide_index=True)

    st.markdown('<div style="font-weight:700; letter-spacing:1.1px; color:#1a365d; padding:8px 0;">TQM YEARLY IMPACTS (CUMULATIVE)</div>', unsafe_allow_html=True)
    tqm_impact_rows = [
        ("Material Cost Reduction", lambda c: f"{c.tqm.material_cost_reduction*100:.1f}%"),
        ("Labor Cost Reduction", lambda c: f"{c.tqm.labor_cost_reduction*100:.1f}%"),
        ("R&D Cycle Time Reduction", lambda c: f"{c.tqm.rd_cycle_time_reduction*100:.1f}%"),
        ("Admin Cost Reduction", lambda c: f"{c.tqm.admin_cost_reduction*100:.1f}%"),
        ("Demand Increase", lambda c: f"+{c.tqm.demand_increase*100:.1f}%"),
        ("Total Cumulative Spend", lambda c: fmt_money(c.tqm.total_expenditures)),
    ]
    tqm_imp_df = pd.DataFrame({"Impact": [m[0] for m in tqm_impact_rows], **{
        c.name: [fn(c) for _, fn in tqm_impact_rows] for c in state.companies
    }})
    st.dataframe(tqm_imp_df, use_container_width=True, hide_index=True)

    st.markdown('<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Page 11</div></div>', unsafe_allow_html=True)


# ============================================================
# TAB: INDUSTRY CONDITIONS REPORT (separate document — where drift LIVES)
# ============================================================

with tab_icr:
    st.markdown(f"""
    <div class="inq-paper">
        <div class="inq-masthead">
            <h1 style="font-size:32px;">INDUSTRY CONDITIONS REPORT</h1>
            <div class="subtitle">Comp-XM 2026 • Released at start of game • drift rates &amp; offsets are FIXED</div>
        </div>
    """, unsafe_allow_html=True)

    st.info("📋 **This is the canonical source for drift information** — in real Capsim, this report is given to you ONCE at the start of the exam (separate from the Inquirer which updates each round). Drift rates and ideal offsets NEVER change between rounds.")

    # Table 1: Segment Circle Drift Rates
    st.markdown('<h2 style="color:#1a365d;">Table 1: Segment Circle Drift Rates</h2>', unsafe_allow_html=True)
    st.caption("Each year, customers demand increased performance and decreased size. The segment **centers** drift by these amounts every year.")
    drift_table = pd.DataFrame([{
        "Segment": s.name,
        "Performance Drift": f"{s.drift_pfmn:+.1f}",
        "Size Drift": f"{s.drift_size:+.1f}",
    } for s in state.segments])
    st.dataframe(drift_table, use_container_width=True, hide_index=True)

    # Table 2: Segment Centers at end of each round
    st.markdown('<h2 style="color:#1a365d; margin-top:24px;">Table 2: Segment Centers at the End of Each Round</h2>', unsafe_allow_html=True)
    st.caption("Computed from R0 center + (drift × rounds). The center is where the 'segment circle' is centered — NOT where customers ideally want products.")
    center_rows = []
    for s in state.segments:
        row = {"Segment": s.name}
        for r in range(0, 5):
            cp = s.center_pfmn + s.drift_pfmn * (r - state.round_num)
            cs = s.center_size + s.drift_size * (r - state.round_num)
            label = f"R{r}" + (" ← current" if r == state.round_num else "")
            row[label] = f"({cp:.1f}, {cs:.1f})"
        center_rows.append(row)
    st.dataframe(pd.DataFrame(center_rows), use_container_width=True, hide_index=True)

    # Table 3: Ideal Spot Offsets (CONSTANT)
    st.markdown('<h2 style="color:#1a365d; margin-top:24px;">Table 3: Ideal Spot Offsets (Constant Across All Rounds)</h2>', unsafe_allow_html=True)
    st.caption("Customers prefer products located this distance from the center of the segment circle. **These NEVER change.**")
    offset_rows = []
    for s in state.segments:
        offset_rows.append({
            "Segment": s.name,
            "Performance Offset": f"{s.ideal_offset_pfmn:+.1f}",
            "Size Offset": f"{s.ideal_offset_size:+.1f}",
            "Why this offset": {
                "Thrift": "Center IS the ideal — no bias",
                "Core": "Slight bias toward faster + smaller",
                "Nano": "Strong bias toward smaller (size matters most)",
                "Elite": "Strong bias toward faster (perf matters most)",
            }.get(s.name, "—"),
        })
    st.dataframe(pd.DataFrame(offset_rows), use_container_width=True, hide_index=True)

    # Formula explanation
    st.markdown("""
    <div style='background:#fef5e7; padding:14px; border-left:4px solid #d69e2e; margin:20px 0; font-family:Georgia,serif;'>
        <h3 style='color:#1a365d; margin-top:0;'>📐 Calculating Customer Ideal Spot at Any Round</h3>
        <code style='background:white; padding:6px 10px; display:block; font-size:13px;'>
        Ideal_Spot(Round_n) = Segment_Center(Round_n) + Ideal_Offset
        </code>
        <br>
        <b>Example: Nano segment in R3</b><br>
        • Center(R3) = Center(R0) + 3 × drift = (8.9, 9.4) + 3 × (+0.8, -1.1) = (11.3, 6.1)<br>
        • Offset = (+0.8, -1.1)<br>
        • Ideal Spot(R3) = (11.3, 6.1) + (+0.8, -1.1) = <b>(12.1, 5.0)</b><br>
        <br>
        ⮕ Your Nano product needs to be at <b>(12.1, 5.0)</b> at end of R3 to score max position points.
    </div>
    """, unsafe_allow_html=True)

    # Table 4: Beginning Segment Growth Rates
    st.markdown('<h2 style="color:#1a365d; margin-top:24px;">Table 4: Industry Conditions Beginning Segment Growth Rates</h2>', unsafe_allow_html=True)
    st.caption("Growth rates may change year to year — check Inquirer Segment Analysis each round for updates.")
    growth_df = pd.DataFrame([{
        "Segment": s.name, "Growth Rate (R1)": f"{s.growth_rate*100:.1f}%",
    } for s in state.segments])
    st.dataframe(growth_df, use_container_width=True, hide_index=True)

    # Section 3: Buying Criteria
    st.markdown('<h2 style="color:#1a365d; margin-top:24px;">Section 3: Buying Criteria by Segment (R0)</h2>', unsafe_allow_html=True)
    st.caption("These weights tell you what customers in each segment value most. They guide pricing, age, MTBF, and position decisions. Weights are stable but importance shifts slightly each round.")
    bc_rows = []
    for s in state.segments:
        bc_rows.append({
            "Segment": s.name,
            "Price Range": f"${s.price_min:.0f}-${s.price_max:.0f}",
            "Price Wt": f"{s.price_weight*100:.0f}%",
            "Ideal Age": f"{s.ideal_age:.1f} yr",
            "Age Wt": f"{s.age_weight*100:.0f}%",
            "MTBF Range": f"{s.mtbf_min:,}-{s.mtbf_max:,}",
            "MTBF Wt": f"{s.mtbf_weight*100:.0f}%",
            "Position Wt": f"{s.position_weight*100:.0f}%",
        })
    st.dataframe(pd.DataFrame(bc_rows), use_container_width=True, hide_index=True)

    # Prime rate
    st.markdown(f'<h2 style="color:#1a365d; margin-top:24px;">Section 4: Projected Interest Rate</h2>', unsafe_allow_html=True)
    st.markdown(f"**Prime Interest Rate Round 1:** {state.prime_interest_rate*100:.1f}%")
    st.caption("Affects short-term debt, long-term bond rates, and emergency loan penalty.")

    st.markdown('<hr style="margin:8px 0;"><div style="text-align:right; font-weight:700; color:#1a365d;">Industry Conditions Report — Comp-XM 2026</div></div>', unsafe_allow_html=True)


# ============================================================
# TAB: SCORECARD
# ============================================================

with tab_bsc:
    st.markdown('<div class="capsim-section-title">Balanced Scorecard</div>', unsafe_allow_html=True)
    bsc = compute_round_bsc(state, "Andrews",
                              prev_state=st.session_state.prev_state_snapshot)

    cols = st.columns(4)
    with cols[0]: kpi_card("Financial", f"{bsc.financial:.1f}", "of 30 pts")
    with cols[1]: kpi_card("Internal Bus.", f"{bsc.internal_business:.1f}", "of 20 pts")
    with cols[2]: kpi_card("Customer", f"{bsc.customer:.1f}", "of 35 pts")
    with cols[3]: kpi_card("Learning & Growth", f"{bsc.learning_growth:.1f}", "of 23 pts")
    st.markdown(f"""
    <div style='background:#1a365d; color:white; padding:16px; text-align:center; margin:12px 0;'>
        <div style='font-size:13px; letter-spacing:2px; text-transform:uppercase; color:#cbd5e0;'>Total Round Score</div>
        <div style='font-size:42px; font-weight:700; color:#d69e2e;'>{bsc.total:.1f}</div>
        <div style='font-size:12px; color:#cbd5e0;'>per-perspective sum (approx 108 max per round in this sim)</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="inq-section-head">Metric Breakdown</div>', unsafe_allow_html=True)
    metric_df = pd.DataFrame([
        {"Metric": k, "Score": f"{v:.1f}"} for k, v in bsc.metrics.items()
    ])
    st.dataframe(metric_df, use_container_width=True, hide_index=True)

    if state.round_num >= 4 and st.session_state.bsc_history:
        st.divider()
        st.markdown('<div class="inq-section-head">Final Cumulative Score (Round 5)</div>', unsafe_allow_html=True)
        cum = compute_cumulative_bsc(st.session_state.bsc_history, state, "Andrews")
        c = st.columns(4)
        with c[0]: kpi_card("Cum Financial", f"{cum.financial:.0f}", "of 200")
        with c[1]: kpi_card("Cum Internal", f"{cum.internal_business:.0f}", "of 100")
        with c[2]: kpi_card("Cum Customer", f"{cum.customer:.0f}", "of 100")
        with c[3]: kpi_card("Cum Learning", f"{cum.learning_growth:.0f}", "of 100")
        round_total = sum(b["total"] for b in st.session_state.bsc_history)
        grand = round_total + cum.total
        st.markdown(f"""
        <div style='background:#d69e2e; color:#1a365d; padding:24px; text-align:center; margin:12px 0;'>
            <div style='font-size:13px; letter-spacing:2px; text-transform:uppercase;'>GRAND TOTAL — Comp-XM Score</div>
            <div style='font-size:64px; font-weight:700;'>{grand:.0f} / 1000</div>
            <div style='font-size:13px;'>{round_total:.0f} round-by-round + {cum.total:.0f} cumulative</div>
            <div style='font-size:12px; margin-top:8px;'>Passing ≈ 662 (50th percentile). {'✅ PASS!' if grand >= 662 else '❌ Below passing threshold'}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# TAB: BOARD QUERIES
# ============================================================

with tab_bq:
    st.markdown('<div class="capsim-section-title">Board Queries</div>', unsafe_allow_html=True)
    round_to_query = st.selectbox("Round", [1, 2, 3, 4, 5],
                                    index=min(state.round_num, 4),
                                    format_func=lambda x: f"Round {x}" if x < 5 else "Round 5 — Final Cumulative")

    questions = get_round_queries(round_to_query)
    if not questions:
        st.warning(f"No queries defined for round {round_to_query}.")
    else:
        st.markdown(f"**{len(questions)} questions** for Round {round_to_query}")
        answers = {}
        for q in questions:
            st.markdown(f"""
            <div style="background:white; border-left:3px solid #1a365d; padding:12px 16px; margin:10px 0; border:1px solid #cbd5e0;">
                <span style="font-size:11px; color:#718096; text-transform:uppercase; letter-spacing:1px;">{q.topic}</span>
                <h4 style="margin:4px 0; color:#1a365d;">{q.id}: {q.question}</h4>
            </div>
            """, unsafe_allow_html=True)
            selected = st.radio(f"Answer ({q.id})", q.options, index=None, key=f"q_{q.id}", label_visibility="collapsed")
            if selected:
                answers[q.id] = q.options.index(selected)

        if st.button("📝 Grade Round", type="primary"):
            result = grade_round(round_to_query, answers)
            st.session_state.board_results[round_to_query] = result
            pct = result['correct']/max(1,result['total'])*100
            color = "#2f855a" if pct >= 70 else ("#d69e2e" if pct >= 50 else "#c53030")
            st.markdown(f"""
            <div style="background:{color}; color:white; padding:20px; text-align:center; margin:12px 0;">
                <div style="font-size:14px; text-transform:uppercase; letter-spacing:1px;">Round {round_to_query} Score</div>
                <div style="font-size:48px; font-weight:700;">{result['correct']}/{result['total']}</div>
                <div>{pct:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
            for d in result["details"]:
                q = next(qq for qq in questions if qq.id == d["id"])
                icon = "✅" if d["is_correct"] else "❌"
                bg = "#c6f6d5" if d["is_correct"] else "#fed7d7"
                st.markdown(f"""
                <div style="background:{bg}; padding:10px; margin:6px 0; border-left:3px solid #1a365d;">
                    {icon} <b>{q.id}</b> — Your: <b>{q.options[d['selected']] if d['selected'] is not None else 'no answer'}</b> | Correct: <b>{q.options[d['correct']]}</b>
                    <div style="font-size:12px; color:#4a5568; margin-top:6px;">💡 {q.explanation}</div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# TAB: HISTORY
# ============================================================

with tab_hist:
    st.markdown('<div class="capsim-section-title">Round-by-Round History & Trends</div>', unsafe_allow_html=True)
    if not state.history:
        st.info("No round history yet. Submit decisions in R&D/Marketing/etc tabs, then click ADVANCE in TQM tab.")
    else:
        df = pd.DataFrame(state.history)
        st.dataframe(df, use_container_width=True, hide_index=True)
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(df, x="round", y="andrews_stock", title="Andrews Stock Price",
                          markers=True, line_shape="spline")
            fig.add_hline(y=95.38, line_dash="dash", line_color="#d69e2e",
                          annotation_text="R0 $95.38", annotation_position="bottom right")
            fig.update_traces(line=dict(color="#1a365d", width=3), marker=dict(size=10))
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300)
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.line(df, x="round", y="andrews_profit", title="Andrews Net Profit",
                            markers=True, line_shape="spline")
            fig2.update_traces(line=dict(color="#2f855a", width=3), marker=dict(size=10))
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300)
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            fig3 = px.line(df, x="round", y="andrews_cash", title="Andrews Cash Position",
                            markers=True, line_shape="spline")
            fig3.update_traces(line=dict(color="#c05621", width=3), marker=dict(size=10))
            fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300)
            st.plotly_chart(fig3, use_container_width=True)

            fig4 = px.line(df, x="round", y="andrews_bsc", title="BSC Score per Round",
                            markers=True, line_shape="spline")
            fig4.update_traces(line=dict(color="#d69e2e", width=3), marker=dict(size=10))
            fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300)
            st.plotly_chart(fig4, use_container_width=True)


# ============================================================
# FOOTER + UTILITY BAR
# ============================================================

st.markdown("---")
fcol1, fcol2, fcol3, fcol4 = st.columns([2, 1, 1, 1])
with fcol1:
    st.markdown(f"""<div class="compxm-footer">
        COMP-XM® 2026 SIMULATOR • ANDREWS CORPORATION • EXAM PREP • R{state.round_num}/4
    </div>""", unsafe_allow_html=True)
with fcol2:
    if st.button("💾 SAVE STATE"):
        save_state()
        st.toast("Saved!")
with fcol3:
    if st.button("🔄 RESET"):
        reset_state()
        st.rerun()
with fcol4:
    st.markdown(f"<div style='text-align:right; padding-top:8px; font-size:11px; color:#718096;'>Cash: <b>{fmt_money(andrews.cash)}</b> • Stock: <b>${andrews.stock_price:.2f}</b></div>", unsafe_allow_html=True)
