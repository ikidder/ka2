from flask import render_template, current_app
import boto3
from botocore.exceptions import ClientError
from .config import Config

client = boto3.client(
    'ses',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_REGION
)

SENDER = "kamagapē <noreply@kamagape.com>"
CHARSET = "UTF-8"


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        user.email,
        'kamagapē - Reset Your Password',
        html_body=render_template('emails/reset_password.html', user=user, token=token),
        text_body=render_template('emails/reset_password.txt', user=user, token=token),
    )


def send_email(to, subject, html_body, text_body):
    assert len(to.split('@')) == 2, "the To argument should only contain one email."

    if Config.ENVIRONMENT != "production":
        to = 'noreply@kamagape.com'

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    to,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': html_body,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': text_body,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])



# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the
# ConfigurationSetName=CONFIGURATION_SET argument below.
#CONFIGURATION_SET = "ConfigSet"



