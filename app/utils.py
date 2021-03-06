import datetime as dt
from math import floor


def get_elapsed(timestamp):
    now = dt.datetime.utcnow()
    delta = now - timestamp
    if delta < dt.timedelta(minutes=1):
        return f"{delta.seconds} секунд назад"
    elif delta < dt.timedelta(hours=1):
        minutes = delta.seconds // 60
        return f"{minutes} минут назад"
    elif delta < dt.timedelta(days=1):
        hours = floor(delta.seconds / 60 / 60)
        return f"{hours} часов назад"
    elif delta < dt.timedelta(weeks=1):
        days = floor(delta.seconds / 60 / 60 / 24)
        return f"{days} дней назад"
    elif delta < dt.timedelta(weeks=4):
        weeks = floor(delta.seconds / 60 / 60 / 24 / 7)
        return f"{weeks} недели назад"
    elif delta < dt.timedelta(days=365):
        months = (now.year - timestamp.year) * 12 + now.month - timestamp.month
        return f"{months} месяцев назад"
    else:
        years = now.year - timestamp.year
        return f"{years} лет назад"


def localize_comments(count):
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} комментарий"
    if count % 10 in (2, 3, 4) and count % 100 // 10 != 1:
        return f"{count} комментария"
    return f"{count} комментариев"
