"""
Utilities package for the Sheet Scraper project.

This package contains utility modules organized by functionality following
Python best practices for module organization. The original scraping_utils.py
file has been refactored into focused, single-responsibility modules.

Modules:
- logging: Debug output, log management, and update logging utilities
- pricing: Price parsing, extraction, and conversion utilities
- web_scraping: Web page interaction, content extraction, and blocking detection
- sheets: Google Sheets API operations and formatting utilities
- data_processing: Data transformation and result processing utilities

For backward compatibility, the main classes and functions are re-exported
at the package level.
"""

# Logging utilities
from .logs_module import (
    debug_print,
    debug_print_column_x_update,
    debug_print_sheet_operation,
    debug_print_price_extraction,
    truncate_log_file,
    log_update,
)

# Pricing utilities
from .pricing import (
    parse_price,
    extract_price,
)

# Web scraping utilities
from .web_scraping import (
    is_blocked,
    extract_shipping_fee,
    is_in_stock,
    simulate_human_interaction,
)

# Google Sheets utilities
from .sheets import (
    read_sheet_data,
    update_sheet,
    create_color_request,
)

# Data processing utilities
from .data_processing import (
    process_scraped_results,
)

# Re-export all utilities for backward compatibility
__all__ = [
    # Logging utilities
    'debug_print',
    'debug_print_column_x_update',
    'debug_print_sheet_operation',
    'debug_print_price_extraction',
    'truncate_log_file',
    'log_update',

    # Pricing utilities
    'parse_price',
    'extract_price',

    # Web scraping utilities
    'is_blocked',
    'extract_shipping_fee',
    'is_in_stock',
    'simulate_human_interaction',

    # Google Sheets utilities
    'read_sheet_data',
    'update_sheet',
    'create_color_request',

    # Data processing utilities
    'process_scraped_results',
]
