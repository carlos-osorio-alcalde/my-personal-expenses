import os
import pickle
from typing import List, Union

import numpy as np
import pyodbc
from dotenv import load_dotenv
from fastapi import FastAPI

from labels.categories import get_merchant_category, update_embeddings
from labels.database import get_cursor
from labels.schemas import LabeledTransaction, TransactionInfo

# Load environment variables
load_dotenv()

# Create the app
app = FastAPI(title="Labels API", version="0.1.0")

# Update the embeddings after the app is created
update_embeddings()

# Create the base endpoint
@app.get("/")
async def index():
    return {"message": "API for the labels merchants working"}


# Endpoint to refresh the embeddings
@app.get("/refresh_embeddings")
async def refresh_embeddings() -> dict:
    """
    Refresh the embeddings of the merchants
    """
    # Update the embeddings
    update_embeddings()
    return {"message": "Embeddings updated successfully"}


# Save labeled categories into the table
@app.post("/database/save_categories")
async def save_categories(
    labeled_transactions: Union[LabeledTransaction, List[LabeledTransaction]]
) -> dict:
    """
    Save the categories into the tables

    Parameters
    ----------
    transactions : Union[LabeledTransaction, List[LabeledTransaction]]
        The labeled transactions
    """
    if isinstance(labeled_transactions, LabeledTransaction):
        labeled_transactions = [labeled_transactions]

    cursor = get_cursor(return_conn=False)

    for transaction in labeled_transactions:
        cursor.execute(
            """
            INSERT INTO categories_trx (merchant, datetime, category, similarity)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM categories_trx
                WHERE
                    merchant = ? AND
                    datetime = ? AND
                    category = ?
            )
            """,
            transaction.merchant,
            transaction.datetime,
            transaction.category,
            transaction.similarity,
            transaction.merchant,
            transaction.datetime,
            transaction.category,
        )
        cursor.commit()

    return {"message": "Data saved successfully"}


# Create the endpoint for the categories
@app.post("/get_category", response_model=List[LabeledTransaction])
async def get_category(
    transactions: List[TransactionInfo],
) -> List[LabeledTransaction]:
    """
    Obtain the category of a merchant.

    Parameters
    ----------
    merchants : List[TransactionInfo]
        The transaction information

    Returns
    -------
    Category
        The category and the similarity score
    """
    merchants = [transaction.merchant for transaction in transactions]
    categories_ = get_merchant_category(merchants)
    return [
        LabeledTransaction(
            merchant=transaction.merchant,
            datetime=transaction.datetime,
            category=result_category["category"],
            similarity=result_category["similarity"],
        )
        for transaction, result_category in zip(transactions, categories_)
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("labels.api:app", host="0.0.0.0", port=5000, reload=True)
