"""NSE Market Breadth & 52-Week High/Low Weekly/Daily Automated Updater.

Self-healing gap-fill updater that inspects the latest trade_date,
aggregates Advance/Decline breadth from official NSE Bhavcopies,
and exports Parquet/CSV atomically.
"""

import sys
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd

# Add local src to path for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from nse_52w_high_low_breadth.fetcher import BreadthFetcher

def get_trading_days(start_date: date, end_date: date) -> list[date]:
    """Generate potential trading weekdays between start and end date inclusive."""
    days = []
    curr = start_date
    while curr <= end_date:
        if curr.weekday() < 5:  # Monday to Friday
            days.append(curr)
        curr += timedelta(days=1)
    return days

def update_market_breadth():
    print(f"[{datetime.now().isoformat()}] Starting Market Breadth update...")
    fetcher = BreadthFetcher()
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_file = output_dir / "market_breadth.csv"
    parquet_file = output_dir / "market_breadth.parquet"

    existing_df = pd.DataFrame()
    if parquet_file.exists():
        existing_df = pd.read_parquet(parquet_file)
        print(f"Loaded {len(existing_df):,} existing breadth sessions from {parquet_file.name}")

    today = date.today()

    if existing_df.empty:
        start_date = today - timedelta(days=7)
    else:
        max_date_str = str(existing_df["trade_date"].max())
        max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
        start_date = max_date - timedelta(days=1)

    target_days = get_trading_days(start_date, today)
    print(f"Targeting {len(target_days)} trading days between {start_date} and {today}...")

    new_records = []
    for d in target_days:
        print(f"Aggregating market breadth for {d.strftime('%Y-%m-%d')}...")
        metrics = fetcher.fetch_date(d)
        if metrics:
            print(f"  Advances: {metrics['advances']} | Declines: {metrics['declines']} | AD Ratio: {metrics['ad_ratio']}")
            new_records.append(metrics)
        else:
            print(f"  No bhavcopy available for {d.strftime('%Y-%m-%d')} (weekend/holiday or unpublished).")

    if not new_records and existing_df.empty:
        raise RuntimeError("No breadth data could be retrieved and no existing database found.")

    combined = []
    if not existing_df.empty:
        combined.append(existing_df)
    if new_records:
        combined.append(pd.DataFrame(new_records))

    merged = pd.concat(combined, ignore_index=True)

    # Core key deduplication on trade_date
    merged = merged.drop_duplicates(subset=["trade_date"], keep="last")

    # Sort chronologically descending
    merged = merged.sort_values(by="trade_date", ascending=False).reset_index(drop=True)

    # Save
    merged.to_parquet(parquet_file, index=False, compression="snappy")
    merged.to_csv(csv_file, index=False)
    print(f"Saved {len(merged):,} breadth sessions to {parquet_file.name} and {csv_file.name}")

    # Run quality gate
    from evaluate_quality import audit_quality
    audit_quality()
    print("Market Breadth update completed successfully.")

if __name__ == "__main__":
    update_market_breadth()
