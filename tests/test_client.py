import pytest
import httpx
from energy_report.client import ElexonClient


SETTLEMENT_DATE = "2023-09-18"

@pytest.fixture
def client():
    return ElexonClient() # Instantiate a new client instance for every test.


def test_get_system_prices_success(client, mocker):
    # Mock the Elexon response structure
    mock_data = {
        "data": [
            {
                "settlementDate": SETTLEMENT_DATE,
                "settlementPeriod": 2,
                "startTime": "2023-09-18T00:30:00Z",
                "createdDateTime": "2023-09-17T15:31:12Z",
                "systemSellPrice": 215,
                "systemBuyPrice": 215,
                "bsadDefaulted": False,
                "priceDerivationCode": "P",
                "reserveScarcityPrice": 0,
                "netImbalanceVolume": 291.9136,
                "sellPriceAdjustment": 0,
                "buyPriceAdjustment": 0,
                "replacementPrice": None,
                "replacementPriceReferenceVolume": None,
                "totalAcceptedOfferVolume": 790.6547,
                "totalAcceptedBidVolume": -738.74115,
                "totalAdjustmentSellVolume": 0,
                "totalAdjustmentBuyVolume": 240,
                "totalSystemTaggedAcceptedOfferVolume": 789.6547,
                "totalSystemTaggedAcceptedBidVolume": -738.74115,
                "totalSystemTaggedAdjustmentSellVolume": None,
                "totalSystemTaggedAdjustmentBuyVolume": 240
            }
        ],
        "metadata": {
            "datasets": [
                "DATASET"
            ]
        }
    }

    mock_get = mocker.patch.object(httpx.Client, "get")
    mock_get.return_value = mocker.Mock(status_code=200)
    mock_get.return_value.json.return_value = mock_data

    result = client.get_system_prices(SETTLEMENT_DATE)

    assert result == mock_data

    mock_get.assert_called_once_with(
        url=f"{client.BASE_URL}{client.PRICES_URL_PREFIX}{SETTLEMENT_DATE}",
        params={"format": "json"}
    )


def test_get_system_prices_success_with_no_data(client, mocker):
    mock_get = mocker.patch.object(httpx.Client, "get")
    mock_get.return_value = mocker.Mock(status_code=200)
    mock_get.return_value.json.return_value = {"data": []}

    result = client.get_system_prices(SETTLEMENT_DATE)

    assert result == {}


def test_get_system_prices_success_after_retries(client, mocker):
    # Mock the sleep to make it instantaneous, regardless of the number of retry attempts.
    mocker.patch("tenacity.nap.time.sleep", side_effect=None)

    mock_get = mocker.patch.object(httpx.Client, "get")
    # Mock 2 failures followed by 1 success
    mock_get.side_effect = [
        httpx.HTTPStatusError(message="Error", request=mocker.Mock(), response=mocker.Mock(status_code=503)),
        httpx.HTTPStatusError(message="Error", request=mocker.Mock(), response=mocker.Mock(status_code=503)),
        mocker.Mock(status_code=200, json=lambda: {"data": "success"})
    ]

    result = client.get_system_prices(SETTLEMENT_DATE)

    assert result == {"data": "success"}
    assert mock_get.call_count == 3


def test_get_system_prices_error_after_retries(client, mocker):
    # Mock the sleep to make it instantaneous, regardless of the number of retry attempts.
    mocker.patch("tenacity.nap.time.sleep", side_effect=None)

    mock_get = mocker.patch.object(httpx.Client, "get")
    # Mock the same failure (every time).
    mock_get.side_effect = httpx.HTTPStatusError(
        message="Error",
        request=mocker.Mock(),
        response=mocker.Mock(status_code=500)
    )

    with pytest.raises(httpx.HTTPStatusError):
        client.get_system_prices(SETTLEMENT_DATE)

    assert mock_get.call_count == 3
