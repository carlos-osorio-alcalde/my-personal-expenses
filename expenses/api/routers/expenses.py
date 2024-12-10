import datetime
from typing import List, Literal

import pytz
from fastapi import APIRouter, Depends

from expenses.api.schemas import (
    LabeledTransactionInfo,
    SummaryADayLikeToday,
    SummaryTransactionInfo,
)
from expenses.api.security import check_access_token
from expenses.api.utils import (
    get_date_from_search,
    get_summary_a_day_like_today,
    get_transactions,
    get_transactions_from_database,
    get_transactions_with_labels,
    process_transactions_api_expenses,
)
from expenses.processors.schemas import TransactionInfo

router = APIRouter(prefix="/expenses")

# Emails to obtain the transactions from
EMAILS_FROM_ = [
    "alertasynotificaciones@notificacionesbancolombia.com",
    "alertasynotificaciones@bancolombia.com.co",
]


# Function to get the transactions from the database
def get_gross_transactions(
    timeframe: Literal["daily", "weekly", "partial_weekly", "monthly"]
) -> List[TransactionInfo]:
    """
    This function returns the full transactions of the current timeframe

    Returns
    -------
    List[TransactionInfo]
        The summary of the expenses of the day, week or month.
    """
    # Get the date to search
    date_to_search = get_date_from_search(timeframe)

    # Search in the database for the transactions
    transactions_from_db = get_transactions_from_database(date_to_search)

    # If there are not transactions in the database, search in the API
    # and process the transactions.
    transactions = (
        transactions_from_db
        if len(transactions_from_db) > 0
        else get_transactions(
            email_from=EMAILS_FROM_[0], date_to_search=date_to_search
        )
        + get_transactions(
            email_from=EMAILS_FROM_[1], date_to_search=date_to_search
        )
    )

    return transactions


# Create the endpoint to get the summary of the expenses of the day, week or
# month
@router.get(
    "/summary/{timeframe}",
    response_model=SummaryTransactionInfo,
    dependencies=[Depends(check_access_token)],
)
async def get_expenses(
    timeframe: Literal["daily", "weekly", "partial_weekly", "monthly"]
) -> SummaryTransactionInfo:
    """
    This function returns the summary of the expenses of the day, week or
    month.

    Parameters
    ----------
    timeframe : Literal["daily", "weekly", "partial_weekly", "monthly"]
        The timeframe to obtain the expenses from.

    Returns
    -------
    SummaryTransactionInfo
        The summary of the expenses of the day, week or month.
    """
    return process_transactions_api_expenses(
        get_gross_transactions(timeframe)
    )


@router.get(
    "/summary/historical",
    response_model=SummaryADayLikeToday,
    dependencies=[Depends(check_access_token)],
)
async def get_expenses_a_day_like_today() -> SummaryADayLikeToday:
    """
    This function returns the summary of the expenses of a day like today.

    Returns
    -------
    SummaryADayLikeToday
        The summary of the expenses of a day like today.
    """
    # Return the summary
    return SummaryADayLikeToday(
        **get_summary_a_day_like_today(
            datetime.datetime.now()
            .astimezone(pytz.timezone("America/Bogota"))
            .isoweekday()
        )
    )


# Create the endpoint to get all the transactions of the current day
@router.get(
    "/full-transactions",
    response_model=List[TransactionInfo],
    dependencies=[Depends(check_access_token)],
)
async def get_full_transactions(
    timeframe: Literal[
        "daily", "weekly", "partial_weekly", "monthly", "from_origin"
    ]
) -> List[TransactionInfo]:
    """
    This function returns the full transactions of the current day

    Parameters
    ----------
    timeframe : Literal["daily", "weekly", "partial_weekly", "monthly", "from_origin"]
        The timeframe to obtain the expenses from.

    Returns
    -------
    List[TransactionInfo]
        The summary of the expenses of the day, week or month.
    """
    return get_gross_transactions(timeframe=timeframe)


# Create the endpoint to get the transactions with the labels
@router.get(
    "/labeled-transactions",
    response_model=List[LabeledTransactionInfo],
    dependencies=[Depends(check_access_token)],
)
async def obtain_transactions_with_labels(
    timeframe: Literal[
        "daily", "weekly", "partial_weekly", "monthly", "from_origin"
    ]
) -> List[LabeledTransactionInfo]:
    """
    This function returns the transactions with the labels

    Parameters
    ----------
    timeframe : Literal["daily", "weekly", "partial_weekly", "monthly", "from_origin"]
        The timeframe to obtain the expenses from.

    Returns
    -------
    List[LabeledTransactionInfo]
        The summary of the expenses of the day, week or month.
    """
    # Get the date to search
    date_to_search = get_date_from_search(timeframe)

    # Get the transactions
    transactions = get_transactions_with_labels(date_from=date_to_search)

    # Return the transactions
    return transactions
