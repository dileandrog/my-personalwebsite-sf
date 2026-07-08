from flask import Flask, render_template
from flask import request
from mail_sender import NotificationManager
import os

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
        return render_template("404.html", message=e)





if __name__=='__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))