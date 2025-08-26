"""
Data models for the automation system.

This module contains all data classes and type definitions used
throughout the automation process, following Python best practices
for data structure organization.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ProductData:
    """Data class for product information."""
    product_id: str
    old_price: float
    row_index: int
    row: List[str]
    supplier_urls: List[str]


@dataclass
class SupplierResult:
    """Data class for supplier scraping results."""
    url: str
    price: Optional[float]
    in_stock: bool
    shipping_fee: Optional[float]
    error: Optional[str]
    supplier_name: str


@dataclass
class PriceUpdateResult:
    """Data class for price update results."""
    new_price: float
    new_va_note: str
    best_supplier_url: Optional[str]
    chosen_shipping_fee: Optional[float]
    chosen_supplier_name: str
    all_blocked: bool
