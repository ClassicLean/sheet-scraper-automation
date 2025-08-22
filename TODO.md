# Project TODOs and Future Goals

This file outlines future enhancements and ongoing tasks for the Sheet-Scraper project.

## High-Priority / Immediate Goals

*   **Address Anti-Bot Measures:** Continue to research and implement free anti-detection techniques for highly protected websites (e.g., Amazon, Walmart, Kohl's). Acknowledge that consistent scraping of these sites may eventually require exploring paid proxy or CAPTCHA-solving services.

## Future Enhancements (from Documentation)

*   **Re-implement Batch Updates for Google Sheets:** Improve efficiency and reduce API call count.
*   **Configurable Selectors:** Store selectors and availability indicators in a separate configuration file (e.g., JSON or YAML) to make them easier to manage and update.
*   **Parallel Scraping:** Implement asynchronous scraping to speed up the process for many URLs, while still respecting rate limits.
*   **Notification System:** Add notifications (e.g., email, Slack) for successful runs, failures, or significant price changes.
*   **Database for Products:** For very large sheets, consider moving product data to a local database for faster processing and more complex queries.
*   **Proxy Rotation:** (Currently a paid option, but listed for future consideration if free options fail) Integrate with proxy services to avoid IP bans.
*   **More Robust Availability Detection:** Implement more sophisticated logic for determining in-stock status, potentially using image recognition or machine learning.
