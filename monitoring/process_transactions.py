import datetime
import os
from typing import List, Literal, Union

import pandas as pd
import pytz
import requests
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from numpy import average
import matplotlib
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()


def get_transactions(
    return_as_pandas: bool = False,
) -> Union[List[dict], pd.DataFrame]:
    """
    This function returns the transactions of the current day.

    Parameters
    ----------
    return_as_pandas : bool, optional
        Whether to return the transactions as a pandas DataFrame or not,
        by default False

    Returns
    -------
    pd.DataFrame
        The dataframe with all the transactions of the current day.
    """
    # Get the transactions of the current day
    url = f"https://personal-expenses-api.orangecliff-ed60441b.eastus.azurecontainerapps.io/expenses/get_full_transactions/?timeframe=daily"  # noqa
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {os.getenv('API_EXPENSES_TOKEN')}",
    }
    response = requests.get(url, headers=headers)

    # Check if the response is 200
    if response.status_code != 200:
        return [
            {
                "datetime": datetime.datetime.now().isoformat(),
                "transaction_type": "No transaction",
                "merchant": "No transaction",
                "amount": 0,
            }
        ]

    # Return the transactions as a DataFrame
    df_transactions = pd.DataFrame(response.json())
    return (
        df_transactions[
            df_transactions["transaction_type"].isin(
                ["Compra", "Transferencia", "QR", "Pago"]
            )
        ]
        if return_as_pandas
        else [
            transaction
            for transaction in response.json()
            if transaction["transaction_type"]
            in ["Compra", "Transferencia", "QR", "Pago"]
        ]
    )


def compute_daily_values(transactions: pd.DataFrame) -> dict:
    """
    Compute the daily values of expenses to pass through the anomaly model.

    Parameters
    ----------
    transactions : pd.DataFrame
        The transactions of the current day.

    Returns
    -------
    dict
        The dictionary with the needed values
    """
    expenses_values = {
        "avg_amount": (-1) * transactions["amount"].mean(),
        "max_amount": (-1) * transactions["amount"].max(),
        "total_trx": transactions.shape[0],
        "weekend": "yes"
        if datetime.datetime.now()
        .astimezone(pytz.timezone("America/Bogota"))
        .isoweekday()
        in [6, 7]
        else "no",
    }
    return expenses_values


def check_anomaly(expenses_values: dict) -> Literal["normal", "anomaly"]:
    """
    Make the request to check if the daily values are an anomaly.

    Parameters
    ----------
    expenses_values : dict
        The dictionary with the needed values

    Returns
    -------
    Literal["normal", "anomaly"]
        Whether the values are an anomaly or not.
    """
    params = {
        "avg_amount": expenses_values["avg_amount"],
        "max_amount": expenses_values["max_amount"],
        "total_trx": expenses_values["total_trx"],
        "weekend": expenses_values["weekend"],
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('API_EXPENSES_TOKEN')}",
    }
    response = requests.get(
        "https://personal-expenses-api.orangecliff-ed60441b.eastus.azurecontainerapps.io/monitoring/predict_anomaly/",  # noqa
        headers=headers,
        params=params
    )
    if response.status_code != 200:
        return "normal"
    
    return response.json()["prediction"]


def get_average_normal_values() -> float:
    """
    This function calls the endpoint to obtain the normal values

    Returns
    -------
    float
        The median of the amount spent in a normal day.
    """
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('API_EXPENSES_TOKEN')}",
    }
    response = requests.get(
        "https://personal-expenses-api.orangecliff-ed60441b.eastus.azurecontainerapps.io/expenses/a_day_like_today/",  # noqa
        headers=headers,
    )
    return (-1) * response.json()["median_amount_of_purchases"]


