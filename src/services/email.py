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
    """
    The render_template function takes a template name and a variable list of
    template variables and returns the rendered template as a string.


    :param template_name: Specify the name of the template to be rendered
    :param **template_vars: Pass in a dictionary of variables to the template
    :return: A string
    :doc-author: Trelent
    """
    template = env.get_template(template_name)
    return template.render(**template_vars)


async def send_email(email, username, host):
    """
    The send_email function sends an email to the user with a link that they can click on to verify their email address.
    The function takes in three arguments:
        - The user's email address (email)
        - The username of the user (username)
        - The hostname of the server where this application is running (host). This will be used for constructing links.

    :param email: Send the email to
    :param username: Display the username in the email
    :param host: Create a link to the verification page
    :return: A coroutine, so we need to await it
    :doc-author: Trelent
    """
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
    """
    The send_reset_password_email function sends an email to the user with a link to reset their password.

    :param email: Identify the user in the database
    :param host: Create the link to reset the password
    :return: A token
    :doc-author: Trelent
    """
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
