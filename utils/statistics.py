import locale

from datetime import date, timedelta

from django.db.models.query import QuerySet

from constants.calendar import DAYS_OF_WEEK, MONTH_OF_YEAR

def build_statistics(records: QuerySet) -> dict:
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    statistics = {
        "per-days": {},
        "per-months": {},
    }

    idx = 0
    temp = {}
    today = date.today()

    while (idx < 7):
        today = date.today() - timedelta(days=idx)
        name = DAYS_OF_WEEK[today.weekday()]
        items = len(records.only("date").filter(date__date=today))
        temp[name] = items
        idx += 1
    statistics["per-days"] = temp

    idx = 0
    temp = {}

    while (idx < 12):
        name = MONTH_OF_YEAR[idx]
        items = len(records.only("date").filter(date__month=idx+1))
        temp[name] = items
        idx += 1
    statistics["per-months"] = temp

    return statistics
