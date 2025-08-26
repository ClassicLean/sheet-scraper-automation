# Price Update Automation Tool

## 1. Project Overview

This tool automates the process of updating product prices in a Google Sheet by scraping the latest prices from various supplier websites. It identifies the lowest in-stock price among multiple suppliers for a given product and updates the Google Sheet accordingly, including the chosen supplier's URL, the new price, and a status note. The automation is designed to run locally on your machine and features enhanced reliability with API quota management, configurable processing parameters, and comprehensive error handling.

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
*   **Start checking from a specific row:** The tool should begin processing data from row 5 onwards in the Google Sheet, with configurable start and end row parameters via environment variables.
*   **Record last check date:** After processing each product, the tool should update the "Last stock check" column (Column D) with the current date.
*   **Handle API quota limits:** The tool should gracefully handle Google Sheets API quota exhaustion with exponential backoff retry logic and rate limiting.

## 3. Technical Architecture & Design

### Technologies Used:

*   **Python:** Core scripting language.
*   **`requests` (Python Library):** For making HTTP requests.
*   **Undetected Playwright (Python Library) (via ninja.py for stealth_sync):** For browser automation to scrape dynamic website content (prices and availability).
*   **`twocaptcha` (Python Library):** For CAPTCHA solving.
*   **Google Sheets API (Python Client Library):** For reading data from and writing data to the Google Sheet with enhanced quota management and retry logic.
*   **Google Cloud Service Account:** For secure and automated authentication with the Google Sheets API.

### Key Enhancements (August 2025):

*   **API Resilience:** Exponential backoff retry logic with randomized jitter for handling HTTP 429 quota errors
*   **Configurable Processing:** Environment variable-based row processing with PROCESS_START_ROW and PROCESS_END_ROW parameters
*   **Enhanced Error Handling:** Comprehensive API error detection and graceful recovery mechanisms
*   **Configuration Validation:** Automatic validation and creation of missing configuration files and directories
*   **Improved Selectors:** Enhanced Vivo price extraction with product area targeting for more accurate price detection
*   **Comprehensive Testing:** 141-test suite with configurable row processing support and 100% pass rate

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
    ├── conftest.py                    # Shared test fixtures and imports
    ├── test_configuration.py          # Config manager and constants validation
    ├── test_core_functionality.py     # Row ranges and main automation logic
    ├── test_features.py               # Shipping, Noah highlighting, blocking, debug
    ├── test_formatting.py             # Column formatting logic and color rules
    ├── test_infrastructure.py         # Browser handling, logging, project structure
    ├── test_project_structure.py      # File cleanup and project integrity validation
    ├── test_web_scraping.py           # Scraping utilities and price parsing
    ├── test_web_ui.py                 # Web UI integration and validation
    └── test_sheet_scraper_BACKUP.py   # Original monolithic test file (backup)
```

### Test Architecture (August 2025 Enhancement):

The project features a **modern, modular test architecture** designed for maintainability and team collaboration:

**Architecture Benefits:**
- **Modular Organization:** 8 focused test files (200-300 lines each) replacing single 1,355-line monolith
- **Clear Separation:** Tests grouped by functionality (configuration, features, infrastructure, etc.)
- **Shared Infrastructure:** Centralized imports and fixtures in `conftest.py` reducing duplication
- **Team Collaboration:** Parallel development with reduced merge conflicts through focused file structure
- **Performance:** Faster IDE loading, selective testing, and improved test discovery

**Test Coverage:**
- **73 comprehensive tests** covering all functionality areas
- **Configuration validation** with constants and config manager testing
- **Core functionality** including row range processing and automation logic
- **Feature testing** for shipping, Noah highlighting, blocking detection, and debug functionality
- **Infrastructure validation** for browser handling, logging, and project structure
- **Web UI integration** with Flask route validation and static file verification
- **Formatting verification** for column logic and color rules
- **Scraping utilities** with comprehensive price parsing and extraction testing

**Modern pytest Patterns:**
- Logical test grouping with clear naming conventions
- Shared fixtures for common test scenarios
- Comprehensive parameterized testing for edge cases
- Integration testing for cross-component functionality
```

### High-Level Flow:

