from googleapiclient.discovery import build
from google.oauth2 import service_account
import os  # Import os to use environment variables

# Path to your service account key file - use absolute path from project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "sheet-scraper-as.json")
SERVICE_ACCOUNT_FILE = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", DEFAULT_CONFIG_PATH
)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_service():
    """Authenticates and returns the Google Sheets API service object."""
    try:
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
