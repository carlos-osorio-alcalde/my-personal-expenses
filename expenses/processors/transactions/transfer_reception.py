from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor


class TransferReceptionEmailProcessor(EmailProcessor):
    """
    This is the class that processes the emails of the transaction type
    "Recepcion transferencia"

    Here's an example of the email:

    Bancolombia te informa recepcion transferencia de PEDRO PEREZ por
    $999,999 en la cuenta *9999. 31/07/2023 09:04. Dudas 018000931987

    """

    def __init__(self, email: TransactionEmail):
        super().__init__(email)
        self.transaction_type = "Recepcion Transferencia"
        self._is_income = True

    def _set_pattern(self) -> str:
        """
        This function sets the pattern of the transaction type.

        Returns
        -------
        str
            The pattern of the transaction type.
        """
        pattern = (
            r"recepcion transferencia de (?P<merchant>.*?) "
            r"por (?P<purchase_amount>.*?) "
            r"en la cuenta \*(?P<payment_method>\d{4}). "
        )
        return pattern
