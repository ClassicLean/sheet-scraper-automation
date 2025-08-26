"""
Product Processing Module

This module handles all product-related data processing including price extraction,
validation, formatting, and business logic. It encapsulates the core business rules
for processing product information from scraped data.

Best Practices Implemented:
- Single Responsibility: Only product processing logic
- Pure Functions: Stateless data transformations where possible
- Input Validation: Comprehensive validation of product data
- Error Handling: Graceful handling of malformed data
- Type Safety: Clear type hints for all functions
"""

import re
import time
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field

from ..scraping_utils import debug_print


@dataclass
class ProductData:
    """Data class representing a product with all its attributes."""
    name: str = ""
    price: Optional[Decimal] = None
    original_price_text: str = ""
    url: str = ""
    row_index: int = -1
    column_index: int = -1
    availability: str = "Unknown"
    last_updated: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate product data after initialization."""
        if self.last_updated is None:
            self.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class ProcessingStats:
    """Statistics for product processing operations."""
    total_processed: int = 0
    successful_updates: int = 0
    failed_updates: int = 0
    skipped_items: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_processed == 0:
            return 0.0
        return (self.successful_updates / self.total_processed) * 100


class PriceExtractor:
    """Handles extraction and validation of price information from text."""

    # Enhanced price patterns for various formats
    PRICE_PATTERNS = [
        # Standard currency formats
        r'(?:USD?[\s$]*)(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        r'(?:\$\s*)(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',

        # European formats
        r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*€',
        r'€\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',

        # Generic number patterns
        r'(\d{1,3}(?:,\d{3})*\.\d{2})',
        r'(\d+\.\d{2})',
        r'(\d+,\d{2})',
        r'(\d+)',
    ]

    @staticmethod
    def extract_price(price_text: str) -> Optional[Decimal]:
        """
        Extract price from text using multiple patterns.

        Args:
            price_text: Raw price text to parse

        Returns:
            Decimal price value or None if extraction fails
        """
        if not price_text or not isinstance(price_text, str):
            debug_print("DEBUG: Empty or invalid price text")
            return None

        # Clean the text
        cleaned_text = price_text.strip().replace('\n', ' ').replace('\t', ' ')
        debug_print(f"DEBUG: Extracting price from: '{cleaned_text}'")

        for pattern in PriceExtractor.PRICE_PATTERNS:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                price_str = match.group(1)

                try:
                    # Handle European format (comma as decimal separator)
                    if ',' in price_str and '.' in price_str:
                        # Assume European format: 1.234,56
                        if price_str.rfind(',') > price_str.rfind('.'):
                            price_str = price_str.replace('.', '').replace(',', '.')
                    elif ',' in price_str and price_str.count(',') == 1:
                        # Check if comma is decimal separator
                        comma_pos = price_str.find(',')
                        if len(price_str) - comma_pos - 1 <= 2:  # Likely decimal separator
                            price_str = price_str.replace(',', '.')

                    # Remove thousands separators (commas)
                    price_str = price_str.replace(',', '')

                    price = Decimal(price_str)
                    debug_print(f"DEBUG: Extracted price: {price}")
                    return price

                except (InvalidOperation, ValueError) as e:
                    debug_print(f"DEBUG: Failed to parse price '{price_str}': {e}")
                    continue

        debug_print(f"DEBUG: No valid price found in '{cleaned_text}'")
        return None

    @staticmethod
    def validate_price(price: Union[Decimal, float, str]) -> Optional[Decimal]:
        """
        Validate and convert price to Decimal.

        Args:
            price: Price value to validate

        Returns:
            Validated Decimal price or None if invalid
        """
        if price is None:
            return None

        try:
            if isinstance(price, str):
                return PriceExtractor.extract_price(price)

            decimal_price = Decimal(str(price))

            # Basic validation
            if decimal_price < 0:
                debug_print(f"DEBUG: Negative price rejected: {decimal_price}")
                return None

            if decimal_price > Decimal('999999.99'):
                debug_print(f"DEBUG: Unreasonably high price rejected: {decimal_price}")
                return None

            return decimal_price

        except (InvalidOperation, ValueError, TypeError) as e:
            debug_print(f"DEBUG: Price validation failed: {e}")
            return None


class ProductDataProcessor:
    """Main class for processing product data and business logic."""

    def __init__(self):
        """Initialize the product processor."""
        self.stats = ProcessingStats()
        self.price_extractor = PriceExtractor()

    def process_product_row(self, row_data: List[str], row_index: int,
                          url_column: int = 1, price_column: int = 2) -> ProductData:
        """
        Process a single product row from sheet data.

        Args:
            row_data: List of cell values for the row
            row_index: Index of the row in the sheet
            url_column: Column index containing the URL
            price_column: Column index containing the price

        Returns:
            ProductData object with processed information
        """
        product = ProductData(row_index=row_index)

        try:
            # Extract basic information
            if len(row_data) > 0:
                product.name = str(row_data[0]).strip()

            if len(row_data) > url_column:
                product.url = str(row_data[url_column]).strip()

            if len(row_data) > price_column:
                product.original_price_text = str(row_data[price_column]).strip()
                product.price = self.price_extractor.extract_price(product.original_price_text)

            # Set column index for price updates
            product.column_index = price_column

            debug_print(f"DEBUG: Processed product '{product.name}' at row {row_index}")
            self.stats.total_processed += 1

        except Exception as e:
            error_msg = f"Error processing row {row_index}: {e}"
            product.error_message = error_msg
            self.stats.errors.append(error_msg)
            debug_print(f"DEBUG: {error_msg}")

        return product

    def batch_process_products(self, sheet_data: List[List[str]],
                             start_row: int = 1, end_row: Optional[int] = None,
                             url_column: int = 1, price_column: int = 2) -> List[ProductData]:
        """
        Process multiple product rows in batch.

        Args:
            sheet_data: Complete sheet data
            start_row: Starting row index (1-based)
            end_row: Ending row index (1-based), None for all rows
            url_column: Column index containing URLs
            price_column: Column index containing prices

        Returns:
            List of processed ProductData objects
        """
        debug_print(f"DEBUG: Batch processing products from row {start_row} to {end_row or 'end'}")

        products = []

        if end_row is None:
            end_row = len(sheet_data)

        # Adjust for 0-based indexing
        start_idx = max(0, start_row - 1)
        end_idx = min(len(sheet_data), end_row)

        for i in range(start_idx, end_idx):
            if i < len(sheet_data):
                product = self.process_product_row(
                    sheet_data[i], i + 1, url_column, price_column
                )
                products.append(product)

        debug_print(f"DEBUG: Batch processed {len(products)} products")
        return products

    def filter_valid_products(self, products: List[ProductData]) -> List[ProductData]:
        """
        Filter products to only include those with valid URLs.

        Args:
            products: List of products to filter

        Returns:
            List of products with valid URLs
        """
        valid_products = []

        for product in products:
            if self.is_valid_product_url(product.url):
                valid_products.append(product)
            else:
                self.stats.skipped_items += 1
                debug_print(f"DEBUG: Skipped invalid product URL: '{product.url}'")

        debug_print(f"DEBUG: Filtered to {len(valid_products)} valid products")
        return valid_products

    def is_valid_product_url(self, url: str) -> bool:
        """
        Validate if a URL is suitable for scraping.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid for scraping
        """
        if not url or not isinstance(url, str):
            return False

        url = url.strip()

        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            return False

        # Check for minimum length
        if len(url) < 10:
            return False

        # Avoid obvious non-product URLs
        invalid_patterns = [
            r'\.pdf$',
            r'\.jpg$',
            r'\.png$',
            r'\.gif$',
            r'/search\?',
            r'/category/',
            r'/brand/',
            r'#',
        ]

        for pattern in invalid_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False

        return True

    def update_processing_stats(self, success: bool, error_message: str = None):
        """
        Update processing statistics.

        Args:
            success: Whether the operation was successful
            error_message: Error message if operation failed
        """
        if success:
            self.stats.successful_updates += 1
        else:
            self.stats.failed_updates += 1
            if error_message:
                self.stats.errors.append(error_message)

    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of processing statistics.

        Returns:
            Dictionary containing processing statistics
        """
        return {
            'total_processed': self.stats.total_processed,
            'successful_updates': self.stats.successful_updates,
            'failed_updates': self.stats.failed_updates,
            'skipped_items': self.stats.skipped_items,
            'success_rate': self.stats.success_rate,
            'error_count': len(self.stats.errors),
            'recent_errors': self.stats.errors[-5:] if self.stats.errors else []
        }

    def reset_stats(self):
        """Reset processing statistics."""
        self.stats = ProcessingStats()


