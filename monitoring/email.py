import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from smtplib import SMTP_SSL, SMTP_SSL_PORT

import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def send_email(html_body: str) -> None:
    """
    This function sends an email with the given html body.

    Parameters
    ----------
    html_body : str
        The html body of the processed transactions.
    """
    from_email = f"Expenses inform 💵 - {datetime.datetime.now().date()} <{os.getenv('FROM_EMAIL')}>"  # noqa
    to_emails = [os.getenv("TO_EMAIL")]

    # Create multipart MIME email
    email_message = MIMEMultipart()
    email_message.add_header("To", ", ".join(to_emails))
    email_message.add_header("From", from_email)
    email_message.add_header("Subject", "Expenses inform")
    email_message.add_header("X-Priority", "1")
    email_message.attach(MIMEText(html_body, "html"))
    step_plot_image = MIMEImage(
        open("monitoring/static/step_plot.png", "rb").read()
    )
    step_plot_image.add_header("Content-ID", "<step_plot>")
    email_message.attach(step_plot_image)

    # Connect, authenticate, and send mail
    smtp_server = SMTP_SSL("imap.gmail.com", port=SMTP_SSL_PORT)
    smtp_server.set_debuglevel(1)
    smtp_server.login(os.getenv("FROM_EMAIL"), os.getenv("GMAIL_TOKEN"))
    smtp_server.sendmail(from_email, to_emails, email_message.as_bytes())

    # Disconnect
    smtp_server.quit()
