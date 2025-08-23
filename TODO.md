# Project TODOs and Future Goals

This file outlines future enhancements and ongoing tasks for the Sheet-Scraper project.

## High-Priority / Immediate Goals

*   **Improve Item Availability Detection:** Investigate and implement more robust methods for accurately detecting whether an item is in stock, especially on dynamic and anti-bot protected websites (e.g., Amazon, Vivo). Research community solutions, advanced Playwright techniques, or alternative detection strategies.
*   **Address Anti-Bot Measures (Local Headful Browsing Focus):** Continue to research and implement anti-detection techniques, primarily leveraging local headful browser execution. Acknowledge that consistent scraping of highly protected websites (e.g., Amazon, Walmart, Kohl's) may eventually require exploring paid proxy or CAPTCHA-solving services.

## Future Enhancements (from Documentation)

*   **Re-implement Batch Updates for Google Sheets:** Improve efficiency and reduce API call count.
*   **Configurable Selectors:** Store selectors and availability indicators in a separate configuration file (e.g., JSON or YAML) to make them easier to manage and update.
*   **Parallel Scraping:** Implement asynchronous scraping (e.g., using `asyncio` with Playwright's async API) to speed up the process for many URLs, while still respecting rate limits.
*   **Notification System:** Add notifications (e.g., email, Slack) for successful runs, failures, or significant price changes.
*   **Database for Products:** For very large sheets, consider moving product data to a local database for faster processing and more complex queries.
*   **More Robust Availability Detection:** Implement more sophisticated logic for determining in-stock status, potentially using image recognition or machine learning.
*   **Advanced Browser Fingerprinting:** Further enhance browser fingerprinting techniques to make the scraper even more stealthy.
*   **Dynamic User-Agent Management:** Implement a more sophisticated user-agent rotation strategy, potentially fetching fresh user-agent lists periodically.
*   **Honeypot Detection:** Implement logic to detect and avoid honeypot traps.
*   **`robots.txt` Parser:** Add a function to parse and respect `robots.txt` rules.

## Completed Tasks

*   **Implemented Proxy Support:** Integrated proxy rotation to bypass IP-based geolocation and anti-bot measures.
*   **Implemented CAPTCHA Solving Support:** Integrated 2Captcha service for automatic CAPTCHA resolution.
*   **Refactored `sheet_scraper.py` for modularity:** Broke down large functions into smaller, more manageable ones.
*   **Restructured project to follow best practices:** Implemented a `src` layout and updated file organization.
*   **Switch to Local Execution:** Shifted from GitHub Actions to local execution to improve anti-bot evasion.
*   **Implement Headful Browsing:** Configured Playwright to run in headful mode.
*   **Integrate `undetected-playwright`:** Replaced `playwright-stealth`.
*   **Add Human-like Interaction:** Implemented basic mouse movements and scrolling.
*   **Remove `tkinter` Notification:** Removed the pop-up to prevent test hangs.
*   **Secure Credentials:** Removed `sheet-scraper-as.json` from Git history.
*   **Add `requests` Dependency:** Added `requests` to `requirements.txt`.
*   **Fixed Linting and Import Errors:** Addressed linting issues in `sheet_scraper.py` by organizing imports, removing unused ones, and correcting import paths for `undetected-playwright` and `twocaptcha`.
