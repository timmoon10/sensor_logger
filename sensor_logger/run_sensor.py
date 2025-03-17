import argparse
import csv
import datetime
import functools
import pathlib
import time

import adafruit_sht4x
import board

from utils import date_to_datetime, root_path, tomorrow

@functools.cache
def sensor() -> adafruit_sht4x.SHT4x:
    """SHT45 temperature and humidity sensor"""
    sht = adafruit_sht4x.SHT4x(board.I2C())
    sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
    return sht

def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius scale to Fahrenheit"""
    return celsius * 1.8 + 32.0

def wait_until_tick(ticks_per_hour: int) -> None:
    """Divide hour into equal intervals and wait until next interval"""
    if ticks_per_hour < 1:
        raise ValueError(
            f"Requires at least one tick per hour (got ticks_per_hour={ticks_per_hour})"
        )
    interval = 3600 / ticks_per_hour
    now = datetime.datetime.now()
    last_hour = now.replace(minute=0, second=0, microsecond=0)
    ticks_since_hour = int((now - last_hour).total_seconds() / interval)
    next_tick = (
        last_hour
        + datetime.timedelta(seconds=(interval * (ticks_since_hour + 1)))
    )
    sleep_time = (next_tick - now).total_seconds()
    if sleep_time <= 0:
        # Something weird is happening, sleep one tick and hope it
        # goes away
        sleep_time = interval
    time.sleep(sleep_time)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("out_file", nargs="?", type=str, default=None)
    parser.add_argument(
        "--frequency", default=12, type=int, help="Sensor measurements per hour",
    )
    parser.add_argument(
        "--until", default=None, type=str, help="Run sensor until specified time",
    )
    parser.add_argument(
        "--duration", default=None, type=float, help="Number of hours to run sensor",
    )
    return parser.parse_args()

def main() -> None:
    """Main function"""

    # Parse command-line options
    args = parse_args()

    # Script duration
    end_time: datetime.datetime
    if args.until is not None:
        end_time = datetime.datetime.fromisoformat(args.until)
    elif args.duration is not None:
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(hours=args.duration)
    else:
        start_time = datetime.datetime.now()
        end_time = date_to_datetime(datetime.date.today(), hour=12)
        if end_time <= start_time:
            end_time = date_to_datetime(tomorrow(), hour=12)

    # Output file path
    out_file = args.out_file
    if out_file is None:
        timestamp = datetime.date.today().isoformat()
        log_dir = root_path() / "logs"
        out_file = log_dir / f"{timestamp}.csv"
    out_file = pathlib.Path(out_file).resolve()

    # Create output file with header if needed
    if not out_file.exists():
        with open(out_file, "w") as f:
            csv.writer(f).writerow(("Time", "Temperature (F)", "Humidity (%)"))

    # Perform sensor measurements at regular intervals
    while True:
        now = datetime.datetime.now()
        if now >= end_time:
            break
        timestamp = now.replace(microsecond=0).isoformat()
        temperature, humidity = sensor().measurements
        temperature = celsius_to_fahrenheit(temperature)
        with open(out_file, "a") as f:
            csv.writer(f).writerow(
                (timestamp, f"{temperature:.1f}", f"{humidity:.0f}")
            )
        wait_until_tick(args.frequency)

if __name__ == "__main__":
    main()
