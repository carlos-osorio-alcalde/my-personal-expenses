from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor


class WithdrawalEmailProcessor(EmailProcessor):
    """
    This is the processor of the withdrawal transaction emails.

    Here's an example of the email:

    Bancolombia le informa Retiro por $999.999,00 en CAJERO.
    Hora 20:50 28/07/2023 T.Deb *9999. Inquietudes al 6045109095/01800093198

    """

    def __init__(self, email: TransactionEmail):
        super().__init__(email)
        self.transaction_type = "Retiro"
        self._is_income = False

    def _set_pattern(self) -> str:
        """
        This function sets the pattern of the transaction type.

        Returns
        -------
        str
            The pattern of the transaction type.
        """
        # TODO: Extend this pattern to withdraw from the "Corresponsal"
        pattern = (
            r"(?i)Retiro por (?P<purchase_amount>.*?) en "
            r"(?P<merchant>[\w\s.*\/]+)."
            r"Hora (?P<time>\d{2}:\d{2}) (?P<date>\d{2}/\d{2}/\d{4})"
            r" (?P<payment_method>T\.Deb \*\d+)"
        )
        return pattern
