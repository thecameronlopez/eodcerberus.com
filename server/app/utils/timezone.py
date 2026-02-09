import os
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_BUSINESS_TIMEZONE = "America/Chicago"

def business_timezone() -> ZoneInfo:
    tz_name = os.environ.get("BUSINESS_TIMEZONE", DEFAULT_BUSINESS_TIMEZONE)
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        if tz_name != DEFAULT_BUSINESS_TIMEZONE:
            return ZoneInfo(DEFAULT_BUSINESS_TIMEZONE)
        raise RuntimeError(
            f"Timezone data unavailable for '{tz_name}'. Install tzdata and ensure BUSINESS_TIMEZONE is valid."
        )
    
    
def business_now() -> datetime:
    return datetime.now(business_timezone())


def business_today() -> date:
    return business_now().date()


def to_business_date(value: datetime) -> date:
    # Treat naive datetimes as UTC to keep behavior deterministic.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(business_timezone()).date()
