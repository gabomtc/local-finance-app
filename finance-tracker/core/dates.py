from __future__ import annotations

from datetime import date
from typing import Tuple


def month_bounds(value: date) -> Tuple[date, date]:
    """Return the first day of the month and the first day of the next month."""
    start = value.replace(day=1)
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1)
    else:
        next_month = start.replace(month=start.month + 1)
    return start, next_month
