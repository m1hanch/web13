import smtplib
from pathlib import Path
from src.conf.config import config
from src.services.auth import auth_service
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape

MAIL_USERNAME = config.MAIL_USERNAME
MAIL_PASSWORD = config.MAIL_PASSWORD
MAIL_FROM = config.MAIL_FROM
MAIL_PORT = config.MAIL_PORT
MAIL_SERVER = config.MAIL_SERVER
MAIL_FROM_NAME = "Web hw13"
TEMPLATE_FOLDER = Path(__file__).parent / 'templates'

env = Environment(
    loader=FileSystemLoader(TEMPLATE_FOLDER),
    autoescape=select_autoescape(['html', 'xml'])
)


def render_template(template_name, **template_vars):
    template = env.get_template(template_name)
    return template.render(**template_vars)


async def send_email(email, username, host):
    try:
        # Create the email token
        token_verification = auth_service.create_email_token({"sub": email})

        # Create the message
        message = EmailMessage()
        message["From"] = MAIL_FROM
        message["To"] = email
        message["Subject"] = "Confirm your email"

        # You might want to use a templating engine like Jinja2 to render HTML emails
        html = render_template('verify_email.html', host=host, username=username, token=token_verification)
        message.set_content(html, subtype='html')

        # Connect to the server and send the email
        with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(message)

    except Exception as err:
        print(err)


async def send_reset_password_email(email, host):
    try:
        # Create the email token
        token_verification = auth_service.create_email_token({"sub": email})

        # Create the message
        message = EmailMessage()
        message["From"] = MAIL_FROM
        message["To"] = email
        message["Subject"] = "Reset your password"

        # You might want to use a templating engine like Jinja2 to render HTML emails
        html = render_template('reset_password_email.html', host=host, token=token_verification)
        message.set_content(html, subtype='html')

        # Connect to the server and send the email
        with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(message)

    except Exception as err:
        print(err)
