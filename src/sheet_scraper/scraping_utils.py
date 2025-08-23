import datetime
import re
import random
import time
from sheet_scraper.constants import IN_STOCK_INDICATORS, OUT_OF_STOCK_INDICATORS

LOG_FILE = "logs/price_update_log.txt"
ERROR_LOG_FILE = "logs/error_log.txt"

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

def log_update(product_id, old_price, new_price, status, message="", row_number=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Row: {row_number}, Product ID: {product_id}, Old Price: {old_price}, New Price: {new_price}, Status: {status}, Message: {message}\n" if row_number is not None else f"[{timestamp}] Product ID: {product_id}, Old Price: {old_price}, New Price: {new_price}, Status: {status}, Message: {message}\n"
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

def parse_price(price_text):
    if price_text is None:
        return None
    # Remove currency symbols, commas, and any non-numeric characters except for the decimal point
    cleaned_price = re.sub(r'[^\d.]', '', price_text)
    try:
        return float(cleaned_price)
    except ValueError:
        return None

def is_blocked(page_content):

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
            return True
    return False

def extract_price(page):
    price_selectors = [
        "div.price", # Added for vivo-us.com
        # Add specific selectors for vivo-us.com here if needed.
        # Example: "#product-price-element", ".price-display"
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
    except Exception:
        print(f"Warning: Price selector not found within timeout for {page.url}")
        # Continue without price, it will be handled as not found

    for selector in price_selectors:
        try:
            price_element = page.query_selector(selector)
            if price_element:
                price_text = price_element.inner_text()
                price = parse_price(price_text)
                if price is not None:
                    return price  # Found a price, no need to check other selectors
        except Exception as e:
            print(f"DEBUG: Error with selector {selector}: {e}")
            continue  # Selector not found or other issue, try next

    # Fallback to regex if no specific selector works
    body_text = page.inner_text("body")
    price = parse_price(body_text)
    if price is not None:
        return price
    else:
        return None

def is_in_stock(page):
    page_content = page.content().lower()

    # Check for out-of-stock indicators first
    for indicator in OUT_OF_STOCK_INDICATORS:
        if indicator in page_content:
            print(f"DEBUG: Out-of-stock detected by indicator: {indicator} for {page.url}")
            return False

    # Check for in-stock indicators
    for indicator in IN_STOCK_INDICATORS:
        if indicator in page_content:
            print(f"DEBUG: In-stock detected by indicator: {indicator} for {page.url}")
            return True

    # Fallback: if no clear indicators, assume in stock (or implement more sophisticated logic)
    print(f"DEBUG: No clear stock indicators found for {page.url}. Assuming in stock.")
    return True

def read_sheet_data(service, spreadsheet_id, sheet_name):
    try:
        result = (
            service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=[f"{sheet_name}!A:AQ"],
            )
            .execute()
        )
        return result.get('valueRanges', [{}])[0].get('values', [])
    except Exception as e:
        print(f"Error reading sheet data: {e}")
        return None

def process_scraped_results(supplier_results):
    lowest_price_found = float("inf")
    best_supplier_url = None
    chosen_supplier_name = "N/A"

    for result in supplier_results:
        if result["in_stock"] and result["price"] is not None:
            if result["price"] < lowest_price_found:
                lowest_price_found = result["price"]
                best_supplier_url = result["url"]
                chosen_supplier_name = result["name"]
            elif result["price"] == lowest_price_found:
                # Tie-breaking: keep the first one encountered (which is implicitly handled by iteration order)
                pass
    
    return lowest_price_found, best_supplier_url, chosen_supplier_name

def update_sheet(service, spreadsheet_id, requests):
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
        ).execute()
        return True
    except Exception as e:
        print(f"Error updating sheet: {e}")
        return False

def simulate_human_interaction(page):
    # Simulate human-like mouse movements before navigation
    for _ in range(random.randint(3, 7)):  # Perform 3 to 7 random mouse movements
        x = random.randint(0, page.viewport_size["width"])
        y = random.randint(0, page.viewport_size["height"])
        page.mouse.move(x, y, steps=random.randint(5, 15))  # Move with random steps
        time.sleep(random.uniform(0.1, 0.5))  # Short random delay between movements

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

def create_color_request(row_index, background_color, col_index=None, text_color=None):
    cell_format = {"backgroundColor": background_color}
    fields = "userEnteredFormat.backgroundColor"
    if text_color:
        cell_format["textFormat"] = {"foregroundColor": text_color}
        fields += ",userEnteredFormat.textFormat.foregroundColor"
    
    range_dict = {
        "sheetId": 0,
        "startRowIndex": row_index,
        "endRowIndex": row_index + 1,
    }
    if col_index is not None:
        range_dict["startColumnIndex"] = col_index
        range_dict["endColumnIndex"] = col_index + 1

    return {
        "repeatCell": {
            "range": range_dict,
            "cell": {"userEnteredFormat": cell_format},
            "fields": fields,
        }
    }


