"""Date helpers for the Date Countdown integration."""

from datetime import date


def anniversary_in_year(month: int, day: int, year: int) -> date:
    """Return the occurrence of a recurring calendar date in ``year``.

    If the date is 29 February and ``year`` is not a leap year, return
    28 February (common practice in France). Other invalid dates still
    raise ``ValueError``.
    """
    try:
        return date(year, month, day)
    except ValueError:
        if month == 2 and day == 29:
            return date(year, 2, 28)
        raise


def years_elapsed(origin: date, as_of: date) -> int:
    """Return the number of full anniversary years from ``origin`` to ``as_of``.

    The anniversary of 29 February is observed on 28 February in non-leap
    years, so the year increments on that observed date.
    """
    years = as_of.year - origin.year
    if as_of < anniversary_in_year(origin.month, origin.day, as_of.year):
        years -= 1
    return years
