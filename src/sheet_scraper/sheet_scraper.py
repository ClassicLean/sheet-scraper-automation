import os
import datetime
import time
import random
import sys
import contextlib

from playwright.sync_api import sync_playwright
from undetected_playwright.ninja import stealth_sync

from sheet_scraper.connect import get_service
from sheet_scraper.proxy_manager import ProxyManager
from sheet_scraper.captcha_solver import CaptchaSolver
from sheet_scraper.scraping_utils import (
    read_sheet_data,
    parse_price,
    process_scraped_results,
    update_sheet,
    log_update,
    truncate_log_file,
    create_color_request,
    LOG_FILE,
    is_blocked,
    extract_price,
    is_in_stock,
    simulate_human_interaction,
)
from sheet_scraper.constants import (
    SHEET_NAME,
    VA_NOTES_COL,
    LAST_STOCK_CHECK_COL,
    PRICE_COL,
    PRODUCT_ID_COL,
    SUPPLIER_URL_COLS,
    COLOR_WHITE,
    COLOR_RED,
    USER_AGENTS,
    COL_AG,
    COL_AB,
    COL_AE,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
)


def scrape_product_details(url, page, captcha_solver):
    print(f"DEBUG: Scraping details for {url}")
    try:
        # Navigate to the URL
        page.goto(url)

        # Simulate human-like interaction
        simulate_human_interaction(page)

        # Check for blocking
        if is_blocked(page.content()):
            print(f"DEBUG: Detected blocked for {url}")
            # Attempt to solve CAPTCHA if blocked
            if captcha_solver and os.environ.get("TWOCAPTCHA_API_KEY"):
                # This part needs to be more sophisticated to identify sitekey and URL for CAPTCHA
                # For now, we'll just return blocked if CAPTCHA is detected
                # In a real scenario, you'd pass sitekey and URL to solve_recaptcha
                print(f"DEBUG: CAPTCHA detected for {url}. Attempting to solve...")
                # Assuming a generic sitekey and URL for demonstration.
                # You would need to extract these from the page content.
                # For now, we'll just return blocked.
                return {"price": None, "in_stock": False, "error": "Blocked by CAPTCHA"}
            else:
                return {"price": None, "in_stock": False, "error": "Blocked"}

        # Extract price
        price = extract_price(page)
        if price is None:
            print(f"DEBUG: No price found for {url}")
            return {"price": None, "in_stock": False, "error": "Price not found"}

        # Check stock status
        in_stock = is_in_stock(page)

        print(f"DEBUG: Final scraped data for {url}: {{'price': {price}, 'in_stock': {in_stock}, 'error': ''}}")
        return {"price": price, "in_stock": in_stock, "error": ""}

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"price": None, "in_stock": False, "error": str(e)}


print("Script started: Initializing...")
print(f"Current working directory: {os.getcwd()}")
print(f"Contents of current directory: {os.listdir()}")


