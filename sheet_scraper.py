import os
import datetime
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError # MOVED BACK TO TOP
from connect import get_service

print("Script started: Initializing...")
print(f"Current working directory: {os.getcwd()}")
print(f"Contents of current directory: {os.listdir()}")

# --- Configuration ---
SHEET_NAME = "FBMP"
LOG_FILE = "price_update_log.txt"

# Column Mappings (0-indexed)
VA_NOTES_COL = 0     # A: "VA Notes"
LAST_STOCK_CHECK_COL = 3 # D: "Last stock check" - NEW
PRICE_COL = 23       # X: "Supplier Price For ONE Unit"
PRODUCT_ID_COL = 31  # AF: "Supplier in use" (also acts as product ID for the row)

# Define supplier URL columns and their corresponding price update columns (if different from PRICE_COL)
# For now, all prices go to PRICE_COL (X)
# We need to define the columns where the URLs are located.
# Example: {URL_COL_INDEX: "Supplier Name for Logging"}
SUPPLIER_URL_COLS = {
    31: "Supplier in use", # AF
    34: "Supplier A",      # AH
    35: "Supplier B",      # AI
    36: "Supplier C",      # AJ
    37: "Supplier D",      # AK
    38: "Supplier E",      # AL
    39: "Supplier F",      # AM
    40: "Supplier G",      # AN
    41: "Supplier H",      # AO
    42: "Supplier I",      # AP
    43: "Supplier J",      # AQ
}

# --- Helper Functions ---
ERROR_LOG_FILE = "error_log.txt" # Define new error log file

def log_update(product_id, old_price, new_price, status, message=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Product ID: {product_id}, Old Price: {old_price}, New Price: {new_price}, Status: {status}, Message: {message}
"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    
    # Log specific errors to a separate file
    if status == "Failed" and ("blocked" in message.lower() or "captcha" in message.lower() or "timeout" in message.lower() or "error" in message.lower()):
        with open(ERROR_LOG_FILE, "a") as f_error:
            f_error.write(log_entry)


def parse_price(text):
    # Extracts a price from text, handling various formats (e.g., $1,234.56, 1.234,56, 1234.56)
    # This is a basic implementation and might need refinement based on actual website formats
    match = re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?|\d+[.,]\d{2})', text)
    if match:
        # Remove commas, replace decimal comma with dot, then convert to float
        price_str = match.group(0).replace(',', '')
        if '.' not in price_str and ',' in price_str: # Handle European decimal comma
            price_str = price_str.replace(',', '.')
        return float(price_str)
    return None

# --- Core Scraping Logic ---
def scrape_product_details(url, page): # Modified to accept page
    price = None
    in_stock = False
    error_message = ""

    if not url or not url.startswith("http"):
        return {"price": None, "in_stock": False, "error": "Invalid URL"}

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000) # Increased timeout

        # --- Price Extraction ---
        # Amazon-specific selectors often include 'span.a-price-whole' and 'span.a-price-fraction'
        # or '#priceblock_ourprice', '#priceblock_dealprice'
        # It's crucial to use robust selectors and wait for them to be present.
        price_selectors = [
                "span.a-price span.a-offscreen", # Common Amazon price selector
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
                "span.price-value"
            ]
        
        # Wait for at least one of the price selectors to be visible
        # This helps with dynamic content loading
        try:
            page.wait_for_selector(" | ".join(price_selectors), timeout=10000) # Wait for any of the selectors
        except PlaywrightTimeoutError:
            print(f"Warning: Price selector not found within timeout for {url}")
            # Continue without price, it will be handled as not found

        for selector in price_selectors:
            try:
                price_element = page.query_selector(selector)
                if price_element:
                    price_text = price_element.inner_text()
                    price = parse_price(price_text)
                    if price is not None:
                        break # Found a price, no need to check other selectors
            except Exception:
                continue # Selector not found or other issue, try next

        # Fallback to regex if no specific selector works
        if price is None:
            body_text = page.inner_text("body")
            price = parse_price(body_text)

        # --- In-Stock/Availability Detection ---
        # Common in-stock indicators (highly site-specific, add more as needed)
        in_stock_indicators = [
            "in stock",
            "add to cart",
            "add to bag",
            "buy now",
            "available",
            "add to basket"
        ]
        out_of_stock_indicators = [
            "out of stock",
            "unavailable",
            "currently unavailable",
            "backorder"
        ]

        page_content = page.content().lower() # Get full page content for broader search

        # Check for positive indicators
        for indicator in in_stock_indicators:
            if indicator in page_content:
                in_stock = True
                break

        # If positive indicator found, check for negative ones to override
        if in_stock:
            for indicator in out_of_stock_indicators:
                if indicator in page_content:
                    in_stock = False # Overwrite if an out-of-stock message is also present
                    break
            else: # If no positive or negative, assume in stock for now (can be refined)
                in_stock = True # Default to True if no clear indicators, but this is risky

    except PlaywrightTimeoutError:
        error_message = "Page load timeout"
    except Exception as e:
        error_message = f"Scraping error: {e}"

    return {"price": price, "in_stock": in_stock, "error": error_message}

