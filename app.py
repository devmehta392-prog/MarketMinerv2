import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG & UI CSS OVERRIDES
# ==========================================
st.set_page_config(page_title="MarketMiner", layout="wide", initial_sidebar_state="expanded")

if "target" not in st.session_state:
    st.session_state.target = "GC=F"

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg: #0a0b0e;
        --card: #141519;          /* matches chart backgrounds exactly */
        --card2: #1a1c22;
        --card3: #22242b;
        --border: #25272f;
        --hair: rgba(255,255,255,0.055);
        --gold: #d4af6a;
        --gold-bright: #eccb7e;
        --gold-deep: #b89352;
        --gold-dim: rgba(212,175,106,0.10);
        --text: #edeef1;
        --text2: #b8bcc6;
        --dim: #767b86;
        --muted: #3c414c;
        --green: #22c55e;
        --green-dim: rgba(34,197,94,0.13);
        --red: #ef4444;
        --red-dim: rgba(239,68,68,0.13);
        --blue: #3b82f6;
        --shadow: 0 6px 28px rgba(0,0,0,0.45);
        --shadow-soft: 0 2px 14px rgba(0,0,0,0.28);
    }

    /* ── BASE ── */
    header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
    .block-container { padding: 1.9rem 2rem 1rem 2rem !important; max-width: 100% !important; }
    [data-testid="stSidebarContent"] { padding: 0 !important; background: var(--card) !important; border-right: 1px solid var(--hair); }
    [data-testid="stSidebar"] { background: var(--card) !important; }
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(1200px 700px at 88% -12%, rgba(59,130,246,0.04), transparent 55%),
            radial-gradient(1000px 600px at -5% 3%, rgba(212,175,106,0.035), transparent 52%),
            var(--bg);
        color: var(--text);
        font-family: 'Manrope', sans-serif;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.011em;
    }
    .mono { font-family: 'JetBrains Mono', monospace; font-feature-settings: "tnum"; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #2a2d36; border-radius: 6px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--gold-deep); }

    /* ── TICKER BAR ── */
    .ticker-bar { background: #0c0d11; border-bottom: 1px solid var(--hair); padding: 9px 0; overflow: hidden; white-space: nowrap; margin: -1.9rem -2rem 20px -2rem; position: relative; }
    .ticker-bar::after { content: ""; position: absolute; top: 0; right: 0; width: 90px; height: 100%; background: linear-gradient(90deg, transparent, #0c0d11); pointer-events: none; }
    .ticker-track { display: inline-flex; animation: scroll 48s linear infinite; }
    .ticker-track:hover { animation-play-state: paused; }
    .t-item { display: inline-flex; align-items: center; gap: 7px; padding: 0 24px; font-size: 12px; border-right: 1px solid var(--hair); }
    .t-item .t-name { color: var(--dim); font-weight: 600; }
    .t-item .t-price { font-weight: 600; color: #fff; font-family: 'JetBrains Mono', monospace; }
    .t-item .t-chg { font-family: 'JetBrains Mono', monospace; font-weight: 600; }
    .t-item .up { color: var(--green); }
    .t-item .dn { color: var(--red); }
    @keyframes scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

    /* ── SIDEBAR BRANDING ── */
    .sb-top { padding: 22px 20px 20px 20px; border-bottom: 1px solid var(--hair); }
    .logo { display: flex; align-items: center; gap: 13px; }
    .logo-mark { width: 42px; height: 42px; background: linear-gradient(135deg, var(--gold-bright), var(--gold-deep)); border-radius: 12px; display: grid; place-items: center; font-size: 21px; color: #1a1300; font-weight: 800; box-shadow: inset 0 1px 0 rgba(255,255,255,0.35), 0 4px 14px rgba(212,175,106,0.18); }
    .logo-name { font-size: 19px; font-weight: 800; color: var(--text); letter-spacing: -0.6px; line-height: 1.05; }
    .logo-name span { color: var(--gold); }
    .logo-sub { font-size: 9px; color: var(--dim); margin-top: 3px; letter-spacing: 1.6px; text-transform: uppercase; font-weight: 600; }
    .sb-label { padding: 18px 20px 8px; font-size: 9px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 1.8px; }

    /* ── SIDEBAR ASSET ROWS ── */
    .sb-asset-row {
        display: flex; align-items: center; padding: 11px 14px; cursor: pointer;
        border: 1px solid transparent; transition: all 0.18s cubic-bezier(0.4,0,0.2,1); gap: 11px;
        margin: 2px 10px; border-radius: 11px; position: relative;
    }
    .sb-asset-row:hover { background: var(--card2); border-color: var(--hair); }
    .sb-asset-row.active {
        background: linear-gradient(100deg, rgba(212,175,106,0.11), rgba(212,175,106,0.015));
        border-color: rgba(212,175,106,0.28);
    }
    .sb-asset-row.active::before { content: ""; position: absolute; left: -1px; top: 24%; bottom: 24%; width: 3px; border-radius: 3px; background: linear-gradient(180deg, var(--gold-bright), var(--gold-deep)); }
    .sb-asset-icon { font-size: 20px; width: 28px; text-align: center; flex-shrink: 0; }
    .sb-asset-info { flex: 1; min-width: 0; }
    .sb-asset-name { font-size: 13px; font-weight: 700; color: var(--text); letter-spacing: -0.2px; }
    .sb-asset-ticker { font-size: 9.5px; color: var(--dim); letter-spacing: 0.4px; font-family: 'JetBrains Mono', monospace; }
    .sb-asset-right { text-align: right; flex-shrink: 0; }
    .sb-asset-price { font-size: 12.5px; font-weight: 600; color: var(--text); font-family: 'JetBrains Mono', monospace; }
    .sb-asset-chg { font-size: 10.5px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
    .sb-asset-chg.up { color: var(--green); }
    .sb-asset-chg.dn { color: var(--red); }
    .sb-spark { width: 58px; height: 30px; flex-shrink: 0; opacity: 0.9; }

    /* ── SIDEBAR BUTTONS (overlay click targets) ── */
    div[data-testid="stButton"] > button {
        width: calc(100% - 20px) !important;
        background: transparent !important;
        border: 1px solid var(--hair) !important;
        color: var(--dim) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 9.5px !important; font-weight: 600 !important; letter-spacing: 1px !important;
        text-transform: uppercase !important;
        padding: 6px 8px !important; border-radius: 8px !important;
        margin: 0 10px 7px 10px !important;
        transition: all 0.18s cubic-bezier(0.4,0,0.2,1);
    }
    div[data-testid="stButton"] > button:hover {
        border-color: var(--gold) !important; color: var(--gold-bright) !important; background: var(--gold-dim) !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(212,175,106,0.18), rgba(212,175,106,0.04)) !important;
        border-color: rgba(212,175,106,0.42) !important; color: var(--gold-bright) !important;
    }

    /* ── MAIN HEADER BAR ── */
    .ch-head {
        padding: 17px 24px; border: 1px solid var(--border); border-radius: 14px 14px 0 0;
        display: flex; align-items: center; gap: 15px; background: var(--card); margin-bottom: 0; flex-wrap: wrap;
        position: relative;
    }
    .ch-head::before { content: ""; position: absolute; top: 0; left: 18px; right: 18px; height: 1px; background: linear-gradient(90deg, transparent, rgba(212,175,106,0.35), transparent); }
    .ch-icon { font-size: 29px; }
    .ch-name { font-size: 22px; font-weight: 800; color: var(--text); letter-spacing: -0.7px; }
    .ch-ticker { font-size: 10.5px; color: var(--gold); background: var(--gold-dim); padding: 4px 10px; border-radius: 7px; border: 1px solid rgba(212,175,106,0.22); font-weight: 600; letter-spacing: 0.4px; font-family: 'JetBrains Mono', monospace; }
    .ch-price { font-size: 31px; font-weight: 700; font-family: 'JetBrains Mono', monospace; letter-spacing: -1.4px; }
    .ch-chg { font-size: 13px; font-weight: 600; padding: 6px 12px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; }
    .ch-chg.up { color: var(--green); background: var(--green-dim); }
    .ch-chg.dn { color: var(--red); background: var(--red-dim); }
    .demo-badge { background: var(--green-dim); color: var(--green); padding: 5px 11px; border-radius: 7px; font-size: 9.5px; font-weight: 700; border: 1px solid rgba(34,197,94,0.22); letter-spacing: 1px; display: inline-flex; align-items: center; gap: 6px; }
    .pulse-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.55); } 70% { box-shadow: 0 0 0 7px rgba(34,197,94,0); } 100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); } }

    /* ── OHLC BAR ── */
    .ohlc-bar {
        background: var(--card); border: 1px solid var(--border); border-top: none;
        display: flex; align-items: center; padding: 11px 24px; gap: 0; flex-wrap: wrap;
    }
    .ohlc-item { display: flex; align-items: center; gap: 7px; padding: 0 20px 0 0; border-right: 1px solid var(--hair); margin-right: 20px; }
    .ohlc-item:last-child { border-right: none; margin-right: 0; }
    .ohlc-lbl { font-size: 9px; color: var(--dim); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .ohlc-val { font-size: 12px; font-weight: 600; color: var(--text); font-family: 'JetBrains Mono', monospace; }
    .ohlc-val.hi { color: var(--green); }
    .ohlc-val.lo { color: var(--red); }

    /* ── SUMMARY STRIP ── */
    .summary {
        background: var(--card); border: 1px solid var(--border); border-top: none; border-radius: 0 0 14px 14px;
        padding: 13px 24px; font-size: 12.5px; line-height: 1.8; color: var(--text2); margin-bottom: 0;
        border-left: 2px solid var(--gold);
    }
    .summary strong { color: var(--text); font-weight: 700; }

    /* ── STATS GRID ── */
    .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 13px; margin: 20px 0 24px 0; }
    .stat {
        background: var(--card); padding: 17px 19px; border-radius: 14px; border: 1px solid var(--border);
        display: flex; flex-direction: column; gap: 2px; transition: all 0.2s cubic-bezier(0.4,0,0.2,1); cursor: default;
        position: relative;
    }
    .stat:hover { border-color: rgba(212,175,106,0.28); transform: translateY(-3px); box-shadow: var(--shadow); }
    .stat-lbl { font-size: 9px; color: var(--dim); text-transform: uppercase; letter-spacing: 1.3px; font-weight: 700; margin-bottom: 9px; }
    .stat-val { font-size: 21px; font-weight: 700; font-family: 'JetBrains Mono', monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: -0.7px; }
    .stat-sub { font-size: 10px; color: var(--dim); margin-top: 7px; display: flex; align-items: center; gap: 5px; font-family: 'JetBrains Mono', monospace; }
    .badge { display: inline-block; font-size: 8.5px; padding: 3px 8px; border-radius: 5px; font-weight: 700; letter-spacing: 0.5px; font-family: 'JetBrains Mono', monospace; }
    .badge.r { background: var(--red-dim); color: var(--red); }
    .badge.g { background: var(--green-dim); color: var(--green); }
    .badge.y { background: var(--gold-dim); color: var(--gold); }

    /* ── CHART AREA ── */
    .chart-wrap { background: var(--card); border: 1px solid var(--border); border-top: none; padding: 0; }
    .chart-box {
        background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 10px;
        transition: border-color 0.2s;
    }
    .chart-box:hover { border-color: rgba(212,175,106,0.2); }

    /* ── SECTION DIVIDER ── */
    .section-head { font-size: 10.5px; font-weight: 700; color: var(--dim); text-transform: uppercase; letter-spacing: 1.8px; margin: 12px 0 16px 0; display: flex; align-items: center; gap: 11px; }
    .section-head::before { content: ""; width: 5px; height: 5px; background: var(--gold); border-radius: 50%; box-shadow: 0 0 7px var(--gold); }
    .section-head::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--hair), transparent); }

    /* ── CHAT UI ── */
    [data-testid="stChatMessage"] { background: var(--card) !important; border: 1px solid var(--border); border-radius: 13px; margin-bottom: 11px; padding: 16px !important; }
    [data-testid="chatAvatarIcon-user"] { background: var(--card3) !important; color: var(--text) !important; }
    [data-testid="chatAvatarIcon-assistant"] { background: linear-gradient(135deg, var(--gold-bright), var(--gold-deep)) !important; color: #000 !important; }
    [data-testid="stChatInput"] { background: var(--card) !important; border-color: var(--border) !important; border-radius: 13px !important; }
    [data-testid="stChatInput"]:focus-within { border-color: var(--gold) !important; box-shadow: 0 0 0 1px var(--gold) !important; }
    [data-testid="stChatInput"] textarea { font-family: 'Manrope', sans-serif !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ASSET MAPPING & TECHNICAL CALCS
# ==========================================
ASSET_MAP = {
    "GC=F": {"name": "Gold", "icon": "🥇", "cat": "Precious"},
    "SI=F": {"name": "Silver", "icon": "🥈", "cat": "Precious"},
    "PL=F": {"name": "Platinum", "icon": "💿", "cat": "Precious"},
    "CL=F": {"name": "WTI Crude", "icon": "🛢️", "cat": "Energy"},
    "BZ=F": {"name": "Brent Crude", "icon": "⛽", "cat": "Energy"},
    "NG=F": {"name": "Natural Gas", "icon": "🔥", "cat": "Energy"},
    "HG=F": {"name": "Copper", "icon": "🔶", "cat": "Metals"},
    "ZW=F": {"name": "Wheat", "icon": "🌾", "cat": "Agri"},
    "ZC=F": {"name": "Corn", "icon": "🌽", "cat": "Agri"},
    "BTC-USD": {"name": "Bitcoin", "icon": "₿", "cat": "Digital"}
}

@st.cache_data(ttl=9, show_spinner=False)
def fetch_live_data():
    tickers = list(ASSET_MAP.keys())
    try:
        return yf.download(tickers, period="5d", interval="15m", group_by='ticker', progress=False)
    except Exception:
        return pd.DataFrame()

def calculate_technicals(df):
    if df.empty or len(df) < 20:
        return {"rsi": 50, "ma20": 0, "bb_width": 0, "macd": 0}
    close = df['Close'].squeeze()
    ma20 = close.rolling(window=20).mean().iloc[-1]
    std = close.rolling(window=20).std().iloc[-1]
    bb_width = (4 * std) if not pd.isna(std) else 0
    
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = (ema12 - ema26).iloc[-1]
    
    return {"rsi": rsi, "ma20": ma20, "bb_width": bb_width, "macd": macd}

def get_stats(df_all, ticker):
    try:
        if df_all.empty or ticker not in df_all.columns.levels[0]: 
            return 0, 0, 0, 0, 0, 0, pd.DataFrame(), {}
        df = df_all[ticker].dropna()
        if len(df) < 2: return 0, 0, 0, 0, 0, 0, df, {}
        
        curr = float(df['Close'].iloc[-1])
        day_open = float(df['Open'].iloc[0]) 
        day_high = float(df['High'].max())
        day_low = float(df['Low'].min())
        vol = float(df['Volume'].iloc[-1])
        pct = ((curr - day_open) / day_open) * 100
        tech = calculate_technicals(df)
        return curr, pct, day_open, day_high, day_low, vol, df, tech
    except:
        return 0, 0, 0, 0, 0, 0, pd.DataFrame(), {}

# ==========================================
# 3. INTERACTIVE RED/GREEN SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class="sb-top">
            <div class="logo">
                <div class="logo-mark">⛏</div>
                <div>
                    <div class="logo-name">Market<span>Miner</span></div>
                    <div class="logo-sub">Commodity Intelligence Platform</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sb-label'>AI Access Key</div>", unsafe_allow_html=True)
    st.session_state.api_key = st.text_input("API Key", type="password", placeholder="Enter Gemini API Key...", label_visibility="collapsed")

def render_live_sidebar():
    df_all = fetch_live_data()
    categories = ["Precious", "Energy", "Metals", "Agri", "Digital"]

    for cat in categories:
        st.markdown(f"<div class='sb-label'>{cat}</div>", unsafe_allow_html=True)
        for sym, details in ASSET_MAP.items():
            if details["cat"] == cat:
                curr, pct, _, _, _, _, df_sym, _ = get_stats(df_all, sym)
                px_format = f"{curr:,.0f}" if sym == "BTC-USD" else f"{curr:,.2f}"
                sign = "+" if pct >= 0 else ""
                chg_cls = "up" if pct >= 0 else "dn"
                is_active = st.session_state.target == sym
                active_cls = "active" if is_active else ""

                # Build inline SVG sparkline from recent close prices
                spark_svg = ""
                if not df_sym.empty and len(df_sym) >= 5:
                    closes = df_sym['Close'].dropna().tail(20).values
                    if len(closes) >= 2:
                        mn, mx = closes.min(), closes.max()
                        rng = mx - mn if mx != mn else 1
                        pts = []
                        for i, v in enumerate(closes):
                            x = i / (len(closes) - 1) * 58
                            y = 28 - ((v - mn) / rng) * 26
                            pts.append(f"{x:.1f},{y:.1f}")
                        color = "#22c55e" if pct >= 0 else "#ef4444"
                        spark_svg = f'<svg viewBox="0 0 60 30" xmlns="http://www.w3.org/2000/svg" width="60" height="30"><polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/></svg>'

                # Render the visual row
                st.markdown(f"""
                <div class="sb-asset-row {active_cls}" id="row_{sym}">
                    <div class="sb-asset-icon">{details['icon']}</div>
                    <div class="sb-asset-info">
                        <div class="sb-asset-name">{details['name']}</div>
                        <div class="sb-asset-ticker">{sym}</div>
                    </div>
                    <div class="sb-spark">{spark_svg}</div>
                    <div class="sb-asset-right">
                        <div class="sb-asset-price">${px_format}</div>
                        <div class="sb-asset-chg {chg_cls}">{sign}{pct:.2f}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Real, visible navigation button directly under the row
                btn_type = "primary" if is_active else "secondary"
                if st.button(f"View {details['name']}", key=f"nav_{sym}", type=btn_type, use_container_width=True):
                    st.session_state.target = sym
                    st.rerun()

    # Intelligence Score
    _, _, _, _, _, _, _, t_tech = get_stats(df_all, st.session_state.target)
    rsi_val = t_tech.get('rsi', 50)
    bb_val = t_tech.get('bb_width', 0)
    mo_val = min(100, max(0, (rsi_val / 100) * 80 + 20))
    iq = 72 if rsi_val > 55 else (35 if rsi_val < 45 else 56)
    iq_grade = "A" if iq >= 70 else ("C" if iq >= 50 else "D")
    iq_label = "Strong Buy" if iq >= 70 else ("Hold" if iq >= 50 else "Caution")
    iq_color = "#22c55e" if iq >= 70 else ("#FFD700" if iq >= 50 else "#ef4444")
    trend_align = min(100, int(rsi_val * 1.1))
    vol_surge = min(100, int(bb_val / 5)) if bb_val > 0 else 60

    def bar(pct_val, color):
        return f'<div style="height:4px;background:var(--border);border-radius:2px;margin-top:3px;"><div style="height:100%;width:{min(100,int(pct_val))}%;background:{color};border-radius:2px;"></div></div>'

    st.markdown(f"""
    <div style="border-top:1px solid var(--border);margin-top:8px;padding:16px;background:var(--card);">
        <div style="font-size:9.5px;color:var(--dim);text-transform:uppercase;letter-spacing:1.2px;font-weight:700;margin-bottom:12px;">Intelligence Score</div>
        <div style="display:flex;align-items:flex-end;gap:8px;margin-bottom:14px;">
            <span style="font-size:42px;font-weight:800;color:{iq_color};line-height:1;">{iq}</span>
            <div style="padding-bottom:6px;">
                <div style="font-size:11px;color:#fff;font-weight:700;">{iq_grade} — {iq_label}</div>
                <div style="font-size:9px;color:var(--dim);">Composite Signal</div>
            </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
            <div>
                <div style="display:flex;justify-content:space-between;font-size:10.5px;"><span style="color:var(--dim);">RSI Signal</span><span style="color:#fff;font-weight:600;">{int(rsi_val)}</span></div>
                {bar(rsi_val, "#3b82f6")}
            </div>
            <div>
                <div style="display:flex;justify-content:space-between;font-size:10.5px;"><span style="color:var(--dim);">Trend Align</span><span style="color:#fff;font-weight:600;">{trend_align}</span></div>
                {bar(trend_align, "#FFD700")}
            </div>
            <div>
                <div style="display:flex;justify-content:space-between;font-size:10.5px;"><span style="color:var(--dim);">Momentum</span><span style="color:#fff;font-weight:600;">{int(mo_val)}</span></div>
                {bar(mo_val, "#22c55e")}
            </div>
            <div>
                <div style="display:flex;justify-content:space-between;font-size:10.5px;"><span style="color:var(--dim);">Vol Surge</span><span style="color:#fff;font-weight:600;">{vol_surge}</span></div>
                {bar(vol_surge, "#a855f7")}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MAIN DASHBOARD (Chart + Aligned Stats)
# ==========================================
def render_live_main():
    df_all = fetch_live_data()
    if df_all.empty:
        st.warning("Awaiting market data stream...")
        return
        
    sym = st.session_state.target
    name = ASSET_MAP[sym]["name"]
    icon = ASSET_MAP[sym]["icon"]
    curr, pct, o, h, l, vol, df, tech = get_stats(df_all, sym)
    
    up_cls = "up" if pct >= 0 else "dn"
    color_hex = "var(--green)" if pct >= 0 else "var(--red)"
    arrow = "+" if pct >= 0 else ""

    # 1. Ticker
    ticker_items = ""
    for tk, det in ASSET_MAP.items():
        c, p, _, _, _, _, _, _ = get_stats(df_all, tk)
        u_cls = "up" if p >= 0 else "dn"
        c_hex = "var(--green)" if p >= 0 else "var(--red)"
        arr = "▲" if p >= 0 else "▼"
        px_fmt = f"{c:,.0f}" if tk == "BTC-USD" else f"{c:,.2f}"
        ticker_items += f'<div class="t-item"><span>{det["icon"]}</span><span class="t-name">{det["name"]}</span><span class="t-price" style="color:{c_hex};">${px_fmt}</span><span class="t-chg {u_cls}">{arr}{abs(p):.2f}%</span></div>'
    
    st.markdown(f'<div class="ticker-bar"><div class="ticker-track">{ticker_items}{ticker_items}</div></div>', unsafe_allow_html=True)

    # 2. Main Header + OHLC Bar
    try:
        ticker_info = yf.Ticker(sym).fast_info
        w52_high = getattr(ticker_info, 'year_high', h)
        w52_low  = getattr(ticker_info, 'year_low', l)
        avg_vol  = getattr(ticker_info, 'three_month_average_volume', vol)
    except Exception:
        w52_high, w52_low, avg_vol = h, l, vol

    vol_fmt = f"{vol/1000:.1f}K" if vol < 1_000_000 else f"{vol/1_000_000:.2f}M"
    avg_vol_fmt = f"{avg_vol/1000:.1f}K" if avg_vol < 1_000_000 else f"{avg_vol/1_000_000:.2f}M"

    st.markdown(f"""
    <div class="ch-head">
        <span class="ch-icon">{icon}</span>
        <span class="ch-name">{name}</span>
        <span class="ch-ticker">{sym}</span>
        <span class="demo-badge"><span class="pulse-dot"></span>LIVE</span>
        <div style="margin-left:auto;display:flex;align-items:center;gap:12px;">
            <div class="ch-price" style="color:{color_hex};">${curr:,.2f}</div>
            <div class="ch-chg {up_cls}">{arrow}{curr-o:,.2f} ({arrow}{pct:.2f}%)</div>
        </div>
    </div>
    <div class="ohlc-bar">
        <div class="ohlc-item"><span class="ohlc-lbl">O</span><span class="ohlc-val">${o:,.2f}</span></div>
        <div class="ohlc-item"><span class="ohlc-lbl">H</span><span class="ohlc-val hi">${h:,.2f}</span></div>
        <div class="ohlc-item"><span class="ohlc-lbl">L</span><span class="ohlc-val lo">${l:,.2f}</span></div>
        <div class="ohlc-item"><span class="ohlc-lbl">52W H</span><span class="ohlc-val hi">${w52_high:,.2f}</span></div>
        <div class="ohlc-item"><span class="ohlc-lbl">52W L</span><span class="ohlc-val lo">${w52_low:,.2f}</span></div>
        <div class="ohlc-item"><span class="ohlc-lbl">Volume</span><span class="ohlc-val">{vol_fmt}</span></div>
        <div class="ohlc-item"><span class="ohlc-lbl">Avg Vol(3M)</span><span class="ohlc-val">{avg_vol_fmt}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Dynamic Candlestick Chart (with Rangebreaks to hide weekends)
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        )])
        ma20_line = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma20_line, line=dict(color='#FFD700', width=1.5, dash='dot'), name='MA20'))

        fig.update_layout(
            template="plotly_dark", height=420, margin=dict(t=10, b=10, l=10, r=50),
            paper_bgcolor='#141519', plot_bgcolor='#141519',
            xaxis=dict(
                showgrid=False,
                rangeslider_visible=False,
                rangebreaks=[dict(bounds=["sat", "mon"])],
                color='#6b7280'
            ),
            yaxis=dict(showgrid=True, gridcolor='#1c1d23', side="right", color='#6b7280'),
            showlegend=True,
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0)', font=dict(color='#6b7280', size=10))
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 4. Summary & Perfectly Aligned Stats Grid
    trend = "bullish uptrend" if pct >= 0 else "bearish downtrend"
    rsi_val = tech.get('rsi', 50)
    rsi_stat = "overbought" if rsi_val > 70 else ("oversold" if rsi_val < 30 else "neutral")
    rsi_col = "var(--red)" if rsi_val > 70 else ("var(--green)" if rsi_val < 30 else "var(--dim)")
    ma_val = tech.get('ma20', 0)
    macd_val = tech.get('macd', 0)

    st.markdown(f"""
    <div class="summary">
        <strong style="color:var(--gold);">◆ AI ORACLE</strong> &nbsp;<strong>{name}</strong> is in a <strong>{trend}</strong>. RSI(14) at <strong class="mono" style="color:{rsi_col};">{rsi_val:.1f}</strong> is <strong style="color:{rsi_col};">{rsi_stat}</strong>. Price is <strong>{'above' if curr > ma_val else 'below'}</strong> the 20-period moving average. IQ Score <strong class="mono">{72 if rsi_val > 55 else (35 if rsi_val < 45 else 56)}/100</strong> — <strong>{'moderately bullish' if pct >= 0 else 'moderately bearish'} bias</strong>. Current: <strong class="mono">${curr:,.2f}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stats">
        <div class="stat">
            <div class="stat-lbl">Current Price</div>
            <div class="stat-val" style="color:{color_hex};">${curr:,.2f}</div>
            <div class="stat-sub">USD / troy oz</div>
        </div>
        <div class="stat">
            <div class="stat-lbl">Day Range</div>
            <div class="stat-val" style="font-size:15px;">{l:,.2f} – {h:,.2f}</div>
            <div class="stat-sub">Low / High</div>
        </div>
        <div class="stat">
            <div class="stat-lbl">52W Range</div>
            <div class="stat-val" style="font-size:15px;">{w52_low:,.0f} – {w52_high:,.0f}</div>
            <div class="stat-sub">Low / High</div>
        </div>
        <div class="stat">
            <div class="stat-lbl">Volume (Last)</div>
            <div class="stat-val">{vol_fmt}</div>
            <div class="stat-sub">Avg10: {avg_vol_fmt}</div>
        </div>
        <div class="stat">
            <div class="stat-lbl">RSI (14)</div>
            <div class="stat-val" style="color:{rsi_col};">{rsi_val:.1f}</div>
            <div class="stat-sub"><span class="badge {'r' if rsi_val > 70 else ('g' if rsi_val < 30 else 'y')}">{rsi_stat.upper()}</span></div>
        </div>
        <div class="stat">
            <div class="stat-lbl">MA (20)</div>
            <div class="stat-val">{ma_val:,.2f}</div>
            <div class="stat-sub">Price {'&gt;' if curr > ma_val else '&lt;'} MA20</div>
        </div>
        <div class="stat">
            <div class="stat-lbl">BB Width</div>
            <div class="stat-val">{tech.get('bb_width',0):.2f}</div>
            <div class="stat-sub">Bollinger Width</div>
        </div>
        <div class="stat">
            <div class="stat-lbl">MACD Signal</div>
            <div class="stat-val" style="color:{'var(--green)' if macd_val > 0 else 'var(--red)'};">{macd_val:.2f}</div>
            <div class="stat-sub"><span class="badge {'g' if macd_val > 0 else 'r'}">{'↑ Bullish' if macd_val > 0 else '↓ Bearish'}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Bottom 3 Analytical Charts
    st.markdown("<div class='section-head' style='margin-top:24px;'>Market Analytics &amp; Models</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    chart_layout = dict(template="plotly_dark", height=250, margin=dict(t=35, b=15, l=10, r=10), paper_bgcolor='#141519', plot_bgcolor='#141519', title_font=dict(size=12, color="#6b7280"), font=dict(color='#6b7280'))

    with c1:
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        assets = ['Metals', 'Energy', 'Agri', 'Equities', 'Crypto']
        perfs = [0.8, -0.4, 1.2, 0.5, 2.1] 
        colors = ['#22c55e' if p > 0 else '#ef4444' for p in perfs]
        fig_bar = go.Figure(data=[go.Bar(x=assets, y=perfs, marker_color=colors)])
        fig_bar.update_layout(**chart_layout, title="📊 Sector Performance Model")
        fig_bar.update_yaxes(showgrid=True, gridcolor='#1c1d23')
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        labels = ['Equities', 'Bonds', 'Gold', 'Cash']
        values = [60, 20, 10, 10]
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker=dict(colors=['#3b82f6', '#8b5cf6', '#FFD700', '#22c55e']))])
        fig_pie.update_layout(**chart_layout, title="🥧 Institutional Allocation", showlegend=False)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        np.random.seed(42)
        x_val = np.random.normal(0.05, 0.02, 50)
        y_val = x_val * 0.7 + np.random.normal(0, 0.015, 50)
        fig_scatter = go.Figure(data=go.Scatter(x=x_val, y=y_val, mode='markers', marker=dict(color='#3b82f6', size=7, opacity=0.8)))
        fig_scatter.update_layout(**chart_layout, title=f"📈 Alpha Correlation vs SPY", xaxis_title="S&P 500", yaxis_title=f"{sym}")
        fig_scatter.update_xaxes(showgrid=True, gridcolor='#1c1d23')
        fig_scatter.update_yaxes(showgrid=True, gridcolor='#1c1d23')
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 6. EXECUTION & AI TUTOR CHAT
# ==========================================
with st.sidebar:
    render_live_sidebar()

render_live_main()

# Market Miner AI Chatbot
st.markdown("<hr style='border:none;border-top:1px solid var(--border); margin: 2.2rem 0 1.2rem 0;'>", unsafe_allow_html=True)
st.markdown(f"<div style='display:flex;align-items:center;gap:13px;margin-bottom:6px;'><div style='width:38px;height:38px;background:linear-gradient(135deg,#FFD700,#f5c542);border-radius:11px;display:grid;place-items:center;font-size:18px;flex-shrink:0;box-shadow:0 2px 10px rgba(245,197,66,0.25);'>🤖</div><div><div style='font-size:15px;font-weight:800;color:var(--text);letter-spacing:-0.3px;'>MarketMiner <span style=\"color:var(--gold);\">AI</span></div><div style='font-size:10.5px;color:var(--dim);margin-top:2px;'>Commodity Intelligence Assistant · Powered by Gemini</div></div></div>", unsafe_allow_html=True)

# Chat Styling
st.markdown("""
<style>
[data-testid="stChatMessage"] { background-color: var(--card) !important; border: 1px solid var(--border); border-radius: 12px; margin-bottom: 10px; padding: 16px !important; box-shadow: var(--shadow-soft); }
[data-testid="chatAvatarIcon-user"] { background-color: var(--card3) !important; color: var(--text) !important; }
[data-testid="chatAvatarIcon-assistant"] { background: linear-gradient(135deg,#FFD700,#f5c542) !important; color: #000 !important; }
[data-testid="stChatInput"] { background-color: var(--card) !important; border-color: var(--border) !important; border-radius: 12px !important; }
[data-testid="stChatInput"]:focus-within { border-color: var(--gold) !important; box-shadow: 0 0 0 1px var(--gold) !important; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Terminal initialized. I am the MarketMiner AI. Ask me to explain technical indicators or macroeconomic drivers."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Query the Oracle..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        api_key = st.session_state.get("api_key", "")
        if not api_key:
            st.error("⚠️ API Key required. Enter it in the sidebar.")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # --- AUTO-DISCOVER AVAILABLE MODEL ---
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                flash_models = [m for m in available_models if 'flash' in m.lower()]
                selected_model = flash_models[0] if flash_models else available_models[0]
                model = genai.GenerativeModel(selected_model)
                # -------------------------------------

                context = f"You are MarketMiner AI, a concise, highly technical trading assistant. The user is currently viewing {ASSET_MAP[st.session_state.target]['name']}. Address the query: {prompt}"
                
                with st.spinner("Processing..."):
                    response = model.generate_content(context)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Oracle Error: {e}")
