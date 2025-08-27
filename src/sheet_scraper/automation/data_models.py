"""
Data models for the automation system.

This module contains all data classes and type definitions used
throughout the automation process, following Python best practices
for data structure organization.
"""

from dataclasses import dataclass


@dataclass
class ProductData:
    """Data class for product information."""
    product_id: str
    old_price: float
    row_index: int
    row: list[str]
    supplier_urls: list[str]


@dataclass
class SupplierResult:
    """Data class for supplier scraping results."""
    url: str
    price: float | None
    in_stock: bool
    shipping_fee: float | None
    error: str | None
    supplier_name: str


@dataclass
class PriceUpdateResult:
    """Data class for price update results."""
    new_price: float | None
    new_va_note: str
    best_supplier_url: str | None
    chosen_shipping_fee: float | None
    chosen_supplier_name: str
    all_blocked: bool
    best_supplier_in_stock: bool = False  # Track if best supplier is actually in stock
