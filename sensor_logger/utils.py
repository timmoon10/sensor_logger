import datetime
import functools
import pathlib

@functools.cache
def root_path() -> pathlib.Path:
    """Project root directory"""
    return pathlib.Path(__file__).resolve().parent.parent

def yesterday() -> datetime.date:
    return datetime.date.today() - datetime.timedelta(days=1)

def tomorrow() -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=1)

def date_to_datetime(
    date: datetime.date,
    *,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
) -> datetime.datetime:
    return datetime.datetime(
        year=date.year,
        month=date.month,
        day=date.day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
    )
