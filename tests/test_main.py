import pandas as pd
from main import get_daily_report


def test_get_daily_report_success(mocker):
    ### Set up mocks

    mock_client = mocker.Mock()
    mock_processor = mocker.Mock()
    mock_visualisation = mocker.patch("main.plot_daily_metrics")

    mock_raw_data = {"data": "some_raw_json"}
    mock_data_frame = pd.DataFrame({
        "period": range(1, 49)
    })
    mock_metrics = {
        "total_daily_imbalance_cost": 56.80,
        "daily_imbalance_unit_rate": 77.41
    }

    mock_client.get_system_prices.return_value = mock_raw_data
    mock_processor.process_prices.return_value = mock_data_frame
    mock_processor.calculate_metrics.return_value = mock_metrics

    ### Test the function

    test_date = "2026-01-01"
    result = get_daily_report(settlement_date=test_date, client=mock_client, processor=mock_processor)

    mock_client.get_system_prices.assert_called_once_with(test_date)
    mock_processor.process_prices.assert_called_once_with(mock_raw_data)
    mock_visualisation.assert_called_once()

    assert result["total_daily_imbalance_cost"] == mock_metrics["total_daily_imbalance_cost"]
    assert result["daily_imbalance_unit_rate"] == mock_metrics["daily_imbalance_unit_rate"]