1.  **Initialization:** The script connects to the Google Sheets API using service account credentials with enhanced authentication and configuration validation.
2.  **Read Sheet Data:** It reads all relevant rows and columns (Product ID, Supplier URLs, Old Price) from the designated Google Sheet, starting from row 5 (configurable via PROCESS_START_ROW environment variable).
3.  **Iterate Products:** For each product (row) in the sheet:
    *   **Scrape Supplier Data:** It iterates through each defined supplier URL column. For each valid URL, it launches a browser (Playwright), navigates to the URL, and attempts to scrape the product's price and determine its availability (in-stock status). A delay is introduced between requests to avoid rate limiting.
    *   **Process Scraped Data:** It collects all scraped prices and availability statuses for the current product from all suppliers.
    *   **Determine Best Supplier:** It filters out out-of-stock products and identifies the supplier offering the lowest price among the remaining in-stock options. Ties are broken by selecting the first encountered supplier in the column order.
    *   **Prepare Updates:** Based on the best supplier found (or lack thereof), it determines the new "Supplier in use" URL, the new "Supplier Price For ONE Unit", and the "VA Notes" status ("Up", "Down", "No change", "Price not found / Out of stock").
    *   **Record Last Check Date:** The current date is recorded for the "Last stock check" column.
4.  **Update Google Sheet:** All prepared updates for the current product's row are sent to the Google Sheet via individual API calls for each cell with enhanced error handling, exponential backoff retry logic, and automatic quota management.
5.  **Logging:** All significant actions and outcomes (successes, failures, errors) are logged to a local file (`price_update_log.txt`) with detailed API error tracking.

### Anti-Blocking Strategies:

To mitigate detection by websites, the scraper employs several anti-blocking techniques, primarily leveraging local headful browser execution:

*   **Local Headful Browsing:** Running Playwright in headful mode (visible browser window) significantly enhances stealth, as it's much harder for websites to distinguish from genuine human interaction.
*   **Undetected Playwright:** Integrates `undetected-playwright` to modify browser fingerprints and behaviors, making the scraper less detectable by anti-bot systems. This library aims to mimic human browser behavior more closely.
*   **User-Agent Rotation:** The script rotates through a list of common browser User-Agents for each request, making it harder for websites to identify automated traffic based on a consistent User-Agent.
*   **Randomized Delays:** Delays between requests are randomized within a specified range to mimic human browsing patterns and avoid rate-limiting.
*   **Human-like Interaction Simulation:** Implements random mouse movements before navigation and varied scrolling after page load to mimic human browsing patterns.
*   **Realistic Viewport:** Sets a common desktop resolution for the browser viewport to appear more like a typical user, with added randomization.
*   **Dynamic Page Load Waiting:** Randomly waits for different page load states (`domcontentloaded`, `load`, `networkidle`) to further mimic varied human browsing patterns.
*   **Enhanced Selector Targeting:** Implements site-specific improvements like Vivo's product area targeting for more accurate price extraction.

**Limitations:** While these strategies enhance the scraper's stealth, they may not be sufficient to bypass highly sophisticated anti-bot systems employed by major e-commerce sites. Consistent and reliable scraping of such sites may eventually require more advanced techniques (e.g., proxies, CAPTCHA solving services) which typically involve external paid services.
*   **Availability Detection Challenges:** Despite ongoing efforts to refine price and stock detection (e.g., adding specific CSS selectors for sites like Amazon and Vivo), reliably identifying item availability remains a significant challenge on highly dynamic and anti-bot protected websites. Further research into more robust detection methods is required. Recent improvements include enhanced Vivo price selectors with .product__price targeting achieving consistent $119.99 extraction.

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

### Conditional Styling Rules

The tool applies specific styling to various columns in the Google Sheet based on the product's stock status and price. These rules are applied when an item is **in stock** and its **price is less than $299.99**. Unless otherwise specified, the text color for these cells will be black.

*   **Column X (Supplier Price For ONE Unit):**
    *   Text color: "dark red 2"
    *   Fill color: "light green 3"
*   **Column Y (QTY of Set):**
    *   Fill color: "light magenta 2"
*   **Column Z (Shipping):**
    *   Fill color: "light yellow 2"
*   **Column AA (Total Supplier Price):**
    *   Text color: "white"
    *   Fill color: "light red 1"
*   **Column AB (AVG Selling Price):**
    *   Text color: "white"
    *   Fill color: "blue"
*   **Column AC (AVG Profit):**
    *   Text color: "white"
    *   Fill color: "dark green 2"
*   **Column AD (AVG %):**
    *   Text color: "white"
    *   Fill color: "dark green 2"
*   **Column AE (On Target %):**
    *   If the text is "Under", the fill color should be "green". (Note: This requires reading cell content, which is not directly implemented in the current coloring logic.)
*   **Column D (Last stock check):**
    *   Text color: "black"
*   **Column E (RNW):**
    *   Text color: "black"
    *   If the text is "RNW", the fill color should be "red".
    *   If the text is not "RNW", the fill color should be "light cyan 3". (Note: This requires reading cell content, which is not directly implemented in the current coloring logic.)
