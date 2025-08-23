import os
import datetime
import time
import re
import random
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.connect import get_service

# --- User-Agent List ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/126.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/119.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0",
]

print("Script started: Initializing...")
print(f"Current working directory: {os.getcwd()}")
print(f"Contents of current directory: {os.listdir()}")

# --- Configuration ---
SHEET_NAME = "FBMP"
LOG_FILE = "logs/price_update_log.txt"
ROW_LIMIT = 5  # Limit the number of rows processed for testing

# Column Mappings (0-indexed)
VA_NOTES_COL = 0  # A: "VA Notes"
LAST_STOCK_CHECK_COL = 3  # D: "Last stock check" - NEW
PRICE_COL = 23  # X: "Supplier Price For ONE Unit"
PRODUCT_ID_COL = 31  # AF: "Supplier in use" (also acts as product ID for the row)

# Define supplier URL columns and their corresponding price update columns (if different from PRICE_COL)
# For now, all prices go to PRICE_COL (X)
# We need to define the columns where the URLs are located.
# Example: {URL_COL_INDEX: "Supplier Name for Logging"}
SUPPLIER_URL_COLS = {
    31: "Supplier in use",  # AF
    34: "Supplier A",  # AH
    35: "Supplier B",  # AI
    36: "Supplier C",  # AJ
    37: "Supplier D",  # AK
    38: "Supplier E",  # AL
    39: "Supplier F",  # AM
    40: "Supplier G",  # AN
    41: "Supplier H",  # AO
    42: "Supplier I",  # AP
    43: "Supplier J",  # AQ
}

# --- Helper Functions ---
ERROR_LOG_FILE = "logs/error_log.txt"  # Define new error log file


def truncate_log_file(file_path, max_lines=100):
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            with open(file_path, "w") as f:
                f.writelines(lines[-max_lines:])
    except FileNotFoundError:
        print(f"Log file not found: {file_path}")
    except Exception as e:
        print(f"Error truncating log file {file_path}: {e}")


