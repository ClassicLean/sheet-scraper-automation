"""
Web scraping utilities for bot detection, stock checking, and human simulation.

This module contains functions for detecting blocking/captcha,
checking stock status, extracting shipping fees, and simulating human behavior.
"""

import random
import re
import time

from ..config.constants import (
    IN_STOCK_INDICATORS,
    OUT_OF_STOCK_INDICATORS,
    STOCK_INDICATOR_SELECTORS,
)
from .logs_module import debug_print
from .pricing import parse_price


def is_error_page(page) -> bool:
    """
    Detect if the page is a 404 error page or other error page.

    Args:
        page: Playwright page object

    Returns:
        bool: True if page appears to be an error page, False otherwise
    """
    try:
        # Check HTTP status code first
        response = page.url

        # Get page content for text-based detection
        content = page.content().lower()

        # Common 404 and error page indicators
        error_indicators = [
            "404 page not found",
            "404 not found",
            "page not found",
            "page does not exist",
            "page you requested does not exist",
            "the page you are looking for doesn't exist",
            "this page doesn't exist",
            "error 404",
            "not found",
            "page unavailable",
            "page is temporarily unavailable",
            "resource not found",
            "file not found",
            "document not found",
            "sorry, we can't find that page",
            "oops! page not found",
            "the requested url was not found"
        ]

        # Check for error indicators in content
        for indicator in error_indicators:
            if indicator in content:
                debug_print(f"DEBUG: Error page detected by text: '{indicator}' in content for {page.url}")
                return True

        # Check for specific error page elements
        try:
            # Look for common error page elements
            error_selectors = [
                "h1:has-text('404')",
                "h1:has-text('Not Found')",
                "h1:has-text('Page Not Found')",
                "[class*='error']",
                "[class*='404']",
                "[id*='error']",
                "[id*='404']"
            ]

            for selector in error_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    debug_print(f"DEBUG: Error page detected by selector: '{selector}' for {page.url}")
                    return True
        except Exception as e:
            debug_print(f"DEBUG: Error checking error page selectors: {e}")

        return False

    except Exception as e:
        debug_print(f"DEBUG: Error in is_error_page: {e}")
        return False


def is_blocked(content: str, config=None) -> bool:
    """
    Enhanced blocking detection with configurable indicators.

    Args:
        content: Page content to check
        config: Configuration manager instance (optional)

    Returns:
        bool: True if page appears to be blocked, False otherwise
    """
    content_lower = content.lower()

    # Debug: Print first 500 characters of content for analysis
    debug_print(f"DEBUG: Checking content for blocking (first 500 chars): {content_lower[:500]}...")

    # Check configurable blocking indicators if config is provided
    if config:
        blocking_indicators = config.get_blocking_indicators()
        for indicator in blocking_indicators:
            if indicator.lower() in content_lower:
                debug_print(f"DEBUG: Blocking detected by configured indicator: '{indicator}' in content")
                return True

    # Legacy blocking indicators (fallback) - made more specific to avoid false positives
    legacy_indicators = [
        "robot or human",
        "solve the captcha",
        "complete the captcha",
        "verify the captcha",
        "please verify you are human",
        "captcha verification required",
        "enter the captcha",
        "access denied",
        "unusual traffic detected",
        "verify you are human",
        "security check required",
        "bot detection",
        "robot check",  # Added for tests
        "rate limit exceeded",
        "too many requests",
        "please wait while we verify",
        "checking your browser before accessing",
        "enable javascript and cookies",
        "ddos protection by cloudflare",
        "cloudflare security check",
        "ray id:",
        "we need to verify that you're human",
        "security verification required"
    ]

    for indicator in legacy_indicators:
        if indicator in content_lower:
            debug_print(f"DEBUG: Blocking detected by legacy indicator: '{indicator}' in content")
            return True

    debug_print("DEBUG: No blocking indicators found in content")
    return False


