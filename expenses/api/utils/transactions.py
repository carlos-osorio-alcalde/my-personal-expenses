import datetime
import os
from collections import defaultdict
from typing import List

from expenses.api.schemas.expenses import (
    BaseTransactionInfo,
    SummaryTransactionInfo,
)
from expenses.core.client import GmailClient
from expenses.core.transaction_email import TransactionEmail
from expenses.processors.factory import EmailProcessorFactory
from expenses.processors.schemas import TransactionInfo


def get_transactions(
    email_from: str,
    date_to_search: datetime.datetime,
) -> List[TransactionInfo]:
    """
    This function obtains the transactions from the specified email address
    and returns the list of the information for all the transactions.

    Parameters
    ----------
    email_from : str
        The email address to obtain the transactions from.

    date_to_search : datetime.datetime
        The date to obtain the transactions from.

    Returns
    -------
    List[TransactionInfo]
        The list of the information for all the transactions.
    """
    gmail_client = GmailClient(os.getenv("EMAIL"))
    emails_list = gmail_client.obtain_emails(
        email_from,
        most_recents_first=True,
        limit=None,
        date_to_search=date_to_search,
    )
    
    if len(emails_list) > 0:
        print(email_from, TransactionEmail(emails_list[0]))

    transactions = []
    processor_factory = EmailProcessorFactory()
    for email in emails_list:
        try:
            transactions.append(
                processor_factory.get_processor(
                    TransactionEmail(email)
                ).process()
            )
        except ValueError:
            continue

    return transactions


def process_transactions_api_expenses(
    transactions: List[TransactionInfo],
) -> SummaryTransactionInfo:
    """
    This function processes the transactions and returns the summary of the
    transactions.

    Parameters
    ----------
    transactions : List[TransactionInfo]
        The list of the information for all the transactions.

    Returns
    -------
    SummaryTransactionInfo
        The summary of the transactions.
    """

    summary = SummaryTransactionInfo(
        purchases=BaseTransactionInfo(name="", amount=0, count=0),
        withdrawals=BaseTransactionInfo(name="", amount=0, count=0),
        transfer_reception=BaseTransactionInfo(name="", amount=0, count=0),
        transfer_qr=BaseTransactionInfo(name="", amount=0, count=0),
        payment=BaseTransactionInfo(name="", amount=0, count=0),
        transfer=BaseTransactionInfo(name="", amount=0, count=0),
    )

    transaction_summary = defaultdict(
        lambda: BaseTransactionInfo(name="", amount=0, count=0)
    )

    for transaction in transactions:
        transaction_summary[
            transaction.transaction_type
        ].name = transaction.transaction_type

        transaction_summary[
            transaction.transaction_type
        ].amount += transaction.amount

        transaction_summary[transaction.transaction_type].count += 1

    # Set the values of the summary
    summary.purchases = transaction_summary["Compra"]
    summary.withdrawals = transaction_summary["Retiro"]
    summary.transfer_reception = transaction_summary[
        "Recepcion Transferencia"
    ]
    summary.transfer_qr = transaction_summary["QR"]
    summary.payment = transaction_summary["Pago"]
    summary.transfer = transaction_summary["Transferencia"]

    return summary