*   **Column N (List Made by):**
    *   Text color: "black"
    *   If the text is "RNW", the fill color should be "#b7e1cd". (Note: This requires reading cell content, which is not directly implemented in the current coloring logic.)
*   **Column P (Product Name):**
    *   Text color: "black"
*   **Column R (Sub Category):**
    *   Text color: "black"
*   **Column S (OUR SKU):**
    *   Text color: "black"
*   **Column V (Supplier):**
    *   Text color: "black"
*   **Column W (Their SKU):**
    *   Text color: "black"
*   **Column AF (Supplier in use):**
    *   Text color: "dark cornflower blue 2"
*   **Column AG:**
    *   Fill color: "black"
*   **Columns AH to AN (Supplier A to Supplier G):**
    *   Text color: "dark cornflower blue 2"


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

## 9. Recent Major Improvements (August 2025)

### ✅ **Web UI Complete Implementation & Cache-Busting (Latest Update)**

#### **Flask Web Interface Enhancement**

**Animated Loading Spinner**: Completely replaced static progress bar with modern CSS animation spinner for enhanced user experience.

**Comprehensive Cache-Busting Strategy:**
- **HTTP Headers**: Cache-Control, Pragma, Expires for browser cache prevention
- **Before-Request Clearing**: `app.jinja_env.cache.clear()` for immediate template updates
- **Template Auto-Reload**: `TEMPLATES_AUTO_RELOAD = True` and `SEND_FILE_MAX_AGE_DEFAULT = 0`
- **Meta Tag Timestamps**: Dynamic cache invalidation with timestamp-based versioning

**Browser Management Fix**: Resolved duplicate browser tab issue in start_ui.py by implementing WERKZEUG_RUN_MAIN environment variable check for Flask reloader subprocess detection.

#### **Wayfair Integration Restoration**

**Site Detection Enhancement**: Restored accurate Wayfair price extraction through comprehensive site detection improvements.

**Resolution Process:**
- **Issue Identified**: Wayfair prices incorrectly showing $5.00 instead of expected $68.75
- **Root Cause**: Missing "wayfair.com" → "wayfair" site detection mapping in config_manager.py
- **Solution Implemented**: Enhanced config_manager.py site detection and added Wayfair-specific selectors
- **Selectors Added**: `[data-test-id='PriceDisplay']`, `StandardPricingPrice-PRIMARY`, `.standardPricing-module_price`
- **Validation**: Confirmed accurate $68.75 price extraction with enhanced selectors

#### **Project Structure Optimization**

**Comprehensive Codebase Cleanup**: Removed 8 temporary/debug files while maintaining 100% functionality.

**Files Previously Cleaned (Historical Reference):**
- **Root Directory**: check_template.py, final_test.py, test_simple.py, verify_ui.py (removed in comprehensive cleanup)
- **Web UI Directory**: debug_template.py, direct_test.py (removed in comprehensive cleanup)
- **Dependencies**: Consolidated Flask requirement from web_ui/requirements.txt to pyproject.toml

**Current Status**: Project structure optimized with all redundant files removed, maintaining clean codebase with 141 passing tests.
- **TestWebUIIntegration**: Flask imports, routes, cache-busting validation, template verification
- **TestProjectStructure**: Dependency consolidation, .gitignore patterns, cleanup confirmation

### ✅ **Critical Architecture Fixes Completed**

This section documents the major architectural improvements that resolved core functionality issues and significantly enhanced the reliability of the system.

#### **9.1 Function Signature Bug Resolution**

**Issue:** Critical bugs in `extract_price()` and `is_in_stock()` functions were causing AttributeError crashes when called with `config=None` parameter.

**Root Cause:** Functions expected a config object but weren't properly handling the None case, leading to crashes before CSS selectors could even execute.

**Resolution:**
- Fixed function signatures to gracefully handle `config=None` with fallback to global config instance
- Added proper error handling and parameter validation
- Implemented consistent config initialization patterns across all utility functions

**Impact:** This was the primary cause of "price not found" failures. CSS selectors were working perfectly but functions crashed before execution.

#### **9.2 CSS Selector Validation and Enhancement**

**Previous Assumption:** CSS selectors were broken and needed research.

**Reality Discovered:** CSS selectors were working flawlessly (finding 22-25 Amazon price elements with correct $130.99 extraction).

**Investigation Results:**
- Debug tools confirmed Amazon selectors successfully extract prices like $129.99, $130.99
- Site-specific selectors work correctly for stock detection
- Generic fallback selectors provide robust coverage

**Current Status:** All CSS selectors validated and working correctly with enhanced error handling.

#### **9.3 Blocking Detection Refinement**

**Issue:** False positive blocking detection was incorrectly flagging legitimate Amazon content.

**Root Cause:** Generic blocking indicators (like the word "blocked") appeared in normal Amazon product descriptions.

