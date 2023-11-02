from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor


class PaymentEmailProcessor(EmailProcessor):
    """
    This class is the processor for payment emails.

    Here are some examples:

    Bancolombia te informa Pago por $99,999.00 a ESTABLECIMIENTO COM
    desde producto *9999. 06/08/2023 14:30.
    Inquietudes al 6045109095/018000931987.

    """

    def __init__(self, email: TransactionEmail):
        super().__init__(email)
        self.transaction_type = "Pago"
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
            r"(?i)Pago por (?P<purchase_amount>.*?) "
            r"a (?P<merchant>[\w\s.*\/-]+) "
            r"desde producto (?:\*(?P<payment_method>\d+))?"
        )
        return pattern
