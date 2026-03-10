import os
import io
from typing import Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

class GoogleDriveClient:
    """
    A client for interacting with Google Drive API, specifically for downloading files.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, credentials_path: str, token_path: str):
        """
        Initialize the GoogleDriveClient.
        
        Args:
            credentials_path (str): Path to the credentials.json file (OAuth 2.0 Client ID).
            token_path (str): Path to store/retrieve the token.json file.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        
    def authenticate(self) -> None:
        """
        Authenticate with Google Drive using OAuth 2.0.
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
                
        self.service = build('drive', 'v3', credentials=creds)
        print("Authentication successful.")

    def download_file(self, file_id: str, output_path: str, mime_type: str = None) -> str:
        """
        Download a file from Google Drive.
        
        Args:
            file_id (str): The Google Drive file ID.
            output_path (str): The local path to save the file.
            mime_type (str, optional): The MIME type to export to (for Google Docs/Sheets).
                                     If None, attempts to download the binary content directly.
                                     
        Returns:
            str: The path to the downloaded file.
        """
        if not self.service:
            self.authenticate()
            
        print(f"Downloading file ID: {file_id} to {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            if mime_type:
                # Export Google Workspace document (Sheet, Doc, Slide)
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType=mime_type
                )
            else:
                # Download binary file
                request = self.service.files().get_media(fileId=file_id)
                
            with io.FileIO(output_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    # Optional: print progress
                    # print(f"Download {int(status.progress() * 100)}%.")
                    
            print(f"Successfully downloaded to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"An error occurred during download: {e}")
            raise

    def list_files(self, query: str = None, page_size: int = 10) -> List[dict]:
        """
        List files in Google Drive.
        """
        if not self.service:
            self.authenticate()
            
        results = self.service.files().list(
            q=query, pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
        return results.get('files', [])
