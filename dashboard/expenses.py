import requests
from typing import Literal
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class MyExpenses:
    def __init__(self, token):
        self.token = token
        if not self._is_api_available():
            raise ValueError("The API is not available")

    def _is_api_available(self):
        """
        This method connects to the API and returns the token
        """
        url = "https://personal-expenses-api.orangecliff-ed60441b.eastus.azurecontainerapps.io/database/test_connection"  # noqa
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return False

        return True

    def get_expenses(
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
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)

        # Get the response as a DataFrame
        df = pd.DataFrame(response.json())

        # Convert the datetime column to datetime
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Create a new column of the year-month
        df["year_month"] = df["datetime"].dt.strftime("%Y-%m")

        # Change the sign of the amount
        df["amount"] = -1 * df["amount"]

        return df[df["merchant"] != "unknown"]

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
        df_expenses_moving_average = df_expenses[
            df_expenses["transaction_type"] == "Compra"
        ].copy()

        # Change the sign of the amount
        df_expenses_moving_average["amount"] = (
            -1 * df_expenses_moving_average["amount"]
        )

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

        # Change the sign of the amount
        df_expenses_moving_average["amount"] = (
            -1 * df_expenses_moving_average["amount"]
        )

        return df_expenses_moving_average

    def get_labeled_expenses(
        self, return_amount: bool = False
    ) -> pd.DataFrame:
        """
        This method returns the labeled expenses

        Parameters:
        ----------
        return_amount: bool
            Whether to return the amount or not
        """
        url = "https://personal-expenses-api.orangecliff-ed60441b.eastus.azurecontainerapps.io/expenses/get_transactions_with_labels/?timeframe=from_origin"  # noqa
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)

        # Get the response as a DataFrame
        df = pd.DataFrame(response.json())
        df["datetime"] = pd.to_datetime(df["datetime"])

        # If return_amount is True, get the full expenses and merge with the labeled expenses
        if return_amount:
            df_expenses = self.get_expenses(timeframe="from_origin")
            df = df.merge(
                df_expenses[["merchant", "datetime", "amount"]],
                on=["datetime", "merchant"],
                how="left",
            )

        return df


if __name__ == "__main__":
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    print(expenses.get_labeled_expenses(return_amount=True))
