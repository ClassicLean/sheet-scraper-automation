"""
Legacy scraping utilities module.

This module provides backward compatibility by re-exporting functions
from the new modular utils package structure.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import directly from the utils submodules:
- sheet_scraper.utils.logs_module
- sheet_scraper.utils.pricing
- sheet_scraper.utils.web_scraping
- sheet_scraper.utils.sheets
- sheet_scraper.utils.data_processing
"""

# Import all functions from the new modular structure
from sheet_scraper.utils.data_processing import (
    process_scraped_results,
)
from sheet_scraper.utils.logs_module import (
    LOG_FILE,
    debug_print,
    debug_print_element_detection,
    debug_print_page_navigation,
    debug_print_price_comparison,
    debug_print_price_extraction,
    debug_print_scraping_attempt,
    debug_print_scraping_failure,
    debug_print_supplier_summary,
    debug_print_url_processing_start,
    log_supplier_result,
    log_update,
    truncate_log_file,
)
from sheet_scraper.utils.pricing import (
    extract_price,
    parse_price,
)
from sheet_scraper.utils.sheets import (
    create_color_request,
    read_sheet_data,
    update_sheet,
)
from sheet_scraper.utils.web_scraping import (
    extract_shipping_fee,
    is_blocked,
    is_in_stock,
    simulate_human_interaction,
)

# Maintain __all__ for explicit exports
__all__ = [
    # Logging utilities
    "debug_print",
    "truncate_log_file",
    "log_update",
    "log_supplier_result",
    "LOG_FILE",
    "debug_print_price_extraction",
    "debug_print_scraping_attempt",
    "debug_print_price_comparison",
    "debug_print_scraping_failure",
    "debug_print_url_processing_start",
    "debug_print_page_navigation",
    "debug_print_element_detection",
    "debug_print_supplier_summary",

    # Pricing utilities
    "parse_price",
    "extract_price",

    # Web scraping utilities
    "is_blocked",
    "extract_shipping_fee",
    "is_in_stock",
    "simulate_human_interaction",

    # Google Sheets utilities
    "read_sheet_data",
    "update_sheet",
    "create_color_request",

    # Data processing utilities
    "process_scraped_results",
]
