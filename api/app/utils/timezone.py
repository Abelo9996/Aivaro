"""
Timezone utilities for Aivaro
Default timezone is Pacific Time (America/Los_Angeles) if not specified
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import re

try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

from app.config import get_settings


def get_default_timezone():
    """Get the default timezone (Pacific Time)"""
    settings = get_settings()
    tz_name = settings.default_timezone
    
    if HAS_PYTZ:
        try:
            return pytz.timezone(tz_name)
        except:
            return pytz.timezone("America/Los_Angeles")
    else:
        # Fallback: Pacific Time is UTC-8 (or UTC-7 during DST)
        # This is a simple approximation
        return timezone(timedelta(hours=-8))


def now_local() -> datetime:
    """Get current time in the default timezone (Pacific)"""
    if HAS_PYTZ:
        tz = get_default_timezone()
        return datetime.now(tz)
    else:
        return datetime.now(timezone(timedelta(hours=-8)))


def now_utc() -> datetime:
    """Get current time in UTC"""
    return datetime.now(timezone.utc)


def to_local(dt: datetime) -> datetime:
    """Convert a datetime to the default timezone (Pacific)"""
    if dt is None:
        return None
    
    tz = get_default_timezone()
    
    # If datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        if HAS_PYTZ:
            dt = pytz.utc.localize(dt)
        else:
            dt = dt.replace(tzinfo=timezone.utc)
    
    if HAS_PYTZ:
        return dt.astimezone(tz)
    else:
        return dt.astimezone(tz)


def to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC"""
    if dt is None:
        return None
    
    # If datetime is naive (no timezone), assume it's in the default timezone
    if dt.tzinfo is None:
        tz = get_default_timezone()
        if HAS_PYTZ:
            dt = tz.localize(dt)
        else:
            dt = dt.replace(tzinfo=tz)
    
    return dt.astimezone(timezone.utc)


def parse_datetime(date_str: str, time_str: Optional[str] = None) -> datetime:
    """
    Parse a date/time string and return a timezone-aware datetime.
    Assumes Pacific Time if no timezone is specified.
    
    Supports formats:
    - 2026-02-15
    - 2026-02-15T10:00
    - 2026-02-15T10:00:00
    - 2026-02-15 10:00
    - Feb 15, 2026
    - February 15, 2026 at 10:00 AM
    """
    tz = get_default_timezone()
    
    # Combine date and time if provided separately
    if time_str:
        date_str = f"{date_str} {time_str}"
    
    # Try various formats
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",  # ISO with timezone
        "%Y-%m-%dT%H:%M:%S",    # ISO without timezone
        "%Y-%m-%dT%H:%M",       # ISO short
        "%Y-%m-%d %H:%M:%S",    # Standard datetime
        "%Y-%m-%d %H:%M",       # Standard short
        "%Y-%m-%d",             # Date only
        "%m/%d/%Y %H:%M",       # US format
        "%m/%d/%Y",             # US date only
        "%B %d, %Y at %I:%M %p", # Full month with time
        "%B %d, %Y",            # Full month
        "%b %d, %Y at %I:%M %p", # Short month with time
        "%b %d, %Y",            # Short month
    ]
    
    dt = None
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            break
        except ValueError:
            continue
    
    if dt is None:
        # Try to extract just the date and time with regex
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        time_match = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*(AM|PM))?', date_str, re.IGNORECASE)
        
        if date_match:
            year, month, day = map(int, date_match.groups())
            hour, minute, second = 0, 0, 0
            
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                second = int(time_match.group(3) or 0)
                am_pm = time_match.group(4)
                
                if am_pm:
                    if am_pm.upper() == 'PM' and hour != 12:
                        hour += 12
                    elif am_pm.upper() == 'AM' and hour == 12:
                        hour = 0
            
            dt = datetime(year, month, day, hour, minute, second)
    
    if dt is None:
        raise ValueError(f"Could not parse datetime: {date_str}")
    
    # If the parsed datetime has no timezone, assume Pacific
    if dt.tzinfo is None:
        if HAS_PYTZ:
            dt = tz.localize(dt)
        else:
            dt = dt.replace(tzinfo=tz)
    
    return dt


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format a datetime in the local timezone"""
    if dt is None:
        return ""
    local_dt = to_local(dt)
    return local_dt.strftime(fmt)


def format_date(dt: datetime) -> str:
    """Format just the date portion in local timezone"""
    return format_datetime(dt, "%Y-%m-%d")


def format_time(dt: datetime) -> str:
    """Format just the time portion in local timezone"""
    return format_datetime(dt, "%H:%M")


def format_iso(dt: datetime) -> str:
    """Format as ISO string with timezone"""
    if dt is None:
        return ""
    return dt.isoformat()


def today_local() -> str:
    """Get today's date in the local timezone as YYYY-MM-DD"""
    return now_local().strftime("%Y-%m-%d")


def current_time_local() -> str:
    """Get current time in the local timezone as HH:MM"""
    return now_local().strftime("%H:%M")
