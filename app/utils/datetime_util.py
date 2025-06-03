"""
Utility functions for handling date and time operations.

Provides functions for getting current UTC time, calculating time differences,
formatting dates and times, and determining the start/end of various periods
(day, week, month, year). Ensures timezone awareness, primarily using UTC.
"""

import calendar
import datetime
import platform
from enum import Enum

import pytz
from dateutil.relativedelta import relativedelta

# Define UTC timezone object for reuse
UTC = datetime.timezone.utc


class Period(str, Enum):
    """Enumeration for time periods."""

    HOURLY = "hour"
    DAILY = "day"
    WEEKLY = "week"
    MONTHLY = "month"
    YEARLY = "year"


def utc_now_iso() -> str:
    """Returns the current UTC time as an ISO 8601 formatted string."""
    return datetime.datetime.now(UTC).isoformat()


def utc_now() -> datetime.datetime:
    """Returns the current UTC time as a timezone-aware datetime object."""
    return datetime.datetime.now(UTC)


def current_time_millis() -> int:
    """Returns the current UTC time in milliseconds since the epoch."""
    # Ensure epoch is timezone-aware (UTC)
    epoch = datetime.datetime(1970, 1, 1, tzinfo=UTC)
    return int((utc_now() - epoch).total_seconds() * 1000)


def before_now(minutes: int) -> datetime.datetime:
    """Returns a UTC datetime object representing a time 'minutes' ago."""
    return utc_now() - datetime.timedelta(minutes=minutes)


def get_date_string_without_year(date_str: str) -> str:
    """
    Formats a date string (YYYY-MM-DDTHH:MM:SS) to 'Mon DD HH:MM' uppercase.
    Assumes input string represents a naive datetime.
    """
    date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    return date.strftime("%b %d %H:%M").upper()


def after_now(hours: int) -> datetime.datetime:
    """Returns a UTC datetime object representing a time 'hours' from now."""
    return utc_now() + datetime.timedelta(hours=hours)


def get_ist_time() -> tuple[str, str]:
    """Returns the current IST date and time as formatted strings."""
    ist = pytz.timezone("Asia/Kolkata")
    ist_time = datetime.datetime.now(ist)

    ist_date = ist_time.strftime("%B %d %Y")  # Format date as "Month day year"
    ist_time_str = ist_time.strftime(
        "%I:%M %p"
    )  # Format time as "hour:minute AM/PM"

    return ist_date, ist_time_str


