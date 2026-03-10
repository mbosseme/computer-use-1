import os
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import base64

class GmailClient:
    """
    A client for interacting with Google Gmail API, specifically for reading emails.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_path: str, token_path: str):
        """
        Initialize the GmailClient.
        
        Args:
            credentials_path (str): Path to the credentials.json file (OAuth 2.0 Client ID).
            token_path (str): Path to store/retrieve the token.json file.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        
    def authenticate(self) -> None:
        """
        Authenticate with Gmail using OAuth 2.0.
        Uses a local server flow for initial authentication and saves the token.
        """
        creds = None
        
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                     print(f"Error refreshing token: {e}. Re-authenticating.")
                     creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at: {self.credentials_path}")
                
                print("Initiating OAuth 2.0 flow. Your browser should open to log in.")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
                
        self.service = build('gmail', 'v1', credentials=creds)
        print("Authentication successful.")

    def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for messages matching the query.
        
        Args:
            query (str): The search query (e.g., "from:someone@example.com subject:meeting").
            max_results (int): Maximum number of results to return.
            
        Returns:
            List[Dict]: A list of message objects (containing id and threadId).
        """
        if not self.service:
            self.authenticate()
            
        print(f"Searching Gmail with query: '{query}'")
        
        try:
            # Execute the search
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            print(f"Found {len(messages)} messages.")
            return messages
            
        except Exception as e:
            print(f"An error occurred during search: {e}")
            raise

    def get_message_details(self, message_id: str) -> Dict[str, Any]:
        """
        Get details of a specific message.
        
        Args:
            message_id (str): The ID of the message to retrieve.
            
        Returns:
            Dict: The message resource including snippet and payload.
        """
        if not self.service:
            self.authenticate()
            
        try:
            # 'full' format returns payload with headers and body
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id, 
                format='full'
            ).execute()
            
            return message
        except Exception as e:
            print(f"An error occurred getting message details: {e}")
            raise

    @staticmethod
    def extract_header(message_details: Dict[str, Any], header_name: str) -> Optional[str]:
        """Helper to extract a specific header value from message details."""
        payload = message_details.get('payload', {})
        headers = payload.get('headers', [])
        for h in headers:
            if h.get('name', '').lower() == header_name.lower():
                return h.get('value')
        return None

    @staticmethod
    def extract_body_text(message_details: Dict[str, Any]) -> str:
        """
        Helper to extract plain text body from message details.
        Handles multipart messages to find text/plain parts.
        """
        payload = message_details.get('payload', {})
        parts = payload.get('parts', [])
        
        # If no parts, body might be in payload itself
        if not parts:
            data = payload.get('body', {}).get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
            return ""

        # Recursive search for text/plain
        def get_text_from_parts(parts_list):
            for part in parts_list:
                mime_type = part.get('mimeType')
                if mime_type == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
                
                # Nested parts
                if part.get('parts'):
                    found = get_text_from_parts(part.get('parts'))
                    if found:
                        return found
            return None

        # Try to find plain text
        text = get_text_from_parts(parts)
        if text:
            return text
            
        # Fallback to snippet if body parse fails
        return message_details.get('snippet', "")

