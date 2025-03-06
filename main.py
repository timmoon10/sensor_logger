import argparse
import csv
import datetime
import functools
import pathlib
import time

import adafruit_sht4x
import board

@functools.cache
def sensor() -> adafruit_sht4x.SHT4x:
    sht = adafruit_sht4x.SHT4x(board.I2C())
    sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
    return sht

def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 1.8 + 32.0

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_file", nargs="?", type=str, default=None)
    return parser.parse_args()

def main() -> None:

    # Parse command-line options
    args = parse_args()

    # Output file path
    out_file = args.out_file
    if out_file is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d')
        log_dir = pathlib.Path(__file__).resolve().parent / "logs"
        out_file = log_dir / f"{timestamp}.csv"
    out_file = pathlib.Path(out_file).resolve()

    # Create output file with header if needed
    if not out_file.exists():
        with open(out_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(("Time", "Temperature (F)", "Humidity (%)"))

    for _ in range(5):
        timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
        temperature, humidity = sensor().measurements
        temperature = celsius_to_fahrenheit(temperature)
        with open(out_file, "a") as f:
            writer = csv.writer(f)
            writer.writerow((timestamp, f"{temperature:.1f}", f"{humidity:.0f}"))
        time.sleep(1)

if __name__ == "__main__":
    main()
