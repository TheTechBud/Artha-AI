from datetime import datetime, date, timedelta
import calendar


def days_in_month(d: date) -> int:
    return calendar.monthrange(d.year, d.month)[1]


def pct_month_elapsed(today: date) -> float:
    return today.day / days_in_month(today)


def days_until_salary(salary_day: int, today: date) -> int:
    """Return days until next salary. Handles month wraparound."""
    if today.day <= salary_day:
        return salary_day - today.day
    # next month
    next_month = today.replace(day=1) + timedelta(days=32)
    next_salary = next_month.replace(day=min(salary_day, days_in_month(next_month)))
    return (next_salary - today).days


def month_start(d: date) -> date:
    return d.replace(day=1)


def month_end(d: date) -> date:
    return d.replace(day=days_in_month(d))


def iso(d: date | datetime) -> str:
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()


def parse_date(s: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")
