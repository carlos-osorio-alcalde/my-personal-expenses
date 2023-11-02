from typing import List, Literal

from fastapi import APIRouter, Depends

from expenses.api.schemas import SummaryMerchant
from expenses.api.security import check_access_token
from expenses.api.utils import get_date_from_search, get_merchants_values

router = APIRouter(prefix="/merchants")


@router.get(
    "/{timeframe}",
    response_model=List[SummaryMerchant],
    dependencies=[Depends(check_access_token)],
)
async def get_merchants(
    timeframe: Literal["daily", "weekly", "partial_weekly", "monthly"]
) -> List[SummaryMerchant]:
    """
    This function returns the merchants of the day, week or month.

    Parameters
    ----------
    timeframe : str
        The timeframe to obtain the merchants from.

    Returns
    -------
    SummaryMerchants
        The merchants of the day, week or month.
    """
    # Get the date to search
    date_to_search = get_date_from_search(timeframe)

    return get_merchants_values(date_to_search)
