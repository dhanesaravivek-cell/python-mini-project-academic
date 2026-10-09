"""visuals.py - Matplotlib charts.
Each function shows a chart window, or saves a PNG if save_path is given."""
import matplotlib.pyplot as plt
import analysis


def _finish(save_path):
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120)
        plt.close()
    else:
        plt.show()


def _need_data(df):
    if df.empty:
        raise ValueError("There is no data to draw a chart")


def monthly_chart(df, save_path=None):
    """Bar chart of total rainfall in each month."""
    _need_data(df)
    data = analysis.monthly_totals(df)
    plt.figure(figsize=(8, 5))
    plt.bar(data.index, data.values, color="steelblue")
    plt.title("Monthly Rainfall Totals")
    plt.xlabel("Month")
    plt.ylabel("Rainfall (mm)")
    plt.xticks(rotation=45)
    _finish(save_path)


def seasonal_chart(df, save_path=None):
    """Bar chart of total rainfall in each season."""
    _need_data(df)
    data = analysis.seasonal_totals(df)
    plt.figure(figsize=(8, 5))
    plt.bar(data.index, data["total"], color="seagreen")
    plt.title("Seasonal Rainfall")
    plt.xlabel("Season")
    plt.ylabel("Total rainfall (mm)")
    _finish(save_path)


def location_chart(df, save_path=None):
    """Bar chart of total rainfall at each location."""
    _need_data(df)
    data = analysis.location_totals(df)
    plt.figure(figsize=(8, 5))
    plt.bar(data.index, data.values, color="orange")
    plt.title("Total Rainfall by Location")
    plt.xlabel("Location")
    plt.ylabel("Total rainfall (mm)")
    _finish(save_path)


def comparison_chart(result, save_path=None):
    """Bar chart comparing the total and average rainfall of two periods."""
    plt.figure(figsize=(8, 5))
    plt.bar(["Period 1 total", "Period 2 total"],
            [result["total1"], result["total2"]], color=["steelblue", "tomato"])
    plt.title("Period Comparison (total rainfall)")
    plt.ylabel("Rainfall (mm)")
    _finish(save_path)
