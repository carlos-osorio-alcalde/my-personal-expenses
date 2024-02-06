import re
from abc import ABC, abstractmethod
from typing import Dict, List, Union

from expenses.constants import (
    TRANSACTION_MESSAGES_TYPES_,
    TRANSACTION_TYPES_NAMES_,
)
from expenses.core.transaction_email import TransactionEmail
from expenses.processors.schemas import TransactionInfo


class EmailProcessor(ABC):
    """
    Abstract class to define the email processor.

    These are the attributes:
        - email: The email object.
        - transaction_email_text: The string email.
        - transaction_type: The transaction type.
        - pattern: The regex pattern to extract the transaction information.
    """

    def __init__(self, email: TransactionEmail):
        self.email = email
        self.transaction_email_text: str = self.email.str_message
        self.transaction_type: str = None
        self._is_income: bool = None
        self.pattern: Union[str, List] = self._set_pattern()

    def __str__(self):
        return f"{self.__class__.__name__}"

    @abstractmethod
    def _set_pattern(self) -> Union[str, List]:
        """
        This abstract method sets the regex pattern to extract the
        transaction information.
        This method must be implemented in the child classes.

        Returns
        -------
        Union[str, List]
            The regex pattern or the possible regex patterns.
        """
        ...

    @staticmethod
    def _has_valid_messages(messages: List[str], email_text: str) -> bool:
        """
        This static method checks if the email contains some of the messages
        in the list.

        Parameters
        ----------
        messages : List[str]
            The list of messages to check.
        email_text : str
            The email text.

        Returns
        -------
        bool
            True if the email contains some of the messages, False otherwise.
        """
        return any(
            (message in email_text)
            or (message.lower() in email_text.lower())
            for message in messages
        )

    def _is_valid_email(self) -> bool:
        """
        This function checks if the email is valid. For that, it must
        contain the following:
            1. The email must be from Bancolombia.
            2. The email must contain the transaction message.
            3. The email must contain the transaction date.
            4. The email must contain the transaction amount.

        Returns
        -------
        bool
            True if the email is valid, False otherwise.
        """
        # Check if the string email contains some of the messages types
        has_valid_message_type = self._has_valid_messages(
            TRANSACTION_MESSAGES_TYPES_, self.transaction_email_text
        )

        # Check if the string email contains some of the transaction types
        has_valid_transaction_type = self._has_valid_messages(
            TRANSACTION_TYPES_NAMES_, self.transaction_email_text
        )

        # Check if the string email contains an amount with "$"
        has_valid_amount = "$" in self.transaction_email_text

        # Return True if all conditions are met, otherwise False
        return (
            has_valid_message_type
            and has_valid_transaction_type
            and has_valid_amount
        )

    @staticmethod
    def _convert_amount_to_float(value_str: str) -> float:
        """
        This static method converts a string amount to float.
        There are several possible formats for the amount:
            1. 57,000.00
            2. 57.000,00
            3. 57,000
            4. 57.000

        Parameters
        ----------
        value_str : str
            The string amount.

        Returns
        -------
        float
            The float amount.
        """
        # Delete the "$" symbol
        value_str = value_str.replace("$", "")

        # Check if the comma or the dot appears first
        if "," in value_str and "." in value_str:
            if value_str.index(",") < value_str.index("."):
                value_str = value_str.split(".")[0]
            else:
                value_str = value_str.split(",")[0]

        # For the values that only have a comma or a dot, check if the
        # number of values that are at the right of the comma are 2.
        # If that is the case, assume that the value is in dollars.
        # Otherwise, assume that the value is in COP.
        if "," in value_str:
            if len(value_str.split(",")[1]) == 2:
                value_str = value_str.replace(",", ".")
                return float(value_str) * 4000

        value_str = value_str.replace(",", "").replace(".", "")
        return float(value_str)

    def _get_match(self) -> re.Match:
        """
        This function returns the match object of the transaction type.

        Returns
        -------
        re.Match
            The match object.
        """
        if isinstance(self.pattern, list):
            for pattern in self.pattern:
                match = re.search(pattern, self.transaction_email_text)
                if match:
                    return match
        else:
            return re.search(self.pattern, self.transaction_email_text)

    def _get_transaction_values(self) -> Dict:
        """
        This function returns the transaction values.

        Returns
        -------
        Dict
            The transaction values in a dictionary.
        """
        if self._is_valid_email():
            # Get the match object
            match = self._get_match()

            # Obtain the elements of the match object
            purchase_amount = (
                match.group("purchase_amount") if match else "$0.0"
            )
            merchant = match.group("merchant") if match else "unknown"
            paynment_method = (
                match.group("payment_method") if match else "unknown"
            )
            log_email_string = None
        else:
            # If the email is not valid, set the default values and log the
            # email.
            purchase_amount = "$0.0"
            merchant = "unknown"
            paynment_method = "unknown"
            log_email_string = self.transaction_email_text

        return {
            "transaction_type": self.transaction_type,
            "amount": self._convert_amount_to_float(purchase_amount)
            if self._is_income
            else -self._convert_amount_to_float(purchase_amount),
            "merchant": merchant,
            "datetime": self.email.date_message,
            "paynment_method": paynment_method,
            "email_log": log_email_string,
        }

    def process(self) -> TransactionInfo:
        """
        This function processes the information of the email. It extracts the
        transaction type, the amount and the merchant.

        Returns
        -------
        TransactionInfo
            The transaction info schema.
        """
        return TransactionInfo(**self._get_transaction_values())
