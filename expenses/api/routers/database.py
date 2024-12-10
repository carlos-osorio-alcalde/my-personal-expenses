import os
from typing import Literal, Tuple, List
import datetime

import pyodbc
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from expenses.api.schemas import (
    AddTransactionInfo,
    LabeledTransactionInfoFull,
)
from expenses.api.security import check_access_token
from expenses.api.utils import (
    get_cursor,
    get_date_from_search,
    get_query_to_insert_values,
    get_transactions,
)

# Emails to obtain the transactions from
EMAILS_FROM_ = [
    "alertasynotificaciones@notificacionesbancolombia.com",
    "alertasynotificaciones@bancolombia.com.co",
]

router = APIRouter(prefix="/database")

# Check if the file exists
if os.path.exists("expenses/.env"):
    load_dotenv(dotenv_path="expenses/.env")


# Function to insert the data into the database
def insert_data_into_database(
    cursor: pyodbc.Cursor, transaction: Tuple
) -> str:
    """
    This function inserts the data into the database.

    Parameters
    ----------
    cursor : pyodbc.Cursor
        The cursor to the database.
    transaction : Tuple
        The transaction to insert.
    """
    try:
        cursor.execute(
            get_query_to_insert_values(), transaction + transaction[:-1]
        )
        cursor.commit()
        return JSONResponse(status_code=200, content={"message": "Success."})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Insertion failed.")


@router.get("/health", dependencies=[Depends(check_access_token)])
def test_connection():
    """
    This function tests the connection to the database.

    Returns
    -------
    str
        A message indicating the status of the connection.
    """
    try:
        # Establish the connection
        cursor = get_cursor()
        # Obtain the rows
        cursor.execute("SELECT TOP 1 * FROM transactions")
        rows = cursor.fetchall()
        cursor.close()
        return JSONResponse(
            status_code=200, content={"message": "Connection sucessful"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Connection failed. Details: " + str(e)
        )


@router.post(
    "/", dependencies=[Depends(check_access_token)], responses={500: {}}
)
def populate_table(
    timeframe: Literal[
        "daily", "weekly", "partial_weekly", "monthly", "from_origin"
    ]
):
    """
    This function populates the transactions table.

    Parameters
    ----------
    timeframe : Literal["daily", "weekly", "partial_weekly",
                        "monthly", "from_origin"]
        The timeframe to obtain the expenses from.

    Returns
    -------
    str
        A message indicating the status of the connection.
    """
    # Check if the timeframe is valid
    if timeframe not in [
        "daily",
        "weekly",
        "partial_weekly",
        "monthly",
        "from_origin",
    ]:
        raise HTTPException(
            status_code=400,
            detail="The timeframe must be daily, weekly, partial_weekly or "
            "monthly",
        )

    try:
        # Get the date to search
        date_to_search = get_date_from_search(timeframe)

        # Establish the connection
        cursor = get_cursor()

        for email in EMAILS_FROM_:
            # Process the transactions
            transactions = get_transactions(
                email_from=email, date_to_search=date_to_search
            )
            if len(transactions) == 0:
                return JSONResponse(
                    status_code=204,
                    content={"message": "No transactions found."},
                )

            for transaction in transactions:
                insert_data_into_database(
                    cursor,
                    (
                        transaction.transaction_type,
                        transaction.amount,
                        transaction.merchant,
                        transaction.datetime.replace(tzinfo=None),
                        transaction.paynment_method,
                        transaction.email_log,
                    ),
                )

        # Close the connection
        cursor.close()
        return JSONResponse(
            status_code=200,
            content={"message": "Operation completed successfully."},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="The process failed.")


@router.post(
    "/individual-transaction", dependencies=[Depends(check_access_token)]
)
async def add_transaction(transaction: AddTransactionInfo) -> str:
    """
    This function adds a transaction to the database.

    Parameters
    ----------
    transaction : AddTransactionInfo
        The transaction to add.

    Returns
    -------
    str
        A message indicating the status of the connection.
    """
    try:
        # Establish the connection
        cursor = get_cursor()

        if transaction.transaction_type != "Compra":
            raise HTTPException(
                status_code=501,
                detail="Right now, only purchases are supported.",
            )

        # Insert the data into the database
        insert_data_into_database(
            cursor,
            (
                transaction.transaction_type,
                transaction.amount,
                transaction.merchant,
                transaction.datetime.replace(tzinfo=None),
                transaction.paynment_method,
                transaction.email_log,
            ),
        )
        # Close the connection
        cursor.close()
        return JSONResponse(
            status_code=200,
            content={"message": "Operation completed successfully."},
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Connection failed.")


@router.get(
    "/unlabeled-transactions",
    dependencies=[Depends(check_access_token)],
)
async def are_there_transactions_without_label() -> bool:
    """
    This function checks if there are transactions without labels.

    Returns
    -------
    bool
        A message indicating the status of the connection.
        If true, there are transactions without labels.
    """
    try:
        # Establish the connection
        cursor = get_cursor()

        # Obtain the rows
        cursor.execute(
            """
            SELECT TOP 10 
                    t.merchant,
                    t.datetime,
                    g.category
            FROM [dbo].[transactions] AS t
            LEFT JOIN [dbo].[categories_trx] AS g
            ON (CAST(t.datetime AS DATETIME) = CAST(g.datetime AS DATETIME) 
                AND CAST(t.merchant AS VARCHAR) = CAST(g.merchant AS VARCHAR))
            WHERE transaction_type = 'Compra' AND g.category IS NULL
            ORDER BY t.datetime DESC;
            """
        )
        rows = cursor.fetchall()
        cursor.close()

        return JSONResponse(
            status_code=200, content={"message": len(rows) > 0}
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Connection failed.")


@router.get(
    "/labeled-transactions",
    dependencies=[Depends(check_access_token)],
)
async def get_transactions_with_labels(
    start_date: datetime.date, end_date: datetime.date
) -> List[LabeledTransactionInfoFull]:
    """
    This function gets the transactions with labels.

    Parameters
    ----------
    start_date : datetime.date
        The start date to search.
    end_date : datetime.date
        The end date to search.

    Returns
    -------
    list
        A list with the transactions with labels.
    """
    # Convert dates to format YYYY-MM-DD
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    try:
        # Establish the connection
        cursor = get_cursor()

        # Obtain the rows
        cursor.execute(
            f"""
            SELECT 
                    t.transaction_type,
                    t.amount,
                    t.merchant,
                    t.datetime,
                    t.payment_method,
                    t.email_log_id,
                    g.category,
                    g.similarity
            FROM [dbo].[transactions] AS t
            LEFT JOIN [dbo].[categories_trx] AS g
            ON (CAST(t.datetime AS DATETIME) = CAST(g.datetime AS DATETIME) 
                AND CAST(t.merchant AS VARCHAR) = CAST(g.merchant AS VARCHAR))
            WHERE CAST(t.datetime AS DATE) BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY t.datetime DESC;
            """
        )
        rows = cursor.fetchall()
        cursor.close()

        # Get the transactions with the correct type
        if len(rows) > 0:
            transactions = [
                LabeledTransactionInfoFull(
                    transaction_type=str(transaction[0]),
                    amount=transaction[1],
                    merchant=str(transaction[2]),
                    datetime=transaction[3],
                    paynment_method=str(transaction[4]),
                    email_log=transaction[5],
                    category=str(transaction[6]),
                )
                for transaction in rows
            ]
        else:
            transactions = []

        return transactions
    except Exception:
        raise HTTPException(status_code=500, detail="Connection failed.")
