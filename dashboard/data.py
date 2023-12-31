import datetime
import os
from typing import Tuple

import pandas as pd

from dashboard.expenses import MyExpenses


def fetch_data(
    expenses: MyExpenses,
) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    This function returns the data to be used in the dashboard

    Parameters:
    ----------
    expenses : MyExpenses
        The expenses object

    Returns:
    -------
    tuple(pd.DataFrame, pd.DataFrame, str)
        The expenses, labeled expenses, and the last updated date
    """
    # Load the data of the expenses
    df_expenses, df_labeled_expenses = expenses.get_expenses_tables(
        return_amount=True
    )
    updated_at = "(Last updated at: {})".format(
        expenses.last_time_update().strftime("%Y-%m-%d %H:%M:%S")
    )

    return df_expenses, df_labeled_expenses, updated_at


if __name__ == "__main__":
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    df_expenses, df_labeled_expenses, updated_at = fetch_data(expenses)
