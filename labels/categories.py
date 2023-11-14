import os
import pickle
from collections import Counter
from typing import Dict, List, Union

import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

from labels.database import get_cursor
from labels.constants import (
    CATEGORIES_MERCHANTS_FILE_NAME,
    CATEGORIES_MERCHANTS_FILE_NAME_BACKUP,
    EMBEDDINGS_FILE_NAME,
    EMBEDDINGS_FILE_NAME_BACKUP,
    MAPPING_CATEGORIES_NAMES,
)

# Load environment variables
load_dotenv()

# Create the OpenAI object
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def update_embeddings() -> None:
    """
    This function updates the embeddings of the merchants
    from the category table
    """
    cursor = get_cursor(return_conn=False)
    cursor.execute(
        """
        SELECT DISTINCT
                merchant,
                category
        FROM [dbo].[categories_trx]
        WHERE category IS NOT NULL
        """
    )
    result = cursor.fetchall()

    # Create the dataframe
    df = pd.DataFrame(
        data=[list(r) for r in result],
        columns=[desc[0] for desc in cursor.description],
    )
    cursor.close()

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

    # Save the categories codes as a pickle file
    with open(MAPPING_CATEGORIES_NAMES, "wb") as f:
        pickle.dump({v: k for k, v in categories_codes.items()}, f)

    return


def get_merchant_category(
    merchant: Union[str, List[str]], top: int = 3
) -> List[Dict[str, float]]:
    """
    This function computes the similarity between the merchant
    and the embeddings and returns the most similar category.

    If the similarity is greater than 0.9, then the category is returned.
    If the similarity is less than 0.9, it is possible to manually label the
    merchant.

    Parameters
    ----------
    merchant : Union[str, List[str]]
        The merchant name, or a list of merchant names

    top : int
        The number of most similar words to consider before returning the category

    Returns
    -------
    List[Dict[str, float]]
        The most likely category and the similarity score
    """
    # Load the mapping categories names
    with open(MAPPING_CATEGORIES_NAMES, "rb") as f:
        CATEGORIES_CODES = pickle.load(f)

    # Load the embeddings
    embeddings_db = np.load(EMBEDDINGS_FILE_NAME)

    # Load the categories of the merchants from the pickle file
    with open(CATEGORIES_MERCHANTS_FILE_NAME, "rb") as f:
        categories_db = pickle.load(f)

    # Get the embedding for a single word
    embeddings_objects = openai_client.embeddings.create(
        input=merchant, model="text-embedding-ada-002"
    ).data
    embeddings = [emb.embedding for emb in embeddings_objects]

    # Compute the similarity between the word and the embeddings using cosine similarity
    similarities_ = cosine_similarity(np.array(embeddings), embeddings_db)

    # Get an empty list to populate with the categories
    final_categories = []

    for similarity in similarities_:
        # Get the index of 5 most similar words
        indices, similarities = (
            np.argsort(np.array(similarity))[::-1][0:top],
            np.sort(np.array(similarity))[::-1][0:top],
        )

        # Check if the first result has more than 0.9 similarity.
        # If so, add the result and continue to the next word
        if similarities[0] > 0.9:
            final_categories.append(
                {
                    "category": CATEGORIES_CODES[categories_db[indices[0]]],
                    "similarity": similarities[0],
                }
            )
            continue

        # Get the categories of the words
        categories = [CATEGORIES_CODES[categories_db[f]] for f in indices]

        # Get the mode of categories list
        common_category = Counter(categories).most_common(1)[0][0]
        final_categories.append(
            {
                "category": common_category,
                "similarity": np.mean(similarities),
            }
        )

    return final_categories


if __name__ == "__main__":
    text = ["RESTAURANTE EL PARA", "EDS PRIMAX", "RAPPI SUPERMERCADOS"]
    print(get_merchant_category(text))
