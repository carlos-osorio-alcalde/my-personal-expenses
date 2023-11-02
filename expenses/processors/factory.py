import importlib
from typing import Dict

from expenses.constants import TRANSACTION_TYPES_
from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor


def import_processors() -> Dict[str, EmailProcessor]:
    """
    This function imports the processors of the transactions. It returns a
    dictionary with the transaction type and the corresponding processor.

    Returns
    -------
    Dict[str, EmailProcessor]
        The dictionary with the transaction type and the corresponding
        processor.
    """
    implemented_processors = {
        transaction: getattr(
            importlib.import_module(
                f"expenses.processors.{implementation['module_name']}"
            ),
            implementation["class_name"],
        )
        for transaction, implementation in TRANSACTION_TYPES_.items()
        if implementation["implemented"]
    }
    return implemented_processors


# Get the processors of the transactions.
TRANSACTIONS_PROCESSORS_ = import_processors()


class EmailProcessorFactory:
    """
    This class is the factory of the email processors. It identifies the
    transaction type of the email and returns the corresponding processor.
    """

    @staticmethod
    def _identify_transaction_type(email: TransactionEmail) -> str:
        """
        This function identifies the transaction type of the email. It checks
        if the email contains a valid transaction type.

        Returns
        -------
        str
            The transaction type.
        """
        str_message_lower = email.str_message.lower()
        for transaction_type in TRANSACTION_TYPES_:
            if transaction_type.lower() in str_message_lower:
                return transaction_type

    def get_processor(self, email: TransactionEmail) -> EmailProcessor:
        """
        This function returns the processor of the email.

        Returns
        -------
        BaseEmailProcessor
            The email processor.
        """
        transaction_type = self._identify_transaction_type(email)

        if transaction_type in TRANSACTIONS_PROCESSORS_:
            return TRANSACTIONS_PROCESSORS_[transaction_type](email)
        else:
            raise ValueError(
                f"The transaction type {transaction_type} is not supported"
            )
