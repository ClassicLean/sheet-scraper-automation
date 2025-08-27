"""
Google Sheets management operations.

This module contains the SheetManager class responsible for
managing Google Sheets operations and data updates.
"""

import random
import time
from datetime import datetime

from ..config.constants import (
    COL_Z,
    LAST_STOCK_CHECK_COL,
    PRICE_COL,
    PRODUCT_ID_COL,
    VA_NOTES_COL,
)
from ..core.sheet_operations import update_sheet
from ..logs_module.automation_logging import get_logger
from ..scraping_utils import log_update
from ..utils.logs_module import debug_print_column_x_update, debug_print_sheet_operation
from .data_models import PriceUpdateResult, ProductData
from .formatters import SheetFormatter


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
        current_date = datetime.now().strftime("%m/%d")
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

        # Always update the date, regardless of price scraping success/failure
        # This provides an audit trail of when we last checked each product
        date_success = self._update_last_check_date_only(product_data, current_date)
        self._date_update_succeeded = date_success  # Store for logging

        # Handle price updates based on scraping results
        if update_result.new_price is None:
            success = False
            self.logger.info("Marking as failure: No price data was successfully scraped")
            self.logger.info(f"Date update {'succeeded' if date_success else 'failed'}")
        else:
            # Execute all price/data requests (excluding date since it's already updated)
            price_requests = [req for req in requests if not self._is_date_update_request(req)]
            success = update_sheet(self.service, self.spreadsheet_id, price_requests)
            self.logger.info(f"Price update {'succeeded' if success else 'failed'}, Date update {'succeeded' if date_success else 'failed'}")
            # Consider overall success if either date or price updates succeeded
            success = success or date_success

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
            # Determine log status based on comprehensive criteria
            price_extracted = update_result.new_price is not None and update_result.new_price > 0
            price_changed = price_extracted and abs(update_result.new_price - (product_data.old_price or 0)) > 0.01
            supplier_found = update_result.best_supplier_url is not None

            # Best practice: Multi-layered success determination
            if supplier_found and price_extracted:
                if price_changed:
                    log_status = "Success"
                    log_message = f"Price updated: ${product_data.old_price} → ${update_result.new_price} ({update_result.chosen_supplier_name})"
                else:
                    log_status = "Success"
                    log_message = f"Price confirmed unchanged: ${update_result.new_price} ({update_result.chosen_supplier_name})"
            elif not supplier_found:
                # When no suppliers found valid prices, this should be treated as failure
                # But note that date update may have succeeded
                log_status = "Failed"
                if update_result.new_price is None and hasattr(self, '_date_update_succeeded') and self._date_update_succeeded:
                    log_message = f"All suppliers failed, but date updated: {update_result.new_va_note or 'No valid price data found'}"
                else:
                    log_message = f"All suppliers failed: {update_result.new_va_note or 'No valid price data found'}"
            else:
                log_status = "Failed"
                log_message = f"Price extraction failed: {update_result.new_va_note or 'No price data available'}"

            # Enhanced debugging for comprehensive status determination
            from ..scraping_utils import debug_print_price_comparison
            debug_print_price_comparison(
                product_data.old_price or 0.0,
                update_result.new_price or 0.0,
                update_result.best_supplier_url or "No URL",
                f"Status determination: {log_status} - {log_message}"
            )

            # Additional debugging for status logic
            from ..utils.logs_module import debug_print_scraping_attempt
            debug_print_scraping_attempt(
                product_data.product_id or "Unknown Product",
                f"Status Determination: {log_status}",
                {
                    "price_extracted": price_extracted,
                    "price_changed": price_changed,
                    "supplier_found": supplier_found,
                    "old_price": product_data.old_price,
                    "new_price": update_result.new_price,
                    "message": log_message
                }
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

            # Determine failure message based on what succeeded
            if hasattr(self, '_date_update_succeeded') and self._date_update_succeeded:
                failure_message = "Price scraping failed, but date updated successfully"
            else:
                failure_message = "Sheet update error (API call failed)"

            log_update(
                product_data.product_id,
                product_data.old_price,
                update_result.new_price,
                "Failed",
                failure_message,
                row=product_data.row_index + 1,
            )

        return success

    def _create_data_update_requests(self, product_data: ProductData,
                                   update_result: PriceUpdateResult,
                                   current_date: str) -> list[dict]:
        """Create data update requests for the sheet."""
        requests = []

        self.logger.info("Creating data update requests...")
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
            "Is Valid Number": isinstance(update_result.new_price, int | float) and update_result.new_price != float("inf"),
            "Will Write As": "numberValue" if isinstance(update_result.new_price, int | float) and update_result.new_price != float("inf") else "stringValue (empty)"
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
                            if isinstance(update_result.new_price, (int, float)) and update_result.new_price is not None and update_result.new_price != float("inf")
                            else {"stringValue": "No Data" if update_result.new_price is None else ""}
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
                            if isinstance(shipping_fee_value, int | float)
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

    def _update_last_check_date_only(self, product_data: ProductData, current_date: str) -> bool:
        """Update only the last check date column, independent of price updates."""
        try:
            date_request = {
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

            self.logger.info(f"Updating last check date for row {product_data.row_index + 1}")
            result = update_sheet(self.service, self.spreadsheet_id, [date_request])
            self.logger.info(f"Date update result: {'SUCCESS' if result else 'FAILED'}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to update last check date: {e}")
            return False

    def _is_date_update_request(self, request: dict) -> bool:
        """Check if a request is for updating the date column."""
        try:
            update_cells = request.get("updateCells", {})
            range_info = update_cells.get("range", {})
            start_col = range_info.get("startColumnIndex")
            return start_col == LAST_STOCK_CHECK_COL
        except:
            return False
