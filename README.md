# MarketMiner

A real-time commodity intelligence dashboard built with Streamlit. Tracks live prices, computes technical indicators, and provides an AI-powered chat assistant for market analysis — all in a single-page web app.

---

## Overview

MarketMiner pulls live market data for 10 commodities and cryptocurrencies via Yahoo Finance, calculates key technical signals, and displays them in an interactive dark-themed dashboard. An integrated Gemini-powered chatbot lets you query the data conversationally.

---

## Features

- Live price feeds updating every 10 seconds for gold, silver, platinum, WTI crude, Brent crude, natural gas, copper, wheat, corn, and Bitcoin
- Candlestick chart with 20-period moving average overlay and weekend range breaks
- Technical indicators: RSI(14), MA(20), Bollinger Band width, MACD
- Composite Intelligence Score derived from RSI and volatility signals
- Animated ticker bar across all tracked assets
- OHLC bar with 52-week high/low, last volume, and 3-month average volume
- Sector performance bar chart, institutional allocation pie chart, and alpha correlation scatter plot
- AI chat assistant powered by Google Gemini with auto-model discovery
- Inline SVG sparklines in the sidebar for each asset

---

## Tech Stack

| Layer | Library |
|---|---|
| UI framework | Streamlit |
| Market data | yfinance |
| Charting | Plotly |
| Data processing | pandas, NumPy |
| AI assistant | Google Generative AI (Gemini) |

---

## Installation

**Requirements:** Python 3.9 or higher

```bash
# Clone the repository
git clone https://github.com/your-username/marketminer.git
cd marketminer

# Install dependencies
pip install streamlit yfinance pandas numpy plotly google-generativeai
```

---

## Usage

```bash
streamlit run marketminer.py
```

Open your browser at `http://localhost:8501`.

To use the AI chat assistant, enter a Google Gemini API key in the sidebar. You can obtain one at [https://aistudio.google.com](https://aistudio.google.com). The key is not stored anywhere beyond the current session.

---

## Project Structure

```
marketminer/
├── marketminer.py      # Main application — all logic and UI in one file
└── README.md
```

The app is intentionally self-contained in a single file. Key sections within it:

- **Section 1** — Page config and CSS overrides
- **Section 2** — Asset map and technical indicator calculations (RSI, MA, BB, MACD)
- **Section 3** — Sidebar with live asset rows, sparklines, and Intelligence Score panel
- **Section 4** — Main dashboard: ticker bar, candlestick chart, stats grid, analytics charts
- **Section 5** — Gemini AI chat interface

---

## Assets Tracked

| Ticker | Name |
|---|---|
| GC=F | Gold |
| SI=F | Silver |
| PL=F | Platinum |
| CL=F | WTI Crude Oil |
| BZ=F | Brent Crude Oil |
| NG=F | Natural Gas |
| HG=F | Copper |
| ZW=F | Wheat |
| ZC=F | Corn |
| BTC-USD | Bitcoin |

---

## Notes

- Data is fetched with a 9-second cache TTL via `@st.cache_data`. Yahoo Finance rate limits may occasionally cause brief gaps in live data.
- The Intelligence Score is a composite heuristic based on RSI thresholds and Bollinger Band width — it is not financial advice.
- The Sector Performance, Institutional Allocation, and Alpha Correlation charts currently use static placeholder data and are intended as layout demonstrations.

---

## License

MIT