# --- Main Automation Logic ---
def run_price_update_automation(page, captcha_solver):
    print("Attempting to get Google Sheets service...")
    service = get_service()
    if not service:
        print("Error: Could not connect to Google Sheets API. Exiting.")
        log_update("N/A", "N/A", "N/A", "Failed", "API Connection Error")
        return

    print("Successfully connected to Google Sheets API.")
    print(f"Attempting to read sheet: {SHEET_NAME}")

    spreadsheet_id = os.environ.get("SPREADSHEET_ID") or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw"
    values = read_sheet_data(service, spreadsheet_id, SHEET_NAME)

    if not values:
        print("No data found in the sheet.")
        return

    current_date = datetime.datetime.now().strftime("%m/%d")

    for row_index, row in enumerate(values[:10]):
        if row_index < 4:
            continue

        product_id = (
            row[PRODUCT_ID_COL] if len(row) > PRODUCT_ID_COL else f"Row_{row_index + 1}"
        )
        old_price_str = row[PRICE_COL] if len(row) > PRICE_COL else "0"
        old_price = parse_price(old_price_str) or 0.0

        supplier_results = []
        for col_index, supplier_name in SUPPLIER_URL_COLS.items():
            if len(row) > col_index:
                supplier_url = row[col_index]
                scraped_data = scrape_product_details(supplier_url, page, captcha_solver)
                supplier_results.append(
                    {
                        "url": supplier_url,
                        "name": supplier_name,
                        "price": scraped_data["price"],
                        "in_stock": scraped_data["in_stock"],
                        "error": scraped_data["error"],
                    }
                )
                time.sleep(random.uniform(2, 5))

        lowest_price_found, best_supplier_url, chosen_supplier_name = (
            process_scraped_results(supplier_results)
        )

        new_va_note = ""
        if lowest_price_found != float("inf") and best_supplier_url is not None:
            new_price_to_update = lowest_price_found
            if new_price_to_update > old_price:
                new_va_note = "Up"
            elif new_price_to_update < old_price:
                new_va_note = "Down"
        else:
            new_price_to_update = old_price
            new_va_note = "Price not found / Out of stock"

        requests = []
        if lowest_price_found != float("inf") and best_supplier_url is not None:
            # Item is available: entire row white background
            requests.append(create_color_request(row_index, COLOR_WHITE))
        else:
            # Item is unavailable: entire row red background, white text
            requests.append(create_color_request(row_index, COLOR_RED, text_color=COLOR_WHITE))
            
            # Exceptions for specific columns
            # Column AG (32): black background, white text (default for unavailable row)
            requests.append(create_color_request(row_index, COLOR_BLACK, col_index=COL_AG, text_color=COLOR_WHITE))
            # Column AB (27): blue background, white text (default for unavailable row)
            requests.append(create_color_request(row_index, COLOR_BLUE, col_index=COL_AB, text_color=COLOR_WHITE))
            # Column AE (30): green background, black text
            requests.append(create_color_request(row_index, COLOR_GREEN, col_index=COL_AE, text_color=COLOR_BLACK))

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
                                if isinstance(new_price_to_update, (int, float)) and new_price_to_update != float("inf")
                                else {"userEnteredValue": {"stringValue": "N/A"}}
                            ]
                        }
                    ],
                    "fields": "userEnteredValue",
                }
            }
        )

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

        log_status = "Success" if lowest_price_found != float("inf") and best_supplier_url is not None else "Failed"
        log_message = f"Chosen supplier: {chosen_supplier_name}" if log_status == "Success" else new_va_note

        if update_sheet(service, spreadsheet_id, requests):
            log_update(
                product_id, old_price, new_price_to_update, log_status, log_message, row_number=row_index + 1
            )
        else:
            log_update(
                product_id, old_price, new_price_to_update, "Failed", "Sheet update error (API call failed)", row_number=row_index + 1
            )

    truncate_log_file(LOG_FILE)
    print("Script run finished.")


if __name__ == "__main__":
    log_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs", "logs.txt"
    )
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    try:
        with open(log_file_path, "w", encoding="utf-8", buffering=1) as f:
            with contextlib.redirect_stdout(f):
                with contextlib.redirect_stderr(f): # Redirect stderr to the same file
                    # Example usage:
                    # Ensure SPREADSHEET_ID is set in your environment or hardcoded in connect.py

                    # Read proxies from proxies.txt
                    try:
                        with open("proxies.txt", "r") as f_proxies: # Renamed to avoid conflict
                            proxies = [line.strip() for line in f_proxies.readlines()]
                    except FileNotFoundError:
                        proxies = []
                        print("proxies.txt not found, running without proxies.")

                    proxy_manager = ProxyManager(proxies)
                    captcha_solver = CaptchaSolver(os.environ.get("TWOCAPTCHA_API_KEY"))

                    with sync_playwright() as p:  # Use sync_playwright directly
                        print("DEBUG: Attempting to launch browser...")
                        proxy = proxy_manager.get_proxy()
                        browser = p.chromium.launch(
                            headless=False,
                            args=[
                                "--disable-dev-shm-usage",
                                "--no-sandbox",
                                "--disable-setuid-sandbox",
                            ],
                            proxy={"server": proxy} if proxy else None,
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
                            locale="en-US",  # Set locale to en-US
                        )  # Create context with user agent and viewport
                        stealth_sync(context)  # Apply stealth to the context (correct usage)
                        # Add the init script to hide webdriver flag to the context
                        context.add_init_script(
                            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
                        )
                        page = context.new_page()  # Create page from context
                        print("DEBUG: Page created successfully.")
                        print("Playwright browser launched successfully.")

                        run_price_update_automation(page, captcha_solver)

                        browser.close()
                        print("Playwright browser closed.")

    except FileNotFoundError as e:
        sys.stdout.write(f"Error: The directory for the log file does not exist or the path is invalid: {e}\n")
    except PermissionError as e:
        sys.stdout.write(f"Error: Permission denied to write to the log file: {e}\n")
    except Exception as e:
        sys.stdout.write(f"An unexpected error occurred during logging setup or script execution: {e}\n")

