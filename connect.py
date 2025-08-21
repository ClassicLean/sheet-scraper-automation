from googleapiclient.discovery import build
from google.oauth2 import service_account
import os # Import os to use environment variables

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "sheet-scraper-as.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_service():
    """Authenticates and returns the Google Sheets API service object."""
    try:
        # Use environment variable for SPREADSHEET_ID if available, otherwise use hardcoded
        # This is for consistency with sheet_scraper.py's use of SPREADSHEET_ID
        spreadsheet_id = os.environ.get('SPREADSHEET_ID') or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw"

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=creds)
        return service
    except Exception as e:
        print(f"Error getting Google Sheets service: {e}")
        return None

# The test code below should be removed or commented out if you only want the function
# if __name__ == '__main__':
#     service = get_service()
#     if service:
#         # Test: Read values from the first sheet, first 10 rows
#         result = service.spreadsheets().values().get(
#             spreadsheetId=os.environ.get('SPREADSHEET_ID') or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw",
#             range="A1:A10"
#         ).execute()
#         values = result.get("values", [])
#         print(values)