**Resolution:**
- Refined blocking indicators in `selectors.json` to be more specific and context-aware
- Removed overly generic terms that caused false positives
- Maintained security while eliminating incorrect blocking detection

**Testing:** Debug tools confirm proper blocking detection without false positives.

#### **9.4 Processing Logic Enhancement**

**Issue:** Despite successful price extraction, all log entries showed "Status: Failed" with generic error messages.

**Root Cause:** Logic was checking for outdated return values (`float("inf")`) instead of the current `None` returns, and didn't distinguish between different failure types.

**Resolution:**
- Updated logic to properly handle `None` returns from processing functions
- Enhanced error categorization to distinguish between:
  - "Price not found" (no price data available)
  - "Out of stock" (price found but item unavailable)
  - "Sheet update error" (API/network failures)
- Improved logging messages for better user understanding

**Impact:** Users now receive accurate, actionable feedback about update failures.

### ✅ **Enhanced Testing Infrastructure**

#### **9.5 Comprehensive Test Suite**

**Achievement:** Expanded from broken tests to 32 passing tests covering all major functionality.

**Test Coverage:**
- Price parsing with 17 test cases covering various formats ($10.00, 1,000.00, Free, etc.)
- Price extraction testing with mock page objects and CSS selectors
- Stock detection testing for both in-stock and out-of-stock scenarios
- Configuration system testing for site detection and selector retrieval
- Browser resilience testing for context closure scenarios
- Log functionality testing including automatic clearing

**Quality Improvements:**
- Removed legacy try/catch blocks for old function signatures
- Standardized on current implementation patterns
- Added proper error scenario testing

#### **9.6 Development Tools and Debugging**

**New Development Infrastructure:**
- `dev_tools/debug_blocking.py` - Test blocking detection on specific URLs
- `dev_tools/selector_research.py` - Research and test CSS selectors
- `dev_tools/test_fixes.py` - Quick validation of configuration fixes
- `dev_tools/README.md` - Documentation for development tools

**Enhanced Logging:**
- Automatic price update log clearing on script startup
- Detailed debug output for selector attempts and results
- Clear error categorization and troubleshooting information

### ✅ **Code Quality and Maintenance**

#### **9.7 Codebase Organization**

**Cleanup Activities:**
- Removed unused imports (`stealth_sync` from `undetected_playwright.ninja`)
- Eliminated cache directories (`__pycache__`, `.pytest_cache`, `.ruff_cache`)
- Organized development tools into dedicated directory structure
- Enhanced `.gitignore` to properly exclude temporary and generated files

**Import Resolution:**
- Added missing `os` import in `scraping_utils.py` to resolve logging errors
- Cleaned up dependency management and removed unused libraries
- Standardized import patterns across modules

#### **9.8 Configuration System Enhancement**

**Dynamic CSS Selector Management:**
- Enhanced `Config` class for site-specific selector management
- Centralized selector configuration in `selectors.json`
- Support for fallback selector chains (site-specific → generic)
- Runtime selector validation and error handling

**Site Detection:**
- Robust URL pattern matching for Amazon, Walmart, Kohls, Vivo
- Automatic fallback to generic selectors for unknown sites
- Configurable blocking indicators per site

### **9.9 Current System Reliability**

**Working Components (✅):**
- Amazon integration: Successfully extracting prices and stock status
- Price parsing: Robust handling of currency symbols, commas, various formats
- Stock detection: Accurate in-stock/out-of-stock detection via CSS selectors
- Google Sheets connection: Reliable API connection and updates
- Error handling: Graceful handling of browser context closures and timeouts
- Test suite: 141 tests with 100% pass rate
- Logging system: Clear, informative logs with proper error categorization

**Limitations (⚠️):**
- Multi-site support: Amazon works perfectly, other major retailers (Walmart, Kohls, Vivo) consistently blocked
- Advanced anti-bot measures: Current stealth techniques insufficient for some major e-commerce sites

**Next Development Priorities:**
- Enhanced anti-bot strategies for blocked retailers
- Premium proxy service integration
- Advanced CAPTCHA detection and solving
- Site-specific behavior simulation patterns

## 10. Current Development Status and Testing Notes

## 10. Legacy Development Notes

**Historical Context:** Previous versions of this system experienced critical architectural issues that have now been resolved through comprehensive debugging and refactoring in August 2025.

**Previous Issues (Now Resolved):**
- Function signature bugs causing crashes
- CSS selector execution problems
- Blocking detection false positives
- Processing logic inconsistencies
- Test suite failures

**Current Status:** All major functionality is working reliably with comprehensive test coverage and enhanced error handling.

## 11. Security Best Practices

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
