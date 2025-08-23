# Price Update Automation Tool

## 1. Project Overview

This tool automates the process of updating product prices in a Google Sheet by scraping the latest prices from various supplier websites. It identifies the lowest in-stock price among multiple suppliers for a given product and updates the Google Sheet accordingly, including the chosen supplier's URL, the new price, and a status note. The automation is designed to run locally on your machine.

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
*   **`requests` (Python Library):** For making HTTP requests.
*   **Undetected Playwright (Python Library) (via ninja.py for stealth_sync):** For browser automation to scrape dynamic website content (prices and availability).
*   **`twocaptcha` (Python Library):** For CAPTCHA solving.
*   **Google Sheets API (Python Client Library):** For reading data from and writing data to the Google Sheet.
*   **Google Cloud Service Account:** For secure and automated authentication with the Google Sheets API.

### File Structure

```
Sheet-Scraper/
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── proxies.txt
├── TODO.md
├── CHANGELOG.md
├── docs/
│   └── automation_tool_documentation.md
├── src/
│   └── sheet_scraper/
│       ├── __init__.py
│       ├── connect.py
│       ├── sheet_scraper.py
│       ├── proxy_manager.py
│       ├── captcha_solver.py
│       └── scraping_utils.py
└── tests/
    ├── __init__.py
    └── test_sheet_scraper.py
```

### High-Level Flow:

1.  **Initialization:** The script connects to the Google Sheets API using service account credentials.
2.  **Read Sheet Data:** It reads all relevant rows and columns (Product ID, Supplier URLs, Old Price) from the designated Google Sheet, starting from row 5.
3.  **Iterate Products:** For each product (row) in the sheet:
    *   **Scrape Supplier Data:** It iterates through each defined supplier URL column. For each valid URL, it launches a browser (Playwright), navigates to the URL, and attempts to scrape the product's price and determine its availability (in-stock status). A delay is introduced between requests to avoid rate limiting.
    *   **Process Scraped Data:** It collects all scraped prices and availability statuses for the current product from all suppliers.
    *   **Determine Best Supplier:** It filters out out-of-stock products and identifies the supplier offering the lowest price among the remaining in-stock options. Ties are broken by selecting the first encountered supplier in the column order.
    *   **Prepare Updates:** Based on the best supplier found (or lack thereof), it determines the new "Supplier in use" URL, the new "Supplier Price For ONE Unit", and the "VA Notes" status ("Up", "Down", "No change", "Price not found / Out of stock").
    *   **Record Last Check Date:** The current date is recorded for the "Last stock check" column.
4.  **Update Google Sheet:** All prepared updates for the current product's row are sent to the Google Sheet via individual API calls for each cell (VA Notes, Price, Supplier URL, Last Stock Check Date).
5.  **Logging:** All significant actions and outcomes (successes, failures, errors) are logged to a local file (`price_update_log.txt`).

### Anti-Blocking Strategies:

To mitigate detection by websites, the scraper employs several anti-blocking techniques, primarily leveraging local headful browser execution:

*   **Local Headful Browsing:** Running Playwright in headful mode (visible browser window) significantly enhances stealth, as it's much harder for websites to distinguish from genuine human interaction.
*   **Undetected Playwright:** Integrates `undetected-playwright` to modify browser fingerprints and behaviors, making the scraper less detectable by anti-bot systems. This library aims to mimic human browser behavior more closely.
*   **User-Agent Rotation:** The script rotates through a list of common browser User-Agents for each request, making it harder for websites to identify automated traffic based on a consistent User-Agent.
*   **Randomized Delays:** Delays between requests are randomized within a specified range to mimic human browsing patterns and avoid rate-limiting.
*   **Human-like Interaction Simulation:** Implements random mouse movements before navigation and varied scrolling after page load to mimic human browsing patterns.
*   **Realistic Viewport:** Sets a common desktop resolution for the browser viewport to appear more like a typical user, with added randomization.
*   **Dynamic Page Load Waiting:** Randomly waits for different page load states (`domcontentloaded`, `load`, `networkidle`) to further mimic varied human browsing patterns.

