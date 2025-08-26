"""
Google Sheets management operations.

This module contains the SheetManager class responsible for
managing Google Sheets operations and data updates.
"""

import time
import random
from datetime import datetime
from typing import List, Dict

from .data_models import ProductData, PriceUpdateResult
from .formatters import SheetFormatter
from ..scraping_utils import log_update
from ..core.sheet_operations import update_sheet
from ..config.constants import *
from ..logs_module.automation_logging import get_logger
from ..utils.logs_module import debug_print_column_x_update, debug_print_sheet_operation


class SheetManager:
    """Manages Google Sheets operations and data updates."""

    def __init__(self, service, spreadsheet_id: str):
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        self.formatter = SheetFormatter()
        self.logger = get_logger()

    def update_product_row(self, product_data: ProductData, update_result: PriceUpdateResult) -> bool:
        """
        Update a product row in the sheet with new data and formatting.

        Args:
            product_data: Original product data
            update_result: Results from product processing

        Returns:
            bool: True if update was successful
        """
        current_date = datetime.now().strftime("%m/%d/%Y")
        requests = []

        self.logger.info(f"Starting sheet update for row {product_data.row_index + 1}")
        self.logger.info(f"Product ID: {product_data.product_id}")
        self.logger.info(f"New VA Note: '{update_result.new_va_note}'")
        self.logger.info(f"Current date for last stock check: {current_date}")
        self.logger.info(f"Best supplier URL: {update_result.best_supplier_url}")

        # Add formatting requests
        formatting_requests = self.formatter.create_formatting_requests(
            product_data.row_index, product_data.row, update_result
        )
        requests.extend(formatting_requests)

        # Add data update requests
        data_requests = self._create_data_update_requests(
            product_data, update_result, current_date
        )
        requests.extend(data_requests)

        self.logger.info(f"Created {len(requests)} update requests total")
        self.logger.info(f"Data requests: {len(data_requests)}")

        # Execute all requests
        success = update_sheet(self.service, self.spreadsheet_id, requests)

        # Final debug output for Column X update result
        debug_print_column_x_update(
            product_data.row_index,
            product_data.old_price,
            update_result.new_price,
            PRICE_COL,
            update_success=success
        )

        self.logger.info(f"Sheet update result: {'SUCCESS' if success else 'FAILED'}")

        if success:
            # Log the update
            log_status = "Success" if update_result.best_supplier_url is not None else "Failed"
            log_message = (
                f"Chosen supplier: {update_result.chosen_supplier_name}"
                if log_status == "Success"
                else update_result.new_va_note
            )

            # Enhanced debugging for log_update
            from ..scraping_utils import debug_print_price_comparison
            debug_print_price_comparison(
                product_data.old_price or 0.0,
                update_result.new_price or 0.0,
                update_result.best_supplier_url or "No URL",
                f"Logging update: {log_status} - {log_message}"
            )

            log_update(
                product_data.product_id,
                product_data.old_price,
                update_result.new_price,
                log_status,
                log_message,
                row=product_data.row_index + 1,
            )

            # Add rate limiting delay
            print("Adding rate limiting delay after API call...")
            time.sleep(random.uniform(2.0, 4.0))
        else:
            # Enhanced debugging for failed update
            from ..scraping_utils import debug_print_scraping_failure
            debug_print_scraping_failure(
                product_data.product_id or "Unknown Product",
                "Sheet update failed",
                f"API call failed - new_price: {update_result.new_price}, old_price: {product_data.old_price}"
            )

            log_update(
                product_data.product_id,
                product_data.old_price,
                update_result.new_price,
                "Failed",
                "Sheet update error (API call failed)",
                row=product_data.row_index + 1,
            )

        return success

    def _create_data_update_requests(self, product_data: ProductData,
                                   update_result: PriceUpdateResult,
                                   current_date: str) -> List[Dict]:
        """Create data update requests for the sheet."""
        requests = []

        self.logger.info(f"Creating data update requests...")
        self.logger.info(f"VA_NOTES_COL = {VA_NOTES_COL} (Column A)")
        self.logger.info(f"LAST_STOCK_CHECK_COL = {LAST_STOCK_CHECK_COL} (Column D)")
        self.logger.info(f"Row index (0-based): {product_data.row_index}")
        self.logger.info(f"New VA Note: '{update_result.new_va_note}'")
        self.logger.info(f"Current date: '{current_date}'")

        # Update price column
        debug_print_column_x_update(
            product_data.row_index,
            product_data.old_price,
            update_result.new_price,
            PRICE_COL
        )

        debug_print_sheet_operation("Price Column Update", {
            "Target Column": f"Column {chr(65 + PRICE_COL)} (index {PRICE_COL})",
            "Row": product_data.row_index + 1,
            "Old Price": product_data.old_price,
            "New Price": update_result.new_price,
            "Price Type": type(update_result.new_price).__name__,
            "Is Valid Number": isinstance(update_result.new_price, (int, float)) and update_result.new_price != float("inf"),
            "Will Write As": "numberValue" if isinstance(update_result.new_price, (int, float)) and update_result.new_price != float("inf") else "stringValue (empty)"
        })

        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": product_data.row_index,
                    "endRowIndex": product_data.row_index + 1,
                    "startColumnIndex": PRICE_COL,
                    "endColumnIndex": PRICE_COL + 1,
                },
                "rows": [{
                    "values": [{
                        "userEnteredValue": (
                            {"numberValue": update_result.new_price}
                            if isinstance(update_result.new_price, (int, float)) and update_result.new_price != float("inf")
                            else {"stringValue": ""}
                        )
                    }]
                }],
                "fields": "userEnteredValue",
            }
        })

        # Update shipping column
        shipping_fee_value = update_result.chosen_shipping_fee if update_result.chosen_shipping_fee is not None else ""
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": product_data.row_index,
                    "endRowIndex": product_data.row_index + 1,
                    "startColumnIndex": COL_Z,
                    "endColumnIndex": COL_Z + 1,
                },
                "rows": [{
                    "values": [{
                        "userEnteredValue": (
                            {"numberValue": shipping_fee_value}
                            if isinstance(shipping_fee_value, (int, float))
                            else {"stringValue": str(shipping_fee_value) if shipping_fee_value else ""}
                        )
                    }]
                }],
                "fields": "userEnteredValue",
            }
        })

        # Update VA Notes column
        va_notes_request = {
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": product_data.row_index,
                    "endRowIndex": product_data.row_index + 1,
                    "startColumnIndex": VA_NOTES_COL,
                    "endColumnIndex": VA_NOTES_COL + 1,
                },
                "rows": [{"values": [{"userEnteredValue": {"stringValue": update_result.new_va_note}}]}],
                "fields": "userEnteredValue",
            }
        }
        self.logger.info(f"VA Notes update request: Row {product_data.row_index + 1}, Col A, Value: '{update_result.new_va_note}'")
        requests.append(va_notes_request)

        # Update supplier URL column
        supplier_url_to_update = update_result.best_supplier_url if update_result.best_supplier_url is not None else ""
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": product_data.row_index,
                    "endRowIndex": product_data.row_index + 1,
                    "startColumnIndex": PRODUCT_ID_COL,
                    "endColumnIndex": PRODUCT_ID_COL + 1,
                },
                "rows": [{"values": [{"userEnteredValue": {"stringValue": supplier_url_to_update}}]}],
                "fields": "userEnteredValue",
            }
        })

        # Update last stock check column
        last_check_request = {
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": product_data.row_index,
                    "endRowIndex": product_data.row_index + 1,
                    "startColumnIndex": LAST_STOCK_CHECK_COL,
                    "endColumnIndex": LAST_STOCK_CHECK_COL + 1,
                },
                "rows": [{"values": [{"userEnteredValue": {"stringValue": current_date}}]}],
                "fields": "userEnteredValue",
            }
        }
        self.logger.info(f"Last stock check update request: Row {product_data.row_index + 1}, Col D, Value: '{current_date}'")
        requests.append(last_check_request)

        self.logger.info(f"Created {len(requests)} data update requests total")
        return requests
