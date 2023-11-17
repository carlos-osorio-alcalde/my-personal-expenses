import datetime
import os

import dash
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv

from dashboard.callbacks import update_metrics
from dashboard.data import fetch_data
from dashboard.layout import app_layout

from dashboard.expenses import MyExpenses

# Load environment variables
load_dotenv()

# Obtain the data
expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
df_expenses, df_labeled_expenses, updated_at = fetch_data(expenses)

# Create Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "My personal expenses 💸"

# Authentication
auth = dash_auth.BasicAuth(
    app, {os.getenv("USER_APP"): os.getenv("PASSWORD_APP")}
)


# Layout of the dashboard
app.layout = app_layout(
    expenses, df_expenses, df_labeled_expenses, updated_at
)

# Callback for updating the table and the bar plot
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
    return update_metrics(
        expenses,
        df_expenses,
        df_labeled_expenses,
        start_date,
        end_date,
        transaction_type,
        window,
    )


# Callback for updating the last updated time
@app.callback(
    [
        Output("live-update-text", "children", allow_duplicate=True),
        Output("expense-table", "data", allow_duplicate=True),
        Output("time-series-plot", "figure", allow_duplicate=True),
        Output("pie-plot", "figure", allow_duplicate=True),
        Output("total-transactions", "children", allow_duplicate=True),
        Output("total-expenses", "children", allow_duplicate=True),
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("date-range-picker", "start_date"),
        Input("date-range-picker", "end_date"),
        Input("transaction-type-dropdown", "value"),
        Input("text-filter", "value"),
    ],
    prevent_initial_call=True,
)
def update_metrics_from_api(
    n: int,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    transaction_type: list,
    window: int,
) -> (pd.DataFrame, px.bar, px.pie, str, str):
    """
    This function updates the last updated time

    Parameters
    ----------
    n : int
        The number of intervals
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
    (pd.DataFrame, px.bar, px.pie, str, str)
        The table, bar plot, and pie plot
    """
    triggered_component = dash.callback_context.triggered_id
    if triggered_component is None:
        raise PreventUpdate

    # Check if the interval component is triggered
    if "interval-component" in triggered_component:
        # Fetch the data
        df_expenses, df_labeled_expenses, updated_at = fetch_data(expenses)
        last_refresh = updated_at

        (
            table,
            bar_plot,
            pie_plot,
            total_transactions,
            total_expenses,
        ) = update_metrics(
            expenses,
            df_expenses,
            df_labeled_expenses,
            start_date,
            end_date,
            transaction_type,
            window,
        )

        return (
            last_refresh,
            table,
            bar_plot,
            pie_plot,
            total_transactions,
            total_expenses,
        )
    else:
        raise PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
