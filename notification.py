"""
This lovely file is to notify the user of when training is complete via Gmail's SMTP service
"""

import ssl, smtplib, keyring
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

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
               f"\n"
               f"Market Saver RL")

    # Plug text into email
    part1 = MIMEText(msg_txt, "plain")
    message.attach(part1)

    # Grab our logs for today
    # train log
    with open(f"logs/train_{datetime.today().strftime('%Y-%m-%d')}.log", 'rb') as file:
        file_name = f"train_{datetime.today().strftime('%Y-%m-%d')}.log"
        part2 = MIMEApplication(file.read(), name=file_name)
        part2['Content-Disposition'] = f'attachment; filename="{file_name}'

    message.attach(part2)

    # Eval log
    with open(f"logs/eval_{datetime.today().strftime('%Y-%m-%d')}.log", 'rb') as file:
        file_name = f"eval_{datetime.today().strftime('%Y-%m-%d')}.log"
        part3 = MIMEApplication(file.read(), name=file_name)
        part3['Content-Disposition'] = f'attachment; filename="{file_name}'

    message.attach(part3)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, recipient, message.as_string()
        )


def send_error_notification(recipient, ticker, error):
    """ Dang it something is wrong email """
    message = MIMEMultipart("alternative")
    message["Subject"] = "Training Failed"
    message["From"] = sender_email
    message["To"] = recipient

    msg_txt = (f"Hello!"
               f"\n\n"
               f"Training failed for {ticker} with error {error}! "
               f"\n\n"
               f"Review logs and try again."
               f"\n\n"
               f"Thanks,"
               f"\n"
               f"Market Saver RL")

    # Plug text into email
    part1 = MIMEText(msg_txt, "plain")
    message.attach(part1)

    # train log
    with open(f"logs/train_{datetime.today().strftime('%Y-%m-%d')}.log", 'rb') as file:
        file_name = f"train_{datetime.today().strftime('%Y-%m-%d')}.log"
        part2 = MIMEApplication(file.read(), name=file_name)
        part2['Content-Disposition'] = f'attachment; filename="{file_name}'

    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, recipient, message.as_string()
        )