def create_html_email(transactions: List[dict]) -> str:
    """
    Create the html email to send.

    Parameters
    ----------
    transactions : List[dict]
        The transactions of the current day.

    Returns
    -------
    str
        The html email to send.
    """
    # Check the day status
    day_status = (
        check_anomaly(compute_daily_values(pd.DataFrame(transactions)))
        if len(transactions) > 0
        else "normal"
    )

    # Create a Jinja2 environment with a template loader
    env = Environment(loader=FileSystemLoader("monitoring/static/"))

    # Load your HTML template
    template = env.get_template("base.html")

    # Get the summary of the transactions
    summary = {
        "num_transactions": len(transactions),
        "sum_transactions": "${:,.2f}".format(
            (-1)
            * sum([transaction["amount"] for transaction in transactions])
        ),
        "avg_amount": "${:,.2f}".format(
            (-1)
            * average(
                [transaction["amount"] for transaction in transactions]
            )
        ),
    }
    # Render the template with the data
    rendered_template = template.render(
        date_value=datetime.datetime.now()
        .astimezone(pytz.timezone("America/Bogota"))
        .date(),
        transactions=[
            {
                "transaction_type": transaction["transaction_type"],
                "merchant": transaction["merchant"],
                "amount": "${:,.2f}".format((-1) * transaction["amount"]),
            }
            for transaction in transactions
        ],
        summary=summary,
        day_status=day_status,
        historical_average_amount="${:,.2f}".format(
            get_average_normal_values()
        ),
        relationship="{:.1f}".format(
            (-1)
            * sum([transaction["amount"] for transaction in transactions])
            / get_average_normal_values()
        ),
    )

    return rendered_template


def create_step_plot(transactions: List[dict]) -> plt.figure:
    """
    This function creates a step plot of the transactions based on the
    time of the transaction.

    Parameters
    ----------
    transactions : List[dict]
        The transactions of the current day.

    Returns
    -------
    plt.figure
        The step plot of the transactions.
    """
    matplotlib.use("agg")

    # Create the figure
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)

    # Values of the transactions
    gross_values = [transaction["amount"] for transaction in transactions]

    # Times of the transactions
    datetimes = (
        [datetime.datetime.now().replace(hour=0, minute=0, second=0)]
        + [
            datetime.datetime.fromisoformat(transaction["datetime"])
            for transaction in transactions
        ]
        + [datetime.datetime.now().replace(hour=23, minute=59, second=59)]
    )
    values = (
        [0]
        + [(-1) * sum(gross_values[:i]) for i in range(len(transactions))]
        + [(-1) * sum(gross_values)]
    )

    # Create the plot. Add the 0:00:00 hours and the 23:59:59 hours. For
    # the 0:00:00 hours, start by zero and for the 23:59:59 hours, end
    # by the number of the last transaction. The y values must be the
    # rolling sum of the amount.
    ax.step(datetimes, values, color="#29A7A0")
    # Create points in the plot
    ax.scatter(
        datetimes,
        values,
        color="#053937",
        s=[30]
        + [(200 * v) / sum(gross_values) for v in gross_values]
        + [30],
    )
    # In the xticks, show uniquely the hours without the date
    ax.set_xticks(
        [
            datetime.datetime.now().replace(hour=i, minute=0, second=0)
            for i in range(0, 24, 3)
        ]
    )
    ax.set_xticklabels(
        [
            datetime.datetime.now()
            .replace(hour=i, minute=0, second=0)
            .time()
            .strftime("%H:%M")
            for i in range(0, 24, 3)
        ]
    )

    # Style the yaxis as $10,000.00
    ax.yaxis.set_major_formatter("${x:,.2f}")

    # Delete the box
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Add the size of the xticks and yticks
    ax.tick_params(axis="x", labelsize=17, colors="#29A7A0")
    ax.tick_params(axis="y", labelsize=17, colors="#29A7A0")

    # Set the background color of the entire picture to f7f7f7
    ax.set_facecolor("none")
    fig.patch.set_facecolor("none")

    # Save the figure
    plt.savefig("monitoring/static/step_plot.png", bbox_inches="tight")

    return fig