# --- Main Automation Logic ---
def run_price_update_automation():
    print("Attempting to get Google Sheets service...")
    service = get_service()
    if not service:
        print("Error: Could not connect to Google Sheets API. Exiting.")
        log_update("N/A", "N/A", "N/A", "Failed", "API Connection Error")
        return

    print("Successfully connected to Google Sheets API.")
    print(f"Attempting to read sheet: {SHEET_NAME}")

    try:
        # Read all data from the sheet
        # We need to read all columns that contain supplier URLs and the price column
        # Range should cover all relevant columns, e.g., A to AQ
        result = service.spreadsheets().values().get(
            spreadsheetId=os.environ.get('SPREADSHEET_ID') or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw", # Use env var or hardcoded
            range=f"{SHEET_NAME}!A:AQ"
        ).execute()
        values = result.get('values', [])

        if not values:
            print("No data found in the sheet.")
            return

        # updates_to_sheet = [] # REMOVE THIS - no longer batching this way
        current_date = datetime.datetime.now().strftime("%Y-%m-%d") # Format: YYYY-MM-DD

        print("Attempting to import Playwright and launch browser...")
        # from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError # REMOVE THIS LINE

        with sync_playwright() as p:
            browser = p.chromium.launch(args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--single-process",
                "--disable-setuid-sandbox",
                "--disable-gpu"
            ])
            page = browser.new_page()
            print("Playwright browser launched successfully.")

            # Iterate through each row (starting from row 5, which is index 4)
            for row_index, row in enumerate(values):
                if row_index < 4: # Skip rows 0, 1, 2, 3 (i.e., up to row 4)
                    continue

                product_id = row[PRODUCT_ID_COL] if len(row) > PRODUCT_ID_COL else f"Row_{row_index+1}"
                old_price_str = row[PRICE_COL] if len(row) > PRICE_COL else "0"
                old_price = parse_price(old_price_str) or 0.0

                best_supplier_url = None
                lowest_price_found = float('inf')
                chosen_supplier_name = "N/A"

                supplier_results = [] # Store results for all suppliers for this product

                # Iterate through supplier URL columns
                for col_index, supplier_name in SUPPLIER_URL_COLS.items():
                    if len(row) > col_index:
                        supplier_url = row[col_index]
                        print(f"Scraping Product ID: {product_id}, Supplier: {supplier_name}, URL: {supplier_url}")
                        scraped_data = scrape_product_details(supplier_url, page) # Pass page to scrape_product_details
                        supplier_results.append({
                            "url": supplier_url,
                            "name": supplier_name,
                            "price": scraped_data["price"],
                            "in_stock": scraped_data["in_stock"],
                            "error": scraped_data["error"]
                        })
                        time.sleep(2) # Be polite, add a delay between requests

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

                if lowest_price_found != float('inf'): # A valid price was found
                    new_price_to_update = str(lowest_price_found)
                    new_supplier_url_to_update = best_supplier_url

                    if lowest_price_found >= 299.99:
                        new_va_note = "$$$"
                    elif lowest_price_found < old_price:
                        new_va_note = "Down"
                    elif lowest_price_found > old_price:
                        new_va_note = "Up"
                    else:
                        new_va_note = "No change"
                    log_update(product_id, old_price, lowest_price_found, "Success", f"Chosen supplier: {chosen_supplier_name}")
                else:
                    # Check for specific error messages from scraping
                    all_suppliers_blocked = True
                    for result in supplier_results:
                        if result["error"] and ("blocked" in result["error"].lower() or "captcha" in result["error"].lower()):
                            new_va_note = "Blocked"
                            break
                        else:
                            all_suppliers_blocked = False

                    if new_va_note != "Blocked": # If not blocked, then it's genuinely not found or out of stock
                        new_va_note = ""

                    new_price_to_update = old_price_str # Keep old price if no new valid price found
                    new_supplier_url_to_update = row[PRODUCT_ID_COL] # Keep old supplier URL
                    log_update(product_id, old_price, "N/A", "Failed", "No valid price found from any supplier or all out of stock")

                # --- COLLECT UPDATES FOR BATCH UPDATE ---
                requests = []

                # Update VA Notes (Column A)
                requests.append({
                    'updateCells': {
                        'rows': [
                            {'values': [{'userEnteredValue': {'stringValue': new_va_note}}]}
                        ],
                        'fields': 'userEnteredValue',
                        'range': {
                            'sheetId': 0, # Assuming sheetId 0 for the first sheet, or get it dynamically
                            'startRowIndex': row_index,
                            'endRowIndex': row_index + 1,
                            'startColumnIndex': VA_NOTES_COL,
                            'endColumnIndex': VA_NOTES_COL + 1
                        }
                    }
                })

                # Update Price (Column X)
                requests.append({
                    'updateCells': {
                        'rows': [
                            {'values': [{'userEnteredValue': {'stringValue': new_price_to_update}}]}
                        ],
                        'fields': 'userEnteredValue',
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': row_index,
                            'endRowIndex': row_index + 1,
                            'startColumnIndex': PRICE_COL,
                            'endColumnIndex': PRICE_COL + 1
                        }
                    }
                })

                # Update Supplier in use URL (Column AF)
                requests.append({
                    'updateCells': {
                        'rows': [
                            {'values': [{'userEnteredValue': {'stringValue': new_supplier_url_to_update}}]}
                        ],
                        'fields': 'userEnteredValue',
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': row_index,
                            'endRowIndex': row_index + 1,
                            'startColumnIndex': PRODUCT_ID_COL,
                            'endColumnIndex': PRODUCT_ID_COL + 1
                        }
                    }
                })

                # Update Last stock check (Column D)
                requests.append({
                    'updateCells': {
                        'rows': [
                            {'values': [{'userEnteredValue': {'stringValue': current_date}}]}
                        ],
                        'fields': 'userEnteredValue',
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': row_index,
                            'endRowIndex': row_index + 1,
                            'startColumnIndex': LAST_STOCK_CHECK_COL,
                            'endColumnIndex': LAST_STOCK_CHECK_COL + 1
                        }
                    }
                })

                # Add row coloring if out of stock across all suppliers and not blocked
                if lowest_price_found == float('inf') and new_va_note != "Blocked":
                    requests.append({
                        'repeatCell': {
                            'range': {
                                'sheetId': 0,
                                'startRowIndex': row_index,
                                'endRowIndex': row_index + 1
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': {
                                        'red': 1.0,
                                        'green': 0.0,
                                        'blue': 0.0
                                    }
                                }
                            },
                            'blue': 0.0
                                }
                            },
                            'textFormat': {
                                'foregroundColor': {
                                    'red': 1.0,
                                    'green': 1.0,
                                    'blue': 1.0
                                }
                            },
                            'fields': 'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.foregroundColor'
                        }
                    })

                # Execute batch update for the current row
                try:
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=os.environ.get('SPREADSHEET_ID') or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw",
                        body={'requests': requests}
                    ).execute()
                    print(f"Successfully updated row {row_index + 1} for Product ID: {product_id}")
                except Exception as e:
                    print(f"Error updating row {row_index + 1} for Product ID: {product_id}: {e}")
                    log_update(product_id, old_price, "N/A", "Failed", f"Sheet update error: {e}")

            browser.close()
            print("Playwright browser closed.")

    except PlaywrightTimeoutError:
        error_message = "Page load timeout"
        print(f"Playwright Timeout Error: {error_message}")
    except Exception as e:
        error_message = f"Scraping error: {e}"
        print(f"General Scraping Error: {error_message}")

    # REMOVE BATCH UPDATE BLOCK - no longer needed with individual updates
    # if updates_to_sheet:
    #     body = {
    #         'valueInputOption': 'RAW',
    #         'data': updates_to_sheet
    #     }
    #     service.spreadsheets().values().batchUpdateByDataRange(
    #         spreadsheetId=os.environ.get('SPREADSHEET_ID') or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw",
    #         body=body
    #     ).execute()
    #     print(f"Successfully updated {len(updates_to_sheet)} cells in the sheet.")

if __name__ == '__main__':
    # Example usage:
    # Ensure SPREADSHEET_ID is set in your environment or hardcoded in connect.py
    run_price_update_automation()
