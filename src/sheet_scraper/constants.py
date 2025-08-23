# Configuration Constants
SHEET_NAME = "FBMP"
ROW_LIMIT = 5  # Limit the number of rows processed for testing

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

# RGB values for specified colors (approximate, Google Sheets API uses 0.0-1.0)
COLOR_LIGHT_GREEN_3 = {"red": 0.76, "green": 0.87, "blue": 0.69}
COLOR_LIGHT_MAGENTA_2 = {"red": 0.835, "green": 0.651, "blue": 0.741}
COLOR_LIGHT_YELLOW_2 = {"red": 1.000, "green": 0.898, "blue": 0.600}
COLOR_LIGHT_RED_1 = {"red": 0.878, "green": 0.400, "blue": 0.400}
COLOR_BLUE = {"red": 0.0, "green": 0.0, "blue": 1.0}
COLOR_DARK_GREEN_2 = {"red": 0.20, "green": 0.60, "blue": 0.20}
COLOR_GREEN = {"red": 0.0, "green": 1.0, "blue": 0.0}
COLOR_BLACK = {"red": 0.0, "green": 0.0, "blue": 0.0}
COLOR_WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
COLOR_RED = {"red": 1.0, "green": 0.0, "blue": 0.0}
COLOR_DARK_RED_2 = {"red": 0.600, "green": 0.000, "blue": 0.000}

# Column indices for coloring (0-indexed)
COL_X = 23
COL_Y = 24
COL_Z = 25
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
    "unavailable",
    "currently unavailable",
    "backorder",
    "sold out",
    "no longer available",
]
