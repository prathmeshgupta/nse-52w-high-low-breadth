"""Market Breadth & Thrust Indicator Tracker."""

import pandas as pd
from typing import Dict, Any, Optional

class BreadthTracker:
    """Evaluates market breadth thrusts and internal divergence signals."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_latest_status(self, as_of_date: str = None) -> Optional[Dict[str, Any]]:
        """Returns the market breadth status and internal health metrics."""
        if self.df.empty:
            return None
        target_date = as_of_date or self.df["trade_date"].max()
        row_df = self.df[self.df["trade_date"] == target_date]
        if row_df.empty:
            return None
        return row_df.iloc[0].to_dict()