**Limitations:** While these strategies enhance the scraper's stealth, they may not be sufficient to bypass highly sophisticated anti-bot systems employed by major e-commerce sites. Consistent and reliable scraping of such sites may eventually require more advanced techniques (e.g., proxies, CAPTCHA solving services) which typically involve external paid services.
*   **Availability Detection Challenges:** Despite ongoing efforts to refine price and stock detection (e.g., adding specific CSS selectors for sites like Amazon and Vivo), reliably identifying item availability remains a significant challenge on highly dynamic and anti-bot protected websites. Further research into more robust detection methods is required.

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
2.  **Secure the JSON Key:** Rename the downloaded JSON file to `sheet-scraper-as.json` and place it in the project's `config/` directory. **Crucially, ensure this file is NOT committed to public repositories. It has been added to `.gitignore` to prevent accidental commits, but if it was previously committed, you must remove it from Git history.**
3.  **Share Google Sheet:** Share your "Sheet Scraping" Google Sheet with the email address of the newly created service account (found in the JSON key file, typically `your-service-account-name@your-project-id.iam.gserviceaccount.com`).

### Web Scraping Selectors:

The `scrape_product_details` function in `sheet_scraper.py` contains generic CSS selectors and keyword lists for price and availability detection. **These are critical and MUST be customized for each specific website you intend to scrape.**

*   **Price Selectors (`price_selectors` list):**
    *   Inspect the HTML of product pages to find the unique CSS selectors for the price element.
    *   Example: `".product-price-value"`, `#current-price`, `span[data-automation-id="price"]`.
*   **In-Stock Indicators (`in_stock_indicators` list):**
    *   Keywords or phrases that indicate a product is available.
    *   Example: `"in stock"`, `"add to cart"`, `"available for immediate dispatch"`.
*   **Out-of-Stock Indicators (`out_of_stock_indicators` list):}
    *   Keywords or phrases that indicate a product is unavailable.
    *   Example: `"out of stock"`, `"unavailable"`, `"currently unavailable"`, `"backorder"`.

## 5. Usage & Execution

### Local Execution:

1.  **Prerequisites:**
    *   Python 3.x installed.
    *   `pip` (Python package installer).
    *   Google Cloud Service Account JSON key (`sheet-scraper-as.json`) in the project's `config/` directory.
    *   Google Sheet shared with the service account.
    *   `proxies.txt` file (optional) in the project root directory, with one proxy per line in `ip:port` format.
    *   `TWOCAPTCHA_API_KEY` environment variable set if CAPTCHA solving is required.
    *   `twocaptcha` library installed.
2.  **Install Dependencies:**
    ```bash
    pip install -e .
    # This will install all required packages from pyproject.toml
    pip install twocaptcha
    playwright install
    ```
    The `playwright install` command will download the necessary browser binaries (Chromium, Firefox, WebKit) for Playwright to function.
3.  **Run the Script:**
    ```bash
    python src/sheet_scraper/sheet_scraper.py
    ```
    Observe the browser window that opens, console output, and check `logs/price_update_log.txt` for results.

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

3.  **Run Linter (Ruff):}
    To check for code style and common errors, you can run the `ruff` linter:
    ```bash
    ruff check .
    ```

## 6. Logging

All price update attempts, including successes, failures, and errors, are logged to `logs/price_update_log.txt` in the project's root directory. This file provides an audit trail and helps in debugging. The script also includes `print` statements for real-time progress tracking.

## 7. Limitations & Gotchas

*   **Website Changes:** Websites frequently update their HTML structure, which can break existing CSS selectors and availability indicators. Regular maintenance and updates to `sheet_scraper.py` will be required.
*   **Anti-Bot Measures:** While local headful browsing significantly improves stealth, some websites employ very sophisticated anti-bot detection or require logins. Specifically, IP-based geolocation is a common detection method. For such sites, more advanced techniques (e.g., proxies, CAPTCHA solving services, or paid scraping APIs) might still be necessary. Implementing proxy support is a high-priority goal.
*   **Rate Limiting:** Scraping too many pages too quickly can still lead to IP bans or temporary blocks, even with local execution. The `time.sleep()` delays and human-like interaction simulations are designed to mitigate this, but careful monitoring is advised.
*   **Dynamic Content Loading:** While Playwright handles JavaScript-rendered content, very complex or lazy-loaded content might require more advanced waiting strategies (e.g., `page.wait_for_selector`, `page.wait_for_load_state`).
*   **Error Handling:** The current error handling is basic. More granular error handling and retry mechanisms could be implemented for robustness.
*   **Google Sheets API Quotas:** Be mindful of Google Sheets API daily quotas. For very large numbers of updates, batching is crucial to stay within limits.
*   **No Desktop Notification:** The desktop notification pop-up (using `tkinter`) has been removed as it caused test suite hangs in certain environments.

