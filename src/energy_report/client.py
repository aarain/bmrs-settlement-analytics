import logging
import httpx
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


def log_retry(retry_state):
    logger.warning(
        f"Retrying {retry_state.fn.__name__}: "
        f"Attempt {retry_state.attempt_number} failed. "
        f"Exception: {retry_state.outcome.exception()}"
    )

class ElexonClient:
    BASE_URL = "https://api.data.elexon.co.uk/v1"
    # The system prices GET URL is /balancing/settlement/system-prices/{settlementDate}
    PRICES_URL_PREFIX = "/balancing/settlement/system-prices/"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        before_sleep=log_retry,
        reraise=True
    )
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Base GET request with retries and error handling.

        :raises: httpx.HTTPStatusError if the request fails after the maximum number of retries.
        :raises: httpx.RequestError if a non-HTTP error occurs.
        """

        url = f"{self.BASE_URL}{endpoint}"
        response = self.client.get(url=url, params=params)

        # Raise a HTTPStatusError for 4XX/5XX errors, triggering the tenacity retry decorator.
        # When this occurs, execution jumps back to the first line of this function.
        response.raise_for_status()

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
