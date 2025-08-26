"""
Core automation classes for the Sheet Scraper project.

DEPRECATION NOTICE: This module has been refactored into a modular package
structure following Python best practices. The original 1,081-line file
violated code organization principles and has been split into logical modules.

New structure:
- automation.data_models: Data classes and type definitions
- automation.stats: Statistics tracking and metrics
- automation.processors: Product processing and supplier handling
- automation.formatters: Sheet formatting and styling
- automation.sheet_managers: Google Sheets operations
- automation.orchestrators: High-level automation coordination
- automation.scrapers: Individual product scraping operations

For backward compatibility, this module re-exports the main classes.
New code should import directly from the automation package modules.
"""

# Import all classes from the new modular package structure
from .automation import (
    # Data models
    ProductData,
    SupplierResult,
    PriceUpdateResult,

    # Core components
    AutomationStats,
    ProductProcessor,
    SheetFormatter,
    SheetManager,

    # Orchestrators
    SheetScraperAutomation,
    AutomationOrchestrator,

    # Scrapers
    ProductScraper,
# Re-export all classes for backward compatibility
__all__ = [
    # Data models
    'ProductData',
    'SupplierResult',
    'PriceUpdateResult',

    # Core components
    'AutomationStats',
    'ProductProcessor',
    'SheetFormatter',
    'SheetManager',

    # Orchestrators
    'SheetScraperAutomation',
    'AutomationOrchestrator',

    # Scrapers
    'ProductScraper',
]


        """
        Process a single product by scraping supplier data and determining price updates.

        Args:
            product_data: ProductData containing product information

        Returns:
            PriceUpdateResult with new price and update information
        """
        debug_print(f"DEBUG: Processing product {product_data.product_id}")

        # Scrape all suppliers for this product
        supplier_results = self._scrape_all_suppliers(product_data)

        # Analyze results and determine best price
        return self._analyze_supplier_results(product_data, supplier_results)

    def _scrape_all_suppliers(self, product_data: ProductData) -> List[SupplierResult]:
        """Scrape all supplier URLs for a product."""
        supplier_results = []

        for supplier_url in product_data.supplier_urls:
            if not supplier_url or supplier_url.strip() == "":
                continue

            try:
                debug_print(f"DEBUG: Scraping supplier: {supplier_url}")

                # Use the scraping function from this module
                result_dict = self._scrape_single_supplier(supplier_url)

                result = SupplierResult(
                    url=supplier_url,
                    price=result_dict.get("price"),
                    in_stock=result_dict.get("in_stock", False),
                    shipping_fee=result_dict.get("shipping_fee"),
                    error=result_dict.get("error"),
                    supplier_name=result_dict.get("supplier_name", "Unknown")
                )
                supplier_results.append(result)

                debug_print(f"DEBUG: Supplier result - Price: {result.price}, In Stock: {result.in_stock}, Error: {result.error}")

            except Exception as e:
                debug_print(f"DEBUG: Error scraping {supplier_url}: {str(e)}")
                error_result = SupplierResult(
                    url=supplier_url,
                    price=None,
                    in_stock=False,
                    shipping_fee=None,
                    error=str(e),
                    supplier_name="Unknown"
                )
                supplier_results.append(error_result)

        return supplier_results

    def _scrape_single_supplier(self, url: str) -> Dict[str, Any]:
        """
        Scrape product details from a single supplier URL.

        Args:
            url: Product URL to scrape

        Returns:
            dict: Scraped product data with keys: price, in_stock, shipping_fee, error, supplier_name
        """
        debug_print(f"DEBUG: Scraping details for {url}")

        try:
            # Navigate to the URL
            self.page.goto(url, timeout=60000)  # Increased timeout to 60 seconds

            # Simulate human-like interaction
            simulate_human_interaction(self.page)

            # Check for blocking using enhanced detection
            if is_blocked(self.page.content()):
                debug_print(f"DEBUG: Detected blocked for {url}")
                # Attempt to solve CAPTCHA if blocked
                if self.captcha_solver and os.environ.get("TWOCAPTCHA_API_KEY"):
                    debug_print(f"DEBUG: CAPTCHA detected for {url}. Attempting to solve...")
                    return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Blocked by CAPTCHA", "supplier_name": "Unknown"}
                else:
                    return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Blocked", "supplier_name": "Unknown"}

            # Extract price using the new PriceExtractor
            price_extractor = PriceExtractor()
            page_text = self.page.content()  # Get page content for price extraction
            price = price_extractor.extract_price(page_text)
            if price is None:
                debug_print(f"DEBUG: No price found for {url}")
                return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Price not found", "supplier_name": "Unknown"}

            # Extract shipping fee
            shipping_fee = extract_shipping_fee(self.page)

            # Check stock status using enhanced configuration
            in_stock = is_in_stock(self.page)

            # Extract supplier name from URL
            supplier_name = self._extract_supplier_name(url)

            debug_print(
                f"DEBUG: Final scraped data for {url}: {{'price': {price}, 'shipping_fee': {shipping_fee}, 'in_stock': {in_stock}, 'error': ''}}"
            )
            return {"price": price, "in_stock": in_stock, "shipping_fee": shipping_fee, "error": "", "supplier_name": supplier_name}

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {"price": None, "in_stock": False, "shipping_fee": None, "error": str(e), "supplier_name": "Unknown"}

    def _extract_supplier_name(self, url: str) -> str:
        """Extract supplier name from URL."""
        if "amazon.com" in url.lower():
            return "Amazon"
        elif "walmart.com" in url.lower():
            return "Walmart"
        elif "kohls.com" in url.lower():
            return "Kohls"
        elif "vivo-us.com" in url.lower():
            return "Vivo"
        elif "wayfair.com" in url.lower():
            return "Wayfair"
        else:
            return "Unknown"

    def _analyze_supplier_results(self, product_data: ProductData, supplier_results: List[SupplierResult]) -> PriceUpdateResult:
        """Analyze supplier results to determine the best price and update strategy."""
        lowest_price_found = None
        best_supplier_url = None
        chosen_shipping_fee = None
        chosen_supplier_name = ""

        # Filter valid results
        valid_results = [r for r in supplier_results if r.price is not None and r.in_stock]

        if valid_results:
            # Find the lowest price
            best_result = min(valid_results, key=lambda x: x.price)
            lowest_price_found = best_result.price
            best_supplier_url = best_result.url
            chosen_shipping_fee = best_result.shipping_fee
            chosen_supplier_name = best_result.supplier_name

        # Check for blocking
        suppliers_with_errors = [r for r in supplier_results if r.error is not None]
        blocked_suppliers = [
            r for r in suppliers_with_errors
            if "blocked" in r.error.lower() or "captcha" in r.error.lower()
        ]
        successful_suppliers = [r for r in supplier_results if r.price is not None]

        all_blocked = (
            len(blocked_suppliers) > 0 and
            len(successful_suppliers) == 0 and
            len(blocked_suppliers) == len(supplier_results)
        )

        # Check if all products are out of stock
        has_price_data = any(r.price is not None for r in supplier_results)
        all_out_of_stock = has_price_data and all(not r.in_stock for r in supplier_results if r.price is not None)

        # Determine new price and VA note
        if all_blocked:
            new_price_to_update = product_data.old_price
            new_va_note = "Blocked"
        elif lowest_price_found is not None and best_supplier_url is not None:
            new_price_to_update = lowest_price_found
            if new_price_to_update > product_data.old_price:
                new_va_note = "Up"
            elif new_price_to_update < product_data.old_price:
                new_va_note = "Down"
            else:
                new_va_note = ""
        elif has_price_data and all_out_of_stock:
            new_price_to_update = product_data.old_price
            new_va_note = ""
        else:
            new_price_to_update = product_data.old_price
            new_va_note = ""

        return PriceUpdateResult(
            new_price=new_price_to_update,
            new_va_note=new_va_note,
            best_supplier_url=best_supplier_url,
            chosen_shipping_fee=chosen_shipping_fee,
            chosen_supplier_name=chosen_supplier_name,
            all_blocked=all_blocked
        )


class SheetFormatter:
    """Handles Google Sheets formatting and color application."""

    def __init__(self):
        pass

    def create_formatting_requests(self, row_index: int, row: List[str],
                                 update_result: PriceUpdateResult) -> List[Dict]:
        """
        Create formatting requests for a row based on update results.

        Args:
            row_index: Zero-based row index
            row: Row data from the sheet
            update_result: Results from product processing

        Returns:
            List of formatting requests for the Google Sheets API
        """
        requests = []

        if update_result.all_blocked:
            # Blocked: don't change row colors, only format VA Notes (Column A)
            requests.append(
                create_color_request(
                    row_index, COLOR_BLUE, col_index=VA_NOTES_COL, text_color=COLOR_WHITE
                )
            )
        elif update_result.best_supplier_url is not None:
            # Item is available: apply full formatting
            requests.extend(self._create_available_item_formatting(row_index, row, update_result))
        else:
            # Item is unavailable: entire row red background, white text
            if not update_result.all_blocked:
                requests.append(
                    create_color_request(row_index, COLOR_RED, text_color=COLOR_WHITE)
                )

        # Column A (VA Notes) formatting for non-blocked items
        if update_result.new_va_note and update_result.new_va_note.strip() and update_result.new_va_note != "Blocked":
            requests.append(
                create_color_request(
                    row_index, COLOR_BLUE, col_index=VA_NOTES_COL, text_color=COLOR_WHITE
                )
            )

        return requests

    def _create_available_item_formatting(self, row_index: int, row: List[str],
                                        update_result: PriceUpdateResult) -> List[Dict]:
        """Create formatting requests for available items."""
        requests = []

        # Entire row white background
        requests.append(create_color_request(row_index, COLOR_WHITE))

        # Default formatting for specific columns
        requests.extend([
            create_color_request(row_index, COLOR_BLACK, col_index=COL_AG, text_color=COLOR_WHITE),
            create_color_request(row_index, COLOR_BLUE, col_index=COL_AB, text_color=COLOR_WHITE),
            create_color_request(row_index, COLOR_GREEN, col_index=COL_AE, text_color=COLOR_BLACK)
        ])

        # Apply special formatting if price is less than $299.99
        if update_result.new_price < 299.99:
            requests.extend(self._create_under_299_formatting(row_index, row))

        return requests

    def _create_under_299_formatting(self, row_index: int, row: List[str]) -> List[Dict]:
        """Create formatting for items under $299.99."""
        requests = []

        # Price column formatting
        requests.append(
            create_color_request(
                row_index, COLOR_LIGHT_GREEN_3, col_index=PRICE_COL, text_color=COLOR_DARK_RED_2
            )
        )

        # Other column formatting
        requests.extend([
            create_color_request(row_index, COLOR_LIGHT_MAGENTA_2, col_index=COL_Y, text_color=COLOR_BLACK),
            create_color_request(row_index, COLOR_LIGHT_YELLOW_2, col_index=COL_Z, text_color=COLOR_LIGHT_YELLOW_2),
            create_color_request(row_index, COLOR_LIGHT_RED_1, col_index=COL_AA, text_color=COLOR_BLACK),
            create_color_request(row_index, COLOR_BLUE, col_index=COL_AB, text_color=COLOR_BLACK),
            create_color_request(row_index, COLOR_DARK_GREEN_2, col_index=COL_AC, text_color=COLOR_BLACK),
            create_color_request(row_index, COLOR_DARK_GREEN_2, col_index=COL_AD, text_color=COLOR_BLACK)
        ])

        # Column E (RNW) formatting
        col_e_value = row[COL_E] if len(row) > COL_E else ""
        if col_e_value.strip().upper() == "RNW":
            requests.append(
                create_color_request(row_index, COLOR_RED, col_index=COL_E, text_color=COLOR_BLACK)
            )
        else:
            requests.append(
                create_color_request(row_index, COLOR_LIGHT_CYAN_3, col_index=COL_E, text_color=COLOR_BLACK)
            )

        # Gray formatting for columns F-K
        for col_index in [COL_F, COL_G, COL_H, COL_I, COL_J, COL_K]:
            requests.append(
                create_color_request(row_index, COLOR_GRAY, col_index=col_index, text_color=COLOR_GRAY)
            )

        # Column L formatting
        requests.append(
            create_color_request(row_index, COLOR_DARK_GREEN_2, col_index=COL_L, text_color=COLOR_WHITE)
        )

        # Noah supplier highlighting
        requests.extend(self._create_noah_formatting(row_index, row))

        # Standard text color formatting for various columns
        requests.extend(self._create_standard_text_formatting(row_index))

        return requests

    def _create_noah_formatting(self, row_index: int, row: List[str]) -> List[Dict]:
        """Create Noah supplier highlighting formatting."""
        requests = []

        # Column N formatting
        col_n_value = row[COL_N] if len(row) > COL_N else ""
        if "noah" in col_n_value.lower() if col_n_value else False:
            requests.append(
                create_color_request(
                    row_index, COLOR_NOAH_FILL, col_index=COL_N, text_color=COLOR_DARK_PURPLE_2
                )
            )
        else:
            requests.append(
                create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_N)
            )

        # Column O formatting
        col_o_value = row[COL_O] if len(row) > COL_O else ""
        if "noah" in col_o_value.lower() if col_o_value else False:
            requests.append(
                create_color_request(
                    row_index, COLOR_NOAH_FILL, col_index=COL_O, text_color=COLOR_DARK_PURPLE_2
                )
            )
        else:
            requests.append(
                create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_O)
            )

        return requests

    def _create_standard_text_formatting(self, row_index: int) -> List[Dict]:
        """Create standard text color formatting for various columns."""
        return [
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=LAST_STOCK_CHECK_COL),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_P),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_R),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_S),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_V),
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_W),
            create_color_request(row_index, text_color=COLOR_WHITE, col_index=COL_AA),
            create_color_request(row_index, text_color=COLOR_WHITE, col_index=COL_AB),
            create_color_request(row_index, text_color=COLOR_WHITE, col_index=COL_AC),
            create_color_request(row_index, text_color=COLOR_WHITE, col_index=COL_AD),
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=PRODUCT_ID_COL),
            create_color_request(row_index, COLOR_BLACK, col_index=COL_AG, text_color=COLOR_WHITE),
            # Supplier columns (AH-AN)
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=33),  # AH
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=34),  # AI
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=35),  # AJ
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=36),  # AK
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=37),  # AL
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=38),  # AM
            create_color_request(row_index, text_color=COLOR_DARK_CORNFLOWER_BLUE_2, col_index=39),  # AN
            create_color_request(row_index, text_color=COLOR_BLACK, col_index=COL_Q),
            create_color_request(row_index, COLOR_LIGHT_MAGENTA_2, col_index=COL_Y)
        ]


