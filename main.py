from flask import Flask, render_template
from flask import request
from mail_sender import NotificationManager
import os


def render_error_page(error, status_code=None):
    error_code = status_code if status_code is not None else getattr(error, 'code', 500)
    fallback_email = os.environ.get("MY_EMAIL", "sofia_fuentes_24@outlook.es")
    if error_code == 404:
        message = "La página solicitada no se encontró."
    elif error_code == 500:
        message = "Ocurrió un error interno al procesar la solicitud."
    else:
        message = "Ocurrió un problema al procesar la solicitud."

    return render_template("404.html", message=message, error_code=error_code, fallback_email=fallback_email), error_code

app = Flask(__name__)



mail_sender = NotificationManager()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/index.html")
def BackToIndex():
    return render_template("index.html")


@app.route("/my-contacts.html")
def myContacts():
    return render_template("my-contacts.html")


@app.errorhandler(404)
def not_found(error):
    return render_error_page(error, 404)


@app.errorhandler(500)
def internal_error(error):
    return render_error_page(error, 500)


@app.route('/my-contacts.html', methods=['POST'])
def contact_form():
    try:
        userEmail = request.form['userEmail']
        userName = request.form['userName']
        userName2 = request.form['userName2']
        userMessage = request.form['userMessage']


        # -------------------------------- USER EMAIL CONTENT ---------------------------------------
        msg_content = "Hello Dear,\n" \
                      f"Thank you for joining to our community!.\n\n" \
                      "Here is your user's Data:\n" \
                      "----------------------------------------------------------------------\n" \
                      f"email: {userEmail} \n" \
                      f"Name: {userName} \n" \
                      f"Last Name: {userName2} \n\n" \
                      f"----------------------------------------------------------------------\n" \
                      "Thanks Sincerely!\n\n" \
                      "--This is a Python automatic message--"

        # --------------------------------------------------------------------------------------

        # -------------------------------- MY EMAIL CONTENT ---------------------------------------
        my_msg_content = "Hello Dear,\n" \
                      f"A new user has loged in!.\n\n" \
                      "Here is the user's Data:\n" \
                      "----------------------------------------------------------------------\n" \
                      f"email: {userEmail} \n" \
                      f"Name: {userName} \n" \
                      f"Last Name: {userName2} \n\n" \
                      f"Message:\n{userMessage} \n" \
                      f"----------------------------------------------------------------------\n" \
                      "Thanks Sincerely!\n\n" \
                      "--This is a Python automatic message--"

        # --------------------------------------------------------------------------------------

        mail_sender.send_emails(msg_content, my_msg_content, userEmail)

        return render_template("successfully-message.html")

    except Exception as e:
        print(e)
        return render_error_page(e)





if __name__=='__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))