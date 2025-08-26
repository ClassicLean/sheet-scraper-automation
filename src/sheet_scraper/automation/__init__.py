"""
Automation package for Sheet Scraper.

This package contains modular components for the automation system,
split from the original monolithic automation_core.py file to follow
Python best practices for code organization and maintainability.

The package is organized into logical modules:
- data_models: Data classes and type definitions
- stats: Statistics tracking and metrics
- processors: Product processing and supplier handling
- formatters: Sheet formatting and styling
- sheet_managers: Google Sheets operations
- orchestrators: High-level automation coordination
- scrapers: Individual product scraping operations
"""

# Import key classes for easy access
from .data_models import ProductData, SupplierResult, PriceUpdateResult
from .stats import AutomationStats
from .processors import ProductProcessor
from .formatters import SheetFormatter
from .sheet_managers import SheetManager
from .orchestrators import SheetScraperAutomation, AutomationOrchestrator
from .scrapers import ProductScraper

__all__ = [
    # Data models
    'ProductData',
    'SupplierResult',
    'PriceUpdateResult',

    # Core components
    'AutomationStats',
    'ProductProcessor',
    'SheetFormatter',
    'SheetManager',

    # Orchestrators
    'SheetScraperAutomation',
    'AutomationOrchestrator',

    # Scrapers
    'ProductScraper',
]
