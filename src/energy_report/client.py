import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ElexonClient:
    BASE_URL = "https://api.data.elexon.co.uk/v1"
    # The system prices GET URL is /balancing/settlement/system-prices/{settlementDate}
    PRICES_URL_PREFIX = "/balancing/settlement/system-prices/"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout)

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        response = self.client.get(url=url, params=params)

        json_response = response.json()

        # Even if the metadata exists, log a warning if there is no data.
        if not json_response.get("data"):
            logger.warning(f"No data field found for {endpoint}")
            return {}

        return json_response

    def get_system_prices(self, settlement_date: str) -> Dict[str, Any]:
        """
        Returns settlement system buy and sell prices for a given settlement day.

        See:
         https://bmrs.elexon.co.uk/api-documentation/endpoint/balancing/settlement/system-prices/%7BsettlementDate%7D
        """

        return self._get(f"{self.PRICES_URL_PREFIX}{settlement_date}", params={"format": "json"})
