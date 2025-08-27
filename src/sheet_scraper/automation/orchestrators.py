"""
High-level automation orchestrators.

This module contains orchestration classes that coordinate the overall
automation process and manage component interactions.
"""

import os

from ..config.config_manager import Config
from ..config.constants import (
    PRICE_COL,
    PRODUCT_ID_COL,
)
from ..core.product_processing import ProductDataProcessor
from ..core.sheet_operations import SheetOperations, read_sheet_data
from ..logs_module.automation_logging import get_logger
from ..scraping_utils import LOG_FILE, debug_print, parse_price, truncate_log_file
from .data_models import ProductData
from .processors import ProductProcessor
from .sheet_managers import SheetManager
from .stats import AutomationStats


class SheetScraperAutomation:
    """Main automation orchestrator that coordinates all components."""

    def __init__(self, page, captcha_solver, config: Config,
                 browser_manager, sheet_service, spreadsheet_id: str):
        self.page = page
        self.captcha_solver = captcha_solver
        self.config = config
        self.browser_manager = browser_manager
        self.stats = AutomationStats()

        # Initialize utility modules
        self.logger = get_logger()
        self.sheet_operations = SheetOperations(sheet_service, spreadsheet_id)
        self.product_processor_util = ProductDataProcessor()

        # Initialize components
        self.product_processor = ProductProcessor(page, captcha_solver, browser_manager, config)
        self.sheet_manager = SheetManager(sheet_service, spreadsheet_id)

    def run_automation(self, start_row_index: int | None = None,
                      end_row_index: int | None = None):
        """
        Run the complete automation process.

        Args:
            start_row_index: Starting row (0-based), None for default
            end_row_index: Ending row (1-based), None for default
        """
        print("=== Starting Enhanced Sheet Scraper Automation ===")
        self.logger.info("[ORCHESTRATOR DEBUG]: run_automation method called!")
        self.logger.info(f"[ORCHESTRATOR DEBUG]: start_row_index={start_row_index}, end_row_index={end_row_index}")

        try:
            # Load sheet data
            self.logger.info("[ORCHESTRATOR DEBUG]: About to call _load_sheet_data()")
            sheet_data = self._load_sheet_data()
            self.logger.info(f"[ORCHESTRATOR DEBUG]: Loaded sheet data with {len(sheet_data)} total rows")

            # Determine row range
            self.logger.info("[ORCHESTRATOR DEBUG]: About to call _determine_row_range()")
            start_idx, end_idx = self._determine_row_range(
                sheet_data, start_row_index, end_row_index
            )

            self.logger.info(f"Processing rows {start_idx + 1} to {end_idx} (1-based)")
            self.logger.info(f"[ORCHESTRATOR DEBUG]: Row range calculation: start_idx={start_idx}, end_idx={end_idx}")
            self.logger.info(f"[ORCHESTRATOR DEBUG]: Will process {end_idx - start_idx} rows using range({start_idx}, {end_idx})")

            # Process each row
            row_count = 0
            self.logger.info("[ORCHESTRATOR DEBUG]: Starting row processing loop")
            for row_index in range(start_idx, end_idx):
                row_count += 1
                try:
                    self.logger.info(f"=== Processing row {row_index + 1} (loop iteration {row_count}) ===")
                    self._process_single_row(sheet_data, row_index)
                    self.logger.info(f"=== Completed row {row_index + 1} ===")
                except Exception as e:
                    self.logger.error(f"Error processing row {row_index + 1}: {str(e)}")
                    self.stats.record_failure()

            self.logger.info(f"[ORCHESTRATOR DEBUG]: Completed processing loop. Processed {row_count} rows total.")

        except Exception as e:
            print(f"Critical error in automation: {str(e)}")
            self.logger.error(f"[ORCHESTRATOR DEBUG]: Critical error in automation: {str(e)}")
            import traceback
            self.logger.error(f"[ORCHESTRATOR DEBUG]: Traceback: {traceback.format_exc()}")

        finally:
            self.logger.info("[ORCHESTRATOR DEBUG]: About to call _finish_automation()")
            self._finish_automation()

    def _load_sheet_data(self) -> list[list[str]]:
        """Load data from the Google Sheet with backwards compatibility for tests."""
        try:
            self.logger.info("Loading sheet data...")
            operation_id = self.logger.start_operation("load_sheet_data")

            # Try to use the backward compatibility function first (for tests)
            try:
                # Import and use the legacy function if available (tests may mock this)
                from ..constants import SHEET_NAME
                sheet_name = SHEET_NAME or "FBMP"  # Default to FBMP as in constants
                debug_print(f"DEBUG: Trying to call read_sheet_data with service={self.sheet_manager.service}, spreadsheet_id={self.sheet_manager.spreadsheet_id}, sheet_name={sheet_name}")
                values = read_sheet_data(self.sheet_manager.service, self.sheet_manager.spreadsheet_id, sheet_name)
                debug_print(f"DEBUG: read_sheet_data returned: {type(values)} with {len(values) if values else 0} rows")
                if values:  # If we got data from the legacy function, use it
                    self.logger.end_operation(operation_id, True)
                    self.logger.info(f"Successfully loaded {len(values)} rows from legacy function")
                    debug_print(f"DEBUG: Retrieved {len(values)} rows from legacy function.")
                    return values
                else:
                    debug_print("DEBUG: Legacy function returned empty data.")
            except Exception as e:
                debug_print(f"DEBUG: Legacy function failed: {e}, trying new method...")

            # Get range configuration from config - use broader range to ensure we get all data
            range_name = self.config.get_range_name() or "FBMP!A1:AQ1000"  # Use AQ (not AN) to get more columns
            debug_print(f"DEBUG: Using range: {range_name}")

            # Use the new sheet operations module as fallback
            values = self.sheet_operations.read_sheet_data(range_name)

            self.logger.end_operation(operation_id, True)
            self.logger.info(f"Successfully loaded {len(values)} rows from sheet")
            debug_print(f"DEBUG: Retrieved {len(values)} rows from sheet.")
            return values

        except Exception as e:
            if 'operation_id' in locals():
                self.logger.end_operation(operation_id, False, str(e))
            error_msg = f"Failed to load sheet data: {e}"
            self.logger.error(error_msg, e)
            debug_print(f"DEBUG: {error_msg}")
            raise

    def _determine_row_range(self, sheet_data: list[list[str]],
                           start_row_index: int | None,
                           end_row_index: int | None) -> tuple[int, int]:
        """Determine the actual row range to process."""
        # Default to row 5 (index 4) if no range specified
        if start_row_index is None and end_row_index is None:
            return 4, 5  # Process only row 5

        start_idx = start_row_index if start_row_index is not None else 4
        end_idx = end_row_index if end_row_index is not None else 5

        # Ensure we don't exceed sheet bounds
        max_rows = len(sheet_data)
        start_idx = max(0, min(start_idx, max_rows - 1))
        end_idx = max(start_idx + 1, min(end_idx, max_rows))

        return start_idx, end_idx

    def _process_single_row(self, sheet_data: list[list[str]], row_index: int):
        """Process a single row of the sheet."""
        row = sheet_data[row_index] if row_index < len(sheet_data) else []

        # Log detailed row information for debugging
        self.logger.info(f"Processing row {row_index + 1} (0-based index {row_index})")
        self.logger.info(f"Row has {len(row)} columns")

        # Show first 10 columns with content for debugging
        self.logger.info("Non-empty columns in this row (first 10):")
        for i, cell in enumerate(row[:10]):
            if cell:
                self.logger.info(f"  Col {i}: '{cell}'")

        # Extract product data
        product_data = self._extract_product_data(row, row_index)

        if not product_data.supplier_urls:
            self.logger.info(f"No supplier URLs found for row {row_index + 1}, skipping...")
            self.logger.info("Checked columns 33-42 and 32 for supplier URLs")
            self.logger.info(f"Row length: {len(row)}")
            return

        self.logger.info(f"Processing row {row_index + 1}: Product ID {product_data.product_id}")
        self.logger.info(f"Found {len(product_data.supplier_urls)} supplier URLs")

        # Process the product
        self.logger.info("Starting product processing...")
        update_result = self.product_processor.process_product(product_data)
        self.logger.info(f"Product processing completed. Best URL: {update_result.best_supplier_url}")

        # Update the sheet
        self.logger.info("Starting sheet update...")
        success = self.sheet_manager.update_product_row(product_data, update_result)
        self.logger.info(f"Sheet update completed: {'SUCCESS' if success else 'FAILED'}")

        # Update statistics
        if success:
            if update_result.all_blocked:
                self.stats.record_blocked()
            elif update_result.best_supplier_url is not None:
                self.stats.record_success()
            else:
                self.stats.record_failure()
        else:
            self.stats.record_failure()

    def _extract_product_data(self, row: list[str], row_index: int) -> ProductData:
        """Extract product data from a sheet row."""
        debug_print(f"DEBUG: Extracting data from row {row_index + 1} (0-based index {row_index})")
        debug_print(f"DEBUG: Row has {len(row)} columns")

        # Extract basic product information
        product_id = row[PRODUCT_ID_COL] if len(row) > PRODUCT_ID_COL else f"Row_{row_index + 1}"
        old_price = parse_price(row[PRICE_COL]) if len(row) > PRICE_COL and row[PRICE_COL] else 0.0

        debug_print(f"DEBUG: Product ID (col {PRODUCT_ID_COL}): '{product_id}'")
        debug_print(f"DEBUG: Old price (col {PRICE_COL}): '{old_price}'")

        # Extract supplier URLs from multiple possible columns for compatibility
        supplier_urls = []

        # Check new standard columns (AH through AN: 33-39)
        debug_print("DEBUG: Checking supplier URL columns 33-39...")
        for col_idx in range(33, 40):  # AH to AN
            if len(row) > col_idx and row[col_idx]:
                supplier_urls.append(row[col_idx])
                debug_print(f"DEBUG: Found URL in col {col_idx}: '{row[col_idx]}'")
            else:
                cell_value = row[col_idx] if len(row) > col_idx else "MISSING"
                debug_print(f"DEBUG: Col {col_idx} empty or missing: '{cell_value}'")

        # Check extended range (AO through AQ: 40-42) for more supplier columns
        debug_print("DEBUG: Checking extended supplier URL columns 40-42...")
        for col_idx in range(40, 43):  # AO to AQ
            if len(row) > col_idx and row[col_idx]:
                supplier_urls.append(row[col_idx])
                debug_print(f"DEBUG: Found URL in extended col {col_idx}: '{row[col_idx]}'")

        # For backward compatibility, also check AG (index 32) used in some tests
        if len(row) > 32 and row[32] and row[32] not in supplier_urls:
            supplier_urls.append(row[32])
            debug_print(f"DEBUG: Found URL in backward compat col 32: '{row[32]}'")

        debug_print(f"DEBUG: Total supplier URLs found: {len(supplier_urls)}")

        if not supplier_urls:
            debug_print(f"DEBUG: WARNING - No supplier URLs found in row {row_index + 1}")
            # Show some raw data for debugging when no URLs found
            debug_print("DEBUG: Raw row data (first 50 cols with values):")
            for i, cell in enumerate(row[:50]):
                if cell:
                    debug_print(f"DEBUG:   Col {i}: '{cell}'")

        return ProductData(
            product_id=product_id,
            old_price=old_price,
            row_index=row_index,
            row=row,
            supplier_urls=supplier_urls
        )

    def _finish_automation(self):
        """Clean up and display final statistics."""
        truncate_log_file(LOG_FILE)

        stats = self.stats.get_summary()
        print("=== Automation Complete ===")
        print(f"Total Processed: {stats['total_processed']}")
        print(f"Successful Updates: {stats['successful_updates']}")
        print(f"Failed Updates: {stats['failed_updates']}")
        print(f"Blocked Updates: {stats['blocked_updates']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Runtime: {stats['runtime_seconds']:.1f} seconds")
        print(f"Average Time per Item: {stats['avg_time_per_item']:.1f} seconds")
        print("Script run finished.")


