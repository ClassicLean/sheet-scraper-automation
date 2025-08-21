import os
import datetime
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from connect import get_service # Assuming get_service will return the authenticated sheets service

# --- Configuration ---
SHEET_NAME = "FBMP" # Changed from "Sheet Scraping"
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
def log_update(product_id, old_price, new_price, status, message=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] Product ID: {product_id}, Old Price: {old_price}, New Price: {new_price}, Status: {status}, Message: {message}\n")

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
def scrape_product_details(url):
    price = None
    in_stock = False
    error_message = ""

    if not url or not url.startswith("http"):
        return {"price": None, "in_stock": False, "error": "Invalid URL"}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch() # You can choose other browsers like firefox or webkit
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000) # Increased timeout

            # --- Price Extraction ---
            # Common price selectors (add more specific ones as needed)
            price_selectors = [
                ".price",
                "#priceblock_ourprice",
                ".product-price",
                "[data-test='product-price']",
                ".current-price",
                "span[itemprop='price']",
                "div.price span",
                "b.price",
                "p.price",
                "span.price-value"
            ]
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
            else: # If no positive indicator, check for explicit out-of-stock
                for indicator in out_of_stock_indicators:
                    if indicator in page_content:
                        in_stock = False
                        break
                else: # If no positive or negative, assume in stock for now (can be refined)
                    in_stock = True # Default to True if no clear indicators, but this is risky

            browser.close()

    except PlaywrightTimeoutError:
        error_message = "Page load timeout"
    except Exception as e:
        error_message = f"Scraping error: {e}"

    return {"price": price, "in_stock": in_stock, "error": error_message}

# --- Main Automation Logic ---
def run_price_update_automation():
    service = get_service()
    if not service:
        print("Error: Could not connect to Google Sheets API.")
        log_update("N/A", "N/A", "N/A", "Failed", "API Connection Error")
        return

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

        updates_to_sheet = [] # To store updates for batch writing
        current_date = datetime.datetime.now().strftime("%Y-%m-%d") # Format: YYYY-MM-DD

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
                    scraped_data = scrape_product_details(supplier_url)
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

                if lowest_price_found < old_price:
                    new_va_note = "Down"
                elif lowest_price_found > old_price:
                    new_va_note = "Up"
                else:
                    new_va_note = "No change"
                log_update(product_id, old_price, lowest_price_found, "Success", f"Chosen supplier: {chosen_supplier_name}")
            else:
                new_va_note = "Price not found / Out of stock"
                new_price_to_update = old_price_str # Keep old price if no new valid price found
                new_supplier_url_to_update = row[PRODUCT_ID_COL] # Keep old supplier URL
                log_update(product_id, old_price, "N/A", "Failed", "No valid price found from any supplier or all out of stock")

            # Prepare updates for the current row
            # We need to update columns A, X, AF, and D (Last stock check)
            # The Sheets API update method requires a list of lists for values
            # We'll update specific cells, so we need to calculate the A1 notation for each.

            # Update VA Notes (Column A)
            updates_to_sheet.append({
                'range': f"{SHEET_NAME}!{chr(65 + VA_NOTES_COL)}{row_index + 1}",
                'values': [[new_va_note]]
            })
            # Update Price (Column X)
            updates_to_sheet.append({
                'range': f"{SHEET_NAME}!{chr(65 + PRICE_COL)}{row_index + 1}",
                'values': [[new_price_to_update]]
            })
            # Update Supplier in use URL (Column AF)
            updates_to_sheet.append({
                'range': f"{SHEET_NAME}!{chr(65 + PRODUCT_ID_COL)}{row_index + 1}",
                'values': [[new_supplier_url_to_update]]
            })
            # Update Last stock check (Column D) - NEW
            updates_to_sheet.append({
                'range': f"{SHEET_NAME}!{chr(65 + LAST_STOCK_CHECK_COL)}{row_index + 1}",
                'values': [[current_date]]
            })

        # Perform batch update to minimize API calls
        if updates_to_sheet:
            body = {
                'valueInputOption': 'RAW',
                'data': updates_to_sheet
            }
            service.spreadsheets().values().batchUpdateByDataRange(
                spreadsheetId=os.environ.get('SPREADSHEET_ID') or "15CLPMfBtu0atxtWWh0Hyr92AWkMdauG0ONJ0X7EUsMw",
                body=body
            ).execute()
            print(f"Successfully updated {len(updates_to_sheet)} cells in the sheet.")

    except Exception as e:
        print(f"An error occurred during automation: {e}")
        log_update("N/A", "N/A", "N/A", "Failed", f"Automation error: {e}")

if __name__ == '__main__':
    # Example usage:
    # Ensure SPREADSHEET_ID is set in your environment or hardcoded in connect.py
    run_price_update_automation()