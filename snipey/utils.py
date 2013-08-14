from datetime import datetime


def datetime_from_milli(timestamp):
    return datetime.utcfromtimestamp(timestamp//1000).replace(
        microsecond=timestamp % 1000*1000)
