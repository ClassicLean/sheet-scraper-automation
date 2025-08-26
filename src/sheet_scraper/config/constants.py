# Configuration Constants
import os

SHEET_NAME = "FBMP"
ROW_LIMIT = 5  # Limit the number of rows processed for testing

# Debug Configuration
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'  # Set to True to enable debug output
HEADFUL_BROWSER = os.getenv('HEADFUL_BROWSER', 'False').lower() == 'true'  # Set to True to show browser window during scraping

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
    33: "Supplier A",  # AH
    34: "Supplier B",  # AI
    35: "Supplier C",  # AJ
    36: "Supplier D",  # AK
    37: "Supplier E",  # AL
    38: "Supplier F",  # AM
    39: "Supplier G",  # AN
    40: "Supplier H",  # AO
    41: "Supplier I",  # AP
    42: "Supplier J",  # AQ
}

# RGB values for specified colors (approximate, Google Sheets API uses 0.0-1.0)
COLOR_DARK_RED_2 = {"red": 153 / 255, "green": 0 / 255, "blue": 0 / 255}
COLOR_LIGHT_GREEN_3 = {"red": 217 / 255, "green": 234 / 255, "blue": 211 / 255}
COLOR_LIGHT_MAGENTA_2 = {"red": 213 / 255, "green": 166 / 255, "blue": 189 / 255}
COLOR_LIGHT_YELLOW_2 = {"red": 255 / 255, "green": 229 / 255, "blue": 153 / 255}
COLOR_LIGHT_RED_1 = {"red": 224 / 255, "green": 102 / 255, "blue": 102 / 255}
COLOR_BLUE = {"red": 0.0, "green": 0.0, "blue": 1.0}
COLOR_DARK_GREEN_2 = {"red": 56 / 255, "green": 118 / 255, "blue": 29 / 255}
COLOR_GREEN = {"red": 0.0, "green": 1.0, "blue": 0.0}
COLOR_BLACK = {"red": 0.0, "green": 0.0, "blue": 0.0}
COLOR_WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
COLOR_RED = {"red": 1.0, "green": 0.0, "blue": 0.0}
COLOR_LIGHT_CYAN_3 = {"red": 208 / 255, "green": 224 / 255, "blue": 227 / 255}
COLOR_DARK_CORNFLOWER_BLUE_2 = {"red": 17 / 255, "green": 85 / 255, "blue": 204 / 255}
COLOR_DARK_PURPLE_2 = {"red": 53 / 255, "green": 28 / 255, "blue": 117 / 255}  # #351c75 for Noah text
COLOR_NOAH_FILL = {"red": 183 / 255, "green": 225 / 255, "blue": 205 / 255}  # #b7e1cd
COLOR_GRAY = {"red": 204 / 255, "green": 204 / 255, "blue": 204 / 255}  # #cccccc Gray for columns F-K

# Column Mappings (0-indexed)
VA_NOTES_COL = 0  # A: "VA Notes"
LAST_STOCK_CHECK_COL = 3  # D: "Last stock check" - NEW
COL_E = 4  # E: "RNW"
COL_F = 5  # F: Column F
COL_G = 6  # G: Column G
COL_H = 7  # H: Column H
COL_I = 8  # I: Column I
COL_J = 9  # J: Column J
COL_K = 10  # K: Column K
COL_L = 11  # L: Column L
COL_N = 13  # N: "List Made by" (start of range)
COL_O = 14  # O: "List Made by" (end of range)
COL_P = 15  # P: "Product Name"
COL_Q = 16  # Q: "Main Category"
COL_R = 17  # R: "Sub Category"
COL_S = 18  # S: "OUR SKU"
COL_V = 21  # V: "Supplier"
COL_W = 22  # W: "Their SKU"
PRICE_COL = 23  # X: "Supplier Price For ONE Unit"
PRODUCT_ID_COL = 31  # AF: "Supplier in use" (also acts as product ID for the row)

# Column indices for coloring (0-indexed)
COL_X = 23
COL_Y = 24
COL_Z = 25  # Shipping column
COL_AA = 26
COL_AB = 27
COL_AC = 28
COL_AD = 29
COL_AE = 30
COL_AG = 32


# In-stock and Out-of-stock Indicators
IN_STOCK_INDICATORS = [
    "in stock",
    "add to cart",
    "add to bag",
    "available",
    "buy now",
    "add to basket",
]

OUT_OF_STOCK_INDICATORS = [
    "out of stock",
    "currently unavailable",
    "backorder",
    "sold out",
    "no longer available",
    "temporarily out of stock",
    "this item is currently unavailable",
]

# New: Selector-based stock indicators
STOCK_INDICATOR_SELECTORS = {
    "in_stock": [
        "div#availability span.a-size-medium.a-color-success",  # Amazon "In stock." text
        "button#add-to-cart-button",  # Amazon Add to Cart button
        "input#add-to-cart-button",  # Amazon Add to Cart button (input type)
        "div#availability span.a-text-bold",  # Amazon "In Stock." text
        ".add-to-cart",  # General add to cart button
        ".in-stock-label",  # General in-stock label
        ".in-stock-indicator",  # General in-stock indicator
        "[aria-label='Add to Cart']",  # Common ARIA label for add to cart
    ],
    "out_of_stock": [
        "div#availability span.a-color-price",  # Amazon "Currently unavailable."
        "div#availability span.a-color-error",  # Amazon "Out of stock."
        ".out-of-stock-label",  # General out-of-stock label
        ".unavailable-label",  # General unavailable label
        ".sold-out-label",  # General sold-out label
        ".out-of-stock",  # General out-of-stock class
        ".unavailable",  # General unavailable class
        "button[disabled].add-to-cart",  # Disabled add to cart button
    ],
}
