import datetime
import os
from typing import Dict, List, Union

import numpy as np
import pyodbc
from dotenv import load_dotenv

from expenses.api.schemas import LabeledTransactionInfo, SummaryMerchant
from expenses.processors.schemas import TransactionInfo

# Check if the file exists
if os.path.exists("expenses/.env"):
    load_dotenv(dotenv_path="expenses/.env")


def get_cursor(return_conn: bool = False) -> Union[pyodbc.Cursor, None]:
    """
    This function creates a connection to the database.

    Parameters
    ----------
    return_conn : bool, optional
        If True, the function returns the connection to the database,
        by default False.
    Returns
    -------
    pyodbc.Connection
        The connection to the database.
    """
    try:
        # Establish the connection
        conn = pyodbc.connect(
            f"""DRIVER=ODBC Driver 18 for SQL Server;\
            SERVER={os.getenv("SERVER")};\
            DATABASE={os.getenv("DATABASE")};\
            UID={os.getenv("USERNAME")};\
            PWD={os.getenv("PASSWORD")}"""
        )
        cursor = conn.cursor()
        return cursor if not return_conn else (conn, cursor)
    except Exception as e:
        print(e)
        return None


def get_transactions_from_database(
    date_from: datetime.datetime,
) -> List[TransactionInfo]:
    """
    Searches for the transactions in the database given a date.

    Parameters
    ----------
    date_from : datetime.datetime
        The date to search.

    Returns
    -------
    List[TransactionInfo]
        The list of transactions.
    """
    try:
        cursor = get_cursor()

        # Get the transactions
        cursor.execute(
            """
            SELECT
                transaction_type,
                amount,
                merchant,
                datetime,
                payment_method,
                email_log_id
            FROM transactions
            WHERE datetime >= ?
            """,
            date_from.date(),
        )
        transactions_from_db = cursor.fetchall()

        # Close the connection
        cursor.close()

        # Get the transactions with the correct type
        if len(transactions_from_db) > 0:
            transactions = [
                TransactionInfo(
                    transaction_type=str(transaction[0]),
                    amount=transaction[1],
                    merchant=str(transaction[2]),
                    datetime=transaction[3],
                    paynment_method=str(transaction[4]),
                    email_log=transaction[5],
                )
                for transaction in transactions_from_db
            ]
        else:
            transactions = []

        return transactions
    except Exception:
        return []


def get_merchants_values(
    date_from: datetime.datetime,
) -> List[SummaryMerchant]:
    """
    This function returns the merchants and the values of the day.

    Parameters
    ----------
    date_from : datetime.datetime
        The date to search.
    """
    try:
        cursor = get_cursor()

        # Get the transactions
        cursor.execute(
            """
            SELECT
                merchant,
                SUM(amount) AS amount,
                COUNT(*) AS count
            FROM transactions
            WHERE datetime >= ? AND transaction_type = 'Compra'
            AND merchant != ''
            GROUP BY merchant
            ORDER BY amount DESC
            """,
            date_from,
        )

        # Get the merchants
        merchants_inform = cursor.fetchall()

        # Close the connection
        cursor.close()

        # Get the transactions with the correct type
        if len(merchants_inform) > 0:
            transactions = [
                SummaryMerchant(
                    merchant=str(merchant[0]),
                    amount=merchant[1],
                    count=merchant[2],
                )
                for merchant in merchants_inform
            ]
        else:
            transactions = []

        return transactions
    except Exception:
        return []


def get_query_to_insert_values() -> str:
    """
    This function returns the query to insert the values in the database.

    Returns
    -------
    str
        The query to insert the values in the database.
    """
    return """
        INSERT INTO transactions
        (
            transaction_type,
            amount,
            merchant,
            datetime,
            payment_method,
            email_log_id
        )
        SELECT ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM transactions
            WHERE
                transaction_type = ? AND
                amount = ? AND
                merchant = ? AND
                datetime = ? AND
                payment_method = ?
        )
        """


def get_summary_a_day_like_today(weekday: int) -> Dict:
    """
    This function returns the summary of all the transactions of a day like
    today.

    Parameters
    ----------
    weekday : int
        The weekday to search.

    Returns
    -------
    dict
        The summary of all the transactions of a day like today.
    """
    try:
        cursor = get_cursor()
        # Get the transactions
        cursor.execute(
            """
                SET DATEFIRST 1;
                SELECT CAST(datetime AS DATE),
                        SUM(amount) AS amount_sum,
                        COUNT(*) AS total_count
                FROM transactions
                WHERE transaction_type = 'Compra' AND
                        DATEPART(weekday, datetime) = ?
                GROUP BY CAST(datetime AS DATE)
            """,
            weekday,
        )

        # Get the summary
        transactions = cursor.fetchall()

        # Close the connection
        cursor.close()
    except Exception:
        return {}

    # Get the summary with the correct type
    if len(transactions) > 0:
        # Compute the values
        summary = {
            "mean_number_of_purchases": np.mean(
                [transaction[2] for transaction in transactions]
            ),
            "median_amount_of_purchases": np.median(
                [transaction[1] for transaction in transactions]
            ),
        }
    else:
        summary = {}

    return summary


def get_transactions_with_labels(
    date_from: datetime.datetime,
) -> List[LabeledTransactionInfo]:
    """
    This function returns the transactions with the labels.

    Parameters
    ----------
    date_from : datetime.datetime
        The date to search.

    Returns
    -------
    List[TransactionInfo]
        The transactions with the labels.
    """
    try:
        cursor = get_cursor()

        # Get the transactions
        cursor.execute(
            """
            SELECT t.merchant, t.datetime, g.category, g.similarity
            FROM [dbo].[transactions] AS t
            LEFT JOIN [dbo].[categories_trx] AS g
            ON (t.merchant = g.merchant AND t.datetime = g.datetime)
            WHERE t.transaction_type = 'Compra' AND t.datetime >= ? 
            AND g.category IS NOT NULL
            """,
            date_from.date(),
        )
        transactions_from_db = cursor.fetchall()

        # Close the connection
        cursor.close()

        # Get the transactions with the correct type
        if len(transactions_from_db) > 0:
            transactions = [
                LabeledTransactionInfo(
                    merchant=str(transaction[0]),
                    datetime=transaction[1],
                    category=str(transaction[2]),
                    similarity=transaction[3],
                )
                for transaction in transactions_from_db
            ]
        else:
            transactions = []

        return transactions
    except Exception:
        return []
