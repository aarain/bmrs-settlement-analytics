import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SettlementProcessor:
    def __init__(self):
        self.columns_map = {
            # Add required columns here for processing/outputting the time series.
            "settlementPeriod": "period",
            "createdDateTime": "creation_time",
            "systemSellPrice": "sell_price",
            "systemBuyPrice": "buy_price",
            "netImbalanceVolume": "niv"
        }

    def process_prices(self, json_response: Dict[str, Any]) -> pd.DataFrame:
        """Process the raw JSON into a cleaned data frame with exactly 48 periods."""

        data_list = json_response.get("data", [])

        if not data_list:
            # Return a data frame filled with NaNs (except the period column) with the correct number of periods.
            column_names = list(self.columns_map.values())
            return self._reindex_forty_eight_periods(pd.DataFrame(columns=column_names))

        data_frame = pd.DataFrame(data_list)

        # Extract the relevant columns and rename them to something more Pythonic.
        data_frame = data_frame[list(self.columns_map.keys())].rename(columns=self.columns_map)

        # Handle duplicates by keeping the latest row if multiple rows exist for a period.
        data_frame = data_frame.drop_duplicates(subset=["period"], keep="last")

        # Handle missing/removed periods by reindexing the exact number required.
        data_frame = self._reindex_forty_eight_periods(data_frame)

        return data_frame

    def _reindex_forty_eight_periods(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Reindex the data frame to have exactly 48 periods, inserting NaN for missing rows."""

        full_index = pd.Index(range(1, 49), name="period")
        data_frame = data_frame.set_index("period").reindex(full_index).reset_index()

        return data_frame
