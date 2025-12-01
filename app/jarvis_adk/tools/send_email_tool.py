"""
Simple email sending tool for Jarvis agent.
"""
import base64
from email.mime.text import MIMEText
from pathlib import Path
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Path for token storage
GMAIL_TOKEN_PATH = Path(os.path.expanduser("~/.credentials/gmail_token.json"))
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"


def get_gmail_service():
    """Get authenticated Gmail service."""
    creds = None
    
    if GMAIL_TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_info(
            json.loads(GMAIL_TOKEN_PATH.read_text()), SCOPES
        )
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        GMAIL_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        GMAIL_TOKEN_PATH.write_text(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def send_email(to: str, subject: str, body: str) -> dict:
    """
    Send an email using Gmail API.
    
    Args:
        to (str): Recipient email address
        subject (str): Email subject
        body (str): Email body text
        
    Returns:
        dict: Status information
    """
    try:
        service = get_gmail_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Gmail. Please check credentials."
            }
        
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return {
            "status": "success",
            "message": f"Email sent successfully to {to}",
            "message_id": result.get('id', '')
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}"
        }
