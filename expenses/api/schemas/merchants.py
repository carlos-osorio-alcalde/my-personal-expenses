from pydantic import BaseModel


class SummaryMerchant(BaseModel):
    """
    This class is the schema for the merchants summary.
    """

    merchant: str | None
    amount: float | None
    count: int | None
