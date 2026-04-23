import logging
import sys
from datetime import date, timedelta
from energy_report.client import ElexonClient
from energy_report.processor import SettlementProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_daily_report(settlement_date: str, client=None, processor=None):
    """
    Retrieve, process, and plot a daily report of system imbalance price and cost for the previous settlement day.
    """

    client = client or ElexonClient()
    processor = processor or SettlementProcessor()

    logger.info(f"Getting system prices for {settlement_date}...")
    raw_data = client.get_system_prices(settlement_date)

    logger.info("Processing raw data...")
    clean_data_frame = processor.process_prices(raw_data)

    logger.info(f"Successfully processed {len(clean_data_frame)} periods.")

    metrics = processor.calculate_metrics(clean_data_frame)
    cost = metrics["total_daily_imbalance_cost"]
    rate = metrics["daily_imbalance_unit_rate"]

    print(f"****** Metrics for {settlement_date} ******")
    print(f"Total daily imbalance cost: £{cost:.2f}")
    print(f"Daily imbalance unit rate: £{rate:.2f}/MWh")

    # TODO:visualisation (plotting)

    return metrics


if __name__ == "__main__":
    date_yesterday = date.today() - timedelta(days=1)
    report_date = date_yesterday.isoformat()

    try:
        get_daily_report(report_date)
    except Exception as e:
        logger.error(f"Error getting daily report: {e}")
        sys.exit(1)
