from googleapiclient.discovery import build
from google.oauth2 import service_account

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "sheet-scraper-as.json"  # update this to your file path
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Spreadsheet ID (the long string in your Google Sheet URL)
SPREADSHEET_ID = "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw"

# Authenticate
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the Sheets API service
service = build("sheets", "v4", credentials=creds)

# Test: Read values from the first sheet, first 10 rows
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range="A1:A10"
).execute()

values = result.get("values", [])
print(values)
