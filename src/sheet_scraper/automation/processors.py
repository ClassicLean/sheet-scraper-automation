"""
Product processing and supplier handling.

This module contains the ProductProcessor class responsible for
processing individual products and scraping supplier data.
"""

import os
from typing import Any

from playwright.sync_api import Page

from ..config.config_manager import Config
from ..infrastructure.browser_manager import EnhancedBrowserManager
from ..infrastructure.captcha_solver import CaptchaSolver
from ..scraping_utils import (
    debug_print,
    extract_shipping_fee,
    is_blocked,
    is_in_stock,
    simulate_human_interaction,
)
from .data_models import PriceUpdateResult, ProductData, SupplierResult


class ProductProcessor:
    """Handles individual product processing and supplier scraping."""

    def __init__(self, page: Page, captcha_solver: CaptchaSolver, browser_manager: EnhancedBrowserManager, config: Config = None):
        self.page = page
        self.captcha_solver = captcha_solver
        self.browser_manager = browser_manager
        self.config = config or Config()

    def process_product(self, product_data: ProductData) -> PriceUpdateResult:
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

    def _scrape_all_suppliers(self, product_data: ProductData) -> list[SupplierResult]:
        """Scrape all supplier URLs for a product."""
        from sheet_scraper.scraping_utils import (
            debug_print_supplier_summary,
            debug_print_url_processing_start,
        )

        supplier_results = []
        total_suppliers = len([url for url in product_data.supplier_urls if url and url.strip()])
        successful_extractions = 0
        failed_extractions = 0

        for supplier_index, supplier_url in enumerate(product_data.supplier_urls):
            if not supplier_url or supplier_url.strip() == "":
                continue

            # Debug: Start processing this URL
            debug_print_url_processing_start(supplier_url, supplier_index, total_suppliers)

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

                # Track success/failure
                if result.price is not None:
                    successful_extractions += 1
                else:
                    failed_extractions += 1

                debug_print(f"DEBUG: Supplier result - Price: {result.price}, In Stock: {result.in_stock}, Error: {result.error}")

            except Exception as e:
                failed_extractions += 1
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

        # Debug: Summary of all supplier processing
        debug_print_supplier_summary(total_suppliers, successful_extractions, failed_extractions)

        return supplier_results

    def _scrape_single_supplier(self, url: str) -> dict[str, Any]:
        """
        Scrape product details from a single supplier URL.

        Args:
            url: Product URL to scrape

        Returns:
            dict: Scraped product data with keys: price, in_stock, shipping_fee, error, supplier_name
        """
        from sheet_scraper.scraping_utils import (
            debug_print_element_detection,
            debug_print_page_navigation,
        )

        debug_print(f"DEBUG: Scraping details for {url}")

        try:
            # Navigate to the URL with enhanced debugging
            debug_print_page_navigation(url, "STARTING", {"timeout": "60000ms", "method": "page.goto()"})

            response = self.page.goto(url, timeout=60000)  # Increased timeout to 60 seconds

            # Debug navigation result
            status_code = response.status if response else "Unknown"
            page_title = self.page.title() if self.page else "Unknown"
            debug_print_page_navigation(url, "COMPLETED", {
                "status_code": status_code,
                "page_title": page_title[:50] + "..." if len(page_title) > 50 else page_title,
                "url_after_redirect": self.page.url
            })

            # Simulate human-like interaction
            simulate_human_interaction(self.page)

            # Check for blocking using enhanced detection
            page_content = self.page.content()
            blocked = is_blocked(page_content)
            debug_print_element_detection(url, "blocking_indicators", not blocked, "Page access status")

            if blocked:
                debug_print(f"DEBUG: Detected blocked for {url}")
                # Attempt to solve CAPTCHA if blocked
                if self.captcha_solver and os.environ.get("TWOCAPTCHA_API_KEY"):
                    debug_print(f"DEBUG: CAPTCHA detected for {url}. Attempting to solve...")
                    return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Blocked by CAPTCHA", "supplier_name": "Unknown"}
                else:
                    return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Blocked", "supplier_name": "Unknown"}

            # Extract price using site-specific selectors
            from ..utils.logs_module import debug_print_price_extraction
            from ..utils.pricing import extract_price

            price = extract_price(self.page, self.config)

            # Enhanced debugging for price extraction
            debug_print_price_extraction(url, price, "extract_price() with selectors")
            debug_print_element_detection(url, "price_selectors", price is not None, f"Found price: {price}" if price else "No price found")

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

    def _analyze_supplier_results(self, product_data: ProductData, supplier_results: list[SupplierResult]) -> PriceUpdateResult:
        """Analyze supplier results to determine the best price and update strategy."""
        from sheet_scraper.scraping_utils import (
            debug_print_price_comparison,
            debug_print_scraping_attempt,
        )

        debug_print_scraping_attempt("", "Analyzing supplier results", {
            "total_suppliers": len(supplier_results),
            "suppliers": [f"{r.supplier_name}: {r.price}" for r in supplier_results]
        })

        lowest_price_found = None
        best_supplier_url = None
        chosen_shipping_fee = None
        chosen_supplier_name = ""

        # Filter valid results
        valid_results = [r for r in supplier_results if r.price is not None and r.in_stock]

        # Enhanced debugging for supplier filtering
        debug_print_scraping_attempt("", "Detailed supplier analysis", {
            "total_suppliers": len(supplier_results),
            "supplier_details": [
                f"{r.supplier_name}: price={r.price}, in_stock={r.in_stock}, error='{r.error}'"
                for r in supplier_results
            ]
        })

        debug_print_scraping_attempt("", "Filtering valid results", {
            "valid_results_count": len(valid_results),
            "valid_suppliers": [f"{r.supplier_name}: ${r.price}" for r in valid_results],
            "filtered_out_suppliers": [
                f"{r.supplier_name}: price={r.price}, in_stock={r.in_stock} ({'PRICE_MISSING' if r.price is None else 'OUT_OF_STOCK'})"
                for r in supplier_results
                if not (r.price is not None and r.in_stock)
            ]
        })

        if valid_results:
            # Find the lowest price
            best_result = min(valid_results, key=lambda x: x.price)
            lowest_price_found = best_result.price
            best_supplier_url = best_result.url
            chosen_shipping_fee = best_result.shipping_fee
            chosen_supplier_name = best_result.supplier_name

            debug_print_price_comparison(
                product_data.old_price or 0.0,
                lowest_price_found,
                best_supplier_url,
                f"Selected {chosen_supplier_name} as best supplier (in stock)"
            )
        else:
            # Fallback: If no in-stock items, consider out-of-stock items with prices
            price_only_results = [r for r in supplier_results if r.price is not None]

            debug_print_scraping_attempt("", "No in-stock items found, checking out-of-stock prices", {
                "price_only_results_count": len(price_only_results),
                "price_only_suppliers": [f"{r.supplier_name}: ${r.price} (out-of-stock)" for r in price_only_results]
            })

            if price_only_results:
                # Find the lowest price among out-of-stock items
                best_result = min(price_only_results, key=lambda x: x.price)
                lowest_price_found = best_result.price
                best_supplier_url = best_result.url
                chosen_shipping_fee = best_result.shipping_fee
                chosen_supplier_name = best_result.supplier_name

                debug_print_price_comparison(
                    product_data.old_price or 0.0,
                    lowest_price_found,
                    best_supplier_url,
                    f"Selected {chosen_supplier_name} as best supplier (out-of-stock but has price)"
                )
            else:
                debug_print_scraping_attempt("", "No valid results found", {
                    "all_results": [f"{r.supplier_name}: price={r.price}, in_stock={r.in_stock}, error={r.error}" for r in supplier_results]
                })

        # Check for blocking
        suppliers_with_errors = [r for r in supplier_results if r.error is not None]
        blocked_suppliers = [
            r for r in suppliers_with_errors
            if "blocked" in r.error.lower() or "captcha" in r.error.lower()
        ]
        successful_suppliers = [r for r in supplier_results if r.price is not None]

        debug_print_scraping_attempt("", "Error analysis", {
            "suppliers_with_errors": len(suppliers_with_errors),
            "blocked_suppliers": len(blocked_suppliers),
            "successful_suppliers": len(successful_suppliers)
        })

        all_blocked = (
            len(blocked_suppliers) > 0 and
            len(successful_suppliers) == 0 and
            len(blocked_suppliers) == len(supplier_results)
        )

        # Check if all products are out of stock
        has_price_data = any(r.price is not None for r in supplier_results)
        all_out_of_stock = has_price_data and all(not r.in_stock for r in supplier_results if r.price is not None)
        has_in_stock_items = any(r.price is not None and r.in_stock for r in supplier_results)

        # Determine new price and VA note
        if all_blocked:
            new_price_to_update = product_data.old_price
            new_va_note = "Blocked"
        elif lowest_price_found is not None and best_supplier_url is not None:
            new_price_to_update = lowest_price_found

            # Determine price change indicator
            if new_price_to_update >= 299.99:
                new_va_note = "$$$"
            elif new_price_to_update > product_data.old_price:
                new_va_note = "Up" + ("*" if not has_in_stock_items else "")  # Add * for out-of-stock price
            elif new_price_to_update < product_data.old_price:
                new_va_note = "Down" + ("*" if not has_in_stock_items else "")  # Add * for out-of-stock price
            else:
                new_va_note = "*" if not has_in_stock_items else ""  # * indicates out-of-stock price
        elif has_price_data and all_out_of_stock:
            new_price_to_update = product_data.old_price
            new_va_note = ""
        else:
            new_price_to_update = product_data.old_price
            new_va_note = ""

        debug_print_scraping_attempt("", "Final result determination", {
            "new_price": new_price_to_update,
            "new_va_note": new_va_note,
            "best_supplier": chosen_supplier_name,
            "best_url": best_supplier_url,
            "has_in_stock_items": has_in_stock_items,
            "all_out_of_stock": all_out_of_stock,
            "all_blocked": all_blocked
        })

        return PriceUpdateResult(
            new_price=new_price_to_update,
            new_va_note=new_va_note,
            best_supplier_url=best_supplier_url,
            chosen_shipping_fee=chosen_shipping_fee,
            chosen_supplier_name=chosen_supplier_name,
            all_blocked=all_blocked
        )
