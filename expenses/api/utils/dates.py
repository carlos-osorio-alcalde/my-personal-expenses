import datetime
from typing import Literal

import pytz


def get_date_from_search(
    timeframe: Literal[
        "daily", "weekly", "partial_weekly", "monthly", "from_origin"
    ]
) -> datetime.datetime:
    """
    This function returns the date to search the emails from.

    Parameters
    ----------
    timeframe : Literal["daily", "weekly", "partial_weekly",
                        "monthly", "from_origin"]
        The timeframe to search the emails from.

    Returns
    -------
    datetime.datetime
        The date to search the emails from.
    """
    timezone = pytz.timezone("America/Bogota")
    now = datetime.datetime.now().astimezone(timezone)

    if timeframe == "daily":
        date_to_search = now

    elif timeframe == "weekly":
        date_to_search = now - datetime.timedelta(days=7)

    elif timeframe == "partial_weekly":
        # This is used to get the expenses of the current week, but only
        # from Monday to the current day
        date_to_search = now - datetime.timedelta(days=now.weekday())

    elif timeframe == "monthly":
        date_to_search = now - datetime.timedelta(days=30)

    elif timeframe == "from_origin":
        # This is used to get all the expenses from the origin of the
        # account
        date_to_search = now - datetime.timedelta(days=9999)
    else:
        raise ValueError(f"Timeframe {timeframe} not found")

    return date_to_search