class AutomationOrchestrator:
    """
    High-level orchestrator for the automation process.

    This class follows the Facade pattern to provide a simplified interface
    to the complex automation subsystem, coordinating all components while
    maintaining clean separation of concerns.
    """

    def __init__(self, config: Config, browser_manager=None, captcha_solver=None):
        """
        Initialize the automation orchestrator.

        Args:
            config: Configuration manager instance
            browser_manager: Enhanced browser manager instance
            captcha_solver: Captcha solver instance
        """
        self.config = config
        self.browser_manager = browser_manager
        self.captcha_solver = captcha_solver
        self.logger = get_logger()
        self.automation = None

    def execute_automation(self, start_row: int = None, end_row: int = None) -> bool:
        """
        Execute the complete automation process.

        Args:
            start_row: Starting row number (1-based)
            end_row: Ending row number (1-based)

        Returns:
            bool: True if automation completed successfully, False otherwise
        """
        try:
            self.logger.info("=== Starting Enhanced Sheet Scraper Automation ===")

            # Initialize Google Sheets service
            from ..infrastructure.connect import get_service
            service = get_service()
            if not service:
                self.logger.error("Could not connect to Google Sheets API")
                return False

            self.logger.info("Google Sheets service connected successfully")

            # Get spreadsheet configuration
            spreadsheet_id = self._get_spreadsheet_id()
            self.logger.info(f"Using spreadsheet ID: {spreadsheet_id}")

            # Create automation instance
            print("DEBUG: Creating browser page...")
            if not self.browser_manager:
                raise Exception("Browser manager is None - cannot create page")

            page = self.browser_manager.create_page()
            if not page:
                raise Exception("Failed to create browser page - page is None")

            print(f"DEBUG: Browser page created successfully: {type(page)}")

            self.automation = SheetScraperAutomation(
                page=page,
                captcha_solver=self.captcha_solver,
                config=self.config,
                browser_manager=self.browser_manager,
                sheet_service=service,
                spreadsheet_id=spreadsheet_id
            )

            # Convert parameters and run automation
            start_index, end_index = self._convert_row_parameters(start_row, end_row)
            self.logger.info(f"Processing rows {start_index + 1} to {end_index} (1-based)")

            # Execute the automation
            self.automation.run_automation(start_index, end_index)

            self.logger.info("Automation completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Critical error in automation orchestration: {e}")
            return False

    def _get_spreadsheet_id(self) -> str:
        """Get the spreadsheet ID from configuration or environment."""
        # First try config file
        spreadsheet_id = self.config.get_spreadsheet_id()

        # Then try environment variable
        if not spreadsheet_id:
            spreadsheet_id = os.environ.get("SPREADSHEET_ID")

        # Finally use the documented default ID
        if not spreadsheet_id:
            spreadsheet_id = "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw"

        # Log the source for debugging
        if spreadsheet_id == "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw":
            debug_print("DEBUG: Using hardcoded default spreadsheet ID")
        elif os.environ.get("SPREADSHEET_ID"):
            debug_print("DEBUG: Using SPREADSHEET_ID from environment variable")
        else:
            debug_print("DEBUG: Using spreadsheet ID from config file")

        return spreadsheet_id

    def _convert_row_parameters(self, start_row: int = None, end_row: int = None) -> tuple[int, int]:
        """
        Convert 1-based row parameters to internal format.

        Args:
            start_row: Starting row number (1-based)
            end_row: Ending row number (1-based)

        Returns:
            Tuple of (start_index, end_index) for internal use
        """
        # Default to row 20 if no parameters provided
        default_row = 20

        # Handle start row
        if start_row is not None:
            start_index = max(0, start_row - 1)  # Convert 1-based to 0-based
        elif os.environ.get("PROCESS_START_ROW"):
            start_index = max(0, int(os.environ.get("PROCESS_START_ROW")) - 1)
        else:
            start_index = default_row - 1  # Default to row 5 (0-based index 4)

        # Handle end row
        if end_row is not None:
            end_index = end_row  # Keep 1-based for end index
        elif os.environ.get("PROCESS_END_ROW"):
            end_index = int(os.environ.get("PROCESS_END_ROW"))
        else:
            end_index = default_row  # Default to row 5

        return start_index, end_index
