import os
from typing import Literal

import pandas as pd
import requests
from dotenv import load_dotenv

# Set pandas options
pd.options.mode.chained_assignment = None

# Load environment variables
load_dotenv()


class MyExpenses:
    """
    This class is used to get the expenses from the API and cache them
    """

    # Path to the cached expenses
    FOLDER_CACHED_EXPENSES = "dashboard/cached_expenses"

    FILE_EXPENSES = os.path.join(FOLDER_CACHED_EXPENSES, "df_expenses.csv")
    FILE_LABELED_EXPENSES = os.path.join(
        FOLDER_CACHED_EXPENSES, "df_labeled_expenses.csv"
    )
    FILE_LAST_UPDATE = os.path.join(
        FOLDER_CACHED_EXPENSES, "last_update.txt"
    )

    # Time to wait before updating the expenses
    TIME_TO_WAIT = 1 * 60

    def __init__(self, token: str, check_av: bool = False):
        self._token = token
        self._availability = None
        if check_av:
            self._availability = self._is_api_available()

    def _is_api_available(self):
        """
        This method connects to the API and returns the token
        """
        url = "https://personal-expenses-api.orangecliff-ed60441b.eastus.azurecontainerapps.io/database/test_connection"  # noqa
        headers = {"Authorization": f"Bearer {self._token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return False

        return True

    def _modify_expenses_table(
        self, df_expenses: pd.DataFrame
    ) -> pd.DataFrame:
        """
        This function makes the minor changes in the df_expenses table.

        Parameters
        ----------
        df_expenses : pd.DataFrame
            The expenses table

        Returns
        -------
        pd.DataFrame
            The expenses table with made changes
        """
        df_expenses["datetime"] = pd.to_datetime(df_expenses["datetime"])

        # Change the sign of the amount
        df_expenses["amount"] = -1 * df_expenses["amount"]

        return df_expenses[df_expenses["merchant"] != "unknown"]

    def _get_expenses_from_cache(self) -> pd.DataFrame:
        """
        This method returns the expenses from the cache
        """
        # Get the expenses from the cache
        return pd.read_csv(MyExpenses.FILE_EXPENSES, sep=";")

    def _get_expenses_from_api(
        self,
        timeframe: Literal[
            "daily", "weekly", "partial_weekly", "monthly", "from_origin"
        ],
    ) -> pd.DataFrame:
        """
        This method returns all expenses from the API

        Parameters:
        ----------
        timeframe: Literal["daily", "weekly", "partial_weekly", "monthly", "from_origin"]
            The timeframe to get the expenses from
        """
        url = f"https://personal-expenses-api.orangecliff-ed60441b.eastus.azurecontainerapps.io/expenses/get_full_transactions/?timeframe={timeframe}"  # noqa
        headers = {"Authorization": f"Bearer {self._token}"}
        response = requests.get(url, headers=headers)

        # Get the response as a DataFrame
        if response.status_code != 200:
            return None

        return pd.DataFrame(response.json())

    def _modify_expenses_labeled_table(
        self,
        df_expenses: pd.DataFrame,
        df_labeled_expenses: pd.DataFrame,
        return_amount: bool = False,
    ) -> pd.DataFrame:
        """
        This function makes the minor changes in the df_labeled_expenses table.

        Parameters
        ----------
        df_labeled_expenses : pd.DataFrame
            The expenses table

        Returns
        -------
        pd.DataFrame
            The expenses table with made changes
        """
        df_labeled_expenses["datetime"] = pd.to_datetime(
            df_labeled_expenses["datetime"]
        )

        # If return_amount is True, get the full expenses and merge with the labeled expenses
        if return_amount:
            df_labeled_expenses = df_expenses.merge(
                df_labeled_expenses[["merchant", "datetime", "category"]],
                on=["datetime", "merchant"],
                how="left",
            )
            # Delete duplicates
            df_labeled_expenses.drop_duplicates(inplace=True)

        # If the category is null, add the value of transaction_type
        df_labeled_expenses["category"] = df_labeled_expenses.apply(
            lambda x: x["transaction_type"]
            if pd.isnull(x["category"])
            else x["category"],
            axis=1,
        )
        return df_labeled_expenses[
            df_labeled_expenses["category"] != "Recepcion Transferencia"
        ]

    def _get_labeled_expenses_from_cache(self) -> pd.DataFrame:
        """
        This method returns the labeled expenses

        Parameters:
        ----------
        return_amount: bool
            Whether to return the amount or not
        """
        # Get the labeled expenses from the cache
        return pd.read_csv(MyExpenses.FILE_LABELED_EXPENSES, sep=";")

    def _get_labeled_expenses_from_api(self) -> pd.DataFrame:
        """
        This method returns the labeled expenses

        Returns:
        -------
        pd.DataFrame
            The labeled expenses from the API

        """
        url = "https://personal-expenses-api.orangecliff-ed60441b.eastus.azurecontainerapps.io/expenses/get_transactions_with_labels/?timeframe=from_origin"  # noqa
        headers = {"Authorization": f"Bearer {self._token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None

        # Get the response as a DataFrame
        return pd.DataFrame(response.json())

    def last_time_update(self) -> pd.Timestamp:
        """
        This method returns the last update datetime of the expenses.
        For that, check the file "last_update.txt" in the folder cached_expenses
        """
        # If the file does not exist, return timestamp 0
        if not os.path.exists(MyExpenses.FILE_LAST_UPDATE):
            last_update_datetime = 0
        else:
            # Get the last update datetime
            with open(MyExpenses.FILE_LAST_UPDATE, "r") as f:
                last_update_datetime = f.read()

        return pd.Timestamp(last_update_datetime)

    def get_expenses_tables(
        self,
        timeframe: Literal[
            "daily", "weekly", "partial_weekly", "monthly", "from_origin"
        ] = "from_origin",
        return_amount: bool = True,
        return_from_cache: bool = False,
    ) -> (pd.DataFrame, pd.DataFrame):
        """
        This method returns all expenses from the API

        Parameters:
        ----------
        timeframe: Literal["daily", "weekly", "partial_weekly", "monthly", "from_origin"]
            The timeframe to get the expenses from
        """
        # Check if the last update timestamp is greater than 30 minutes
        if (
            (pd.Timestamp.now() - self.last_time_update()).total_seconds()
            > MyExpenses.TIME_TO_WAIT
            or not os.path.exists(MyExpenses.FILE_EXPENSES)
            or not os.path.exists(MyExpenses.FILE_LABELED_EXPENSES)
        ) and not return_from_cache:
            # Get the expenses from the API
            df_expenses = self._get_expenses_from_api(timeframe)
            df_expenses = self._modify_expenses_table(df_expenses)

            # Get the labeled expenses from the API
            df_labeled_expenses = self._get_labeled_expenses_from_api()
            df_labeled_expenses = self._modify_expenses_labeled_table(
                df_expenses, df_labeled_expenses, return_amount=return_amount
            )

            # Save the expenses and the labeled expenses in the cache
            df_expenses.to_csv(
                MyExpenses.FILE_EXPENSES, sep=";", index=False
            )
            df_labeled_expenses.to_csv(
                MyExpenses.FILE_LABELED_EXPENSES, sep=";", index=False
            )

            # Save the last update datetime
            with open(MyExpenses.FILE_LAST_UPDATE, "w") as f:
                f.write(str(pd.Timestamp.now()))
        else:
            # If the last update timestamp is less than 30 minutes, get from the cache
            df_expenses = self._get_expenses_from_cache()
            df_labeled_expenses = self._get_labeled_expenses_from_cache()

        return df_expenses, df_labeled_expenses

    def get_moving_average(
        self, df_expenses: pd.DataFrame, window: int = 30
    ) -> pd.DataFrame:
        """
        This method returns the moving average of the expenses

        Parameters:
        ----------
        df_expenses: pd.DataFrame
            The DataFrame of expenses
        """
        # Get the expenses that are purchases
        df_expenses_moving_average = df_expenses.copy()

        # Remove outliers. All the purchases in the quantile 0.99 are removed
        df_expenses_moving_average = df_expenses_moving_average[
            df_expenses_moving_average["amount"]
            <= df_expenses_moving_average["amount"].quantile(0.99)
        ]

        # Sort the DataFrame by datetime
        df_expenses_moving_average.sort_values(by="datetime", inplace=True)

        # Get the moving average of the expenses
        df_expenses_moving_average["amount_moving_average"] = (
            df_expenses_moving_average["amount"]
            .rolling(window=window, min_periods=1)
            .mean()
            .round(2)
        )

        return df_expenses_moving_average


if __name__ == "__main__":
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    df_expenses, df_labeled_expenses = expenses.get_expenses_tables()
