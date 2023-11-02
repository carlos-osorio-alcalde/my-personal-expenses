from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor


class TransferEmailProcessor(EmailProcessor):
    """
    This is the class that processes the emails of the transaction type
    "Recepcion transferencia"

    Here's an example of the email:

    Bancolombia le informa Transferencia por $999,9999 desde cta *9999 a
    cta 999999999999. 08/08/2023 19:30.
    Inquietudes al 6045109095/018000931987.

    """

    def __init__(self, email: TransactionEmail):
        super().__init__(email)
        self.transaction_type = "Transferencia"
        self._is_income = False

    def _set_pattern(self) -> str:
        """
        This function sets the pattern of the transaction type.

        Returns
        -------
        str
            The pattern of the transaction type.
        """
        pattern = (
            r"Transferencia por (?P<purchase_amount>.*?) "
            r"desde cta (?:\*(?P<payment_method>\d+))? a "
            r"cta (?P<merchant>\d+)"
        )
        return pattern