def log_update(product_id, old_price, new_price, status, message=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Product ID: {product_id}, Old Price: {old_price}, New Price: {new_price}, Status: {status}, Message: {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

    # Log specific errors to a separate file
    if status == "Failed" and (
        "blocked" in message.lower()
        or "captcha" in message.lower()
        or "timeout" in message.lower()
        or "error" in message.lower()
    ):
        with open(ERROR_LOG_FILE, "a") as f_error:
            f_error.write(log_entry)


def parse_price(text):
    # Extracts a price from text, handling various formats (e.g., $1,234.56, 1.234,56, 1234.56)
    # This is a basic implementation and might need refinement based on actual website formats
    match = re.search(r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?|\d+[.,]\d{2})", text)
    if match:
        # Remove commas, replace decimal comma with dot, then convert to float
        price_str = match.group(0).replace(",", "")
        if "." not in price_str and "," in price_str:  # Handle European decimal comma
            price_str = price_str.replace(",", ".")
        return float(price_str)
    return None


# --- Core Scraping Logic ---
def scrape_product_details(url, page):  # Reverted to original
    price = None
    in_stock = False
    error_message = ""

    if not url or not url.startswith("http"):
        return {"price": None, "in_stock": False, "error": "Invalid URL"}

    try:
        # Simulate human-like mouse movements before navigation
        for _ in range(random.randint(3, 7)):  # Perform 3 to 7 random mouse movements
            x = random.randint(0, page.viewport_size["width"])
            y = random.randint(0, page.viewport_size["height"])
            page.mouse.move(x, y, steps=random.randint(5, 15))  # Move with random steps
            time.sleep(random.uniform(0.1, 0.5))  # Short random delay between movements

        page.goto(
            url,
            wait_until=random.choice(["domcontentloaded", "load", "networkidle"]),
            timeout=30000,
        )  # Reverted to page.goto

        # Simulate human-like scrolling after page load
        scroll_height = page.evaluate("document.body.scrollHeight")
        scroll_steps = random.randint(3, 7)  # Random number of scroll steps
        for i in range(scroll_steps):
            # Scroll to a random position within the page
            target_scroll = random.uniform(0, scroll_height)
            page.evaluate(f"window.scrollTo(0, {target_scroll})")
            time.sleep(random.uniform(0.5, 1.5))  # Random delay between scrolls
        page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight)"
        )  # Ensure it ends at the bottom
        time.sleep(random.uniform(1, 3))  # Add a random delay after scroll

        page_content = (
            page.content().lower()
        )  # Get full page content for broader search
        print(
            f"DEBUG: Page content for {url}:\n{page_content[:1000]}... (truncated)"
        )  # Log first 1000 chars

        # --- Blocked Detection ---
        blocked_indicators = [
            "robot or human activate and hold the button to confirm that you’re human. thank you",
            "captcha",  # General captcha detection
            "access denied",
            "verify you are human",
            "are you a robot?",
            "to continue, please type the characters below",
            "unusual traffic from your computer network",
        ]
        for indicator in blocked_indicators:
            if indicator in page_content:
                print(f"DEBUG: Detected blocked for {url}")
                return {
                    "price": None,
                    "in_stock": False,
                    "error": "Blocked: Robot/Human verification or Captcha",
                }

        # --- Out of Stock / Page Not Found Detection ---
        out_of_stock_page_indicators = [
            "sorry we couldn't find that page. try searching or go to amazon's home page.",
            "currently unavailable. we don't know when or if this item will be back in stock.",
            "404 page not found the page you requested does not exist.",
        ]
        for indicator in out_of_stock_page_indicators:
            if indicator in page_content:
                print(f"DEBUG: Detected out of stock/404 for {url}")
                return {
                    "price": None,
                    "in_stock": False,
                    "error": "Out of Stock: Page not found or item unavailable",
                }

        # --- Price Extraction ---
        # Amazon-specific selectors often include 'span.a-price-whole' and 'span.a-price-fraction'
        # or '#priceblock_ourprice', '#priceblock_dealprice'
        # It's crucial to use robust selectors and wait for them to be present.
        price_selectors = [
            "span.a-price span.a-offscreen",  # Common Amazon price selector
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            ".price",
            ".product-price",
            "[data-test='product-price']",
            ".current-price",
            "span[itemprop='price']",
            "div.price span",
            "b.price",
            "p.price",
            "span.price-value",
        ]

        # Wait for at least one of the price selectors to be visible
        # This helps with dynamic content loading
        try:
            page.wait_for_selector(
                ", ".join(price_selectors), timeout=10000
            )  # Wait for any of the selectors
        except PlaywrightTimeoutError:
            print(f"Warning: Price selector not found within timeout for {url}")
            error_message = "Price selector timeout"
            # Continue without price, it will be handled as not found

        for selector in price_selectors:
            try:
                price_element = page.query_selector(selector)
                if price_element:
                    price_text = price_element.inner_text()
                    price = parse_price(price_text)
                    if price is not None:
                        print(
                            f"DEBUG: Price found for {url} using selector {selector}: {price}"
                        )
                        break  # Found a price, no need to check other selectors
            except Exception as e:
                print(f"DEBUG: Error with selector {selector} for {url}: {e}")
                continue  # Selector not found or other issue, try next

        # Fallback to regex if no specific selector works
        if price is None:
            body_text = page.inner_text("body")
            price = parse_price(body_text)
            if price is not None:
                print(f"DEBUG: Price found for {url} using regex fallback: {price}")
            else:
                print(f"DEBUG: No price found for {url} even with regex fallback.")

        # --- In-Stock/Availability Detection (after price, as price implies availability) ---
        # Common in-stock indicators (highly site-specific, add more as needed)
        in_stock_indicators = [
            "in stock",
            "add to cart",
            "add to bag",
            "buy now",
            "available",
            "add to basket",
        ]
        out_of_stock_indicators = [
            "out of stock",
            "currently unavailable",
            "backorder",
        ]

        # Check for positive indicators
        for indicator in in_stock_indicators:
            if indicator in page_content:
                in_stock = True
                print(f'DEBUG: Positive stock indicator "{indicator}" found for {url}')
                break

        # If positive indicator found, check for negative ones to override
        if in_stock:
            for indicator in out_of_stock_indicators:
                if indicator in page_content:
                    in_stock = (
                        False  # Overwrite if an out-of-stock message is also present
                    )
                    print(
                        f'DEBUG: Negative stock indicator "{indicator}" found for {url}, overriding to out of stock.'
                    )
                    break
            else:  # If no clear positive or negative, assume in stock if price was found
                if price is not None:  # If a price was found, it's likely in stock
                    in_stock = True
                else:  # If no price and no clear indicators, default to False (safer)
                    in_stock = False
        else:
            print(f"DEBUG: No positive stock indicators found for {url}")

    except PlaywrightTimeoutError:
        error_message = "Page load timeout"
        print(f"DEBUG: Page load timeout for {url}")
    except Exception as e:
        error_message = f"Scraping error: {e}"
        print(f"DEBUG: General scraping error for {url}: {e}")

    final_result = {"price": price, "in_stock": in_stock, "error": error_message}
    print(f"DEBUG: Final scraped data for {url}: {final_result}")
    return final_result


