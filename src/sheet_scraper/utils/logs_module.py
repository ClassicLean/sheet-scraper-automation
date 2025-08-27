"""
Logging utilities for the sheet scraper application.

This module contains functions for debug printing, log file management,
and update logging functionality.
"""

import os
from datetime import datetime
from pathlib import Path

from sheet_scraper.config.constants import DEBUG_MODE

# Use absolute paths to ensure logs are created in the correct location
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_FILE = str(PROJECT_ROOT / "logs" / "price_update_log.txt")


def debug_print(message: str) -> None:
    """Print debug message only if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        print(message)


def debug_print_column_x_update(row_index: int, old_price: float, new_price: float,
                               price_col: int, update_success: bool = None) -> None:
    """Enhanced debugging specifically for Column X price updates."""
    if DEBUG_MODE:
        print("[COLUMN X DEBUG]")
        print(f"   Row: {row_index + 1} (1-based) / {row_index} (0-based)")
        print(f"   Column X Index: {price_col} (0-based) = Column {chr(65 + price_col)}")
        print(f"   Old Price: {old_price}")
        print(f"   New Price: {new_price}")
        print(f"   Price Type: {type(new_price)}")
        print(f"   Update Success: {update_success if update_success is not None else 'Pending...'}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_sheet_operation(operation_type: str, details: dict) -> None:
    """Enhanced debugging for sheet operations."""
    if DEBUG_MODE:
        print("[SHEET OPERATION DEBUG]")
        print(f"   Operation: {operation_type}")
        for key, value in details.items():
            print(f"   {key}: {value}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_price_extraction(url: str, extracted_price: float, extraction_method: str = "unknown") -> None:
    """Enhanced debugging for price extraction."""
    if DEBUG_MODE:
        print("[PRICE EXTRACTION DEBUG]")
        print(f"   URL: {url[:100]}{'...' if len(url) > 100 else ''}")
        print(f"   Extracted Price: {extracted_price}")
        print(f"   Price Type: {type(extracted_price)}")
        print(f"   Extraction Method: {extraction_method}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_scraping_attempt(url: str, step: str, details: dict) -> None:
    """Enhanced debugging for individual scraping attempts."""
    if DEBUG_MODE:
        print("[SCRAPING ATTEMPT DEBUG]")
        print(f"   URL: {url[:80]}{'...' if len(url) > 80 else ''}")
        print(f"   Step: {step}")
        for key, value in details.items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"   {key}: {value}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_price_comparison(old_price: float, new_price: float, url: str, decision: str) -> None:
    """Enhanced debugging for price comparison and selection."""
    if DEBUG_MODE:
        print("[PRICE COMPARISON DEBUG]")
        print(f"   URL: {url[:80]}{'...' if len(url) > 80 else ''}")
        print(f"   Old Price: {old_price} ({type(old_price)})")
        print(f"   New Price: {new_price} ({type(new_price)})")
        print(f"   Decision: {decision}")
        print(f"   Price Changed: {old_price != new_price}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_scraping_failure(url: str, error_type: str, error_details: str) -> None:
    """Enhanced debugging for scraping failures."""
    if DEBUG_MODE:
        print("[SCRAPING FAILURE DEBUG]")
        print(f"   URL: {url[:80]}{'...' if len(url) > 80 else ''}")
        print(f"   Error Type: {error_type}")
        print(f"   Error Details: {error_details[:200]}{'...' if len(error_details) > 200 else ''}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_url_processing_start(url: str, supplier_index: int, total_suppliers: int) -> None:
    """Debug output when starting to process a specific URL."""
    if DEBUG_MODE:
        print(f"[URL PROCESSING START] ({supplier_index + 1}/{total_suppliers})")
        print(f"   Current URL: {url}")
        print(f"   Supplier Index: {supplier_index}")
        print(f"   Domain: {url.split('/')[2] if len(url.split('/')) > 2 else 'Unknown'}")
        print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_page_navigation(url: str, status: str, details: dict) -> None:
    """Debug output for page navigation attempts."""
    if DEBUG_MODE:
        print("[PAGE NAVIGATION DEBUG]")
        print(f"   URL: {url[:80]}{'...' if len(url) > 80 else ''}")
        print(f"   Navigation Status: {status}")
        for key, value in details.items():
            print(f"   {key}: {value}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_element_detection(url: str, selector: str, found: bool, element_text: str = "") -> None:
    """Debug output for HTML element detection attempts."""
    if DEBUG_MODE:
        print("[ELEMENT DETECTION DEBUG]")
        print(f"   URL: {url[:60]}{'...' if len(url) > 60 else ''}")
        print(f"   Selector: {selector}")
        print(f"   Element Found: {found}")
        if found and element_text:
            print(f"   Element Text: {element_text[:100]}{'...' if len(element_text) > 100 else ''}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def debug_print_supplier_summary(suppliers_processed: int, successful_extractions: int, failed_extractions: int) -> None:
    """Debug summary of all supplier processing results."""
    if DEBUG_MODE:
        print("[SUPPLIER PROCESSING SUMMARY]")
        print(f"   Total Suppliers: {suppliers_processed}")
        print(f"   Successful Extractions: {successful_extractions}")
        print(f"   Failed Extractions: {failed_extractions}")
        print(f"   Success Rate: {(successful_extractions/suppliers_processed*100) if suppliers_processed > 0 else 0:.1f}%")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ===============================")


def truncate_log_file(file_path: str, max_lines: int = 100) -> None:
    """
    Truncate log file to maximum number of lines.

    Args:
        file_path: Path to the log file
        max_lines: Maximum number of lines to keep (default: 100)
    """
    try:
        with open(file_path) as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            with open(file_path, "w") as f:
                f.writelines(lines[-max_lines:])
    except FileNotFoundError:
        print(f"Log file not found: {file_path}")
    except Exception as e:
        print(f"Error truncating log file {file_path}: {e}")


def log_update(
    product_id: str,
    old_price: float | None,
    new_price: float | None,
    status: str,
    message: str,
    row: int | None = None,
    log_file_path: str | None = None,
) -> None:
    """
    Enhanced logging with better error handling and formatting.

    Args:
        product_id: Product identifier
        old_price: Previous price (None if no previous price)
        new_price: New price (None if scraping failed)
        status: Update status (Success/Failed)
        message: Descriptive message
        row: Row number (optional)
        log_file_path: Custom log file path (optional, defaults to LOG_FILE)
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_info = f"Row: {row}, " if row is not None else ""

        # Truncate very long URLs for readability
        display_id = product_id
        if len(product_id) > 100:
            display_id = product_id[:50] + "..." + product_id[-47:]

        # Format prices with proper handling of None values
        old_price_str = str(old_price) if old_price is not None else "No Data"
        new_price_str = str(new_price) if new_price is not None else "No Data"

        log_entry = (
            f"[{timestamp}] {row_info}Product ID: {display_id}, "
            f"Old Price: {old_price_str}, New Price: {new_price_str}, "
            f"Status: {status}, Message: {message}\n"
        )

        # Use provided log file path or default
        actual_log_file = log_file_path or LOG_FILE

        # Ensure log directory exists
        os.makedirs(os.path.dirname(actual_log_file), exist_ok=True)

        with open(actual_log_file, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)

    except Exception as e:
        print(f"ERROR: Failed to write to log file: {e}")
        # Fallback: print to console
        print(f"LOG: {product_id} | {old_price} -> {new_price} | {status}: {message}")