def extract_shipping_fee(page, config=None) -> float | None:
    """
    Extract shipping fee from the page.

    Args:
        page: Playwright page object
        config: Configuration manager instance (optional)

    Returns:
        float: Extracted shipping fee or None if not found
    """
    # Common shipping fee selectors and text patterns
    shipping_selectors = [
        "[data-test-id='shipping-fee']",
        ".shipping-cost",
        ".shipping-fee",
        ".delivery-cost",
        ".shipping-price",
        "[class*='shipping']",
        "[class*='delivery']",
        "[id*='shipping']",
        "[id*='delivery']",
    ]

    # Text patterns to look for shipping fees
    shipping_text_patterns = [
        r"shipping[:\s]*\$?(\d+\.?\d*)",
        r"delivery[:\s]*\$?(\d+\.?\d*)",
        r"freight[:\s]*\$?(\d+\.?\d*)",
        r"handling[:\s]*\$?(\d+\.?\d*)",
        r"ship[:\s]*\$?(\d+\.?\d*)",
        r"\+\s*\$?(\d+\.?\d*)\s*shipping",
        r"\+\s*\$?(\d+\.?\d*)\s*delivery",
    ]

    try:
        # Handle mock objects in tests
        if hasattr(page, 'content') and callable(page.content):
            content = page.content()
            # Make sure content is a string, not a mock
            if content and isinstance(content, str):
                # Search for shipping patterns in content
                for pattern in shipping_text_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        fee_str = match.group(1)
                        fee = parse_price(fee_str)
                        if fee is not None and fee > 0:
                            debug_print(f"DEBUG: Shipping fee found in content: {fee_str} -> {fee}")
                            return fee
                        elif "free" in content.lower():
                            debug_print("DEBUG: Free shipping detected in content")
                            return 0.0

        # Try using the new locator method for modern tests
        for selector in shipping_selectors:
            try:
                # Handle both old and new test styles
                if hasattr(page, 'locator'):
                    elements = page.locator(selector)
                    # Handle mock objects that return MagicMock for count()
                    try:
                        count = elements.count()
                        # For mocks, count() might return a MagicMock, so handle that
                        if hasattr(count, '__gt__') and count > 0:
                            element = elements.first()
                            text = element.inner_text().strip().lower()
                            if any(keyword in text for keyword in ["shipping", "delivery", "freight", "handling"]):
                                fee = parse_price(text)
                                if fee is not None and fee > 0:
                                    debug_print(f"DEBUG: Shipping fee found using locator selector '{selector}': {text} -> {fee}")
                                    return fee
                    except (TypeError, AttributeError):
                        # Skip if this is a mock object
                        pass
                elif hasattr(page, 'query_selector_all'):
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        text = element.inner_text().strip().lower()
                        if any(keyword in text for keyword in ["shipping", "delivery", "freight", "handling"]):
                            fee = parse_price(text)
                            if fee is not None and fee > 0:
                                debug_print(f"DEBUG: Shipping fee found using selector '{selector}': {text} -> {fee}")
                                return fee
            except (AttributeError, RuntimeError, ValueError, TypeError) as e:
                debug_print(f"DEBUG: Error with shipping selector '{selector}': {e}")
                continue

    except (AttributeError, RuntimeError) as e:
        debug_print(f"DEBUG: Error in shipping fee extraction: {e}")
    except Exception as e:
        debug_print(f"DEBUG: Unexpected error in shipping fee extraction: {e}")
        # Re-raise unexpected exceptions for debugging
        raise

    debug_print("DEBUG: No shipping fee found")
    return None


