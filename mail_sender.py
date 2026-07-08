
import os
import json
from pathlib import Path
import smtplib
import socket
import urllib.request
import urllib.error


MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASSWORD = os.environ.get("MY_PASSWORD")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_TIMEOUT = int(os.environ.get("SMTP_TIMEOUT", "15"))
SMTP_SECURITY = os.environ.get("SMTP_SECURITY", "starttls").lower()
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

raw_method = (os.environ.get("MAIL_DELIVERY_METHOD") or "").strip().strip('"\'').lower()
if not raw_method:
    raw_method = "resend" if RESEND_API_KEY else "smtp"
if raw_method not in {"smtp", "resend"}:
    raw_method = "smtp"
MAIL_DELIVERY_METHOD = raw_method

MAIL_FROM_EMAIL = os.environ.get("MAIL_FROM_EMAIL") or MY_EMAIL
MAIL_TO_EMAIL = os.environ.get("MAIL_TO_EMAIL") or MY_EMAIL


def create_smtp_socket(host, port, timeout):
    addresses = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    addresses.sort(key=lambda item: 0 if item[0] == socket.AF_INET else 1)

    last_error = None
    for family, socktype, proto, _, sockaddr in addresses:
        smtp_socket = None
        try:
            smtp_socket = socket.socket(family, socktype, proto)
            smtp_socket.settimeout(timeout)
            smtp_socket.connect(sockaddr)
            return smtp_socket
        except OSError as exc:
            last_error = exc
            if smtp_socket is not None:
                smtp_socket.close()

    if last_error is None:
        raise OSError(f"Unable to resolve SMTP host: {host}")

    raise last_error


class IPv4PreferredSMTP(smtplib.SMTP):
    def _get_socket(self, host, port, timeout):
        if timeout is not None and not timeout:
            raise ValueError("Non-blocking socket (timeout=0) is not supported")
        return create_smtp_socket(host, port, timeout)


class IPv4PreferredSMTP_SSL(smtplib.SMTP_SSL):
    def _get_socket(self, host, port, timeout):
        if timeout is not None and not timeout:
            raise ValueError("Non-blocking socket (timeout=0) is not supported")
        raw_socket = create_smtp_socket(host, port, timeout)
        return self.context.wrap_socket(raw_socket, server_hostname=host)


class NotificationManager:
    def _send_with_resend(self, to_addr, subject, body):
        if not RESEND_API_KEY:
            raise ValueError("Missing RESEND_API_KEY for Resend delivery.")
        if not MAIL_FROM_EMAIL:
            raise ValueError("Missing MAIL_FROM_EMAIL for Resend delivery.")

        payload = json.dumps(
            {
                "from": MAIL_FROM_EMAIL,
                "to": [to_addr],
                "subject": subject,
                "text": body,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=SMTP_TIMEOUT) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"Resend API returned status {response.status}")

    def _open_connection(self):
        if SMTP_SECURITY == "ssl":
            return IPv4PreferredSMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)

        connection = IPv4PreferredSMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)
        connection.ehlo()

        if SMTP_SECURITY == "starttls":
            connection.starttls()
            connection.ehlo()

        return connection

    def send_emails(self, msg_content, my_msg_content, userEmail):

        my_email = MY_EMAIL
        password = MY_PASSWORD
        owner_email = MAIL_TO_EMAIL

        print(f"userEmail: {userEmail}")

        user_subject = "dileandrog-development .:: WELLCOME TO MY-RESUME!"
        owner_subject = "dileandrog-development .:: You Have a new user!!"

        if MAIL_DELIVERY_METHOD == "resend":
            if not owner_email:
                raise ValueError("Missing MAIL_TO_EMAIL or MY_EMAIL for Resend delivery.")
            self._send_with_resend(userEmail, user_subject, msg_content)
            self._send_with_resend(owner_email, owner_subject, my_msg_content)
            return

        if not my_email or not password:
            raise ValueError("Missing MY_EMAIL or MY_PASSWORD environment variables.")

        try:
            with self._open_connection() as connection:
                connection.login(my_email, password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=userEmail,
                    msg=f"Subject:{user_subject}\n\n{msg_content}\n".encode('utf-8'))
                print(f"msg content: {msg_content} \n")
                print("\n\nMessage sent successfully!")

                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=owner_email,
                    msg=f"Subject:{owner_subject}\n\n{my_msg_content}\n".encode('utf-8'))
                print(f"msg content: {my_msg_content} \n")
                print("\n\nMessage sent successfully!")
        except (OSError, smtplib.SMTPException) as exc:
            if RESEND_API_KEY:
                if not owner_email:
                    raise ValueError("Missing MAIL_TO_EMAIL or MY_EMAIL for Resend fallback delivery.") from exc
                self._send_with_resend(userEmail, user_subject, msg_content)
                self._send_with_resend(owner_email, owner_subject, my_msg_content)
                return
            raise RuntimeError(
                "Mail delivery failed over SMTP. Configure RESEND_API_KEY and MAIL_FROM_EMAIL "
                "to send mail over HTTPS, or verify outbound SMTP/TLS access on the host."
            ) from exc

