"""NSE Market Breadth & 52-Week High/Low Fetcher.

Downloads daily security-wise Bhavcopy from NSE archives, aggregating
market-wide Advance/Decline statistics, turnover breadth, and TRIN ratios.
"""

import io
import requests
import pandas as pd
from datetime import datetime, date
from typing import Optional, Dict, Any

NSE_BHAV_URL = "https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class BreadthFetcher:
    """Computes daily market-wide breadth and internal momentum indicators."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_date(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Download bhavcopy and compute breadth aggregates for a given date."""
        date_str = target_date.strftime("%d%m%Y")
        url = NSE_BHAV_URL.format(date_str=date_str)

        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200 or not resp.text.strip():
                return None

            df = pd.read_csv(io.StringIO(resp.text))
            df.columns = [c.strip().upper() for c in df.columns]

            for c in df.select_dtypes(include="object").columns:
                df[c] = df[c].astype(str).str.strip()

            # Filter for active equities
            series_mask = df["SERIES"].isin(["EQ", "BE", "SM", "ST"])
            eq_df = df[series_mask].copy()

            for col in ["CLOSE_PRICE", "PREV_CLOSE", "HIGH_PRICE", "LOW_PRICE", "TURNOVER_LACS"]:
                if col in eq_df.columns:
                    eq_df[col] = pd.to_numeric(eq_df[col].astype(str).str.replace("-", ""), errors="coerce")

            eq_df = eq_df.dropna(subset=["CLOSE_PRICE", "PREV_CLOSE"])
            total_traded = len(eq_df)

            if total_traded == 0:
                return None

            advances = int((eq_df["CLOSE_PRICE"] > eq_df["PREV_CLOSE"]).sum())
            declines = int((eq_df["CLOSE_PRICE"] < eq_df["PREV_CLOSE"]).sum())
            unchanged = int((eq_df["CLOSE_PRICE"] == eq_df["PREV_CLOSE"]).sum())

            ad_ratio = round(advances / max(declines, 1), 2)

            adv_df = eq_df[eq_df["CLOSE_PRICE"] > eq_df["PREV_CLOSE"]]
            dec_df = eq_df[eq_df["CLOSE_PRICE"] < eq_df["PREV_CLOSE"]]

            adv_turnover_cr = round(float(adv_df["TURNOVER_LACS"].sum()) / 100.0, 2)
            dec_turnover_cr = round(float(dec_df["TURNOVER_LACS"].sum()) / 100.0, 2)

            # Arms Index / TRIN: (Advances / Declines) / (Adv_Vol / Dec_Vol)
            if dec_turnover_cr > 0 and (adv_turnover_cr / dec_turnover_cr) > 0:
                trin = round((advances / max(declines, 1)) / (adv_turnover_cr / dec_turnover_cr), 2)
            else:
                trin = 1.0

            # 52-Week High / Low proxies (Scrips closing within 1% of day's high with >10 Cr volume)
            high_breakout_count = int(((eq_df["CLOSE_PRICE"] >= eq_df["HIGH_PRICE"] * 0.99) & (eq_df["TURNOVER_LACS"] >= 50.0)).sum())
            low_breakdown_count = int(((eq_df["CLOSE_PRICE"] <= eq_df["LOW_PRICE"] * 1.01) & (eq_df["TURNOVER_LACS"] >= 50.0)).sum())
            net_highs = high_breakout_count - low_breakdown_count

            # Breadth Regime
            if ad_ratio >= 2.0 and net_highs > 10:
                regime = "STRONG_BULLISH_EXPANSION"
            elif ad_ratio > 1.1:
                regime = "MILD_BULLISH"
            elif ad_ratio >= 0.9:
                regime = "NEUTRAL_BALANCED"
            elif ad_ratio >= 0.5:
                regime = "MILD_BEARISH"
            else:
                regime = "STRONG_BEARISH_LIQUIDATION"

            trade_date_str = target_date.strftime("%Y-%m-%d")

            return {
                "trade_date": trade_date_str,
                "total_traded_scrips": total_traded,
                "advances": advances,
                "declines": declines,
                "unchanged": unchanged,
                "ad_ratio": ad_ratio,
                "adv_turnover_cr": adv_turnover_cr,
                "dec_turnover_cr": dec_turnover_cr,
                "trin_ratio": trin,
                "high_breakout_count": high_breakout_count,
                "low_breakdown_count": low_breakdown_count,
                "net_new_highs": net_highs,
                "breadth_regime": regime,
                "source": "NSE_SEC_BHAVDATA_AGGREGATED"
            }

        except Exception as e:
            print(f"Error computing breadth for {target_date}: {e}")
            return None
