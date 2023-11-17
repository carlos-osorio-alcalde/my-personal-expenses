import datetime
import os
from typing import Tuple

import pandas as pd

from dashboard.expenses import MyExpenses


def fetch_data() -> Tuple[MyExpenses, pd.DataFrame, pd.DataFrame, str]:
    """
    This function returns the data to be used in the dashboard

    Returns:
        Tuple[MyExpenses, pd.DataFrame, pd.DataFrame]: The first element is the dataframe
    """
    # Load the data of the expenses
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    df_expenses = expenses.get_expenses(timeframe="from_origin")
    df_labeled_expenses = expenses.get_labeled_expenses(return_amount=True)
    updated_at = "(Last updated at: {})".format(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return expenses, df_expenses, df_labeled_expenses, updated_at
