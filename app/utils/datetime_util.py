import datetime
from enum import Enum
import pytz
import calendar
from dateutil.relativedelta import relativedelta
import platform


class Period(str, Enum):
    hourly = "hour"
    daily = "day"
    weekly = "week"
    monthly = "month"
    yearly = "year"


def datetime_now():
    return datetime.datetime.utcnow().isoformat()


def current_time_millis():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def before_now(minutes):
    return datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)


def get_date_string_without_year(date_str):
    date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    return date.strftime("%b %d %H:%M").upper()


def after_now(hours):
    return datetime.datetime.utcnow() + datetime.timedelta(hours=hours)


def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    ist_time = datetime.datetime.now(ist)

    ist_date = ist_time.strftime('%B %d %Y')  # Format date as "Month day year"
    ist_time_str = ist_time.strftime('%I:%M %p')  # Format time as "hour:minute AM/PM"

    return ist_date, ist_time_str


def start_of_day(dt):
    return datetime.datetime.combine(dt, datetime.time.min)


def end_of_day(dt):
    return datetime.datetime.combine(dt, datetime.time.max)


def start_of_week(dt):
    start = dt - datetime.timedelta(days=dt.weekday())  # Monday as the first day of the week
    return datetime.datetime.combine(start, datetime.time.min)


def end_of_week(dt):
    end = dt + datetime.timedelta(days=(6 - dt.weekday()))  # Sunday as the last day of the week
    return datetime.datetime.combine(end, datetime.time.max)


def start_of_month(dt):
    return datetime.datetime.combine(dt.replace(day=1), datetime.time.min)


def end_of_month(dt):
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return datetime.datetime.combine(dt.replace(day=last_day), datetime.time.max)


def start_of_year(dt):
    return datetime.datetime.combine(dt.replace(month=1, day=1), datetime.time.min)


def end_of_year(dt):
    return datetime.datetime.combine(dt.replace(month=12, day=31), datetime.time.max)


def get_end_of_period(dt: datetime, period: Period):
    periods = {
        Period.daily: lambda: end_of_day(dt),
        Period.weekly: lambda: end_of_week(dt),
        Period.monthly: lambda: end_of_month(dt),
        Period.yearly: lambda: end_of_year(dt)
    }
    end = periods[period]()
    return end


def get_start_of_period(period, offset=0):
    today = datetime.date.today()
    periods = {
        Period.daily: lambda: today - datetime.timedelta(days=offset),
        Period.weekly: lambda: today - datetime.timedelta(days=today.weekday() + 7 * offset),
        Period.monthly: lambda: (today - relativedelta(months=offset)).replace(day=1),
        Period.yearly: lambda: (today - relativedelta(years=offset)).replace(day=1, month=1)
    }
    start_of_period = periods[period]()
    return start_of_period


def decimal_four_places(total):
    return f"{total:.4f}"


def format_datetime_custom(dt):
    """
    Format a datetime object to the pattern "December 12 6:00 pm".
    """
    if platform.system() == 'Windows':
        formatted_date = dt.strftime('%B %d %#I:%M %p')
    else:
        formatted_date = dt.strftime('%B %d %-I:%M %p')

    return formatted_date


def format_date_dd_mm_yyyy(date_obj: datetime) -> str:
    """Formats a datetime object into the string 'dd-Month Abbreviation-yyyy' format.

    Args:
        date_obj: The datetime object to format.

    Returns:
        A string representing the date in the desired format (e.g., '24-May-2024').
    """
    return date_obj.strftime("%d-%b-%Y")


def format_datetime_hh_mm_pm_am(dt):
    """
    Format a datetime object to the pattern "6:00 pm".
    """
    if platform.system() == 'Windows':
        formatted_date = dt.strftime('%#I:%M %p')
    else:
        formatted_date = dt.strftime('%-I:%M %p')

    return formatted_date
