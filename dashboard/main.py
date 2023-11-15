import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import datetime
import pandas as pd
from dashboard.expenses import MyExpenses
import os
import dash_auth
import plotly.express as px

# Load your data from the backend (assuming a CSV file)
expenses = MyExpenses(token=os.getenv("TOKEN_EXPENSES_API"))
df_expenses = expenses.get_expenses(timeframe="from_origin")

# Create Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Authentication
auth = dash_auth.BasicAuth(
    app, {os.getenv("USER_APP"): os.getenv("PASSWORD_APP")}
)

# Define the background color
bg_color = "#ffffff"
text_color = "#333"

# Layout of the dashboard
app.layout = dbc.Container(
    fluid=True,
    style={
        "backgroundColor": bg_color,
        "color": text_color,
        "padding": "75px",
        "margin": "center",
    },
    children=[
        html.H1(
            "Personal Expenses Dashboard",
            className="display-4 mb-5",
            style={
                "font-size": "2.5em",
                "color": "white",
                "font-weight": "bold",
                "text-align": "center",
                "margin-bottom": "20px",
                "text-transform": "uppercase",
                "background-color": "#007BFF",
            },
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
                                start_date=df_expenses["datetime"].max()
                                - pd.DateOffset(
                                    days=df_expenses["datetime"]
                                    .max()
                                    .weekday()
                                    + 1
                                ),
                                end_date=df_expenses["datetime"].max(),
                                display_format="YYYY-MM-DD",
                            ),
                        ],
                        style={"margin-bottom": "20px", "width": "80%"},
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
                                style={
                                    "color": "white",
                                    "background-color": "#007BFF",
                                    "padding": "10px",
                                    "border-radius": "5px",
                                },
                            ),
                            html.H1(
                                "${:,.2f}".format(
                                    (-1) * df_expenses["amount"].sum()
                                ),
                                id="total-expenses",
                                style={
                                    "text-align": "center",
                                    "font-size": "2.5em",
                                    "color": "#007BFF",
                                    "font-weight": "bold",
                                    "margin-bottom": "20px",
                                    "text-transform": "uppercase",
                                },
                            ),
                        ],
                        style={
                            "box-shadow": "2px 2px 2px 2px #D8D8D8",
                            "padding": "20px",
                            "height": "200px",
                            "transform": "translate(52%, 0%)",
                        },
                    ),
                    width=4,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                "Total transactions",
                                className="mb-4",
                                style={
                                    "color": "white",
                                    "background-color": "#007BFF",
                                    "padding": "10px",
                                    "border-radius": "5px",
                                },
                            ),
                            html.H1(
                                "{:,.0f}".format(df_expenses.shape[0]),
                                id="total-transactions",
                                style={
                                    "text-align": "center",
                                    "font-size": "2.5em",
                                    "color": "#007BFF",
                                    "font-weight": "bold",
                                    "margin-bottom": "20px",
                                    "text-transform": "uppercase",
                                },
                            ),
                        ],
                        style={
                            "box-shadow": "2px 2px 2px 2px #D8D8D8",
                            "padding": "20px",
                            "height": "200px",
                            "margin": "auto",
                            "align": "center",
                            "left": "50%",
                            "transform": "translate(56%, 0%)",
                        },
                    ),
                    width=4,
                ),
            ],
            style={
                "margin-bottom": "20px",
                "margin": "auto",
                "align": "center",
                "border-radius": "5px",
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
                                "Expense Details",
                                className="mb-4",
                                style={
                                    "color": "white",
                                    "background-color": "#007BFF",
                                    "padding": "10px",
                                    "border-radius": "5px",
                                },
                            ),
                            dash_table.DataTable(
                                id="expense-table",
                                columns=[
                                    {"name": col, "id": col}
                                    for col in df_expenses.columns
                                ],
                                data=df_expenses.to_dict("records"),
                                style_table={
                                    "backgroundColor": "white",
                                    "color": "#333",
                                    "width": "100%",
                                    "height": "100%",
                                    "margin": "auto",
                                    "maxHeight": "350px",
                                },
                                style_cell_conditional=[
                                    {
                                        "if": {"column_id": c},
                                        "textAlign": "left",
                                    }
                                    for c in df_expenses.columns
                                ],
                                editable=True,
                                filter_action="native",
                                sort_action="native",
                                fixed_rows={"headers": True, "data": 0},
                            ),
                        ],
                        style={
                            "box-shadow": "2px 2px 2px 2px #D8D8D8",
                            "padding": "20px",
                            "height": "500px",
                            "width": "100%",
                            "border-radius": "5px",
                            "overflow": "hidden",
                        },
                    ),
                    width=6,
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                "Expense Distribution by Category",
                                className="mb-4",
                                style={
                                    "color": "white",
                                    "background-color": "#007BFF",
                                    "padding": "10px",
                                    "border-radius": "5px",
                                },
                            ),
                            dcc.Graph(
                                id="pie-plot",
                                figure=px.pie(
                                    df_expenses, names="transaction_type"
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
                        style={
                            "box-shadow": "2px 2px 2px 2px #D8D8D8",
                            "padding": "20px",
                            "height": "500px",
                        },
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
                                "Monthly Expense Summary",
                                className="mb-4",
                                style={
                                    "color": "white",
                                    "background-color": "#007BFF",
                                    "padding": "10px",
                                    "border-radius": "5px",
                                },
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
                                figure=px.line(
                                    expenses.get_moving_average(df_expenses),
                                    x="datetime",
                                    y="amount_moving_average",
                                ),
                                config={"displayModeBar": False},
                            ),
                        ],
                        style={
                            "box-shadow": "2px 2px 2px 2px #D8D8D8",
                            "padding": "20px",
                        },
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
)
def update_table(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    transaction_type: list,
    window: int,
) -> (pd.DataFrame, px.bar, px.pie):
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
    df_expenses_filtered = df_expenses[
        (df_expenses["datetime"] >= start_date)
        & (df_expenses["datetime"] <= end_date)
        & (df_expenses["transaction_type"].isin(transaction_type))
    ]

    # Update the table
    table = df_expenses_filtered.to_dict("records")

    bar_plot = px.line(
        expenses.get_moving_average(
            df_expenses_filtered, window=30 if window is None else window
        ),
        x="datetime",
        y="amount_moving_average",
    )

    # Update the pie plot
    pie_plot = px.pie(df_expenses_filtered, names="transaction_type")

    # Update the total expenses
    total_expenses = "${:,.2f}".format(
        (-1) * df_expenses_filtered["amount"].sum()
    )

    # Update the total transactions
    total_transactions = "{:,.0f}".format(df_expenses_filtered.shape[0])

    return table, bar_plot, pie_plot, total_transactions, total_expenses


if __name__ == "__main__":
    app.run_server(debug=True)
