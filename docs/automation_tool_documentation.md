# Price Update Automation Tool

## 1. Project Overview

This tool automates the process of updating product prices in a Google Sheet by scraping the latest prices from various supplier websites. It identifies the lowest in-stock price among multiple suppliers for a given product and updates the Google Sheet accordingly, including the chosen supplier's URL, the new price, and a status note. The automation is designed to run on a schedule, ideally via GitHub Actions.

## 2. User Stories / Functional Requirements

As a user, I want to:

*   **Automatically update product prices:** The tool should visit external supplier websites, scrape product prices, and update the corresponding entries in a Google Sheet.
*   **Find the lowest in-stock price:** For each product, the tool should check multiple supplier URLs, identify if the product is in stock, and select the supplier offering the lowest price among available options.
*   **Handle price ties:** In case of a tie for the lowest price among multiple in-stock suppliers, the tool should select the first supplier encountered in the predefined column order.
*   **Update "Supplier in use" URL:** The Google Sheet's "Supplier in use" column should be updated with the URL of the supplier that provided the chosen lowest in-stock price.
*   **Update "Supplier Price For ONE Unit":** The Google Sheet's "Supplier Price For ONE Unit" column should be updated with the actual lowest price found.
*   **Track price changes:** The tool should update a "VA Notes" column to indicate if the new price is "Up", "Down", or "$$$" compared to the previous price.  - Update with "$$$" if the price is greater than or equal to $299.99
*   **Receive status feedback:** The tool should log all price updates, including product ID, old price, new price, status (Success/Failed), and a descriptive message for auditing and debugging.
*   **Be notified of issues:** If a product is not found, is out of stock across all suppliers, or if there are scraping errors, the tool should reflect this in the "VA Notes" column and logs.  - If a product is not found because we are blocked or because of captcha issues, we put "Blocked" in the "VA Notes" column  - If a product is out of stock across all suppliers, we fill the entire row with the color red
*   **Start checking from a specific row:** The tool should begin processing data from row 5 onwards in the Google Sheet.
*   **Record last check date:** After processing each product, the tool should update the "Last stock check" column (Column D) with the current date.

## 3. Technical Architecture & Design

### Technologies Used:

*   **Python:** Core scripting language.
*   **Playwright (Python Library):** For headless browser automation to scrape dynamic website content (prices and availability).
*   **Google Sheets API (Python Client Library):** For reading data from and writing data to the Google Sheet.
*   **Google Cloud Service Account:** For secure and automated authentication with the Google Sheets API.
*   **GitHub Actions:** For scheduling and running the automation workflow in a serverless environment.

### High-Level Flow:

1.  **Initialization:** The script connects to the Google Sheets API using service account credentials.
2.  **Read Sheet Data:** It reads all relevant rows and columns (Product ID, Supplier URLs, Old Price) from the designated Google Sheet, starting from row 5.
3.  **Iterate Products:** For each product (row) in the sheet:
    *   **Scrape Supplier Data:** It iterates through each defined supplier URL column. For each valid URL, it launches a headless browser (Playwright), navigates to the URL, and attempts to scrape the product's price and determine its availability (in-stock status). A delay is introduced between requests to avoid rate limiting.
    *   **Process Scraped Data:** It collects all scraped prices and availability statuses for the current product from all suppliers.
    *   **Determine Best Supplier:** It filters out out-of-stock products and identifies the supplier offering the lowest price among the remaining in-stock options. Ties are broken by selecting the first encountered supplier in the column order.
    *   **Prepare Updates:** Based on the best supplier found (or lack thereof), it determines the new "Supplier in use" URL, the new "Supplier Price For ONE Unit", and the "VA Notes" status ("Up", "Down", "No change", "Price not found / Out of stock").
    *   **Record Last Check Date:** The current date is recorded for the "Last stock check" column.
4.  **Update Google Sheet:** All prepared updates for the current product's row are sent to the Google Sheet via individual API calls for each cell (VA Notes, Price, Supplier URL, Last Stock Check Date).
5.  **Logging:** All significant actions and outcomes (successes, failures, errors) are logged to a local file (`price_update_log.txt`).

## 4. Configuration

### Google Sheet Details:

