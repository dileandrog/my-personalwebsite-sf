
import os
import json
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
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")

raw_method = (os.environ.get("MAIL_DELIVERY_METHOD") or "").strip().strip('"\'').lower()
if not raw_method:
    if BREVO_API_KEY:
        raw_method = "brevo"
    elif RESEND_API_KEY:
        raw_method = "resend"
    else:
        raw_method = "smtp"
if raw_method not in {"smtp", "resend", "brevo"}:
    raw_method = "smtp"
MAIL_DELIVERY_METHOD = raw_method

MAIL_FROM_EMAIL = ((os.environ.get("MAIL_FROM_EMAIL") or MY_EMAIL) or "").strip().strip('"\'')
MAIL_TO_EMAIL = ((os.environ.get("MAIL_TO_EMAIL") or MY_EMAIL) or "").strip().strip('"\'')
BREVO_SENDER_EMAIL = ((os.environ.get("BREVO_SENDER_EMAIL") or MAIL_FROM_EMAIL) or "").strip().strip('"\'')
BREVO_SENDER_NAME = (os.environ.get("BREVO_SENDER_NAME") or "My Personal Website").strip().strip('"\'')


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
    def _send_with_brevo(self, to_addr, subject, body):
        if not BREVO_API_KEY:
            raise ValueError("Missing BREVO_API_KEY for Brevo delivery.")
        if not BREVO_SENDER_EMAIL:
            raise ValueError("Missing BREVO_SENDER_EMAIL or MAIL_FROM_EMAIL for Brevo delivery.")

        payload = json.dumps(
            {
                "sender": {"email": BREVO_SENDER_EMAIL, "name": BREVO_SENDER_NAME},
                "to": [{"email": to_addr}],
                "subject": subject,
                "textContent": body,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            "https://api.brevo.com/v3/smtp/email",
            data=payload,
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=SMTP_TIMEOUT) as response:
                if response.status not in (200, 201, 202):
                    raise RuntimeError(f"Brevo API returned status {response.status}")
        except urllib.error.HTTPError as exc:
            try:
                response_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                response_body = "<unable to parse response body>"
            raise RuntimeError(
                f"Brevo HTTPError {exc.code}: {response_body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Brevo URLError: {exc}") from exc

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

        try:
            with urllib.request.urlopen(request, timeout=SMTP_TIMEOUT) as response:
                if response.status not in (200, 201):
                    raise RuntimeError(f"Resend API returned status {response.status}")
        except urllib.error.HTTPError as exc:
            try:
                response_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                response_body = "<unable to parse response body>"
            raise RuntimeError(
                f"Resend HTTPError {exc.code}: {response_body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Resend URLError: {exc}") from exc

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
        user_email_clean = (userEmail or "").strip().strip('"\'')

        print(f"MAIL_DELIVERY_METHOD: {MAIL_DELIVERY_METHOD}")
        print(f"MAIL_FROM_EMAIL: {MAIL_FROM_EMAIL}")
        print(f"MAIL_TO_EMAIL: {owner_email}")
        print(f"userEmail: {user_email_clean}")

        user_subject = "dileandrog-development .:: WELLCOME TO MY-RESUME!"
        owner_subject = "dileandrog-development .:: You Have a new user!!"

        if MAIL_DELIVERY_METHOD == "brevo":
            if not owner_email:
                raise ValueError("Missing MAIL_TO_EMAIL or MY_EMAIL for Brevo delivery.")
            self._send_with_brevo(user_email_clean, user_subject, msg_content)
            self._send_with_brevo(owner_email, owner_subject, my_msg_content)
            return

        if MAIL_DELIVERY_METHOD == "resend":
            if not owner_email:
                raise ValueError("Missing MAIL_TO_EMAIL or MY_EMAIL for Resend delivery.")
            self._send_with_resend(user_email_clean, user_subject, msg_content)
            self._send_with_resend(owner_email, owner_subject, my_msg_content)
            return

        if not my_email or not password:
            raise ValueError("Missing MY_EMAIL or MY_PASSWORD environment variables.")

        try:
            with self._open_connection() as connection:
                connection.login(my_email, password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=user_email_clean,
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
            if BREVO_API_KEY:
                if not owner_email:
                    raise ValueError("Missing MAIL_TO_EMAIL or MY_EMAIL for Brevo fallback delivery.") from exc
                self._send_with_brevo(user_email_clean, user_subject, msg_content)
                self._send_with_brevo(owner_email, owner_subject, my_msg_content)
                return
            if RESEND_API_KEY:
                if not owner_email:
                    raise ValueError("Missing MAIL_TO_EMAIL or MY_EMAIL for Resend fallback delivery.") from exc
                self._send_with_resend(user_email_clean, user_subject, msg_content)
                self._send_with_resend(owner_email, owner_subject, my_msg_content)
                return
            raise RuntimeError(
                "Mail delivery failed over SMTP. Configure BREVO_API_KEY/BREVO_SENDER_EMAIL or "
                "RESEND_API_KEY/MAIL_FROM_EMAIL to send mail over HTTPS, "
                "or verify outbound SMTP/TLS access on the host."
            ) from exc