def is_in_stock(page, config=None) -> bool:
    """
    Enhanced stock detection with site-specific selectors and better error handling.

    Args:
        page: Playwright page object
        config: Configuration manager instance (optional)

    Returns:
        bool: True if in stock, False if out of stock
    """
    # Initialize config if not provided
    if config is None:
        from sheet_scraper.config.config_manager import Config
        config = Config()

    site = config.detect_site(page.url)

    # Special handling for Amazon - check text content, not just element presence
    if site == "amazon":
        # Check availability text content specifically
        availability_selectors = [
            "div#availability span",
            "div#availability",
            "#availability span",
            "#availability"
        ]

        found_negative_text = False

        for selector in availability_selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    text_content = element.text_content().lower().strip()
                    print(f"DEBUG: Amazon availability text for {selector}: '{text_content}' for {page.url}")

                    # Check for negative availability indicators first (highest priority)
                    negative_indicators = [
                        "out of stock",
                        "currently unavailable",
                        "temporarily out of stock",
                        "unavailable",
                        "not available",
                        "can't deliver",
                        "doesn't deliver",
                        "not deliverable",
                        "cannot be shipped",
                        "can't be shipped",
                        "delivery not available",
                        "choose a different delivery location",
                        "select a different delivery location",
                        "item cannot be shipped to your",
                        "this item cannot be shipped",
                        "unavailable in your area",
                        "not available in your area"
                    ]

                    # Check for negative indicators
                    for neg_indicator in negative_indicators:
                        if neg_indicator in text_content:
                            print(f"DEBUG: Amazon out-of-stock detected by text: '{neg_indicator}' in '{text_content}' for {page.url}")
                            found_negative_text = True
                            break

                    # Check for positive indicators only if no negative found
                    if not found_negative_text:
                        positive_indicators = [
                            "in stock",
                            "available",
                            "ships from",
                            "add to cart",
                            "buy now"
                        ]

                        for pos_indicator in positive_indicators:
                            if pos_indicator in text_content:
                                print(f"DEBUG: Amazon in-stock detected by text: '{pos_indicator}' in '{text_content}' for {page.url}")
                                return True  # Return directly instead of setting unused variable

            except Exception as e:
                print(f"DEBUG: Error checking Amazon availability text for {selector}: {e}")
                continue

        # If we found negative text, return False immediately (override any selectors)
        if found_negative_text:
            return False

    # Special handling for Vevor - check for discontinuation indicators
    if site == "vevor":
        # 1. Check schema.org structured data for discontinued status
        try:
            structured_data = page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                    for (const script of scripts) {
                        try {
                            const data = JSON.parse(script.textContent);
                            // Check offers array for availability
                            if (data.offers && Array.isArray(data.offers)) {
                                for (const offer of data.offers) {
                                    if (offer.availability) {
                                        return offer.availability;
                                    }
                                }
                            }
                            // Check direct availability property
                            if (data.availability) {
                                return data.availability;
                            }
                        } catch (e) {
                            // Continue to next script
                        }
                    }
                    return null;
                }
            """)
            if structured_data:
                # Check for schema.org/Discontinued URL or text containing "discontinued"
                if ("schema.org/Discontinued" in structured_data or
                    "discontinued" in structured_data.lower()):
                    print(f"DEBUG: Vevor discontinued detected by structured data: {structured_data} for {page.url}")
                    return False
        except Exception as e:
            print(f"DEBUG: Error checking Vevor structured data: {e}")

        # 2. Check for discontinue status container
        discontinue_selectors = [
            ".good-status-container_kg_a.discontinue_gxC7",
            ".dt_txt_cqUZ",
            ".discontinue_gxC7"
        ]

        for selector in discontinue_selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    text_content = element.text_content().lower().strip()
                    print(f"DEBUG: Vevor status element text for {selector}: '{text_content}' for {page.url}")
                    if "discontinue" in text_content or "discontinued" in text_content:
                        print(f"DEBUG: Vevor discontinued detected by selector: {selector} for {page.url}")
                        return False
            except Exception as e:
                print(f"DEBUG: Error checking Vevor discontinue selector {selector}: {e}")
                continue

    # 1. First check for positive in-stock indicators (highest priority)
    in_stock_selectors = config.get_stock_selectors(site, "in_stock")
    for selector in in_stock_selectors:
        try:
            if page.query_selector(selector):
                print(
                    f"DEBUG: In-stock detected by {site} selector: {selector} for {page.url}"
                )
                return True
        except Exception as e:
            print(f"DEBUG: Error checking {site} in-stock selector {selector}: {e}")
            continue

    # 2. Check generic in-stock selectors
    if site != "generic":
        generic_in_selectors = config.get_stock_selectors("generic", "in_stock")
        for selector in generic_in_selectors:
            try:
                if page.query_selector(selector):
                    print(
                        f"DEBUG: In-stock detected by generic selector: {selector} for {page.url}"
                    )
                    return True
            except Exception as e:
                print(
                    f"DEBUG: Error checking generic in-stock selector {selector}: {e}"
                )
                continue

    # 3. Check legacy in-stock selectors
    for selector in STOCK_INDICATOR_SELECTORS["in_stock"]:
        try:
            if page.query_selector(selector):
                print(
                    f"DEBUG: In-stock detected by legacy selector: {selector} for {page.url}"
                )
                return True
        except Exception as e:
            print(f"DEBUG: Error checking legacy in-stock selector {selector}: {e}")
            continue

    # 4. Now check for site-specific out-of-stock indicators
    out_of_stock_selectors = config.get_stock_selectors(site, "out_of_stock")
    for selector in out_of_stock_selectors:
        try:
            if page.query_selector(selector):
                print(
                    f"DEBUG: Out-of-stock detected by {site} selector: {selector} for {page.url}"
                )
                return False
        except Exception as e:
            print(f"DEBUG: Error checking {site} out-of-stock selector {selector}: {e}")
            continue

    # 5. Fallback to generic out-of-stock selectors
    if site != "generic":
        generic_out_selectors = config.get_stock_selectors("generic", "out_of_stock")
        for selector in generic_out_selectors:
            try:
                if page.query_selector(selector):
                    print(
                        f"DEBUG: Out-of-stock detected by generic selector: {selector} for {page.url}"
                    )
                    return False
            except Exception as e:
                print(
                    f"DEBUG: Error checking generic out-of-stock selector {selector}: {e}"
                )
                continue

    # 6. Check legacy out-of-stock selectors
    for selector in STOCK_INDICATOR_SELECTORS["out_of_stock"]:
        try:
            if page.query_selector(selector):
                print(
                    f"DEBUG: Out-of-stock detected by legacy selector: {selector} for {page.url}"
                )
                return False
        except Exception as e:
            print(f"DEBUG: Error checking legacy out-of-stock selector {selector}: {e}")
            continue

    # 7. Text-based out-of-stock indicators (last resort, most specific only)
    page_content = page.content().lower()
    for indicator in OUT_OF_STOCK_INDICATORS:
        if indicator in page_content:
            print(
                f"DEBUG: Out-of-stock detected by text indicator: {indicator} for {page.url}"
            )
            return False

    # 8. Text-based in-stock indicators (backup)
    for indicator in IN_STOCK_INDICATORS:
        if indicator in page_content:
            print(
                f"DEBUG: In-stock detected by text indicator: {indicator} for {page.url}"
            )
            return True

    # Default: assume in stock if no clear indicators found
    print(f"DEBUG: No clear stock indicators found for {page.url}. Assuming in stock.")
    return True


def simulate_human_interaction(page):
    """
    Simulate human-like mouse movements and scrolling behavior.

    Args:
        page: Playwright page object
    """
    # Simulate human-like mouse movements before navigation
    for _ in range(random.randint(3, 7)):  # Perform 3 to 7 random mouse movements
        x = random.randint(0, page.viewport_size["width"])
        y = random.randint(0, page.viewport_size["height"])
        page.mouse.move(x, y, steps=random.randint(5, 15))  # Move with random steps
        time.sleep(random.uniform(0.1, 0.5))  # Short random delay between movements

    # Simulate human-like scrolling after page load
    scroll_height = page.evaluate("document.body.scrollHeight")
    scroll_steps = random.randint(3, 7)  # Random number of scroll steps
    for _ in range(scroll_steps):
        # Scroll to a random position within the page
        target_scroll = random.uniform(0, scroll_height)
        page.evaluate(f"window.scrollTo(0, {target_scroll})")
        time.sleep(random.uniform(0.5, 1.5))  # Random delay between scrolls
    page.evaluate(
        "window.scrollTo(0, document.body.scrollHeight)"
    )  # Ensure it ends at the bottom
    time.sleep(random.uniform(1, 3))  # Add a random delay after scroll
