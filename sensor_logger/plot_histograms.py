import argparse
import collections
import csv
import datetime
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from utils import root_path

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", nargs="?", type=str, default=None)
    parser.add_argument("--data", default=None, type=str, help="Path to sensor logs")
    parser.add_argument(
        "--temperature-bin",
        default=0.1,
        type=float,
        help="Temperature bin size",
    )
    parser.add_argument(
        "--humidity-bin",
        default=1,
        type=float,
        help="Humidity bin size",
    )
    return parser.parse_args()

def main() -> None:
    """Main function"""

    # Parse command-line options
    args = parse_args()

    # Output directory
    out_dir = pathlib.Path(args.out_dir or root_path()).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Directory with log files
    data_dir = pathlib.Path(args.data or (root_path() / "logs")).resolve()

    # Load data from log files
    temperature_data = {
        minute: collections.defaultdict(lambda: 1)
        for minute in range(0, 60 * 24, 5)
    }
    humidity_data = {
        minute: collections.defaultdict(lambda: 1)
        for minute in range(0, 60 * 24, 5)
    }
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
                temperature_bin = round(float(row[1]) / args.temperature_bin)
                humidity_bin = round(float(row[2]) / args.humidity_bin)
                temperature_data[minute][temperature_bin] += 1
                humidity_data[minute][humidity_bin] += 1

    # Convert temperature data to DataFrame
    min_temp = 65
    max_temp = 80
    min_bin = round(min_temp / args.temperature_bin)
    max_bin = round(max_temp / args.temperature_bin)
    bins = pd.Index(range(min_bin, max_bin + 1), name="temperature")
    temperature_df = (
        pd.DataFrame.from_dict(temperature_data, orient="columns")
        .fillna(1)
        .reindex(index=bins, columns=sorted(temperature_data), fill_value=1)
        .astype(int)
    )
    max_count = temperature_df.to_numpy().max()

    # Plot temperature data
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots()
    sns.heatmap(
        temperature_df,
        ax=ax,
        vmin=0,
        vmax=max_count,
        cmap="viridis",
        cbar=False,
    )
    ax.invert_yaxis()
    ax.set_title("Temperature")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (F)")
    ax.set_xticks(
        np.linspace(0, temperature_df.shape[1], 9),
        ["12pm", "3pm", "6pm", "9pm", "12am", "3am", "6am", "9am", "12pm"],
    )
    ax.set_yticks(
        np.linspace(0, temperature_df.shape[0], 7),
        np.linspace(min_temp, max_temp, 7),
    )
    fig.autofmt_xdate(rotation=45)
    plt.savefig(out_dir / "temperature_histogram.png")
    plt.close()

    # Convert humidity data to DataFrame
    min_humidity = 50
    max_humidity = 80
    min_bin = round(min_humidity / args.humidity_bin)
    max_bin = round(max_humidity / args.humidity_bin)
    bins = pd.Index(range(min_bin, max_bin + 1), name="humidity")
    humidity_df = (
        pd.DataFrame.from_dict(humidity_data, orient="columns")
        .fillna(1)
        .reindex(index=bins, columns=sorted(humidity_data), fill_value=1)
        .astype(int)
    )
    max_count = humidity_df.to_numpy().max()

    # Plot humidity data
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots()
    sns.heatmap(
        humidity_df,
        ax=ax,
        vmin=0,
        vmax=max_count,
        cmap="viridis",
        cbar=False,
    )
    ax.invert_yaxis()
    ax.set_title("Humidity")
    ax.set_xlabel("Time")
    ax.set_ylabel("Humidity (%)")
    ax.set_xticks(
        np.linspace(0, humidity_df.shape[1], 9),
        ["12pm", "3pm", "6pm", "9pm", "12am", "3am", "6am", "9am", "12pm"],
    )
    ax.set_yticks(
        np.linspace(0, humidity_df.shape[0], 7),
        np.linspace(min_humidity, max_humidity, 7),
    )
    fig.autofmt_xdate(rotation=45)
    plt.savefig(out_dir / "humidity_histogram.png")
    plt.close()

if __name__ == "__main__":
    main()
