"""
Pricing utilities for parsing and extracting price information.

This module contains functions for price parsing with support for
various formats and currency symbols.
"""

import re


def parse_price(price_text: str | None) -> float | None:
    """
    Parse price text and extract numeric value.

    Args:
        price_text: Text containing price information (must be string)

    Returns:
        float: Parsed price value or None if parsing fails
    """
    if price_text is None:
        return None

    # Only accept string types for parsing
    if not isinstance(price_text, str):
        return None

    # Clean the text to remove extra whitespace
    price_text = price_text.strip()

    # Remove common currency symbols and normalize spacing
    cleaned_text = re.sub(r"[$€£¥₹]\s*", "", price_text)

    # Try multiple patterns in order of priority
    patterns = [
        # Pattern 1: Proper thousands separators like 1,000.00 or 1,000,000.50
        r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?)",
        # Pattern 2: Simple numbers like 12345 or 123.45
        r"(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            price_str = match.group(1)

            # For comma patterns, validate comma usage
            if "," in price_str:
                parts = price_str.split(",")
                # First part: 1-3 digits, subsequent parts: exactly 3 digits (before decimal)
                if len(parts[0]) > 3:
                    continue  # Try next pattern
                for part in parts[1:]:
                    # Handle decimal in last part
                    digit_part = part.split(".")[0] if "." in part else part
                    if len(digit_part) != 3 or not digit_part.isdigit():
                        continue  # Try next pattern

                # Valid comma pattern - remove commas and convert
                price_str = price_str.replace(",", "")
                try:
                    return float(price_str)
                except ValueError:
                    continue
            else:
                # Simple number pattern - check if original text has invalid commas
                if "," in cleaned_text:
                    # Cleaned text has commas but we matched without them
                    # This might be a "1,2,3" pattern - reject it
                    comma_count = cleaned_text.count(",")
                    if comma_count > 0:
                        # Check if it looks like a valid thousands separator
                        if not re.search(r"\d{1,3}(?:,\d{3})+", cleaned_text):
                            continue  # Skip invalid comma patterns

                try:
                    return float(price_str)
                except ValueError:
                    continue

    return None


def is_quantity_element(element) -> bool:
    """
    Enhanced detection of quantity-related elements to filter out.

    Args:
        element: Playwright element

    Returns:
        bool: True if this element appears to be quantity-related
    """
    try:
        # Check element attributes
        name_attr = element.get_attribute("name") or ""
        id_attr = element.get_attribute("id") or ""
        class_attr = element.get_attribute("class") or ""

        # Check for quantity-related attributes
        quantity_indicators = ["quantity", "qty", "amount", "count"]
        for indicator in quantity_indicators:
            if (indicator in name_attr.lower() or
                indicator in id_attr.lower() or
                indicator in class_attr.lower()):
                return True

        # Check tag type - form controls are often quantity selectors
        tag_name = element.tag_name.lower()
        if tag_name in ["option", "select", "input"]:
            # Additional checks for form elements
            input_type = element.get_attribute("type") or ""
            if input_type in ["number", "range", "hidden"]:
                return True

        # Check if element is inside a form with quantity-related attributes
        try:
            # Look for ancestor elements with quantity indicators
            ancestors = element.locator("xpath=ancestor-or-self::*[@name or @id or @class]")
            for i in range(min(5, ancestors.count())):  # Check up to 5 ancestor levels
                ancestor = ancestors.nth(i)
                ancestor_name = ancestor.get_attribute("name") or ""
                ancestor_id = ancestor.get_attribute("id") or ""
                ancestor_class = ancestor.get_attribute("class") or ""

                for indicator in quantity_indicators:
                    if (indicator in ancestor_name.lower() or
                        indicator in ancestor_id.lower() or
                        indicator in ancestor_class.lower()):
                        return True
        except Exception:
            pass

        # Check if element is inside select/option structure
        try:
            if element.locator("xpath=ancestor::select").first:
                return True
            if element.locator("xpath=ancestor::option").first:
                return True
        except Exception:
            pass

        return False
    except Exception:
        return False


