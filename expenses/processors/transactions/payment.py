from typing import List, Union

from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor


class PaymentEmailProcessor(EmailProcessor):
    """
    This class is the processor for payment emails.

    Here are some examples:

    Bancolombia te informa Pago por $99,999.00 a ESTABLECIMIENTO COM
    desde producto *9999. 06/08/2023 14:30.
    Inquietudes al 6045109095/018000931987.

    Bancolombia: Pagaste $99,999.00 a ESTABLECIMIENTO desde tu producto
    *9999 el 05/02/2024 09:55. ¿Dudas? 6045109095/018000931987.
    """

    def __init__(self, email: TransactionEmail):
        super().__init__(email)
        self.transaction_type = "Pago"
        self._is_income = False

    def _set_pattern(self) -> Union[str, List]:
        """
        This function sets the pattern of the transaction type.

        Returns
        -------
        Union[str, List]
            The pattern of the transaction type.
        """
        patterns = [
            (
                r"(?i)Pago por (?P<purchase_amount>.*?) "
                r"a (?P<merchant>[\w\s.*\/-]+) "
                r"desde producto (?:\*(?P<payment_method>\d+))?"
            ),
            (
                r"(?i)Pagaste (?P<purchase_amount>.*?) "
                r"a (?P<merchant>[\w\s.*\/-]+)"
                r" desde tu producto (?:\*(?P<payment_method>\d+)) el "
                r"(?P<datetime>\d{2}/\d{2}/\d{4} \d{2}:\d{2})."
            ),
        ]

        return patterns
