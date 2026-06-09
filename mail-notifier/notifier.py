import argparse
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


class EmailNotifier:
    def __init__(self, sender: str, password: str, recipient: str) -> None:
        self.sender = sender
        self.password = password
        self.recipient = recipient

    def send(self, subject: str, body: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = self.sender
        msg["To"] = self.recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.recipient, msg.as_string())


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a test email via Gmail SMTP.")
    parser.add_argument("--subject", default="Test from mail-notifier")
    parser.add_argument("--body", default="This is a test email from notifier.py.")
    args = parser.parse_args()

    sender = os.getenv("MAIL_SENDER")
    password = os.getenv("MAIL_PASSWORD")
    recipient = os.getenv("MAIL_RECIPIENT")

    if not all([sender, password, recipient]):
        raise EnvironmentError(
            "Missing one or more required env vars: MAIL_SENDER, MAIL_PASSWORD, MAIL_RECIPIENT"
        )

    notifier = EmailNotifier(sender, password, recipient)
    notifier.send(args.subject, args.body)
    print(f"Email sent to {recipient}")


if __name__ == "__main__":
    main()
