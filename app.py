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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg: #08090c;
        --card: #121318;
        --card2: #181a20;
        --card3: #20222a;
        --border: #23252f;
        --border-soft: #1b1d25;
        --gold: #f5c542;
        --gold-bright: #FFD700;
        --gold-dim: rgba(245,197,66,0.10);
        --text: #f4f5f7;
        --dim: #717784;
        --muted: #3a3f4b;
        --green: #2dd4a7;
        --green-dim: rgba(45,212,167,0.12);
        --red: #f0556d;
        --red-dim: rgba(240,85,109,0.12);
        --blue: #4f8cff;
        --teal: #14b8a6;
        --shadow: 0 4px 24px rgba(0,0,0,0.40);
        --shadow-soft: 0 2px 12px rgba(0,0,0,0.25);
    }

    /* Header */
    header[data-testid="stHeader"] { background-color: transparent !important; }
    .block-container { padding: 2.4rem 1.6rem 1rem 1.6rem !important; max-width: 100% !important; }
    [data-testid="stSidebarContent"] { padding: 0 !important; background-color: var(--card) !important; border-right: 1px solid var(--border-soft); }
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(1200px 600px at 80% -10%, rgba(79,140,255,0.04), transparent 60%),
            radial-gradient(1000px 500px at 0% 0%, rgba(245,197,66,0.03), transparent 55%),
            var(--bg);
        color: var(--text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.01em;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: #2a2b35; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--gold); }

    /* ── TICKER BAR ── */
    .ticker-bar { background: #080909; border-bottom: 1px solid var(--border); padding: 7px 0; overflow: hidden; white-space: nowrap; margin: -2rem -1.5rem 18px -1.5rem; }
    .ticker-track { display: inline-flex; animation: scroll 40s linear infinite; }
    .ticker-track:hover { animation-play-state: paused; }
    .t-item { display: inline-flex; align-items: center; gap: 6px; padding: 0 22px; font-size: 12px; border-right: 1px solid #1a1b22; }
    .t-item .t-name { color: var(--dim); font-weight: 500; }
    .t-item .t-price { font-weight: 700; color: #fff; }
    .t-item .up { color: var(--green); }
    .t-item .dn { color: var(--red); }
    @keyframes scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

    /* ── SIDEBAR BRANDING ── */
    .sb-top { padding: 20px 18px 18px 18px; border-bottom: 1px solid var(--border-soft); background: linear-gradient(180deg, var(--card2) 0%, var(--card) 100%); }
    .logo { display: flex; align-items: center; gap: 12px; }
    .logo-mark { width: 38px; height: 38px; background: linear-gradient(135deg, var(--gold-bright) 0%, var(--gold) 100%); border-radius: 10px; display: grid; place-items: center; font-size: 19px; color: #1a1500; font-weight: bold; box-shadow: 0 2px 10px rgba(245,197,66,0.25); }
    .logo-name { font-size: 18px; font-weight: 800; color: var(--text); letter-spacing: -0.5px; line-height: 1.1; }
    .logo-name span { color: var(--gold); }
    .logo-sub { font-size: 10px; color: var(--dim); margin-top: 2px; letter-spacing: 0.2px; }
    .sb-label { padding: 16px 18px 7px; font-size: 9.5px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 1.4px; }

    /* ── SIDEBAR ASSET ROWS ── */
    .sb-asset-row {
        display: flex; align-items: center; padding: 11px 16px; cursor: pointer;
        border-left: 3px solid transparent; transition: all 0.18s cubic-bezier(0.4,0,0.2,1); gap: 10px;
        margin: 1px 8px; border-radius: 9px;
    }
    .sb-asset-row:hover { background: var(--card2); }
    .sb-asset-row.active { background: linear-gradient(90deg, rgba(245,197,66,0.10), rgba(245,197,66,0.02)); border-left-color: var(--gold); box-shadow: inset 0 0 0 1px rgba(245,197,66,0.10); }
    .sb-asset-icon { font-size: 20px; width: 28px; text-align: center; flex-shrink: 0; }
    .sb-asset-info { flex: 1; min-width: 0; }
    .sb-asset-name { font-size: 13px; font-weight: 600; color: var(--text); }
    .sb-asset-ticker { font-size: 10px; color: var(--dim); letter-spacing: 0.3px; }
    .sb-asset-right { text-align: right; flex-shrink: 0; }
    .sb-asset-price { font-size: 13px; font-weight: 700; color: var(--text); font-variant-numeric: tabular-nums; }
    .sb-asset-chg { font-size: 11px; font-weight: 600; font-variant-numeric: tabular-nums; }
    .sb-asset-chg.up { color: var(--green); }
    .sb-asset-chg.dn { color: var(--red); }

    /* ── SIDEBAR SPARKLINE WRAPPER ── */
    .sb-spark { width: 60px; height: 30px; flex-shrink: 0; }

    /* ── SIDEBAR BUTTONS ── */
    div[data-testid="stButton"] > button {
        width: 100%;
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--dim) !important;
        font-size: 10.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        padding: 5px 8px !important;
        border-radius: 7px !important;
        margin: -2px 8px 6px 8px !important;
        width: calc(100% - 16px) !important;
        transition: all 0.18s cubic-bezier(0.4,0,0.2,1);
    }
    div[data-testid="stButton"] > button:hover {
        border-color: var(--gold) !important;
        color: var(--gold) !important;
        background: var(--gold-dim) !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(245,197,66,0.18), rgba(245,197,66,0.06)) !important;
        border-color: var(--gold) !important;
        color: var(--gold) !important;
    }

    /* ── MAIN HEADER BAR ── */
    .ch-head {
        padding: 16px 22px; border: 1px solid var(--border); border-radius: 14px 14px 0 0;
        display: flex; align-items: center; gap: 14px;
        background: linear-gradient(180deg, var(--card2) 0%, var(--card) 100%); margin-bottom: 0px;
        flex-wrap: wrap; box-shadow: var(--shadow-soft);
    }
    .ch-icon { font-size: 28px; }
    .ch-name { font-size: 21px; font-weight: 800; color: var(--text); letter-spacing: -0.5px; }
    .ch-ticker { font-size: 11px; color: var(--dim); background: var(--card3); padding: 4px 9px; border-radius: 6px; border: 1px solid var(--border); font-weight: 600; letter-spacing: 0.3px; }
    .ch-price { font-size: 30px; font-weight: 800; font-variant-numeric: tabular-nums; letter-spacing: -1px; }
    .ch-chg { font-size: 13px; font-weight: 700; padding: 5px 11px; border-radius: 7px; font-variant-numeric: tabular-nums; }
    .ch-chg.up { color: var(--green); background: var(--green-dim); }
    .ch-chg.dn { color: var(--red); background: var(--red-dim); }
    .demo-badge { background: var(--gold-dim); color: var(--gold); padding: 4px 10px; border-radius: 6px; font-size: 9.5px; font-weight: 700; border: 1px solid rgba(245,197,66,.25); letter-spacing: 0.5px; }

    /* ── OHLC BAR (below header) ── */
    .ohlc-bar {
        background: var(--card); border: 1px solid var(--border); border-top: none;
        display: flex; align-items: center; padding: 9px 22px; gap: 0; flex-wrap: wrap;
    }
    .ohlc-item { display: flex; align-items: center; gap: 6px; padding: 0 18px 0 0; border-right: 1px solid var(--border-soft); margin-right: 18px; }
    .ohlc-item:last-child { border-right: none; margin-right: 0; }
    .ohlc-lbl { font-size: 9.5px; color: var(--dim); font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; }
    .ohlc-val { font-size: 12px; font-weight: 700; color: var(--text); font-variant-numeric: tabular-nums; }
    .ohlc-val.hi { color: var(--green); }
    .ohlc-val.lo { color: var(--red); }

    /* ── SUMMARY STRIP ── */
    .summary {
        background: linear-gradient(90deg, rgba(245,197,66,0.06) 0%, transparent 70%);
        border: 1px solid var(--border); border-top: none; border-radius: 0 0 14px 14px;
        padding: 12px 22px; font-size: 12.5px; line-height: 1.75; color: #9ca3af; margin-bottom: 0;
        box-shadow: var(--shadow-soft);
    }
    .summary strong { color: var(--text); }

    /* ── STATS GRID ── */
    .stats {
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 18px 0 22px 0;
    }
    .stat {
        background: linear-gradient(180deg, var(--card2) 0%, var(--card) 100%);
        padding: 17px 19px; border-radius: 13px; border: 1px solid var(--border);
        display: flex; flex-direction: column; gap: 2px; transition: all 0.22s cubic-bezier(0.4,0,0.2,1); cursor: default;
        box-shadow: var(--shadow-soft);
    }
    .stat:hover { border-color: rgba(245,197,66,0.30); transform: translateY(-3px); box-shadow: var(--shadow); }
    .stat-lbl { font-size: 9.5px; color: var(--dim); text-transform: uppercase; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 7px; }
    .stat-val { font-size: 21px; font-weight: 800; font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: -0.5px; }
    .stat-sub { font-size: 10px; color: var(--dim); margin-top: 6px; display: flex; align-items: center; gap: 5px; }
    .badge { display: inline-block; font-size: 9px; padding: 3px 8px; border-radius: 5px; font-weight: 700; letter-spacing: 0.3px; }
    .badge.r { background: var(--red-dim); color: var(--red); }
    .badge.g { background: var(--green-dim); color: var(--green); }
    .badge.y { background: var(--gold-dim); color: var(--gold); }

    /* ── CHART AREA ── */
    .chart-wrap { background: var(--card); border: 1px solid var(--border); border-top: none; padding: 0; }
    .chart-box { background: linear-gradient(180deg, var(--card2) 0%, var(--card) 100%); border: 1px solid var(--border); border-radius: 13px; padding: 10px; box-shadow: var(--shadow-soft); transition: border-color 0.2s; }
    .chart-box:hover { border-color: rgba(245,197,66,0.20); }

    /* ── SECTION DIVIDER ── */
    .section-head { font-size: 11px; font-weight: 700; color: var(--dim); text-transform: uppercase; letter-spacing: 1.4px; margin: 10px 0 14px 0; display: flex; align-items: center; gap: 10px; }
    .section-head::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }

    /* ── CHAT UI ── */
    [data-testid="stChatMessage"] { background-color: var(--card) !important; border: 1px solid var(--border); border-radius: 8px; margin-bottom: 10px; padding: 14px !important; }
    [data-testid="chatAvatarIcon-user"] { background-color: var(--card3) !important; color: var(--text) !important; }
    [data-testid="chatAvatarIcon-assistant"] { background-color: var(--gold) !important; color: #000 !important; }
    [data-testid="stChatInput"] { background-color: var(--card) !important; border-color: var(--border) !important; }
    [data-testid="stChatInput"]:focus-within { border-color: var(--gold) !important; box-shadow: 0 0 0 1px var(--gold) !important; }
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
        <span class="demo-badge">LIVE INTEL</span>
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
            increasing_line_color='#2dd4a7', decreasing_line_color='#f0556d',
            increasing_fillcolor='#2dd4a7', decreasing_fillcolor='#f0556d'
        )])
        ma20_line = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma20_line, line=dict(color='#f5c542', width=1.6, dash='dot'), name='MA20'))

        fig.update_layout(
            template="plotly_dark", height=430, margin=dict(t=14, b=12, l=12, r=52),
            paper_bgcolor='#121318', plot_bgcolor='#121318',
            font=dict(family='Inter, sans-serif'),
            xaxis=dict(
                showgrid=False,
                rangeslider_visible=False,
                rangebreaks=[dict(bounds=["sat", "mon"])],
                color='#717784'
            ),
            yaxis=dict(showgrid=True, gridcolor='#1b1d25', side="right", color='#717784'),
            showlegend=True,
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0)', font=dict(color='#717784', size=10))
        )
        st.markdown("<div class='chart-wrap' style='border-radius:0 0 14px 14px;padding:8px;box-shadow:var(--shadow-soft);'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Summary & Perfectly Aligned Stats Grid
    trend = "bullish uptrend" if pct >= 0 else "bearish downtrend"
    rsi_val = tech.get('rsi', 50)
    rsi_stat = "overbought" if rsi_val > 70 else ("oversold" if rsi_val < 30 else "neutral")
    rsi_col = "var(--red)" if rsi_val > 70 else ("var(--green)" if rsi_val < 30 else "var(--dim)")
    ma_val = tech.get('ma20', 0)
    macd_val = tech.get('macd', 0)

    st.markdown(f"""
    <div class="summary">
        ✨ <strong>AI Oracle:</strong> <strong>{name}</strong> is in a <strong>{trend}</strong>. RSI(14) at <strong style="color:{rsi_col};">{rsi_val:.1f}</strong> is <strong style="color:{rsi_col};">{rsi_stat}</strong>. Price is <strong>{'above' if curr > ma_val else 'below'}</strong> the 20-period moving average. IQ Score <strong>{72 if rsi_val > 55 else (35 if rsi_val < 45 else 56)}/100</strong> — <strong>{'moderately bullish' if pct >= 0 else 'moderately bearish'} bias</strong>. Current: <strong>${curr:,.2f}</strong>
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
    chart_layout = dict(template="plotly_dark", height=250, margin=dict(t=38, b=15, l=10, r=10), paper_bgcolor='#121318', plot_bgcolor='#121318', title_font=dict(size=12, color="#9ca3af"), font=dict(color='#717784', family='Inter, sans-serif'))

    with c1:
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        assets = ['Metals', 'Energy', 'Agri', 'Equities', 'Crypto']
        perfs = [0.8, -0.4, 1.2, 0.5, 2.1] 
        colors = ['#2dd4a7' if p > 0 else '#f0556d' for p in perfs]
        fig_bar = go.Figure(data=[go.Bar(x=assets, y=perfs, marker_color=colors)])
        fig_bar.update_layout(**chart_layout, title="📊 Sector Performance Model")
        fig_bar.update_yaxes(showgrid=True, gridcolor='#1b1d25')
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        labels = ['Equities', 'Bonds', 'Gold', 'Cash']
        values = [60, 20, 10, 10]
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.55, marker=dict(colors=['#4f8cff', '#a855f7', '#f5c542', '#2dd4a7'], line=dict(color='#121318', width=2)))])
        fig_pie.update_layout(**chart_layout, title="🥧 Institutional Allocation", showlegend=False)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
        np.random.seed(42)
        x_val = np.random.normal(0.05, 0.02, 50)
        y_val = x_val * 0.7 + np.random.normal(0, 0.015, 50)
        fig_scatter = go.Figure(data=go.Scatter(x=x_val, y=y_val, mode='markers', marker=dict(color='#4f8cff', size=8, opacity=0.75, line=dict(color='#121318', width=1))))
        fig_scatter.update_layout(**chart_layout, title=f"📈 Alpha Correlation vs SPY", xaxis_title="S&P 500", yaxis_title=f"{sym}")
        fig_scatter.update_xaxes(showgrid=True, gridcolor='#1b1d25')
        fig_scatter.update_yaxes(showgrid=True, gridcolor='#1b1d25')
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