def log_supplier_result(
    row: int,
    supplier_name: str,
    supplier_url: str,
    price: float | None,
    in_stock: bool,
    error: str | None = None,
    log_file_path: str | None = None,
) -> None:
    """
    Log individual supplier processing results.

    Args:
        row: Row number being processed
        supplier_name: Name of the supplier (Amazon, Vivo, etc.)
        supplier_url: The supplier URL
        price: Price found (or None)
        in_stock: Whether item is in stock
        error: Error message if any
        log_file_path: Custom log file path (optional)
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Truncate long URLs for readability
        display_url = supplier_url
        if len(supplier_url) > 80:
            display_url = supplier_url[:40] + "..." + supplier_url[-37:]

        # Determine status
        if error:
            status = "Error"
            # Clean error message of problematic characters while preserving readability
            message = str(error).replace('❌', 'X').replace('✓', 'OK').replace('\u274c', 'X')
        elif price is not None:
            status = "Price Found"
            stock_status = "In Stock" if in_stock else "Out of Stock"
            message = f"${price} ({stock_status})"
        else:
            status = "No Price"
            message = "Price not found"

        log_entry = (
            f"[{timestamp}] Row: {row}, Supplier: {supplier_name}, "
            f"URL: {display_url}, Status: {status}, Result: {message}\n"
        )

        # Use provided log file path or default
        actual_log_file = log_file_path or LOG_FILE

        # Ensure log directory exists
        os.makedirs(os.path.dirname(actual_log_file), exist_ok=True)

        try:
            with open(actual_log_file, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
        except UnicodeEncodeError as ue:
            # Fallback: Remove problematic Unicode characters and retry
            clean_entry = log_entry.encode('ascii', 'replace').decode('ascii')
            with open(actual_log_file, "a", encoding="utf-8") as log_file:
                log_file.write(clean_entry)
            print(f"WARNING: Unicode encoding issue resolved in log entry: {ue}")

    except Exception as e:
        print(f"ERROR: Failed to write supplier result to log file: {e}")
        # Fallback: print to console with clean characters
        clean_error = str(error).replace('❌', 'X').replace('✓', 'OK') if error else "None"
        print(f"SUPPLIER LOG: Row {row} | {supplier_name} | {price} | {in_stock} | {clean_error}")
