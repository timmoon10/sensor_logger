import argparse
import collections
import csv
import datetime
import math
import pathlib

import matplotlib.pyplot as plt
import seaborn as sns

from utils import root_path

def compute_percentile_in_sorted(data: list[float], percentile: float) -> float:
    """Get percentile within sorted list"""
    idx = (percentile / 100) * (len(data) - 1)
    idx = min(max(round(idx), 0), len(data) - 1)
    return data[idx]

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", nargs="?", type=str, default=None)
    parser.add_argument("--data", default=None, type=str, help="Path to sensor logs")
    parser.add_argument(
        "--percentiles",
        nargs="+",
        type=float,
        default=[50],
        help="List of percentiles to compute",
    )
    return parser.parse_args()

def main() -> None:
    """Main function"""

    # Parse command-line options
    args = parse_args()
    percentiles = sorted(args.percentiles)

    # Output directory
    out_dir = pathlib.Path(args.out_dir or root_path()).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Directory with log files
    data_dir = pathlib.Path(args.data or (root_path() / "logs")).resolve()

    # Load data from log files
    temperature_data = { minute: [] for minute in range(0, 60 * 24, 5) }
    humidity_data = { minute: [] for minute in range(0, 60 * 24, 5) }
    for data_file in data_dir.glob("*.csv"):

        # Make sure file name is timestamp
        try:
            datetime.date.fromisoformat(data_file.stem)
        except ValueError:
            continue

        # Parse log file
        with open(data_file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:

                # Closest 5 minute interval, measured from noon
                row_time = datetime.datetime.fromisoformat(row[0])
                minute = (
                    (row_time.hour + 12) * 60
                    + row_time.minute
                    + row_time.second / 60
                )
                minute = 5 * round(minute / 5)
                minute = minute % (60 * 24)

                # Record data
                temperature_data[minute].append(float(row[1]))
                humidity_data[minute].append(float(row[2]))

    # Sort data
    for minute_data in temperature_data.values():
        minute_data.sort()
    for minute_data in humidity_data.values():
        minute_data.sort()

    # Plot temperature
    sns.set_theme(style="whitegrid")
    plt.figure()
    for percentile in percentiles:
        xs, ys = [], []
        for minute, minute_data in temperature_data.items():
            if not minute_data:
                continue
            xs.append(minute)
            ys.append(compute_percentile_in_sorted(minute_data, percentile))
        sns.lineplot(x=xs, y=ys, label=f"{percentile:g}th percentile")
    plt.title("Temperature")
    plt.xlabel("Time")
    plt.ylabel("Temperature (F)")
    plt.xlim(0, 60*24)
    plt.ylim(60, 80)
    plt.xticks(
        [60 * hour for hour in (0, 3, 6, 9, 12, 15, 18, 21, 24)],
        ["12pm", "3pm", "6pm", "9pm", "12am", "3am", "6am", "9am", "12pm"],
    )
    plt.legend()
    plt.savefig(out_dir / "temperature_percentiles.png")
    plt.close()

    # Plot humidity
    sns.set_theme(style="whitegrid")
    plt.figure()
    for percentile in percentiles:
        xs, ys = [], []
        for minute, minute_data in humidity_data.items():
            if not minute_data:
                continue
            xs.append(minute)
            ys.append(compute_percentile_in_sorted(minute_data, percentile))
        sns.lineplot(x=xs, y=ys, label=f"{percentile:g}th percentile")
    plt.title("Humidity")
    plt.xlabel("Time")
    plt.ylabel("Humidity (%)")
    plt.xlim(0, 60*24)
    plt.ylim(40, 80)
    plt.xticks(
        [60 * hour for hour in (0, 3, 6, 9, 12, 15, 18, 21, 24)],
        ["12pm", "3pm", "6pm", "9pm", "12am", "3am", "6am", "9am", "12pm"],
    )
    plt.legend()
    plt.savefig(out_dir / "humidity_percentiles.png")
    plt.close()

if __name__ == "__main__":
    main()
