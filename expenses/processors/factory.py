from expenses.constants import (
    TRANSACTION_TYPES_MAPPING_,
    TRANSACTION_TYPES_NAMES_,
)
from expenses.core.transaction_email import TransactionEmail
from expenses.processors.base import EmailProcessor
from expenses.processors.imports import import_processors

# Get the processors of the transactions.
TRANSACTIONS_PROCESSORS_ = import_processors()


class EmailProcessorFactory:
    """
    This class is the factory of the email processors. It identifies the
    transaction type of the email and returns the corresponding processor.
    """

    @staticmethod
    def _identify_transaction_type(email_str: str) -> str:
        """
        This function identifies the transaction type of the email. It checks
        if the email contains a valid transaction type.

        Returns
        -------
        str
            The transaction type.
        """
        str_message_lower = email_str.lower()

        for transaction_type in TRANSACTION_TYPES_NAMES_:
            # Check if the transaction type is in the message.
            if transaction_type.lower() in str_message_lower:
                # If the transaction type is in the mapping, return the
                # mapped transaction type.
                if transaction_type in TRANSACTION_TYPES_MAPPING_:
                    return TRANSACTION_TYPES_MAPPING_[transaction_type]

                return transaction_type

    def get_processor(self, email: TransactionEmail) -> EmailProcessor:
        """
        This function returns the processor of the email.

        Returns
        -------
        BaseEmailProcessor
            The email processor.
        """
        transaction_type = self._identify_transaction_type(email.str_message)

        if transaction_type in TRANSACTIONS_PROCESSORS_:
            return TRANSACTIONS_PROCESSORS_[transaction_type](email)
        else:
            raise ValueError(
                f"The transaction type {transaction_type} is not supported"
            )