# --- Main Automation Logic ---
def run_price_update_automation(page):
    print("Attempting to get Google Sheets service...")
    service = get_service()
    if not service:
        print("Error: Could not connect to Google Sheets API. Exiting.")
        log_update("N/A", "N/A", "N/A", "Failed", "API Connection Error")
        return

    print("Successfully connected to Google Sheets API.")
    print(f"Attempting to read sheet: {SHEET_NAME}")

    try:
        result = (
            service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=os.environ.get("SPREADSHEET_ID")
                or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw",  # Use env var or hardcoded
                ranges=[f"{SHEET_NAME}!A:AQ"],
            )
            .execute()
        )
        # batchGet returns a dictionary with 'valueRanges' key, which is a list
        # We are requesting only one range, so we take the first item's values
        values = result.get('valueRanges', [{}])[0].get('values', [])

        if not values:
            print("No data found in the sheet.")
            return

        current_date = datetime.datetime.now().strftime("%m/%d")  # Format: MM/DD

        # Iterate through each row (starting from row 5, which is index 4)
        for row_index, row in enumerate(
            values[:10]
        ):  # Process only up to ROW_LIMIT rows
            if row_index < 4:  # Skip rows 0, 1, 2, 3 (i.e., up to row 4)
                continue

            product_id = (
                row[PRODUCT_ID_COL]
                if len(row) > PRODUCT_ID_COL
                else f"Row_{row_index + 1}"
            )
            old_price_str = row[PRICE_COL] if len(row) > PRICE_COL else "0"
            old_price = parse_price(old_price_str) or 0.0

            best_supplier_url = None
            lowest_price_found = float("inf")
            chosen_supplier_name = "N/A"

            supplier_results = []  # Store results for all suppliers for this product

            # Iterate through supplier URL columns
            for col_index, supplier_name in SUPPLIER_URL_COLS.items():
                if len(row) > col_index:
                    supplier_url = row[col_index]
                    print(
                        f"Scraping Product ID: {product_id}, Supplier: {supplier_name}, URL: {supplier_url}"
                    )
                    scraped_data = scrape_product_details(
                        supplier_url, page
                    )  # Pass page to scrape_product_details
                    supplier_results.append(
                        {
                            "url": supplier_url,
                            "name": supplier_name,
                            "price": scraped_data["price"],
                            "in_stock": scraped_data["in_stock"],
                            "error": scraped_data["error"],
                        }
                    )
                    time.sleep(
                        random.uniform(2, 5)
                    )  # Be polite, add a delay between requests

            # Process scraped results to find the best supplier
            for result in supplier_results:
                if result["in_stock"] and result["price"] is not None:
                    if result["price"] < lowest_price_found:
                        lowest_price_found = result["price"]
                        best_supplier_url = result["url"]
                        chosen_supplier_name = result["name"]
                    elif result["price"] == lowest_price_found:
                        # Tie-breaking: keep the first one encountered (which is implicitly handled by iteration order)
                        pass

            new_va_note = ""
            new_price_to_update = ""
            new_supplier_url_to_update = ""

            # Initialize logging variables for the current product
            log_status = "Success" # Assume success initially
            log_message = f"Chosen supplier: {chosen_supplier_name}" # Default success message

            # --- COLLECT UPDATES FOR BATCH UPDATE ---
            requests = [] # Initialize requests list here

            # Determine background color based on status
            background_color = {}
            if log_status == "Success":
                background_color = {"red": 1.0, "green": 1.0, "blue": 1.0}  # White
                new_price_to_update = lowest_price_found
                new_va_note = f"Price updated {current_date}"
            elif log_status == "Failed":
                background_color = {"red": 1.0, "green": 0.0, "blue": 0.0}  # Red
                new_price_to_update = old_price # Keep old price
                new_va_note = log_message # Use the error message as VA note
            elif log_status == "No Change":
                background_color = {"red": 0.8, "green": 0.8, "blue": 0.8}  # Grey (or some other neutral color)
                new_price_to_update = old_price # Keep old price
                new_va_note = "No change"

            # Add request to color the entire row
            requests.append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,  # Assuming the first sheet (index 0)
                            "startRowIndex": row_index,
                            "endRowIndex": row_index + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": background_color,
                                "textFormat": {
                                    "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0} # Black text
                                }
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.foregroundColor",
                    }
                }
            )

            # Add request to update price
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": row_index,
                            "endRowIndex": row_index + 1,
                            "startColumnIndex": PRICE_COL,
                            "endColumnIndex": PRICE_COL + 1,
                        },
                        "rows": [
                            {
                                "values": [
                                    {"userEnteredValue": {"numberValue": new_price_to_update}}
                                ]
                            }
                        ],
                        "fields": "userEnteredValue",
                    }
                }
            )

            # Add request to update VA Notes
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": row_index,
                            "endRowIndex": row_index + 1,
                            "startColumnIndex": VA_NOTES_COL,
                            "endColumnIndex": VA_NOTES_COL + 1,
                        },
                        "rows": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": new_va_note}}
                                ]
                            }
                        ],
                        "fields": "userEnteredValue",
                    }
                }
            )

            # Add request to update Last Stock Check
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": row_index,
                            "endRowIndex": row_index + 1,
                            "startColumnIndex": LAST_STOCK_CHECK_COL,
                            "endColumnIndex": LAST_STOCK_CHECK_COL + 1,
                        },
                        "rows": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": current_date}}
                                ]
                            }
                        ],
                        "fields": "userEnteredValue",
                    }
                }
            )

            if lowest_price_found == float("inf"):
                log_status = "Failed"
                log_message = "No valid price found from any supplier or all out of stock"
                # If no price found, ensure new_va_note reflects this
                if new_va_note != "Blocked": # Don't overwrite if already blocked
                    new_va_note = "Price not found / Out of stock"


            # Execute batch update for the current row only if there's a change
            if new_va_note != "No change": # This condition is for updating the sheet, not logging
                try:
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=os.environ.get("SPREADSHEET_ID")
                        or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw",
                        body={"requests": requests},
                    ).execute()
                    print(
                        f"Successfully updated row {row_index + 1} for Product ID: {product_id}"
                    )
                    # If batch update was successful, log_status and log_message are already set correctly (Success or Failed due to scraping)
                except Exception as e:
                    print(
                        f"Error updating row {row_index + 1} for Product ID: {product_id}: {e}"
                    )
                    log_status = "Failed" # Override status to Failed
                    log_message = f"Sheet update error: {e}" # Set specific error message
            else:
                print(f"No change for Product ID: {product_id}. Skipping update.")
                log_status = "No Change"
                log_message = "No change in price or stock status."

            # Log the final status for the current product
            log_update(
                product_id,
                old_price,
                new_price_to_update, # Use new_price_to_update as it reflects the final price (or old price if no change)
                log_status,
                log_message,
            )

    except PlaywrightTimeoutError:
        error_message = "Page load timeout"
        print(f"Playwright Timeout Error: {error_message}")
    except Exception as e:
        error_message = f"Scraping error: {e}"
        print(f"General Scraping Error: {e}")

    truncate_log_file(LOG_FILE)  # Truncate the price update log after automation run
    print("Script run finished.")

    # Display a notification pop-up
    # try:
    #     import tkinter as tk
    #     from tkinter import messagebox
    #
    #     root = tk.Tk()
    #     root.withdraw()  # Hide the main window
    #     messagebox.showinfo("Sheet Scraper", "Script run finished successfully!")
    #     root.destroy()
    # except ImportError:
    #     print("Tkinter not found. Cannot display pop-up notification.")
    # except Exception as e:
    #     print(f"Error displaying pop-up notification: {e}")