def extract_price(page, config=None) -> float | None:
    """
    Enhanced price extraction with site-specific selectors and better error handling.

    Args:
        page: Playwright page object
        config: Configuration manager instance (optional)

    Returns:
        float: Extracted price or None if not found
    """
    # Initialize config if not provided
    if config is None:
        from sheet_scraper.config.config_manager import Config
        config = Config()

    # Check if this is an error page before attempting price extraction
    from sheet_scraper.utils.web_scraping import is_error_page
    # Skip error page detection for Amazon after geolocation setup since we've already handled location
    is_amazon = 'amazon.com' in page.url.lower()
    if not is_amazon and is_error_page(page):
        print(f"DEBUG: Skipping price extraction - detected error page: {page.url}")
        return None
    elif is_amazon:
        print(f"DEBUG: Amazon URL detected - proceeding with price extraction despite error page detection: {page.url}")

    site = config.detect_site(page.url)

    # Wait for page to be properly loaded
    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        # Additional wait for dynamic content
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"DEBUG: Timeout waiting for page load: {e}")

    selectors = config.get_price_selectors(site)

    print(f"DEBUG: extract_price - URL: {page.url}")
    print(f"DEBUG: extract_price - Detected site: {site}")
    print(f"DEBUG: extract_price - Using {len(selectors)} selectors")

    # Try site-specific selectors first
    for selector_idx, selector in enumerate(selectors):
        try:
            elements = page.query_selector_all(selector)
            print(f"DEBUG: Selector #{selector_idx+1} '{selector}' found {len(elements)} elements")

            # Special handling for Amazon hidden inputs
            if site == "amazon" and "input" in selector and "customerVisiblePrice" in selector:
                for element_idx, element in enumerate(elements):
                    try:
                        value = element.get_attribute("value")
                        if value:
                            price = parse_price(value)
                            print(f"DEBUG: Amazon input element #{element_idx+1} value: '{value}' -> parsed: {price}")
                            if price is not None and price > 0:
                                print(f"DEBUG: [SUCCESS] VALID PRICE FOUND using Amazon input '{selector}': {value} -> {price}")
                                return price
                    except Exception as e:
                        print(f"DEBUG: Error with Amazon input element #{element_idx+1}: {e}")
                        continue
                continue

            for element_idx, element in enumerate(elements):
                # Enhanced filtering for quantity/form elements
                if is_quantity_element(element):
                    print(f"DEBUG: Skipping element #{element_idx+1} - detected as quantity element")
                    continue

                price_text = element.inner_text().strip()
                if price_text:
                    price = parse_price(price_text)
                    print(f"DEBUG: Element #{element_idx+1} text: '{price_text}' -> parsed: {price}")

                    # Enhanced filtering: skip suspicious values that are likely quantities
                    if price is not None and price > 0:
                        # Skip single digits that appear without currency symbols (likely quantities)
                        if price <= 10 and price == int(price) and not any(symbol in price_text for symbol in ['$', '£', '€', '¥']):
                            print(f"DEBUG: Skipping price {price} - likely quantity (no currency symbol)")
                            continue

                        print(f"DEBUG: [SUCCESS] VALID PRICE FOUND using {site} selector '{selector}': {price_text} -> {price}")
                        return price
                    else:
                        print(f"DEBUG: Skipping invalid/zero price: {price}")
        except Exception as e:
            print(f"DEBUG: Error with {site} selector '{selector}': {e}")
            continue

    # Fallback to generic selectors
    if site != "generic":
        generic_selectors = config.get_price_selectors("generic")
        print(f"DEBUG: Falling back to {len(generic_selectors)} generic selectors")

        for selector_idx, selector in enumerate(generic_selectors):
            try:
                elements = page.query_selector_all(selector)
                print(f"DEBUG: Generic selector #{selector_idx+1} '{selector}' found {len(elements)} elements")

                for element_idx, element in enumerate(elements):
                    # Enhanced filtering for quantity/form elements
                    if is_quantity_element(element):
                        print(f"DEBUG: Skipping generic element #{element_idx+1} - detected as quantity element")
                        continue

                    price_text = element.inner_text().strip()
                    if price_text:
                        price = parse_price(price_text)
                        print(f"DEBUG: Generic element #{element_idx+1} text: '{price_text}' -> parsed: {price}")

                        # Enhanced filtering: skip suspicious values that are likely quantities
                        if price is not None and price > 0:
                            # Skip single digits that appear without currency symbols (likely quantities)
                            if price <= 10 and price == int(price) and not any(symbol in price_text for symbol in ['$', '£', '€', '¥']):
                                print(f"DEBUG: Skipping generic price {price} - likely quantity (no currency symbol)")
                                continue

                            print(f"DEBUG: [SUCCESS] VALID PRICE FOUND using generic selector '{selector}': {price_text} -> {price}")
                            return price
                        else:
                            print(f"DEBUG: Skipping invalid/zero generic price: {price}")
            except Exception as e:
                print(f"DEBUG: Error with generic selector '{selector}': {e}")
                continue

    # Amazon-specific handling for split price elements
    if site == "amazon":
        print("DEBUG: Trying Amazon-specific split price extraction")
        try:
            # Get all price-whole and price-fraction elements to find the right ones
            whole_elements = page.query_selector_all("span.a-price-whole")
            fraction_elements = page.query_selector_all("span.a-price-fraction")
            print(f"DEBUG: Found {len(whole_elements)} whole elements, {len(fraction_elements)} fraction elements")

            for whole_idx, whole_element in enumerate(whole_elements):
                # Enhanced filtering for quantity elements
                if is_quantity_element(whole_element):
                    print(f"DEBUG: Skipping Amazon whole element #{whole_idx+1} - detected as quantity element")
                    continue

                # Find corresponding fraction element nearby
                for _, fraction_element in enumerate(fraction_elements):
                    if is_quantity_element(fraction_element):
                        continue

                    try:
                        # Check if fraction is near the whole element (same price container)
                        whole_price = whole_element.inner_text().strip()
                        fraction_price = fraction_element.inner_text().strip()

                        if whole_price and fraction_price and whole_price.isdigit() and fraction_price.isdigit():
                            combined_price = f"{whole_price}.{fraction_price}"
                            price = parse_price(combined_price)
                            print(f"DEBUG: Amazon split price: {whole_price}.{fraction_price} -> {price}")

                            # Enhanced filtering: skip quantities but allow legitimate prices
                            if price is not None and price > 0:
                                # Skip single digits that are likely quantities
                                if price <= 10 and price == int(price):
                                    print(f"DEBUG: Skipping Amazon split price {price} - likely quantity")
                                    continue

                                print(f"DEBUG: [SUCCESS] VALID AMAZON SPLIT PRICE: {whole_price}.{fraction_price} -> {price}")
                                return price
                    except Exception:
                        continue
        except Exception as e:
            print(f"DEBUG: Error with Amazon split price extraction: {e}")

    # Final fallback: search page content for price patterns
    print("DEBUG: Trying final content-based price extraction")
    try:
        content = page.content()

        # Amazon-specific: Look for JSON price data first
        if site == "amazon":
            print("DEBUG: Searching for Amazon JSON price data")
            # Look for displayPrice in JSON
            json_price_match = re.search(r'"displayPrice"\s*:\s*"?\$?([0-9,]+\.?[0-9]*)"?', content, re.IGNORECASE)
            if json_price_match:
                price_text = json_price_match.group(1)
                price = parse_price(price_text)
                if price is not None and price > 0:
                    print(f"DEBUG: [SUCCESS] VALID PRICE found in Amazon JSON: {price_text} -> {price}")
                    return price

            # Look for priceAmount in JSON
            json_amount_match = re.search(r'"priceAmount"\s*:\s*([0-9,]+\.?[0-9]*)', content, re.IGNORECASE)
            if json_amount_match:
                price_text = json_amount_match.group(1)
                price = parse_price(price_text)
                if price is not None and price > 0:
                    print(f"DEBUG: [SUCCESS] VALID PRICE found in Amazon JSON priceAmount: {price_text} -> {price}")
                    return price

            # Look for hidden input values
            input_price_match = re.search(r'name="[^"]*customerVisiblePrice[^"]*"\s+value="?\$?([0-9,]+\.?[0-9]*)"?', content, re.IGNORECASE)
            if input_price_match:
                price_text = input_price_match.group(1)
                price = parse_price(price_text)
                if price is not None and price > 0:
                    print(f"DEBUG: [SUCCESS] VALID PRICE found in Amazon hidden input: {price_text} -> {price}")
                    return price

        # Generic price pattern search
        content_lower = content.lower()
        price_match = re.search(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", content_lower)
        if price_match:
            price_text = price_match.group(1)
            price = parse_price(price_text)
            if price is not None and price > 0:
                print(f"DEBUG: [SUCCESS] VALID PRICE found in content: ${price_text} -> {price}")
                return price
        else:
            print("DEBUG: No price pattern found in page content")
    except Exception as e:
        print(f"DEBUG: Error searching content for price: {e}")

    print(f"DEBUG: NO VALID PRICE FOUND for {page.url}")
    return None
