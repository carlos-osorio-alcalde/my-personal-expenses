import os

import pandas as pd
import plotly.express as px

from dashboard.expenses import MyExpenses
from dashboard.styles import Styles


def pie_chart_plot(df: pd.DataFrame) -> px.line:
    """
    This function creates the pie chart plot

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame of expenses

    Returns
    -------
    px.line
        The pie chart plot
    """
    figure = px.pie(
        df,
        values="amount",
        names="category",
        title="Expenses by category or transaction type",
        template="plotly_white",
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )

    # Update the layout
    figure.update_layout(
        font=dict(size=18),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    return figure


if __name__ == "__main__":
    # Load your data from the backend (assuming a CSV file)
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    df_expenses = expenses.get_labeled_expenses(return_amount=True)

    # Create the time series plot
    pie_chart_plot(df_expenses)
