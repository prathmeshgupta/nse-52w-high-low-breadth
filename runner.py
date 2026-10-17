"""CLI Tool for NSE Market Breadth & 52-Week High/Low.

Usage:
    python runner.py --summary
    python runner.py --date 2026-10-16
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from nse_52w_high_low_breadth.tracker import BreadthTracker

def main():
    parser = argparse.ArgumentParser(description="NSE Market Breadth & 52-Week High/Low CLI")
    parser.add_argument("--summary", action="store_true", help="Show latest market breadth status and regime")
    parser.add_argument("--date", help="Query specific trade date (YYYY-MM-DD)")
    args = parser.parse_args()

    parquet_path = Path(__file__).parent / "output" / "market_breadth.parquet"
    if not parquet_path.exists():
        print("Dataset not found. Run python update.py first.")
        return

    df = pd.read_parquet(parquet_path)
    tracker = BreadthTracker(df)

    target_date = args.date or df["trade_date"].max()
    status = tracker.get_latest_status(target_date)

    if not status:
        print(f"No breadth data available for date {target_date}.")
        return

    print(f"\n==========================================================================")
    print(f" NSE MARKET BREADTH & INTERNAL HEALTH AS OF {target_date}")
    print(f"==========================================================================")
    print(f"  * Total Traded Scrips : {status['total_traded_scrips']:,}")
    print(f"  * Advances            : {status['advances']:,} (Rs. {status['adv_turnover_cr']:,.2f} Cr)")
    print(f"  * Declines            : {status['declines']:,} (Rs. {status['dec_turnover_cr']:,.2f} Cr)")
    print(f"  * Unchanged           : {status['unchanged']:,}")
    print(f"  * Advance/Decline (AD): {status['ad_ratio']:.2f}")
    print(f"  * Arms Index (TRIN)   : {status['trin_ratio']:.2f}")
    print(f"  * High Breakouts      : {status['high_breakout_count']}")
    print(f"  * Low Breakdowns      : {status['low_breakdown_count']}")
    print(f"  * Net New Highs (NNH) : {status['net_new_highs']}")
    print(f"  * Market Regime       : {status['breadth_regime']}")
    print(f"==========================================================================\n")

if __name__ == "__main__":
    main()
