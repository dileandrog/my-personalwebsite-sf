
import os
from dotenv import load_dotenv
import smtplib


ENV_FILE= ".env"
load_dotenv(f"{os.getcwd()}/{ENV_FILE}")

MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASSWORD = os.environ.get("MY_PASSWORD")


class NotificationManager:

    def send_emails(self, msg_content, my_msg_content, userEmail):

        my_email = MY_EMAIL
        password = MY_PASSWORD
        smtp_address = "smtp.gmail.com"

        print(f"userEmail: {userEmail}")

        with smtplib.SMTP(smtp_address) as connection:
            connection.starttls()
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

