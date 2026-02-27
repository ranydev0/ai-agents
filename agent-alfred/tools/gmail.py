import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from smolagents import tool

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_TOKEN_PATH = os.path.join(_TOOLS_DIR, "token.json")
_CREDENTIALS_PATH = os.path.join(_TOOLS_DIR, "credentials.json")


def _authenticate():
    """Authenticate with the Gmail API and return an authorised service client."""
    creds = None

    if os.path.exists(_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(_TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(_TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


_service = _authenticate()


@tool
def create_draft_email(message: str, receiver: str, subject: str) -> str:
    """Compose and save a new Gmail draft without sending it.

    Use this tool when the user wants to write an email but review or edit
    it before sending, or when explicitly asked to create a draft. Do NOT
    use this tool if the user wants to send an email immediately.

    Args:
        message (str): The plain-text body of the email
            (e.g. "Hi Alice,\\n\\nJust checking in.\\n\\nBest,\\nBob").
        receiver (str): The recipient's email address
            (e.g. "alice@example.com").
        subject (str): The subject line of the email
            (e.g. "Meeting tomorrow at 10 am").

    Returns:
        str: Confirmation message with the draft ID on success,
             or an error message if the draft could not be created.

    Raises:
        HttpError: Raised by the Gmail API client when the request fails
            (e.g. invalid credentials, network error, or quota exceeded).
    """
    try:
        email = EmailMessage()
        email.set_content(message)
        email["To"] = receiver
        email["Subject"] = subject

        encoded = base64.urlsafe_b64encode(email.as_bytes()).decode()
        body = {"message": {"raw": encoded}}

        draft = _service.users().drafts().create(userId="me", body=body).execute()

        return f"Draft created successfully with ID: {draft['id']}"

    except HttpError as error:
        return f"Failed to create draft: {error}"