def _ensure_aware(dt: datetime.datetime) -> datetime.datetime:
    """Ensures the datetime object is timezone-aware, assuming UTC if naive."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # Assume UTC if naive
        return dt.replace(tzinfo=UTC)
    # Convert to UTC if it's aware but not UTC
    return dt.astimezone(UTC)


def ensure_naive(dt: datetime.datetime) -> datetime.datetime:
    """Ensures the datetime object is timezone-naive by removing tzinfo."""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def start_of_day(dt: datetime.datetime) -> datetime.datetime:
    """Returns the start of the day (00:00:00)
    for the given datetime in UTC."""
    aware_dt = _ensure_aware(dt)
    return aware_dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime.datetime) -> datetime.datetime:
    """Returns the end of the day (23:59:59.999999)
    for the given datetime in UTC."""
    aware_dt = _ensure_aware(dt)
    return aware_dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def start_of_week(dt: datetime.datetime) -> datetime.datetime:
    """Returns the start of the week (Monday 00:00:00)
    for the given datetime in UTC."""
    aware_dt = _ensure_aware(dt)
    start = aware_dt - datetime.timedelta(days=aware_dt.weekday())
    return start.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_week(dt: datetime.datetime) -> datetime.datetime:
    """Returns the end of the week (Sunday 23:59:59.999999)
    for the given datetime in UTC."""
    aware_dt = _ensure_aware(dt)
    end = aware_dt + datetime.timedelta(days=(6 - aware_dt.weekday()))
    return end.replace(hour=23, minute=59, second=59, microsecond=999999)


def start_of_month(dt: datetime.datetime) -> datetime.datetime:
    """Returns the start of the month (Day 1, 00:00:00)
    for the given datetime in UTC."""
    aware_dt = _ensure_aware(dt)
    return aware_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def end_of_month(dt: datetime.datetime) -> datetime.datetime:
    """Returns the end of the month (Last day, 23:59:59.999999)
    for the given datetime in UTC."""
    aware_dt = _ensure_aware(dt)
    last_day = calendar.monthrange(aware_dt.year, aware_dt.month)[1]
    return aware_dt.replace(
        day=last_day, hour=23, minute=59, second=59, microsecond=999999
    )


def start_of_year(dt: datetime.datetime) -> datetime.datetime:
    """Returns the start of the year (Jan 1, 00:00:00)
    for the given datetime in UTC."""
    aware_dt = _ensure_aware(dt)
    return aware_dt.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    )


def end_of_year(dt: datetime.datetime) -> datetime.datetime:
    """Returns the end of the year (Dec 31, 23:59:59.999999)
    for the given datetime in UTC."""
    aware_dt = _ensure_aware(dt)
    return aware_dt.replace(
        month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
    )


def get_end_of_period(
    dt: datetime.datetime, period: Period
) -> datetime.datetime:
    """Calculates the end of the specified period
    for the given UTC datetime."""
    periods = {
        Period.DAILY: end_of_day,
        Period.WEEKLY: end_of_week,
        Period.MONTHLY: end_of_month,
        Period.YEARLY: end_of_year,
    }
    if period not in periods:
        raise ValueError(f"Unsupported period: {period}")
    # Ensure dt is aware UTC before passing to period functions
    aware_dt = _ensure_aware(dt)
    return periods[period](aware_dt)


def get_start_of_period(period: Period, offset: int = 0) -> datetime.datetime:
    """
    Calculates the start of the specified period
    relative to the current UTC time.

    Args:
        period: The period type (daily, weekly, monthly, yearly).
        offset: The number of periods to offset
        from the current period (0 for current).

    Returns:
        A timezone-aware UTC datetime object
        representing the start of the period.
    """
    now_aware = utc_now()
    start_dt = None

    if period == Period.DAILY:
        start_dt = now_aware - datetime.timedelta(days=offset)
        start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == Period.WEEKLY:
        start_dt = now_aware - datetime.timedelta(
            days=now_aware.weekday() + 7 * offset
        )
        start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == Period.MONTHLY:
        start_dt = now_aware - relativedelta(months=offset)
        start_dt = start_dt.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
    elif period == Period.YEARLY:
        start_dt = now_aware - relativedelta(years=offset)
        start_dt = start_dt.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    else:
        raise ValueError(f"Unsupported period: {period}")

    return start_dt


def decimal_four_places(total: float) -> str:
    """Formats a float to a string with four decimal places."""
    return f"{total:.4f}"


def format_datetime_custom(dt: datetime.datetime) -> str:
    """
    Format a datetime object to the pattern "Month Day H:MM am/pm".
    Handles platform differences for padding removal.
    Assumes input dt might be naive or aware.
    """
    # Use aware dt for formatting if possible, otherwise use naive
    dt_to_format = _ensure_aware(dt) if dt.tzinfo else dt
    if platform.system() == "Windows":
        formatted_date = dt_to_format.strftime("%B %d %#I:%M %p")
    else:
        # Linux/macOS: %-I removes leading zero for hours
        formatted_date = dt_to_format.strftime("%B %d %-I:%M %p")

    return formatted_date


def format_date_dd_mm_yyyy(date_obj: datetime.datetime) -> str:
    """Formats a datetime object into the string 'dd-Mon-yyyy' format.
    Example: '24-May-2024'.
    Assumes input date_obj might be naive or aware.
    """
    # Use aware dt for formatting if possible, otherwise use naive
    dt_to_format = _ensure_aware(date_obj) if date_obj.tzinfo else date_obj
    return dt_to_format.strftime("%d-%b-%Y")


def format_datetime_hh_mm_pm_am(dt: datetime.datetime) -> str:
    """
    Format a datetime object to the pattern "H:MM am/pm".
    Handles platform differences for padding removal.
    Assumes input dt might be naive or aware.
    """
    # Use aware dt for formatting if possible, otherwise use naive
    dt_to_format = _ensure_aware(dt) if dt.tzinfo else dt
    if platform.system() == "Windows":
        formatted_date = dt_to_format.strftime("%#I:%M %p")
    else:
        formatted_date = dt_to_format.strftime("%-I:%M %p")

    return formatted_date


def start_of_a_non_leap_year() -> datetime.datetime:
    non_leap_year = 2023

    start_of_year = datetime.datetime(
        year=non_leap_year,
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    return start_of_year


def get_billing_period_datetimes(
    billing_year: int, billing_month: int
) -> tuple[datetime.datetime, datetime.datetime]:
    """
    Calculates the start and end datetimes
    for a given billing month and year.
    Start datetime will be the first day of the month at 00:00:00.
    End datetime will be the last day of the month at 23:59:59.

    Args:
        billing_year: The year of the billing cycle.
        billing_month: The month of the billing cycle.

    Returns:
        A tuple containing the start and end datetime objects (UTC aware).

    Raises:
        ValueError: If the billing_month or billing_year is invalid.
    """
    if not 1 <= billing_month <= 12:
        raise ValueError("Billing month must be between 1 and 12.")
    base_date = datetime.datetime(billing_year, billing_month, 1)

    start_dt = start_of_month(base_date)
    end_dt = end_of_month(base_date)
    return start_dt, end_dt