# Utility functions for price operations
def format_price_for_display(price: Optional[Decimal], currency: str = "$") -> str:
    """
    Format price for display in sheets.

    Args:
        price: Price value to format
        currency: Currency symbol

    Returns:
        Formatted price string
    """
    if price is None:
        return "N/A"

    try:
        return f"{currency}{price:.2f}"
    except (ValueError, TypeError):
        return "N/A"


def compare_prices(old_price: Optional[Decimal], new_price: Optional[Decimal]) -> Dict[str, Any]:
    """
    Compare two prices and return analysis.

    Args:
        old_price: Previous price
        new_price: Current price

    Returns:
        Dictionary with price comparison results
    """
    result = {
        'changed': False,
        'increase': False,
        'decrease': False,
        'percentage_change': 0.0,
        'absolute_change': Decimal('0.00')
    }

    if old_price is None or new_price is None:
        return result

    try:
        old_price = Decimal(str(old_price))
        new_price = Decimal(str(new_price))

        if old_price != new_price:
            result['changed'] = True
            result['absolute_change'] = new_price - old_price

            if new_price > old_price:
                result['increase'] = True
            else:
                result['decrease'] = True

            if old_price != 0:
                result['percentage_change'] = float((new_price - old_price) / old_price * 100)

    except (InvalidOperation, ValueError, TypeError) as e:
        debug_print(f"DEBUG: Price comparison failed: {e}")

    return result
