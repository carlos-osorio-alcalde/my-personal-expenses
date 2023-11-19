import datetime
import os

import dash
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from dotenv import load_dotenv

from dashboard.callbacks import update_metrics
from dashboard.data import fetch_data
from dashboard.expenses import MyExpenses
from dashboard.layout import app_layout

# Load environment variables
load_dotenv()

# Create Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "My personal expenses 💸"

# Authentication
auth = dash_auth.BasicAuth(
    app, {os.getenv("USER_APP"): os.getenv("PASSWORD_APP")}
)

app.layout = app_layout

# Callback for updating the table and the bar plot when the filter
# is changed
@app.callback(
    [
        Output("expense-table", "data"),
        Output("time-series-plot", "figure"),
        Output("pie-plot", "figure"),
        Output("total-transactions", "children"),
        Output("total-expenses", "children"),
    ],
    [
        Input("date-range-picker", "start_date"),
        Input("date-range-picker", "end_date"),
        Input("transaction-type-dropdown", "value"),
        Input("text-filter", "value"),
    ],
)
def filter_table(
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
    # Obtain the data
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    df_expenses, df_labeled_expenses, _ = fetch_data(
        expenses, return_from_cache=True
    )

    return update_metrics(
        expenses,
        df_expenses,
        df_labeled_expenses,
        start_date,
        end_date,
        transaction_type,
        window,
    )


# Callback to open the popup every 15 minutes
@app.callback(
    Output("live-update-text", "children"),
    [
        Input("interval-component", "n_intervals"),
        Input("live-update-text", "children"),
    ],
    prevent_initial_call=True,
)
def change_last_updated_text(n_intervals: int, last_update: str):
    """
    This function changes the text of the last update if the time has passed
    """
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    if (
        pd.Timestamp.now() - expenses.last_time_update()
    ).total_seconds() > MyExpenses.TIME_TO_WAIT:
        return "(Last updated at: {})".format(
            expenses.last_time_update().strftime("%Y-%m-%d %H:%M:%S")
        )

    return last_update


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
