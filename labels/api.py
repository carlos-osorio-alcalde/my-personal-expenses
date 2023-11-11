import os
import pickle
from typing import List, Union

import numpy as np
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI

from labels.categories import get_merchant_category
from labels.constants import (
    CATEGORIES_MERCHANTS_FILE_NAME,
    CATEGORIES_MERCHANTS_FILE_NAME_BACKUP,
    EMBEDDINGS_FILE_NAME,
    EMBEDDINGS_FILE_NAME_BACKUP,
)
from labels.database import get_cursor
from labels.schemas import LabeledTransaction, TransactionInfo

# Load environment variables
load_dotenv()

# Create the app
app = FastAPI(title="Labels API", version="0.1.0")

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
    cursor = get_cursor(return_conn=False)
    cursor.execute(
        """
        SELECT DISTINCT
                merchant,
                category
        FROM categories_trx
        WHERE category IS NOT NULL
        """
    )
    result = cursor.fetchall()
    cursor.commit()

    # Create the dataframe
    df = pd.DataFrame(result, columns=["merchant", "category"])

    # Create the embeddings
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Compute the embeddings
    embeddings = openai_client.embeddings.create(
        input=df["merchant"].tolist(), model="text-embedding-ada-002"
    ).data

    # Extract the data as a numpy array
    embeddings = np.array([emb.embedding for emb in embeddings])

    # Codify the categories from string to int
    categories_codes = {
        category: i for i, category in enumerate(df["category"].unique())
    }
    categories_merchants = dict(
        zip(df.index, df["category"].map(categories_codes))
    )

    # Before saving the data, create a backup of the old data
    if os.path.exists(CATEGORIES_MERCHANTS_FILE_NAME):
        os.rename(
            CATEGORIES_MERCHANTS_FILE_NAME,
            CATEGORIES_MERCHANTS_FILE_NAME_BACKUP,
        )
    if os.path.exists(EMBEDDINGS_FILE_NAME):
        os.rename(EMBEDDINGS_FILE_NAME, EMBEDDINGS_FILE_NAME_BACKUP)

    # Save the categories_merchants as a pickle file
    with open(CATEGORIES_MERCHANTS_FILE_NAME, "wb") as f:
        pickle.dump(categories_merchants, f)

    # Save the embeddings as a npy file
    np.save(EMBEDDINGS_FILE_NAME, embeddings)

    return {"message": "Embeddings refreshed successfully"}


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
            VALUES (?, ?, ?, ?)
            """,
            transaction.merchant,
            transaction.datetime,
            transaction.category,
            transaction.similarity,
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
