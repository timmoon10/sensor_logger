import argparse
import csv
import datetime
import pathlib

import seaborn as sns

from utils import root_path

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", nargs="?", type=str, default=None)
    parser.add_argument("--start", default=None, type=str, help="Time range start")
    parser.add_argument("--end", default=None, type=str, help="Time range end")
    parser.add_argument("--data", default=None, type=str, help="Path to sensor logs")
    return parser.parse_args()

def main() -> None:
    """Main function"""

    # Parse command-line options
    args = parse_args()

    # Output directory
    out_dir = args.out_dir
    if out_dir is None:
        out_dir = root_path()
    out_dir = pathlib.Path(out_dir).resolve()

    # Time range
    start_time: datetime.datetime
    end_time: datetime.datetime
    if args.start is not None:
        start_time = datetime.datetime.fromisoformat(args.start)
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        start_time = datetime.datetime(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day,
            hour=12,
        )
    if args.end is not None:
        end_time = datetime.datetime.fromisoformat(args.end)
    else:
        end_time = datetime.datetime.now()
    start_date = start_time.date()
    end_date = end_time.date()

    # Find date files in time range
    data_dir = args.data
    if data_dir is None:
        data_dir = root_path() / "logs"
    data_dir = pathlib.Path(data_dir).resolve()
    data_files = []
    for data_file in data_dir.glob("*.csv"):
        name = data_file.stem
        try:
            date = datetime.date.fromisoformat(name)
        except ValueError:
            pass
        else:
            if start_date <= date <= end_date:
                data_files.append(data_file)

    # Load data from log files
    data = []
    for data_file in data_files:
        with open(data_file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                row_time = datetime.datetime.fromisoformat(row[0])
                if not (start_time <= row_time <= end_time):
                    continue
                data.append((row_time, float(row[1]), float(row[2])))

    # Extract data fields
    data.sort()
    times = [row[0] for row in data]
    temperature_data = [row[1] for row in data]
    humidity_data = [row[2] for row in data]

    # Plot results
    sns.set_theme(style="whitegrid")
    ax = sns.lineplot(x=times, y=temperature_data)
    ax.set_xlim(start_time, end_time)
    ax.get_figure().savefig(out_dir / "temperature.png")
    ax.cla()
    ax = sns.lineplot(x=times, y=humidity_data)
    ax.set_xlim(start_time, end_time)
    ax.set_ylim(0, 100)
    ax.get_figure().savefig(out_dir / "humidity.png")

if __name__ == "__main__":
    main()
