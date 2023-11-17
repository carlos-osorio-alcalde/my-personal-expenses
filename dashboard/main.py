import datetime
import os

import dash
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from dotenv import load_dotenv

from dashboard.callbacks import update_metrics
from dashboard.data import fetch_data
from dashboard.plots import pie_chart_plot, time_series_plot
from dashboard.styles import Styles

# Load environment variables
load_dotenv()

# Obtain the data
expenses, df_expenses, df_labeled_expenses, updated_at = fetch_data()

# Create Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "My personal expenses 💸"

# Authentication
auth = dash_auth.BasicAuth(
    app, {os.getenv("USER_APP"): os.getenv("PASSWORD_APP")}
)

# Layout of the dashboard
app.layout = dbc.Container(
    fluid=True,
    style=Styles.CONTAINER,
    children=[
        html.H1(
            "My personal expenses 💸",
            className="display-4 mb-5",
            style=Styles.H1,
        ),
        html.Div(
            [
                html.H4(
                    updated_at,
                    id="live-update-text",
                    className="display-4 mb-5",
                    style=Styles.H4,
                ),
                dcc.Interval(
                    id="interval-component",
                    interval=30 * 60 * 1000,
                    n_intervals=0,
                ),
            ]
        ),
        # Filters
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Label("Select range:  "),
                            dcc.DatePickerRange(
                                id="date-range-picker",
                                start_date=datetime.datetime.now().date()
                                - pd.DateOffset(
                                    days=datetime.datetime.now()
                                    .date()
                                    .weekday()
                                ),
                                end_date=datetime.datetime.now().date()
                                + pd.DateOffset(days=1),
                                display_format="YYYY-MM-DD",
                            ),
                        ],
                        style={
                            "margin-bottom": "20px",
                            "width": "80%",
                            "align": "center",
                            "margin-top": "30px",
                        },
                    ),
                    width=6,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Label("Select Transaction Type:"),
                            dcc.Dropdown(
                                id="transaction-type-dropdown",
                                options=[
                                    {"label": t, "value": t}
                                    for t in df_expenses[
                                        "transaction_type"
                                    ].unique()
                                ],
                                multi=True,
                                value=df_expenses[
                                    "transaction_type"
                                ].unique(),
                            ),
                        ],
                        style={"margin-bottom": "20px", "width": "80%"},
                    ),
                    width=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                "Total Expenses",
                                className="mb-4",
                                style=Styles.H3,
                            ),
                            html.H1(
                                "${:,.2f}".format(
                                    (-1) * df_expenses["amount"].sum()
                                ),
                                id="total-expenses",
                                style=Styles.VALUE_CARD,
                            ),
                        ],
                        style=Styles.DIV_LEFT_VALUE,
                    ),
                    width=4,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                "Total transactions",
                                className="mb-4",
                                style=Styles.H3,
                            ),
                            html.H1(
                                "{:,.0f}".format(df_expenses.shape[0]),
                                id="total-transactions",
                                style=Styles.VALUE_CARD,
                            ),
                        ],
                        style=Styles.DIV_RIGHT_VALUE,
                    ),
                    width=4,
                ),
            ],
            style={
                "margin-bottom": "20px",
                "margin": "auto",
                "align": "center",
                "border-radius": "5px",
                "overflow": "hidden",
            },
        ),
        html.Hr(),
        # Table and Bar Plot (Two Columns)
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                "Expense details",
                                className="mb-4",
                                style=Styles.H3,
                            ),
                            dash_table.DataTable(
                                id="expense-table",
                                columns=[
                                    {"name": col, "id": col}
                                    for col in [
                                        "merchant",
                                        "datetime",
                                        "category",
                                        "amount",
                                    ]
                                ],
                                data=df_labeled_expenses[
                                    [
                                        "merchant",
                                        "datetime",
                                        "category",
                                        "amount",
                                    ]
                                ].to_dict("records"),
                                style_table=Styles.TABLE,
                                editable=False,
                                filter_action="native",
                                sort_action="native",
                                fixed_rows={"headers": True, "data": 0},
                                style_cell={
                                    "minWidth": "100px",
                                    "width": "100px",
                                    "maxWidth": "100px",
                                    "overflow": "hidden",
                                    "textOverflow": "ellipsis",
                                },
                            ),
                        ],
                        style=Styles.DIV_CARD,
                    ),
                    width=6,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                "Expense distribution by category",
                                className="mb-4",
                                style=Styles.H3,
                            ),
                            dcc.Graph(
                                id="pie-plot",
                                figure=pie_chart_plot(df_labeled_expenses),
                                config={"displayModeBar": False},
                                responsive=True,
                                style={
                                    "height": "80%",
                                    "width": "100%",
                                    "margin": "auto",
                                },
                            ),
                        ],
                        style=Styles.DIV_CARD,
                    ),
                    width=6,
                ),
            ],
            className="mb-4",
        ),
        # Time series
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                "Time series of my expenses",
                                className="mb-4",
                                style=Styles.H3,
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Moving average window size (default: 30 days)"
                                    ),
                                    html.Br(),
                                    dcc.Input(
                                        id="text-filter",
                                        type="number",
                                        placeholder="Enter the window size",
                                        debounce=True,
                                    ),
                                ],
                                style={
                                    "margin-bottom": "20px",
                                    "margin": "center",
                                },
                            ),
                            dcc.Graph(
                                id="time-series-plot",
                                figure=time_series_plot(
                                    expenses.get_moving_average(df_expenses)
                                ),
                                config={"displayModeBar": False},
                            ),
                        ],
                        style=Styles.DIV_TIME_SERIES,
                    ),
                    width=12,
                )
            ],
            className="mb-4",
        ),
    ],
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
    prevent_initial_call=False,
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
) -> str:
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
    str
        The last updated time
    """
    # Fetch the data
    expenses, df_expenses, df_labeled_expenses, updated_at = fetch_data()

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
        updated_at,
        table,
        bar_plot,
        pie_plot,
        total_transactions,
        total_expenses,
    )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
