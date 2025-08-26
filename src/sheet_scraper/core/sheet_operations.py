"""
Google Sheets Operations Module

This module handles all Google Sheets API operations including reading data,
updating cells, and applying formatting. It provides a clean interface for
interacting with Google Sheets while encapsulating the API complexity.

Best Practices Implemented:
- Single Responsibility: Only Google Sheets operations
- Error Handling: Comprehensive error handling with retries
- Interface Segregation: Small, focused functions
- Documentation: Clear function purposes and parameters
"""

import time
import random
from typing import List, Dict, Any, Optional, Tuple
from googleapiclient.errors import HttpError

from ..scraping_utils import debug_print


class SheetsAPIError(Exception):
    """Custom exception for Google Sheets API errors."""
    pass


class SheetOperations:
    """Handles all Google Sheets API operations with error handling and retries."""

    def __init__(self, service, spreadsheet_id: str):
        """
        Initialize Sheet Operations.

        Args:
            service: Google Sheets API service instance
            spreadsheet_id: The ID of the spreadsheet to operate on
        """
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        self.max_retries = 3
        self.base_delay = 1.0

    def read_sheet_data(self, range_name: str = "FBMP!A1:AN1000") -> List[List[str]]:
        """
        Read data from a Google Sheet with retry logic.

        Args:
            range_name: The range to read (e.g., "FBMP!A1:AN1000")

        Returns:
            List of rows, where each row is a list of cell values

        Raises:
            SheetsAPIError: If the operation fails after retries
        """
        debug_print(f"DEBUG: Reading sheet data from range: {range_name}")

        for attempt in range(self.max_retries):
            try:
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name
                ).execute()

                values = result.get("values", [])
                debug_print(f"DEBUG: Successfully read {len(values)} rows from sheet")
                return values

            except HttpError as e:
                if attempt == self.max_retries - 1:
                    raise SheetsAPIError(f"Failed to read sheet data after {self.max_retries} attempts: {e}")

                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                debug_print(f"DEBUG: Read attempt {attempt + 1} failed, retrying in {delay:.2f}s")
                time.sleep(delay)

            except Exception as e:
                raise SheetsAPIError(f"Unexpected error reading sheet data: {e}")

    def batch_update_cells(self, requests: List[Dict[str, Any]]) -> bool:
        """
        Perform batch updates on the sheet with retry logic.

        Args:
            requests: List of batch update requests

        Returns:
            True if successful, False otherwise

        Raises:
            SheetsAPIError: If the operation fails after retries
        """
        if not requests:
            debug_print("DEBUG: No requests to process")
            return True

        debug_print(f"DEBUG: Performing batch update with {len(requests)} requests")

        for attempt in range(self.max_retries):
            try:
                body = {"requests": requests}

                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                ).execute()

                debug_print("DEBUG: Batch update successful")

                # Add rate limiting delay
                delay = random.uniform(2.0, 4.0)
                debug_print(f"DEBUG: Adding rate limiting delay: {delay:.2f}s")
                time.sleep(delay)

                return True

            except HttpError as e:
                error_code = e.resp.status if hasattr(e, 'resp') else 'Unknown'

                if error_code == 429:  # Rate limit exceeded
                    delay = self.base_delay * (2 ** attempt) + random.uniform(2, 5)
                    debug_print(f"DEBUG: Rate limit hit, retrying in {delay:.2f}s")
                    time.sleep(delay)
                    continue

                if attempt == self.max_retries - 1:
                    raise SheetsAPIError(f"Failed to update sheet after {self.max_retries} attempts: {e}")

                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                debug_print(f"DEBUG: Update attempt {attempt + 1} failed, retrying in {delay:.2f}s")
                time.sleep(delay)

            except Exception as e:
                raise SheetsAPIError(f"Unexpected error updating sheet: {e}")

        return False

    def update_single_cell(self, cell_range: str, value: Any) -> bool:
        """
        Update a single cell value.

        Args:
            cell_range: Cell address (e.g., "A1" or "Sheet1!A1")
            value: Value to set in the cell

        Returns:
            True if successful, False otherwise
        """
        debug_print(f"DEBUG: Updating single cell {cell_range} with value: {value}")

        try:
            body = {
                "values": [[value]]
            }

            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=cell_range,
                valueInputOption="RAW",
                body=body
            ).execute()

            debug_print(f"DEBUG: Successfully updated cell {cell_range}")
            return True

        except Exception as e:
            debug_print(f"DEBUG: Failed to update cell {cell_range}: {e}")
            return False

    def format_cells(self, formatting_requests: List[Dict[str, Any]]) -> bool:
        """
        Apply formatting to cells.

        Args:
            formatting_requests: List of formatting requests

        Returns:
            True if successful, False otherwise
        """
        if not formatting_requests:
            return True

        debug_print(f"DEBUG: Applying formatting with {len(formatting_requests)} requests")

        try:
            return self.batch_update_cells(formatting_requests)
        except Exception as e:
            debug_print(f"DEBUG: Failed to apply formatting: {e}")
            return False

    def clear_range(self, range_name: str) -> bool:
        """
        Clear values in a specified range.

        Args:
            range_name: Range to clear (e.g., "A1:Z100")

        Returns:
            True if successful, False otherwise
        """
        debug_print(f"DEBUG: Clearing range: {range_name}")

        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()

            debug_print(f"DEBUG: Successfully cleared range {range_name}")
            return True

        except Exception as e:
            debug_print(f"DEBUG: Failed to clear range {range_name}: {e}")
            return False

    def get_sheet_properties(self) -> Dict[str, Any]:
        """
        Get sheet properties and metadata.

        Returns:
            Dictionary containing sheet properties
        """
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()

            debug_print("DEBUG: Successfully retrieved sheet properties")
            return sheet_metadata

        except Exception as e:
            debug_print(f"DEBUG: Failed to get sheet properties: {e}")
            return {}


# Convenience functions for backward compatibility
def read_sheet_data(service, spreadsheet_id: str, range_name: str = "FBMP!A1:AN1000") -> List[List[str]]:
    """
    Backward compatibility function for reading sheet data.

    Args:
        service: Google Sheets API service
        spreadsheet_id: Spreadsheet ID
        range_name: Range to read

    Returns:
        List of rows from the sheet
    """
    sheet_ops = SheetOperations(service, spreadsheet_id)
    return sheet_ops.read_sheet_data(range_name)


def update_sheet(service, spreadsheet_id: str, requests: List[Dict[str, Any]]) -> bool:
    """
    Backward compatibility function for batch updates.

    Args:
        service: Google Sheets API service
        spreadsheet_id: Spreadsheet ID
        requests: List of update requests

    Returns:
        True if successful, False otherwise
    """
    sheet_ops = SheetOperations(service, spreadsheet_id)
    return sheet_ops.batch_update_cells(requests)
