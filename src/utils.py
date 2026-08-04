import datetime


def ms_to_dt(ms: int) -> datetime.datetime:
    return datetime.datetime.utcfromtimestamp(ms / 1000)
