import datetime

from pydantic import BaseModel


class TransactionInfo(BaseModel):
    """
    Class that represents the transaction information.
    """

    transaction_type: str
    amount: float
    merchant: str
    datetime: datetime.datetime
    paynment_method: str | None
    email_log: str | None
