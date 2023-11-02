from datetime import datetime
from email.message import Message

import pytz
from bs4 import BeautifulSoup


class TransactionEmail:
    """
    This class is a wrapper of the email object from the email library.
    Is intended to be used to extract the transaction message from the email.
    """

    def __init__(self, email: Message):
        self.body_email = email
        self.date_message: datetime = self.get_date_message()
        self.str_message: str = self.get_str_message()

    def __str__(self) -> str:
        """
        This function returns the transaction message.

        Returns
        -------
        str
            The transaction message.
        """
        if self.str_message:
            return self.str_message
        else:
            return "No transaction message found."

    def get_str_message(self) -> str:
        """
        This property obtains the transaction message from the email.

        The logic behind this is the following:
            1. The transaction message is the first line that starts with
                "Bancolombia" in the entire mail.

        Returns
        -------
        str
            The transaction message.
        """
        for part in self.body_email.walk():
            if part.get_content_type() == "text/html":
                body = part.get_payload(decode=True)
                soup = BeautifulSoup(body, "html.parser")
                text_message = soup.get_text(separator=" ")

                for val in text_message.split("\xa0"):
                    if val.strip().startswith(
                        "Bancolombia"
                    ) or val.strip().startswith("Realizaste"):
                        self._str_message = val.strip()
                        break

        return self._str_message

    def get_date_message(self) -> datetime:
        """
        This property obtains the date when the email was received.
        Notice that this date is obtained from the email itself, not from the
        transaction message, so it could be differences.

        Returns
        -------
        datetime
            The date when the email was received.
        """
        # Get the date of the email.
        # Format: "Tue, 25 Jul 2023 01:07:29 +0000 (UTC)"
        datetime_email = self.body_email["Date"]

        # Convert to datetime object
        try:
            datetime_email = datetime.strptime(
                datetime_email, "%a, %d %b %Y %H:%M:%S %z (%Z)"
            )
        except ValueError:
            datetime_email = datetime.strptime(
                datetime_email.replace(" (EDT)", ""),
                "%a, %d %b %Y %H:%M:%S %z",
            )

        # The date is given in the UTC. We need UTC-5
        self._date = datetime_email.astimezone(
            pytz.timezone("America/Bogota")
        )
        return self._date
