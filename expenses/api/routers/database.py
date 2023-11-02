import os
from typing import Literal, Tuple

import pyodbc
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from expenses.api.schemas import AddTransactionInfo
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
    except Exception:
        raise HTTPException(status_code=500, detail="Insertion failed.")

    return "Operation completed successfully."


@router.get("/test_connection", dependencies=[Depends(check_access_token)])
def test_connection() -> str:
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
        return f"Connection successful. This is the first row: {str(rows)}"
    except Exception:
        raise HTTPException(status_code=500, detail="Connection failed.")


@router.post("/populate_table/", dependencies=[Depends(check_access_token)])
def populate_table(
    timeframe: Literal[
        "daily", "weekly", "partial_weekly", "monthly", "from_origin"
    ]
) -> str:
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
            print(email, transactions)

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
        return "Operation completed successfully."
    except Exception:
        raise HTTPException(status_code=500, detail="Connection failed.")


@router.post("/add_transaction", dependencies=[Depends(check_access_token)])
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
        return "Operation completed successfully."
    except Exception:
        raise HTTPException(status_code=500, detail="Connection failed.")
