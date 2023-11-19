import datetime

import pandas as pd
import plotly.express as px

from dashboard.expenses import MyExpenses
from dashboard.plots import pie_chart_plot, time_series_plot


def update_metrics(
    expenses: MyExpenses,
    df_expenses: pd.DataFrame,
    df_labeled_expenses: pd.DataFrame,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    transaction_type: list,
    window: int,
) -> (pd.DataFrame, px.bar, px.pie, str, str):
    """
    This function updates the table and the bar plot

    Parameters
    ----------
    start_date : datetime.datetime
        The start date of the range
    end_date : datetime.datetime
        The end date of the range
    transaction_type : list
        The transaction type
    window : int
        The window size for the moving average

    Returns
    -------
    tuple(pd.DataFrame, px.bar, px.pie)
        The table, bar plot, and pie plot
    """
    # Filter the data
    df_expenses_filtered = df_labeled_expenses[
        (df_labeled_expenses["datetime"] >= start_date)
        & (df_labeled_expenses["datetime"] <= end_date)
        & (df_labeled_expenses["category"].isin(transaction_type))
    ]

    # Update the table
    table = df_expenses_filtered[
        ["merchant", "datetime", "category", "amount"]
    ].to_dict("records")

    # Update the time series plot
    bar_plot = time_series_plot(
        expenses.get_moving_average(
            df_expenses_filtered, window=30 if window is None else window
        )
    )

    # Update the pie plot
    pie_plot = pie_chart_plot(df_expenses_filtered)

    # Update the total expenses
    total_expenses = "${:,.2f}".format(df_expenses_filtered["amount"].sum())

    # Update the total transactions
    total_transactions = "{:,.0f}".format(df_expenses_filtered.shape[0])

    return (
        table,
        bar_plot,
        pie_plot,
        total_transactions,
        total_expenses,
    )