if __name__ == "__main__":
    import sys
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Redirect stdout and stderr to logs.txt
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'logs.txt')
    sys.stdout = open(log_file_path, 'w', encoding='utf-8')
    sys.stderr = sys.stdout # Redirect stderr to the same file

    try:
        # Example usage:
        # Ensure SPREADSHEET_ID is set in your environment or hardcoded in connect.py
        print("Attempting to import Playwright and launch browser...")
        from playwright.sync_api import sync_playwright  # Import sync_playwright directly
        from undetected_playwright import (
            stealth_sync,
        )  # Import stealth_sync (correct import)

        with sync_playwright() as p:  # Use sync_playwright directly
            print("DEBUG: Attempting to launch browser...")
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
            )
            print("DEBUG: Browser launched successfully.")
            print("DEBUG: Attempting to create new page context...")
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={
                    "width": random.randint(1200, 1600),
                    "height": random.randint(700, 1000),
                },
                device_scale_factor=random.uniform(1, 2),
                locale="en-US", # Set locale to en-US
            )  # Create context with user agent and viewport
            stealth_sync(context)  # Apply stealth to the context (correct usage)
            # Add the init script to hide webdriver flag to the context
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
            page = context.new_page()  # Create page from context
            print("DEBUG: Page created successfully.")
            print("Playwright browser launched successfully.")

            run_price_update_automation(page)

            browser.close()
            print("Playwright browser closed.")

    finally:
        if sys.stdout is not original_stdout:
            sys.stdout.close()
            sys.stdout = original_stdout
        if sys.stderr is not original_stderr:
            sys.stderr.close()
            sys.stderr = original_stderr