## 8. Future Enhancements

*   **Re-implement Batch Updates for Google Sheets:** Once the core scraping and individual updates are stable, re-implementing batch updates for Google Sheets API calls will significantly improve efficiency and reduce API call count.
*   **Configurable Selectors:** Store selectors and availability indicators in a separate configuration file (e.g., JSON or YAML) to make them easier to manage and update without modifying code.
*   **Parallel Scraping:** Implement asynchronous scraping (e.g., using `asyncio` with Playwright's async API) to speed up the process for many URLs, while still respecting rate limits.
*   **Notification System:** Add notifications (e.g., email, Slack) for successful runs, failures, or significant price changes.
*   **Database for Products:** For very large sheets, consider moving product data to a local database for faster processing and more complex queries.
*   **More Robust Availability Detection:** Implement more sophisticated logic for determining in-stock status, potentially using image recognition or machine learning for complex cases.
*   **Advanced Browser Fingerprinting:** Further enhance browser fingerprinting techniques to make the scraper even more stealthy.
*   **Dynamic User-Agent Management:** Implement a more sophisticated user-agent rotation strategy, potentially fetching fresh user-agent lists periodically.
*   **Honeypot Detection:** Implement logic to detect and avoid honeypot traps.
*   **`robots.txt` Parser:** Add a function to parse and respect `robots.txt` rules.

## 9. Current Development Status and Testing Notes

The test suite is currently passing, ensuring the stability and correctness of the implemented features.

## 10. Security Best Practices

When working with this project, especially if you intend to share your code on platforms like GitHub, it is crucial to adhere to security best practices to protect sensitive information.

### What to Keep Private (Never Commit to Git):

*   **API Keys and Secrets:** This includes your Google Cloud Service Account JSON key (`config/sheet-scraper-as.json`), any other third-party API keys, authentication tokens, or secret access keys.
*   **Credentials:** Usernames, passwords, and database connection strings.
*   **Private Keys:** SSH keys, GPG keys, SSL certificates.
*   **Personal Identifiable Information (PII):** Any data that could identify individuals if it's part of your code, test data, or configuration.
*   **Sensitive Configuration Files:** Any configuration files that directly contain the above sensitive data.

### How to Keep Sensitive Data Private:

*   **`.gitignore`:** Use a `.gitignore` file in your project's root directory to tell Git to ignore specific files and directories. This prevents them from being accidentally committed. For this project, `config/sheet-scraper-as.json` and the `logs/` directory are already included in `.gitignore`.
*   **Environment Variables:** Store sensitive values as environment variables on your system where the code runs. Access them in your code using `os.environ.get()`. This project already uses this for `SPREADSHEET_ID`.
*   **Example/Template Files:** For configuration files, you can commit a template file (e.g., `config/sheet-scraper-as.json.example`) with placeholder values, so others know what parameters are needed without exposing your actual secrets.

### Removing Already Committed Sensitive Data:

If sensitive files were accidentally committed to your Git history, simply adding them to `.gitignore` will not remove them from past commits. To truly remove them, you must rewrite your Git history.

*   **Tool:** The recommended tool for this is `git filter-repo`.
*   **Process:** This involves running `git filter-repo` to remove the file from all commits, followed by a **force push** (`git push --force --all`) to your remote repository. This is a destructive operation that alters your repository's history.
*   **Collaborator Impact:** If you have collaborators, they **MUST** delete their local clones and re-clone the repository after a force push.
*   **Invalidate Credentials:** **Crucially, immediately invalidate and regenerate any API keys or credentials that were exposed**, as they might have been compromised.
