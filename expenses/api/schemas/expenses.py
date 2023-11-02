import datetime
from typing import Union

from pydantic import BaseModel

from expenses.processors.schemas import TransactionInfo


class BaseTransactionInfo(BaseModel):
    """
    This class represents the base of the transaction info.
    """

    name: Union[str, None]
    amount: Union[float, None]
    count: Union[int, None]


class SummaryTransactionInfo(BaseModel):
    """
    This class represents the summary of all the transactions of the
    day, week or month.
    """

    purchases: BaseTransactionInfo
    withdrawals: BaseTransactionInfo
    transfer_reception: BaseTransactionInfo
    transfer_qr: BaseTransactionInfo
    payment: BaseTransactionInfo
    transfer: BaseTransactionInfo


class AddTransactionInfo(TransactionInfo):
    """
    This class is used to add a transaction manually.
    This inherits from TransactionInfo.
    """

    transaction_type: str = "Compra"
    datetime = datetime.datetime.now()
    paynment_method: str = "Cash"
    email_log: str = ""


class SummaryADayLikeToday(BaseModel):
    """
    This class represents the summary of all the transactions of a day like
    today.
    """

    mean_number_of_purchases: Union[float, None]
    median_amount_of_purchases: Union[float, None]


class AnomalyPredictionOutput(BaseModel):
    """
    This class represents the input of the anomaly prediction.
    """

    score: float
    prediction: str
