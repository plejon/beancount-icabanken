from datetime import datetime


def make_date_obj(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()
