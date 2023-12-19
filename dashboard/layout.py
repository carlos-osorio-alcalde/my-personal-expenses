import datetime
import os

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table, dcc, html

from dashboard.data import fetch_data
from dashboard.expenses import MyExpenses
from dashboard.plots import pie_chart_plot, time_series_plot, barplot_weekly
from dashboard.styles import Styles


def app_layout() -> dbc.Container:
    """
    This function returns the layout of the dashboard

    Returns
    -------
    dbc.Container
        The layout of the dashboard
    """
    # Obtain the data
    expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
    _, df_labeled_expenses, updated_at = fetch_data(expenses)

    return dbc.Container(
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
                        interval=1 * 60 * 1000,
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
                                        + 1
                                    ),
                                    end_date=datetime.datetime.now().date()
                                    + pd.DateOffset(days=1),
                                    display_format="YYYY-MM-DD",
                                    number_of_months_shown=2,
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
                                html.Label(
                                    "Select transaction type or category:"
                                ),
                                dcc.Dropdown(
                                    id="transaction-type-dropdown",
                                    options=[
                                        {"label": t, "value": t}
                                        for t in df_labeled_expenses[
                                            "category"
                                        ].unique()
                                    ],
                                    multi=True,
                                    value=df_labeled_expenses[
                                        "category"
                                    ].unique(),
                                ),
                            ],
                            style={
                                "margin-bottom": "20px",
                                "width": "80%",
                            },
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
                                    "${:,.0f}".format(
                                        (-1)
                                        * df_labeled_expenses["amount"].sum()
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
                                    "{:,.0f}".format(
                                        df_labeled_expenses.shape[0]
                                    ),
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
            html.Hr(),
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
                                    fixed_rows={
                                        "headers": True,
                                        "data": 0,
                                    },
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
                                    figure=pie_chart_plot(
                                        df_labeled_expenses
                                    ),
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
                                        expenses.get_moving_average(
                                            df_labeled_expenses
                                        )
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
