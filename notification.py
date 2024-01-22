"""
This lovely file is to notify the user of when training is complete via Gmail's SMTP service
"""

import ssl, smtplib, keyring
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "hermitnotifs@gmail.com"
# set password with keyring.set_password('market_saver', 'your gmail', 'password')
password = keyring.get_password('market_saver', 'hermitnotifs')


def send_training_notification(recipient, ticker):
    """ Send training finished email """
    message = MIMEMultipart("alternative")
    message["Subject"] = "Training Successful"
    message["From"] = sender_email
    message["To"] = recipient

    msg_txt = (f"Hello!"
               f"\n\n"
               f"Training has completed for {ticker}!"
               f"\n\n"
               f"Thanks,"
               f"Market Saver RL")

    # Plug text into email
    part1 = MIMEText(msg_txt, "plain")
    message.attach(part1)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, recipient, message.as_string()
        )


def send_error_notification(recipient, ticker):
    """ Dang it something is wrong email """
    message = MIMEMultipart("alternative")
    message["Subject"] = "Training Failed"
    message["From"] = sender_email
    message["To"] = recipient

    msg_txt = (f"Hello!"
               f"\n\n"
               f"Training failed for {ticker}! Review logs and try again"
               f"\n\n"
               f"Thanks,"
               f"Market Saver RL")

    # Plug text into email
    part1 = MIMEText(msg_txt, "plain")
    message.attach(part1)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, recipient, message.as_string()
        )