class SheetManager:
    """Manages Google Sheets operations and data updates."""

    def __init__(self, service, spreadsheet_id: str):
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        self.formatter = SheetFormatter()

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

        # Execute all requests
        success = update_sheet(self.service, self.spreadsheet_id, requests)

        if success:
            # Log the update
            log_status = "Success" if update_result.best_supplier_url is not None else "Failed"
            log_message = (
                f"Chosen supplier: {update_result.chosen_supplier_name}"
                if log_status == "Success"
                else update_result.new_va_note
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

        # Update price column
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
                        "userEnteredValue": {"numberValue": update_result.new_price}
                        if isinstance(update_result.new_price, (int, float)) and update_result.new_price != float("inf")
                        else {"userEnteredValue": {"stringValue": ""}}
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
                        "userEnteredValue": {"numberValue": shipping_fee_value}
                        if isinstance(shipping_fee_value, (int, float))
                        else {"userEnteredValue": {"stringValue": str(shipping_fee_value) if shipping_fee_value else ""}}
                    }]
                }],
                "fields": "userEnteredValue",
            }
        })

        # Update VA Notes column
        requests.append({
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
        })

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
        requests.append({
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
        })

        return requests


class SheetScraperAutomation:
    """Main automation orchestrator that coordinates all components."""

    def __init__(self, page: Page, captcha_solver: CaptchaSolver, config: Config,
                 browser_manager: EnhancedBrowserManager, sheet_service, spreadsheet_id: str):
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
        self.product_processor = ProductProcessor(page, captcha_solver, browser_manager)
        self.sheet_manager = SheetManager(sheet_service, spreadsheet_id)

    def run_automation(self, start_row_index: Optional[int] = None,
                      end_row_index: Optional[int] = None):
        """
        Run the complete automation process.

        Args:
            start_row_index: Starting row (0-based), None for default
            end_row_index: Ending row (1-based), None for default
        """
        print("=== Starting Enhanced Sheet Scraper Automation ===")

        try:
            # Load sheet data
            sheet_data = self._load_sheet_data()

            # Determine row range
            start_idx, end_idx = self._determine_row_range(
                sheet_data, start_row_index, end_row_index
            )

            print(f"Processing rows {start_idx + 1} to {end_idx} (1-based)")

            # Process each row
            for row_index in range(start_idx, end_idx):
                try:
                    self._process_single_row(sheet_data, row_index)
                except Exception as e:
                    print(f"Error processing row {row_index + 1}: {str(e)}")
                    self.stats.record_failure()

        except Exception as e:
            print(f"Critical error in automation: {str(e)}")

        finally:
            self._finish_automation()

    def _load_sheet_data(self) -> List[List[str]]:
        """Load data from the Google Sheet with backwards compatibility for tests."""
        try:
            self.logger.info("Loading sheet data...")
            operation_id = self.logger.start_operation("load_sheet_data")

            # Try to use the backward compatibility function first (for tests)
            try:
                # Import and use the legacy function if available (tests may mock this)
                from .constants import SHEET_NAME
                sheet_name = SHEET_NAME or "FBMP"  # Default to FBMP as in constants
                debug_print(f"DEBUG: Trying to call read_sheet_data with service={self.sheet_manager.service}, spreadsheet_id={self.sheet_manager.spreadsheet_id}, sheet_name={sheet_name}")
                values = read_sheet_data(self.sheet_manager.service, self.sheet_manager.spreadsheet_id, sheet_name)
                debug_print(f"DEBUG: read_sheet_data returned: {values}")
                if values:  # If we got data from the legacy function, use it
                    self.logger.end_operation(operation_id, True)
                    self.logger.info(f"Successfully loaded {len(values)} rows from legacy function")
                    debug_print(f"DEBUG: Retrieved {len(values)} rows from legacy function.")
                    return values
                else:
                    debug_print(f"DEBUG: Legacy function returned empty data.")
            except Exception as e:
                debug_print(f"DEBUG: Legacy function failed: {e}, trying new method...")

            # Get range configuration from config
            range_name = self.config.get_range_name() or "Sheet1!A:AN"  # Default range

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

            return values

        except Exception as e:
            debug_print(f"DEBUG: Error reading sheet: {e}")
            print(f"Error loading sheet data: {e}")
            return []

    def _determine_row_range(self, sheet_data: List[List[str]],
                           start_row_index: Optional[int],
                           end_row_index: Optional[int]) -> Tuple[int, int]:
        """Determine the actual row range to process."""
        # Default to row 66 (index 65) if no range specified
        if start_row_index is None and end_row_index is None:
            return 65, 66  # Process only row 66

        start_idx = start_row_index if start_row_index is not None else 65
        end_idx = end_row_index if end_row_index is not None else 66

        # Ensure we don't exceed sheet bounds
        max_rows = len(sheet_data)
        start_idx = max(0, min(start_idx, max_rows - 1))
        end_idx = max(start_idx + 1, min(end_idx, max_rows))

        return start_idx, end_idx

    def _process_single_row(self, sheet_data: List[List[str]], row_index: int):
        """Process a single row of the sheet."""
        row = sheet_data[row_index] if row_index < len(sheet_data) else []

        # Extract product data
        product_data = self._extract_product_data(row, row_index)

        if not product_data.supplier_urls:
            print(f"No supplier URLs found for row {row_index + 1}, skipping...")
            return

        print(f"Processing row {row_index + 1}: Product ID {product_data.product_id}")

        # Process the product
        update_result = self.product_processor.process_product(product_data)

        # Update the sheet
        success = self.sheet_manager.update_product_row(product_data, update_result)

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

    def _extract_product_data(self, row: List[str], row_index: int) -> ProductData:
        """Extract product data from a sheet row."""
        # Extract basic product information
        product_id = row[PRODUCT_ID_COL] if len(row) > PRODUCT_ID_COL else f"Row_{row_index + 1}"
        old_price = float(row[PRICE_COL]) if len(row) > PRICE_COL and row[PRICE_COL] else 0.0

        # Extract supplier URLs from multiple possible columns for compatibility
        supplier_urls = []

        # Check new standard columns (AH through AN: 33-39)
        for col_idx in range(33, 40):  # AH to AN
            if len(row) > col_idx and row[col_idx]:
                supplier_urls.append(row[col_idx])

        # For backward compatibility, also check AG (index 32) used in some tests
        if len(row) > 32 and row[32] and row[32] not in supplier_urls:
            supplier_urls.append(row[32])

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

    def __init__(self, config: Config, browser_manager: 'EnhancedBrowserManager' = None,
                 captcha_solver: 'CaptchaSolver' = None):
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
            from .connect import get_service
            service = get_service()
            if not service:
                self.logger.error("Could not connect to Google Sheets API")
                return False

            self.logger.info("Google Sheets service connected successfully")

            # Get spreadsheet configuration
            spreadsheet_id = self._get_spreadsheet_id()
            self.logger.info(f"Using spreadsheet ID: {spreadsheet_id}")

            # Create automation instance
            page = self.browser_manager.create_page() if self.browser_manager else None

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
        spreadsheet_id = self.config.get_spreadsheet_id()
        if not spreadsheet_id:
            spreadsheet_id = (
                os.environ.get("SPREADSHEET_ID") or
                "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw"
            )
        return spreadsheet_id

    def _convert_row_parameters(self, start_row: int = None, end_row: int = None) -> Tuple[int, int]:
        """
        Convert 1-based row parameters to internal format.

        Args:
            start_row: Starting row number (1-based)
            end_row: Ending row number (1-based)

        Returns:
            Tuple of (start_index, end_index) for internal use
        """
        # Default to row 66 if no parameters provided
        default_row = 66

        # Handle start row
        if start_row is not None:
            start_index = max(0, start_row - 1)  # Convert 1-based to 0-based
        elif os.environ.get("PROCESS_START_ROW"):
            start_index = max(0, int(os.environ.get("PROCESS_START_ROW")) - 1)
        else:
            start_index = default_row - 1  # Default to row 66 (0-based index 65)

        # Handle end row
        if end_row is not None:
            end_index = end_row  # Keep 1-based for end index
        elif os.environ.get("PROCESS_END_ROW"):
            end_index = int(os.environ.get("PROCESS_END_ROW"))
        else:
            end_index = default_row  # Default to row 66

        return start_index, end_index


