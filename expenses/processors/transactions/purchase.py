from typing import List, Union

from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor


class PurchaseEmailProcessor(EmailProcessor):
    """
    This class is the processor of the transaction type "Compra".

    Here are some examples of the emails:

    Bancolombia le informa Compra por $999.999,00 en ESTABLECIMIENTO 19:45.
    31/07/2023 T.Cred *9999. Inquietudes al 6045109095/018000931987.

    Bancolombia le informa compra por $999.999,00 en ESTABLECIMIENTO 13:25.
    01/08/2023 compra afiliada a T.Cred *9999.
    Inquietudes al 6045109095/01800931987.

    """

    def __init__(self, email: TransactionEmail):
        super().__init__(email)
        self.transaction_type = "Compra"
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
                r"(?i)Compra por (?P<purchase_amount>.*?) "
                r"en (?P<merchant>[\w\s.*\/,-]+)"
                r"(?: (?P<time>\d{2}:\d{2}). (?P<date>\d{2}/\d{2}/\d{4}))"
                r"(?i)(?: (?P<payment_method>(?:T\.Cred|T\.Deb|compra afiliada"
                r" a T\.Cred) \*\d+))?"
            ),
            (
                r"(?i)Compra por COP(?P<purchase_amount>.*?) "
                r"en (?P<merchant>[\w\s.*\/,-]+)"
                r"(?: (?P<time>\d{2}:\d{2}). (?P<date>\d{2}/\d{2}/\d{4}))"
                r"(?i)(?: (?P<payment_method>(?:T\.Cred|T\.Deb|compra afiliada"
                r" a T\.Cred) \*\d+))?"
            ),
            (
                r"(?i)Compra por USD(?P<purchase_amount>.*?) "
                r"en (?P<merchant>[\w\s.*\/,-]+)"
                r"(?: (?P<time>\d{2}:\d{2}). (?P<date>\d{2}/\d{2}/\d{4}))"
                r"(?i)(?: (?P<payment_method>(?:T\.Cred|T\.Deb|compra afiliada"
                r" a T\.Cred) \*\d+))?"
            ),
        ]
        return patterns
