import datetime

from pydantic import BaseModel


#
class TransactionInfo(BaseModel):
    """
    Class that represents the transaction information.
    """

    transaction_type: str
    amount: float
    merchant: str
    datetime: datetime.datetime
    paynment_method: str
    email_log: str | None


# Model for the labeled transaction
class LabeledTransaction(BaseModel):
    """
    This class represents a labeled transaction.
    """

    merchant: str
    datetime: datetime.datetime
    category: str
    similarity: float
