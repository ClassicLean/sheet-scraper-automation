"""
Google Sheets operations utilities.

This module contains functions for reading from and writing to Google Sheets,
including batch operations and formatting.
"""

import random
import time
from typing import Optional, List, Dict, Any

from googleapiclient.errors import HttpError


def read_sheet_data(service, spreadsheet_id: str, sheet_name: str) -> Optional[List[List[str]]]:
    """
    Read data from a Google Sheet.

    Args:
        service: Google Sheets service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet

    Returns:
        List of rows or None if error occurred
    """
    try:
        result = (
            service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=[f"{sheet_name}!A:AQ"],
            )
            .execute()
        )
        return result.get("valueRanges", [{}])[0].get("values", [])
    except Exception as e:
        print(f"Error reading sheet data: {e}")
        return None


def update_sheet(service, spreadsheet_id: str, requests: List[Dict[str, Any]]) -> bool:
    """
    Update sheet with exponential backoff and retry logic for quota exhaustion.

    Args:
        service: Google Sheets service instance
        spreadsheet_id: ID of the spreadsheet
        requests: List of batch update requests

    Returns:
        bool: True if successful, False otherwise
    """
    max_retries = 5
    base_delay = 1.0  # Start with 1 second

    for attempt in range(max_retries):
        try:
            print(f"Attempting sheet update (attempt {attempt + 1}/{max_retries}) with {len(requests)} requests...")

            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": requests},
            ).execute()

            print("Sheet update successful!")
            return True

        except HttpError as e:
            if e.resp.status == 429:  # Quota exhausted
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"API quota exhausted (429 error). Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"API quota exhausted after {max_retries} attempts. Giving up.")
                    print(f"Error details: {e}")
                    return False
            else:
                print(f"API error (status {e.resp.status}): {e}")
                return False

        except Exception as e:
            print(f"Unexpected error updating sheet: {e}")
            return False

    return False


def create_color_request(
    row_index: int,
    background_color: Optional[Dict[str, float]] = None,
    col_index: Optional[int] = None,
    text_color: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Create a color formatting request for a Google Sheet cell or row.

    Args:
        row_index: Row index (0-based)
        background_color: Background color dict with RGB values (0-1)
        col_index: Column index (0-based), None for entire row
        text_color: Text color dict with RGB values (0-1)

    Returns:
        Dict: Formatted request for Google Sheets API
    """
    cell_format = {}
    fields = ""

    if background_color:
        cell_format["backgroundColor"] = background_color
        fields += "userEnteredFormat.backgroundColor"

    if text_color:
        cell_format["textFormat"] = {"foregroundColor": text_color}
        if fields:
            fields += ","
        fields += "userEnteredFormat.textFormat.foregroundColor"

    range_dict = {
        "sheetId": 0,
        "startRowIndex": row_index,
        "endRowIndex": row_index + 1,
    }

    if col_index is not None:
        range_dict["startColumnIndex"] = col_index
        range_dict["endColumnIndex"] = col_index + 1

    return {
        "repeatCell": {
            "range": range_dict,
            "cell": {"userEnteredFormat": cell_format},
            "fields": fields,
        }
    }
