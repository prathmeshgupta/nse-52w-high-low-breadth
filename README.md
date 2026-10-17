# NSE Market Breadth & 52-Week High/Low Dynamics

[![Daily/Weekly Market Breadth Dataset Update](https://github.com/prathmeshgupta/nse-52w-high-low-breadth/actions/workflows/weekly_update.yml/badge.svg)](https://github.com/prathmeshgupta/nse-52w-high-low-breadth/actions/workflows/weekly_update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Audited, daily time-series dataset of National Stock Exchange of India (NSE) **Market Breadth, Advance/Decline (A/D) Ratios, TRIN (Arms Index), and 52-Week High/Low expansions**.

Tracks market internals and structural regime shifts across all 3,000+ actively traded Indian equities.

---

### The Quantitative Problem (Market Internals vs Headline Distortions)

Headline index prices (such as Nifty 50) are heavily distorted by top mega-caps (Reliance, HDFC Bank, ICICI Bank, TCS, Infosys). During distribution phases, headline indices can grind higher while **70% of the broader market is quietly breaking down**.

Tracking internal market breadth reveals institutional health:
1. **Advance/Decline Ratio (ADR):** Proportion of scrips advancing vs declining.
2. **Turnover Breadth:** Capital committed to advances vs declines in ₹ Crore.
3. **Arms Index (TRIN):**
   $$\text{TRIN} = \frac{\text{Advances} / \text{Declines}}{\text{Advancing Turnover} / \text{Declining Turnover}}$$
   Values $< 1.0$ indicate strong buying pressure into advancing stocks; values $> 1.0$ indicate panic volume dumping.
4. **Zweig-Style Breadth Thrusts:** Sudden expansion from deep oversold to $ADR > 3.0$ signaling durable regime turns.

---

### Dataset Schema

Outputs are distributed in both **Apache Parquet (`snappy` compressed)** and standard **CSV**:
* `output/market_breadth.parquet`
* `output/market_breadth.csv`

| Field | Type | Description |
| :--- | :--- | :--- |
| `trade_date` | `string` | Trade session date in `YYYY-MM-DD` |
| `total_traded_scrips` | `int64` | Total number of actively traded equities |
| `advances` | `int64` | Number of scrips with `Close > Prev Close` |
| `declines` | `int64` | Number of scrips with `Close < Prev Close` |
| `unchanged` | `int64` | Number of scrips closing flat |
| `ad_ratio` | `float` | `Advances / Declines` ratio |
| `adv_turnover_cr` | `float` | Turnover in advancing stocks (₹ Crore) |
| `dec_turnover_cr` | `float` | Turnover in declining stocks (₹ Crore) |
| `trin_ratio` | `float` | Arms Index (TRIN volume breadth) |
| `high_breakout_count` | `int64` | Scrips closing near intraday highs with high volume |
| `low_breakdown_count` | `int64` | Scrips closing near intraday lows with high volume |
| `net_new_highs` | `int64` | Net Highs (`High Breakouts - Low Breakdowns`) |
| `breadth_regime` | `string` | `STRONG_BULLISH_EXPANSION`, `MILD_BULLISH`, `NEUTRAL`, `BEARISH` |
| `source` | `string` | Origin (`NSE_SEC_BHAVDATA_AGGREGATED`) |

---

### Automated Weekly & Daily Updates

* **Schedule**: Automated GitHub Actions workflow executes at **14:00 UTC (19:30 IST) Monday to Friday**, with a Sunday reconciliation at **02:00 UTC**.
* **Accounting Validation Gate**: Enforces `Advances + Declines + Unchanged == Total Traded Scrips`.

---

### Quickstart & CLI Usage

```bash
# 1. Clone the repository
git clone https://github.com/prathmeshgupta/nse-52w-high-low-breadth.git
cd nse-52w-high-low-breadth

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the automated updater locally
python update.py

# 4. View latest market breadth health
python runner.py --summary

# 5. Query a specific date
python runner.py --date 2026-10-16
```
