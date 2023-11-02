from fastapi import FastAPI
from monitoring.email import send_email
from monitoring.process_transactions import (
    get_transactions,
    create_html_email,
    create_step_plot,
)

# Create the app
app = FastAPI()

# Create the only endpoint to send the email
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
