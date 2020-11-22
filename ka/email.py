from flask import render_template, current_app
from ka.config import Config
import requests
import json


def send_password_reset_email(user, token):
    send_email(
        user.email,
        'kamagapē - Reset Your Password',
        render_template('emails/reset_password.html', user=user, token=token),
        track=False
    )


def send_welcome_email(user, token):
    send_email(
        user.email,
        'Welcome to kamagapē!',
        render_template('emails/welcome.html', user=user, token=token),
    )


def send_invite_email(invite):
    send_email(
        invite.to_email,
        "You've been invited to kamagapē!",
        render_template('emails/invitation.html', token=invite.token())
    )


def send_email(to, subject, body, track=True):
    if Config.ENVIRONMENT != 'production':
        new_to = 'i@kamagape.com'
        print(f"Warning: rewriting email addr {to} to {new_to}.")
        to = new_to

    headers = {
        'Content-Type': 'application/json',
        'Authorization': Config.SPARKPOST_API_KEY,
    }
    data = {
        "options": {
            "click_tracking": track,
            "transactional": not track,
            "inline_css": True
        },
        "content":
            {
                "from": {
                    "name": Config.SPARKPOST_FROM_NAME,
                    "email": Config.SPARKPOST_FROM_ADDRESS
                },
                "reply_to": Config.SPARKPOST_REPLY_TO,
                "subject": subject,
                "html": body
            },
        "recipients": [{"address": to}]
    }
    response = requests.post(
        Config.SPARKPOST_ENDPOINT,
        headers=headers,
        data=json.dumps(data)
    )
    return response


# def send_email(to, subject, html_body, text_body):
#     assert len(to.split('@')) == 2, "the To argument should only contain one email."
#
#     if Config.ENVIRONMENT != "production":
#         to = 'noreply@kamagape.com'
#
#     try:
#         response = client.send_email(
#             Destination={
#                 'ToAddresses': [
#                     to,
#                 ],
#             },
#             Message={
#                 'Body': {
#                     'Html': {
#                         'Charset': CHARSET,
#                         'Data': html_body,
#                     },
#                     'Text': {
#                         'Charset': CHARSET,
#                         'Data': text_body,
#                     },
#                 },
#                 'Subject': {
#                     'Charset': CHARSET,
#                     'Data': subject,
#                 },
#             },
#             Source=SENDER,
#             # If you are not using a configuration set, comment or delete the
#             # following line
#             #ConfigurationSetName=CONFIGURATION_SET,
#         )
#     except ClientError as e:
#         print(e.response['Error']['Message'])
#     else:
#         print("Email sent! Message ID:"),
#         print(response['MessageId'])



# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the
# ConfigurationSetName=CONFIGURATION_SET argument below.
#CONFIGURATION_SET = "ConfigSet"



