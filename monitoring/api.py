from fastapi import FastAPI
import json
import requests
from monitoring.email import send_email
from monitoring.process_transactions import (
    get_transactions,
    create_html_email,
    create_step_plot,
)

# Create the app
app = FastAPI()

# Endpoint to get the daily transactions and save them labeled to the database
@app.post("/label_and_save_transactions")
def label_and_save_transactions():
    """
    This endpoint gets the daily transactions and saves them labeled to the database
    """
    gross_transactions = get_transactions()
    gross_transactions = [
        trx
        for trx in gross_transactions
        if trx["transaction_type"] == "Compra" and "*" not in trx["merchant"]
    ]

    url_label_transactions = "https://label-categories.orangecliff-ed60441b.eastus.azurecontainerapps.io/get_category"  # noqa
    url_save_to_database = "https://label-categories.orangecliff-ed60441b.eastus.azurecontainerapps.io/database/save_categories"  # noqa

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response_labeling = requests.post(
        url_label_transactions,
        headers=headers,
        data=json.dumps(gross_transactions),
    )
    response_save_db = requests.post(
        url_save_to_database,
        headers=headers,
        data=json.dumps(response_labeling.json()),
    )

    if response_save_db.status_code != 200:
        return {"status": "Error saving transactions!"}

    return {"status": "Transactions saved succesfully!"}


# Endpoint to send the email
@app.post("/send_daily_report")
def send_daily_report():
    """
    This endpoint sends the email with the summary of the transactions
    """
    gross_transactions = get_transactions(return_as_pandas=False)
    html = create_html_email(gross_transactions)

    # Create the step plot
    if gross_transactions[0]["transaction_type"] != "No transaction":
        create_step_plot(gross_transactions)

    # Save the html
    with open("monitoring/static/processed_transactions.html", "w") as f:
        f.write(html)

    # Send the email
    send_email(html)

    return {"status": "Report sent succesfully!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("monitoring.api:app", host="0.0.0.0", port=5000, reload=True)
