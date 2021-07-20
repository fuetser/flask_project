import datetime as dt
from math import floor


def get_elapsed(timestamp):
    now = get_current_time()
    delta = now - timestamp
    seconds = delta.total_seconds()

    if delta < dt.timedelta(minutes=1):
        return "только что"

    elif delta < dt.timedelta(hours=1):
        minutes = floor(seconds / 60)
        return _put_in_minutes_form(minutes)

    elif delta < dt.timedelta(days=1):
        hours = floor(seconds / 60 / 60)
        return _put_in_hours_form(hours)

    elif delta < dt.timedelta(weeks=1):
        days = floor(seconds / 60 / 60 / 24)
        return _put_in_days_form(days)

    elif delta < dt.timedelta(weeks=4):
        weeks = floor(seconds / 60 / 60 / 24 / 7)
        return _put_in_weeks_form(weeks)

    elif delta < dt.timedelta(days=365):
        months = (now.year - timestamp.year) * 12 + now.month - timestamp.month
        return _put_in_months_form(months)

    else:
        years = now.year - timestamp.year
        return _put_in_years_form(years)


def _put_in_minutes_form(minutes):
    if minutes == 1:
        return "минуту назад"
    elif minutes % 10 in (2, 3, 4):
        return f"{minutes} минуты назад"
    return f"{minutes} минут назад"


def _put_in_hours_form(hours):
    if hours == 1:
        return "час назад"
    elif hours in (2, 3, 4):
        return f"{hours} часа назад"
    return f"{hours} часов назад"


def _put_in_days_form(days):
    if days == 1:
        return "вчера"
    elif days in (2, 3, 4):
        return f"{days} дня назад"
    return f"{days} дней назад"


def _put_in_weeks_form(weeks):
    if weeks == 1:
        return "неделю назад"
    return f"{weeks} недели назад"


def _put_in_months_form(months):
    if months == 1:
        return "месяц назад"
    elif months in (2, 3, 4):
        return f"{months} месяца назад"
    return f"{months} месяцев назад"


def _put_in_years_form(years):
    if years == 1:
        return "год назад"
    elif years % 10 == 1 and years % 100 // 10 != 1:
        return f"{years} год назад"
    elif years % 10 in (2, 3, 4) and years % 100 // 10 != 1:
        return f"{years} года назад"
    return f"{years} лет назад"


def localize_comments(count):
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} комментарий"
    if count % 10 in (2, 3, 4) and count % 100 // 10 != 1:
        return f"{count} комментария"
    return f"{count} комментариев"


def localize_subscribers(count):
    """Представление числа участников как словосочетание.

    1 -> "1 участник"
    4 -> "4 участника"
    10 -> "10 участников"
    """
    localized_subscribers = "Участник"
    if 4 < count < 21 or count % 10 in (5, 6, 7, 8, 9, 0):
        localized_subscribers = "Участников"
    elif count % 10 in (2, 3, 4):
        localized_subscribers = "Участника"
    return localized_subscribers


def get_current_time():
    return dt.datetime.utcnow()
