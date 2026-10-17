"""Quality and Integrity Audit for NSE Market Breadth Dataset."""

import pandas as pd
from pathlib import Path

def audit_quality():
    print("=" * 65)
    print(" NSE MARKET BREADTH & 52W HIGH/LOW - DATA QUALITY AUDIT")
    print("=" * 65)

    parquet_path = Path(__file__).parent / "output" / "market_breadth.parquet"
    assert parquet_path.exists(), f"Missing {parquet_path.name}"

    df = pd.read_parquet(parquet_path)
    print(f"Total Market Sessions Indexed: {len(df):,}")

    null_dates = df["trade_date"].isnull().sum()
    null_adv = df["advances"].isnull().sum()
    null_dec = df["declines"].isnull().sum()

    print(f"Null Trade Dates: {null_dates} {'[PASS]' if null_dates == 0 else '[FAIL]'}")
    print(f"Null Advances: {null_adv} {'[PASS]' if null_adv == 0 else '[FAIL]'}")
    print(f"Null Declines: {null_dec} {'[PASS]' if null_dec == 0 else '[FAIL]'}")

    # Accounting Identity: advances + declines + unchanged == total_traded_scrips
    sum_check = (df["advances"] + df["declines"] + df["unchanged"] != df["total_traded_scrips"]).sum()
    print(f"Accounting Balance Identity (Adv + Dec + Unch == Total): {sum_check} {'[PASS]' if sum_check == 0 else '[FAIL]'}")

    # AD ratio positive
    invalid_ad = (df["ad_ratio"] < 0.0).sum()
    print(f"Invalid Negative AD Ratios: {invalid_ad} {'[PASS]' if invalid_ad == 0 else '[FAIL]'}")

    print("\nRecent Market Breadth Observations:")
    cols = ["trade_date", "total_traded_scrips", "advances", "declines", "ad_ratio", "trin_ratio", "breadth_regime"]
    print(df[cols].tail(5).to_string(index=False))

    assert null_dates == 0, "Trade dates contain nulls!"
    assert sum_check == 0, "Advances + Declines does not equal Total!"
    assert invalid_ad == 0, "Negative AD ratios found!"

    print("=" * 65)
    print("ALL AUDIT CHECKS PASSED.")
    print("=" * 65)

if __name__ == "__main__":
    audit_quality()
