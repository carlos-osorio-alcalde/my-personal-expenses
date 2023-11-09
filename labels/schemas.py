from pydantic import BaseModel


# Model for the response of the categories
class Category(BaseModel):
    """
    This class represents the category of a merchant.
    """

    merchant: str
    category: str
    similarity: float
