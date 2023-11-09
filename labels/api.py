from fastapi import FastAPI
import pandas as pd
from typing import Union, List
from labels.categories import get_merchant_category
from labels.schemas import Category
from labels.database import get_cursor
import pyodbc 


# Create the app
app = FastAPI(title="Labels API", version="0.1.0")

# Create the base endpoint
@app.get("/")
async def index():
    return {"message": "API for the labels merchants working"}


# Create the table in the server to store categories
@app.post("/database/create_table")
async def create_table():
    """
    Create the table in the server to store the categories
    """
    cursor = get_cursor()
    cursor.execute(
        """
        CREATE TABLE categories (
            id INT IDENTITY(1,1) PRIMARY KEY,
            merchant VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL
        )
        """
    )
    cursor.commit()
    return {'message': 'Table created successfully'}

# Save labeled categories
@app.post("/database/save_categories")
async def save_categories():
    """
    Save the labeled categories in the database
    """
    cursor = get_cursor(return_conn=False)
    df = pd.read_csv("labels/expenses_labeled_full.csv", sep=';')
    
    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO categories (merchant, category)
            VALUES (?, ?)
            """,
            row["merchant"],
            row["category"]
        )
        cursor.commit()

    return {'message': 'Data saved successfully'}


# Create the endpoint for the categories
@app.post("/get_category")
async def get_category(merchants: Union[str, List[str]]) -> List[Category]:
    """
    Obtain the category of a merchant.

    Parameters
    ----------
    merchants : Union[str, List[str]]
        The merchant name, or a list of merchant names

    Returns
    -------
    Category
        The category and the similarity score
    """
    if merchants is None:
        return [Category(merchant=None, category=None, similarity=None)]

    categories_ = get_merchant_category(merchants)
    return [
        Category(
            merchant=merchant,
            category=result_category["category"],
            similarity=result_category["similarity"],
        )
        for merchant, result_category in zip(merchants, categories_)
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("labels.api:app", host="0.0.0.0", port=5000, reload=True)
