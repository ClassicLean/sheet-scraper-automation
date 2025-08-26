"""
Individual product scraping operations.

This module contains the ProductScraper class responsible for
handling individual product scraping operations from supplier websites.
"""

import os

from playwright.sync_api import Page

from ..config.config_manager import Config
from ..logs_module.automation_logging import get_logger
from ..scraping_utils import (
    debug_print,
    extract_shipping_fee,
    is_blocked,
    is_in_stock,
    simulate_human_interaction,
)


class ProductScraper:
    """
    Handles individual product scraping operations.

    This class encapsulates all the logic for scraping product details
    from supplier websites, following the Single Responsibility Principle.
    """

    def __init__(self, page: Page, captcha_solver=None, config: Config = None):
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
        from sheet_scraper.scraping_utils import (
            debug_print_price_extraction,
            debug_print_scraping_attempt,
            debug_print_scraping_failure,
        )

        debug_print(f"DEBUG: Scraping details for {url}")
        self.logger.info(f"Scraping product details from {url}")
        debug_print_scraping_attempt(url, "Starting scrape", {"method": "scrape_product"})

        try:
            # Navigate to the URL
            debug_print_scraping_attempt(url, "Navigating to URL", {"timeout": "60000ms"})
            self.page.goto(url, timeout=60000)
            debug_print_scraping_attempt(url, "Navigation successful", {"status": "completed"})

            # Simulate human-like interaction
            simulate_human_interaction(self.page)
            debug_print_scraping_attempt(url, "Human interaction simulated", {"status": "completed"})

            # Check for blocking
            if self._is_page_blocked():
                debug_print_scraping_failure(url, "Page blocked", "Captcha or anti-bot detection triggered")
                return self._handle_blocked_page(url)

            # Extract product data
            debug_print_scraping_attempt(url, "Extracting price", {"method": "_extract_price"})
            price = self._extract_price()
            if price is None:
                debug_print(f"DEBUG: No price found for {url}")
                debug_print_scraping_failure(url, "Price extraction failed", "No price element found or price is None")
                return {"price": None, "in_stock": False, "shipping_fee": None, "error": "Price not found"}

            debug_print_price_extraction(url, price, "successful_extraction")

            debug_print_scraping_attempt(url, "Extracting shipping fee", {"method": "_extract_shipping_fee"})
            shipping_fee = self._extract_shipping_fee()

            debug_print_scraping_attempt(url, "Checking stock status", {"method": "_check_stock_status"})
            in_stock = self._check_stock_status()

            result = {
                "price": price,
                "in_stock": in_stock,
                "shipping_fee": shipping_fee,
                "error": ""
            }

            debug_print(f"DEBUG: Final scraped data for {url}: {result}")
            debug_print_scraping_attempt(url, "Scraping completed successfully", {
                "price": price,
                "in_stock": in_stock,
                "shipping_fee": shipping_fee
            })
            self.logger.info(f"Successfully scraped product data: price={price}, in_stock={in_stock}")
            return result

        except Exception as e:
            error_msg = f"Error scraping {url}: {e}"
            debug_print_scraping_failure(url, "Exception occurred", error_msg)
            self.logger.error(error_msg)
            return {"price": None, "in_stock": False, "shipping_fee": None, "error": str(e)}

    def _is_page_blocked(self) -> bool:
        """Check if the current page is blocked."""
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
        from ..scraping_utils import extract_price
        return extract_price(self.page, self.config)

    def _extract_shipping_fee(self) -> float:
        """Extract shipping fee from the current page."""
        return extract_shipping_fee(self.page, self.config)

    def _check_stock_status(self) -> bool:
        """Check if the product is in stock."""
        return is_in_stock(self.page, self.config)
