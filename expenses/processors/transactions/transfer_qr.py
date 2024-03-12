from typing import List, Union

from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor


class QREmailProcessor(EmailProcessor):
    """
    This is the processor of the QR transaction emails.

    Here's an example of the email:

    Realizaste una transferencia con QR por $999,9999.00, desde cta 9999
    a cta 0000. 29/07/2023 03:06. Dudas al 018000931987. Bancolombia

    """

    def __init__(self, email: TransactionEmail):
        super().__init__(email)
        self.transaction_type = "QR"
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
                r"transferencia con QR por (?P<purchase_amount>.*?), "
                r"desde cta (?P<payment_method>\d+) a cta (?P<merchant>\d+)."
                r" (?P<datetime>\d{4}/\d{2}/\d{2} \d{2}:\d{2})."
            ),
            (
                r"transferencia con QR por (?P<purchase_amount>.*?), "
                r"desde cta (?P<payment_method>\d+) a cta (?P<merchant>\d+)."
                r" (?P<datetime>\d{2}/\d{2}/\d{4} \d{2}:\d{2})."
            ),
        ]
        return patterns
