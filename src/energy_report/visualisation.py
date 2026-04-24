import matplotlib.pyplot as plt
import pandas as pd


def plot_daily_metrics(data_frame: pd.DataFrame, settlement_date: str):
    """Generate a plot of sell/buy prices and net imbalance volume."""

    figure, axis_1 = plt.subplots(figsize=(12, 6))

    axis_1.set_xlabel("Settlement Period (1-48)")
    axis_1.set_ylabel("Price (£/MWh)")  # default y-axis is left.
    axis_1.grid(alpha=0.3)

    axis_1.step(
        data_frame["period"], data_frame["sell_price"],
        color="tab:green", linestyle="-", label="Sell Price", where="mid"
    )

    axis_1.step(
        data_frame["period"], data_frame["buy_price"],
        color="tab:red", linestyle="--", label="Buy Price", where="mid"
    )

    axis_2 = axis_1.twinx() # secondary y-axis is right.
    axis_2.set_ylabel(ylabel="Net Imbalance Volume (MWh)", color="tab:blue")
    axis_2.tick_params(axis="y", labelcolor="tab:blue")

    axis_2.bar(
        data_frame["period"], data_frame["niv"],
        color="tab:blue", label="NIV"
    )

    # Create a legend for the sell price, buy price, and NIV.
    lines, labels = axis_1.get_legend_handles_labels()
    bars, bar_labels = axis_2.get_legend_handles_labels()
    axis_1.legend(lines + bars, labels + bar_labels, loc="upper left")

    plt.title(f"Elexon System Prices vs NIV - {settlement_date}")
    figure.tight_layout()

    filename = f"report_{settlement_date}.png"
    plt.savefig(filename)
    print(f"Plot saved as {filename}")
