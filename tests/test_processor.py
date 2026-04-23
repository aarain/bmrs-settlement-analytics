import numpy as np
import pytest
import pandas as pd
from energy_report.processor import SettlementProcessor


@pytest.fixture
def processor():
    return SettlementProcessor()

@pytest.fixture()
def raw_data():
    return {
        "data": [
            {
                "settlementPeriod": 1,
                "createdDateTime": "2023-09-17T15:31:12Z",
                "systemSellPrice": 50,
                "systemBuyPrice": 60,
                "netImbalanceVolume": 100
            },
            {
                "settlementPeriod": 2,
                "createdDateTime": "2023-09-17T16:00:00Z",
                "systemSellPrice": 55,
                "systemBuyPrice": 65,
                "netImbalanceVolume": -20
            }
        ]
    }


def test_process_prices_success(processor, raw_data):
    data_frame = processor.process_prices(raw_data)

    assert len(data_frame) == 48
    assert list(data_frame.columns) == ["period", "creation_time", "sell_price", "buy_price", "niv"]

    period_1 = data_frame[data_frame["period"] == 1]
    assert period_1["creation_time"].values[0] == "2023-09-17T15:31:12Z"
    assert period_1["sell_price"].values[0] == 50
    assert period_1["buy_price"].values[0] == 60
    assert period_1["niv"].values[0] == 100
    period_2 = data_frame[data_frame["period"] == 2]
    assert period_2["creation_time"].values[0] == "2023-09-17T16:00:00Z"
    assert period_2["sell_price"].values[0] == 55
    assert period_2["buy_price"].values[0] == 65
    assert period_2["niv"].values[0] == -20


def test_process_prices_success_empty_data_frame(processor):
    raw_data = {"data": []}
    data_frame = processor.process_prices(raw_data)

    assert len(data_frame) == 48

    # The period column is still indexed 1-48 so drop it before checking everything else is NaN.
    assert data_frame.drop(columns=['period']).isna().values.all()


def test_process_prices_handles_duplicates(processor, raw_data):
    raw_data["data"][1]["settlementPeriod"] = 1

    data_frame = processor.process_prices(raw_data)

    assert len(data_frame) == 48

    # period 1 should contain the last processed period 1 values.
    period_1 = data_frame[data_frame["period"] == 1]
    assert period_1["creation_time"].values[0] == "2023-09-17T16:00:00Z"
    assert period_1["sell_price"].values[0] == 55
    assert period_1["buy_price"].values[0] == 65
    assert period_1["niv"].values[0] == -20


def test_process_prices_handles_missing_periods(processor, raw_data):
    raw_data["data"][1]["settlementPeriod"] = 3

    data_frame = processor.process_prices(raw_data)

    assert len(data_frame) == 48

    # period 2 should exist but contain NaN values.
    period_2 = data_frame[data_frame["period"] == 2]
    assert pd.isna(period_2["creation_time"].values[0])
    assert pd.isna(period_2["sell_price"].values[0])
    assert pd.isna(period_2["buy_price"].values[0])
    assert pd.isna(period_2["niv"].values[0])


def test_process_prices_enforces_numeric_types(processor, raw_data):
    raw_data["data"][0]["systemSellPrice"] = "50.5"

    data_frame = processor.process_prices(raw_data)

    assert pd.api.types.is_float_dtype(data_frame["sell_price"])
    assert data_frame.loc[data_frame["period"] == 1, "sell_price"].values[0] == 50.5


def test_process_prices_coerces_invalid_numeric_data(processor, raw_data):
    raw_data["data"][0]["systemSellPrice"] = "not a number"

    data_frame = processor.process_prices(raw_data)

    assert pd.isna(data_frame.loc[data_frame["period"] == 1, "sell_price"].values[0])


def test_process_prices_sorts_by_creation_time(processor, raw_data):
    newest_date_time = "3000-09-17T15:31:12Z"
    raw_data["data"][0]["createdDateTime"] = newest_date_time
    raw_data["data"][1]["settlementPeriod"] = 1

    data_frame = processor.process_prices(raw_data)

    assert data_frame.loc[data_frame["period"] == 1, "creation_time"].values[0] == newest_date_time


def test_reindex_forty_eight_periods_exact_index(processor):
    data_frame_in = pd.DataFrame({
        "period": [10, 20] # This data frame has fewer than 48 periods (2 periods).
    })

    data_frame_out = processor._reindex_forty_eight_periods(data_frame_in)

    assert len(data_frame_out) == 48
    assert data_frame_out["period"].iloc[0] == 1
    assert data_frame_out["period"].iloc[-1] == 48


def test_calculate_metrics(processor):
    data_frame = pd.DataFrame({
        "period": [1, 2],
        "sell_price": [100, 200],
        "buy_price": [160, 250],
        "niv": [10, -5]
    })

    # Total daily imbalance cost = (10*160) + (-5*200) = 1600 - 1000 = 600
    # Total absolute volume = 10 + 5 = 15
    # Daily imbalance unit rate = 600 / 15 = 40

    metrics = processor.calculate_metrics(data_frame)

    assert metrics["total_daily_imbalance_cost"] == 600.0
    assert metrics["daily_imbalance_unit_rate"] == 40.0


def test_calculate_metrics_with_nans(processor):
    data_frame = pd.DataFrame({
        "period": [1, 2],
        "sell_price": [10.5, np.nan],   # period 2 values will be ignored.
        "buy_price": [160, 250],
        "niv": [10, -5]
    })

    # Total daily imbalance cost = (10*160) = 1600
    # Total absolute volume = 10
    # Daily imbalance unit rate = 1600 / 10 = 160

    metrics = processor.calculate_metrics(data_frame)

    assert metrics["total_daily_imbalance_cost"] == 1600.0
    assert metrics["daily_imbalance_unit_rate"] == 160.0
