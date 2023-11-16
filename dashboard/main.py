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
df_labeled_expenses = expenses.get_labeled_expenses(return_amount=True)

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
    style={
        "backgroundColor": "#ffffff",
        "color": "#333",
        "padding": "75px",
        "margin": "center",
    },
    children=[
        html.H1(
            "My personal expenses 💸",
            className="display-4 mb-5",
            style={
                "font-size": "2.5em",
                "color": "white",
                "font-weight": "bold",
                "text-align": "center",
                "margin-bottom": "20px",
                "background-color": "#007BFF",
                "padding": "15px",
                "border-radius": "10px",
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
                            "height": "180px",
                            "margin": "auto",
                            "align": "center",
                            "left": "50%",
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
                            "height": "180px",
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
                                data=df_expenses[
                                    [
                                        "transaction_type",
                                        "merchant",
                                        "datetime",
                                        "amount",
                                    ]
                                ].to_dict("records"),
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
                            "height": "450px",
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
                                "Expense distribution by category",
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
                                    df_labeled_expenses,
                                    names="category",
                                    values="amount",
                                    width=500,
                                    height=500,
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
                            "height": "450px",
                            "width": "100%",
                            "border-radius": "5px",
                            "overflow": "hidden",
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
                                "Time series of my expenses",
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
                            "height": "650px",
                            "width": "100%",
                            "border-radius": "5px",
                            "overflow": "hidden",
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
    df_labeled_expenses_filtered = df_labeled_expenses[
        (df_labeled_expenses["datetime"] >= start_date)
        & (df_labeled_expenses["datetime"] <= end_date)
    ]

    # Update the table
    table = df_expenses_filtered[
        ["transaction_type", "merchant", "datetime", "amount"]
    ].to_dict("records")

    # Change the sign of the amount
    df_expenses_filtered["amount"] = -1 * df_expenses_filtered["amount"]

    bar_plot = px.line(
        expenses.get_moving_average(
            df_expenses_filtered, window=30 if window is None else window
        ),
        x="datetime",
        y="amount_moving_average",
    )

    # Update the pie plot
    pie_plot = px.pie(
        df_labeled_expenses_filtered,
        names="category",
        values="amount",
        hole=0.4,
        color_discrete_map={
            "comida": "#FFC300",
            "diversion": "#FF5733",
            "carro": "#C70039",
            "facturas": "#900C3F",
            "mercado": "#581845",
            "servicios": "#FFC300",
            "movilidad": "#FF5733",
        },
    )

    # Update the total expenses
    total_expenses = "${:,.2f}".format(
        (-1) * df_expenses_filtered["amount"].sum()
    )

    # Update the total transactions
    total_transactions = "{:,.0f}".format(df_expenses_filtered.shape[0])

    return table, bar_plot, pie_plot, total_transactions, total_expenses


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