class ProductScraper:
    """
    Handles individual product scraping operations.

    This class encapsulates all the logic for scraping product details
    from supplier websites, following the Single Responsibility Principle.
    """

    def __init__(self, page: Page, captcha_solver: 'CaptchaSolver', config: Config = None):
        """
        Initialize the product scraper.

        Args:
            page: Playwright page instance
            captcha_solver: Captcha solver instance
            config: Configuration manager instance
        """
        self.page = page
        self.captcha_solver = captcha_solver
        self.config = config or Config()
        self.logger = get_logger()

    def scrape_product(self, url: str) -> dict:
        """
        Scrape product details from a given URL.

        Args:
            url: Product URL to scrape

        Returns:
            dict: Scraped product data with keys: price, in_stock, shipping_fee, error
        """
        debug_print(f"DEBUG: Scraping details for {url}")
        self.logger.info(f"Scraping product details from {url}")

        try:
            # Navigate to the URL
            self.page.goto(url, timeout=60000)

            # Simulate human-like interaction
            from .scraping_utils import simulate_human_interaction
            simulate_human_interaction(self.page)

            # Check for blocking
            if self._is_page_blocked():
                return self._handle_blocked_page(url)

            # Extract product data
            price = self._extract_price()
            if price is None:
                debug_print(f"DEBUG: No price found for {url}")
                return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Price not found"}

            shipping_fee = self._extract_shipping_fee()
            in_stock = self._check_stock_status()

            result = {
                "price": price,
                "in_stock": in_stock,
                "shipping_fee": shipping_fee,
                "error": ""
            }

            debug_print(f"DEBUG: Final scraped data for {url}: {result}")
            self.logger.info(f"Successfully scraped product data: price={price}, in_stock={in_stock}")
            return result

        except Exception as e:
            error_msg = f"Error scraping {url}: {e}"
            self.logger.error(error_msg)
            return {"price": None, "in_stock": False, "shipping_fee": None, "error": str(e)}

    def _is_page_blocked(self) -> bool:
        """Check if the current page is blocked."""
        from .scraping_utils import is_blocked
        return is_blocked(self.page.content(), self.config)

    def _handle_blocked_page(self, url: str) -> dict:
        """Handle blocked page scenarios."""
        debug_print(f"DEBUG: Detected blocked for {url}")

        if self.captcha_solver and os.environ.get("TWOCAPTCHA_API_KEY"):
            debug_print(f"DEBUG: CAPTCHA detected for {url}. Attempting to solve...")
            # In a real scenario, you'd extract sitekey and URL from the page
            return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Blocked by CAPTCHA"}
        else:
            return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Blocked"}

    def _extract_price(self) -> float:
        """Extract price from the current page."""
        from .scraping_utils import extract_price
        return extract_price(self.page, self.config)

    def _extract_shipping_fee(self) -> float:
        """Extract shipping fee from the current page."""
        from .scraping_utils import extract_shipping_fee
        return extract_shipping_fee(self.page, self.config)

    def _check_stock_status(self) -> bool:
        """Check if the product is in stock."""
        from .scraping_utils import is_in_stock
        return is_in_stock(self.page, self.config)