*   **Google Sheet File Name:** "Sheet Scraping"
*   **Sheet Tab Name:** "FBMP" (This is the actual tab name used in the script's range definitions).
*   **Spreadsheet ID:** This is the long alphanumeric string found in your Google Sheet's URL (e.g., `https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID_HERE/edit`). This ID should be configured as an environment variable (`SPREADSHEET_ID`) or hardcoded in `connect.py` and `sheet_scraper.py`.

### Column Mappings (0-indexed):

These mappings are crucial for the script to correctly read from and write to your Google Sheet.

*   `VA_NOTES_COL = 0` (Column A): "VA Notes" - Used for status updates ("Up", "Down", etc.).
*   `LAST_STOCK_CHECK_COL = 3` (Column D): "Last stock check" - Updated with the current date after each product check.
*   `PRICE_COL = 23` (Column X): "Supplier Price For ONE Unit" - Where the final chosen price is written.
*   `PRODUCT_ID_COL = 31` (Column AF): "Supplier in use" - This column serves as the primary product identifier for each row and will also be updated with the chosen supplier's URL.

*   **`SUPPLIER_URL_COLS` Dictionary:** This dictionary maps column indices to their descriptive names for logging and processing. The script will iterate through these columns to find supplier URLs.
    ```python
    SUPPLIER_URL_COLS = {
        31: "Supplier in use", # AF - Note: This column is both a source and a target for updates
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
    ```

### Service Account Authentication:

1.  **Create a Google Cloud Service Account:**
    *   Go to the Google Cloud Console: `https://console.cloud.google.com/`
    *   Navigate to IAM & Admin -> Service Accounts.
    *   Create a new service account.
    *   Grant it the "Google Sheets API Editor" role (or a more restrictive role if preferred, but Editor ensures write access).
    *   Create a new JSON key for the service account and download it.
2.  **Secure the JSON Key:** Rename the downloaded JSON file to `sheet-scraper-as.json` and place it in the project's `config/` directory. **Ensure this file is NOT committed to public repositories.** For GitHub Actions, you will store its content as a GitHub Secret.
3.  **Share Google Sheet:** Share your "Sheet Scraping" Google Sheet with the email address of the newly created service account (found in the JSON key file, typically `your-service-account-name@your-project-id.iam.gserviceaccount.com`).

### Web Scraping Selectors:

The `scrape_product_details` function in `sheet_scraper.py` contains generic CSS selectors and keyword lists for price and availability detection. **These are critical and MUST be customized for each specific website you intend to scrape.**

*   **Price Selectors (`price_selectors` list):**
    *   Inspect the HTML of product pages to find the unique CSS selectors for the price element.
    *   Example: `".product-price-value"`, `#current-price`, `span[data-automation-id="price"]`.
*   **In-Stock Indicators (`in_stock_indicators` list):**
    *   Keywords or phrases that indicate a product is available.
    *   Example: `"in stock"`, `"add to cart"`, `"available for immediate dispatch"`.
*   **Out-of-Stock Indicators (`out_of_stock_indicators` list):**
    *   Keywords or phrases that indicate a product is unavailable.
    *   Example: `"out of stock"`, `"unavailable"`, `"currently unavailable"`, `"backorder"`.

## 5. Usage & Execution

### Local Execution:

1.  **Prerequisites:**
    *   Python 3.x installed.
    *   `pip` (Python package installer).
    *   Google Cloud Service Account JSON key (`sheet-scraper-as.json`) in the project root.
    *   Google Sheet shared with the service account.
2.  **Install Dependencies:**
    ```bash
    pip install playwright google-api-python-client google-auth-oauthlib google-auth-httplib2
    playwright install
    ```
3.  **Run the Script:**
    ```bash
    python src/sheet_scraper.py
    ```
    Observe console output and check `logs/price_update_log.txt` for results.

### Running Tests:

To ensure the correctness of the code, unit tests have been implemented using `pytest`.

1.  **Install Testing Dependencies:**
    ```bash
    pip install pytest ruff
    ```
2.  **Execute Tests:**
    From the project root directory, run:
    ```bash
    pytest
    ```
    `pytest` will automatically discover and run tests in files named `test_*.py` or `*_test.py`.

3.  **Run Linter (Ruff):**
    To check for code style and common errors, you can run the `ruff` linter:
    ```bash
    ruff check .
    ```

### Scheduled Execution with GitHub Actions:

1.  **Create `.github/workflows/scrape.yml`:**
    Create a directory `.github/workflows/` in your repository root and add a file named `scrape.yml` with content similar to this:
    ```yaml
    name: Scheduled Price Scraper

    on:
      schedule:
        # Runs every day at 0:00 UTC
        - cron: '0 0 * * *'
      workflow_dispatch: # Allows manual triggering from GitHub UI

    jobs:
      scrape-prices:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout code
            uses: actions/checkout@v4

          - name: Set up Python
            uses: actions/setup-python@v5
            with:
              python-version: '3.x' # Use your desired Python version

          - name: Install Python dependencies
            run: |
              pip install playwright google-api-python-client google-auth-oauthlib google-auth-httplib2
            timeout-minutes: 5

          - name: Install Playwright browsers
            run: |
              playwright install chromium
            timeout-minutes: 10

          - name: Create Service Account Key File
            env:
              SA_KEY_JSON: ${{ secrets.SA_KEY_JSON }}
            run: |
              echo "$SA_KEY_JSON" > sheet-scraper-as.json

          - name: Run Price Scraper
            env:
              SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
            run: |
              python -c "print('Python interpreter is working!')"
              python -v sheet_scraper.py > script_output.log 2>&1 & # Run in background
              sleep 30 # Give time for output
              cat script_output.log # Print output to console
              # The timeout for the step itself will handle the overall execution time
    ```
2.  **Configure GitHub Secrets:**
    *   In your GitHub repository, go to `Settings` -> `Secrets and variables` -> `Actions`.
    *   Add two new repository secrets:
        *   `SPREADSHEET_ID`: The ID of your Google Sheet.
        *   `SA_KEY_JSON`: The *entire content* of your `sheet-scraper-as.json` file. Copy and paste the JSON content directly into this secret.

## 6. Logging

All price update attempts, including successes, failures, and errors, are logged to `logs/price_update_log.txt` in the project's root directory. This file provides an audit trail and helps in debugging. The script also includes `print` statements for real-time progress tracking in the GitHub Actions logs.

## 7. Limitations & Gotchas

*   **Website Changes:** Websites frequently update their HTML structure, which can break existing CSS selectors and availability indicators. Regular maintenance and updates to `sheet_scraper.py` will be required.
*   **Anti-Bot Measures:** Some websites employ sophisticated anti-bot detection, CAPTCHAs, or require logins. This script does not handle these scenarios. For such sites, more advanced techniques (e.g., proxies, CAPTCHA solving services, or paid scraping APIs) would be necessary.
*   **Rate Limiting:** Scraping too many pages too quickly can lead to IP bans or temporary blocks. The `time.sleep()` delays are a basic measure; more advanced rate limiting strategies might be needed for large-scale operations.
*   **Dynamic Content Loading:** While Playwright handles JavaScript-rendered content, very complex or lazy-loaded content might require more advanced waiting strategies (e.g., `page.wait_for_selector`, `page.wait_for_load_state`).
*   **Error Handling:** The current error handling is basic. More granular error handling and retry mechanisms could be implemented for robustness.
*   **Google Sheets API Quotas:** Be mindful of Google Sheets API daily quotas. For very large numbers of updates, batching (which we temporarily removed for debugging) is crucial to stay within limits.

## 8. Future Enhancements

*   **Re-implement Batch Updates for Google Sheets:** Once the core scraping and individual updates are stable, re-implementing batch updates for Google Sheets API calls will significantly improve efficiency and reduce API call count.
*   **Configurable Selectors:** Store selectors and availability indicators in a separate configuration file (e.g., JSON or YAML) to make them easier to manage and update without modifying code.
*   **Parallel Scraping:** Implement asynchronous scraping (e.g., using `asyncio` with Playwright's async API) to speed up the process for many URLs, while still respecting rate limits.
*   **Notification System:** Add notifications (e.g., email, Slack) for successful runs, failures, or significant price changes.
*   **Database for Products:** For very large sheets, consider moving product data to a local database for faster processing and more complex queries.
*   **Proxy Rotation:** Integrate with proxy services to avoid IP bans.
*   **More Robust Availability Detection:** Implement more sophisticated logic for determining in-stock status, potentially using image recognition or machine learning for complex cases.