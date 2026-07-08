
import os
from pathlib import Path
from dotenv import load_dotenv
import smtplib


ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASSWORD = os.environ.get("MY_PASSWORD")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_TIMEOUT = int(os.environ.get("SMTP_TIMEOUT", "15"))


class NotificationManager:

    def send_emails(self, msg_content, my_msg_content, userEmail):

        my_email = MY_EMAIL
        password = MY_PASSWORD
        if not my_email or not password:
            raise ValueError("Missing MY_EMAIL or MY_PASSWORD environment variables.")

        print(f"userEmail: {userEmail}")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as connection:
            connection.ehlo()
            connection.starttls()
            connection.ehlo()
            connection.login(my_email, password)
            try:
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=userEmail,
                    msg=f"Subject:dileandrog-development .:: WELLCOME TO MY-RESUME!\n\n{msg_content}\n".encode('utf-8'))
                print(f"msg content: {msg_content} \n")
                print("\n\nMessage sent successfully!")

                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=my_email,
                    msg=f"Subject:dileandrog-development .:: You Have a new user!!\n\n{my_msg_content}\n".encode(
                        'utf-8'))
                print(f"msg content: {my_msg_content} \n")
                print("\n\nMessage sent successfully!")
            except UnicodeError as msg:
                print(f"-- ERROR: send_to could not be sent: {msg}")

