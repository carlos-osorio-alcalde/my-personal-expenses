import os

import pandas as pd
import plotly.express as px

from dashboard.expenses import MyExpenses
from dashboard.styles import Styles


def barplot_weekly(df: pd.DataFrame) -> px.bar:
    """
    This function creates a barplot that shows the weekly expenses

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame of expenses

    Returns
    -------
    px.bar
    """
    # Create the plot
    figure = px.bar(
        df,
        x=df["week"].map(lambda x: f"{str(x).split('-')[1]}"),
        y="amount",
        title="",
        template="plotly_white",
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )

    # Update the layout so that a bar for each week is shown
    figure.update_layout(
        font=dict(size=18),
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis=dict(tickmode="linear", tick0=0, dtick=5),
    )

    return figure


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # Load your data from the backend (assuming a CSV file)
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    df_expenses = expenses._get_expenses_from_api(timeframe="from_origin")

    df_weekly = expenses.get_weekly_expenses(df_expenses)

    figure = barplot_weekly(df_weekly)
    figure.show()
