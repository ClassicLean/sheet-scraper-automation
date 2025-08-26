"""
Sheet Scraper - Enhanced Automation Framework

A clean, modular automation framework for updating Google Sheets with product pricing data.
This package provides comprehensive tools for web scraping, price monitoring, and automated
spreadsheet updates with built-in anti-detection capabilities.

Main Components:
- AutomationOrchestrator: High-level automation coordination
- SheetScraperApplication: Main application facade
- Config: Configuration management
- Enhanced browser and proxy management
- Comprehensive logging and monitoring

Example:
    from sheet_scraper import SheetScraperApplication

    app = SheetScraperApplication()
    app.setup()
    app.run()
"""

from .sheet_scraper import SheetScraperApplication, run_price_update_automation
from .config.config_manager import Config
from .automation.orchestrators import AutomationOrchestrator
from .automation.data_models import ProductData, SupplierResult
from .logs_module.automation_logging import get_logger, setup_logging_directories

__version__ = "2.0.0"
__author__ = "Sheet Scraper Team"
__email__ = "contact@sheetscraper.com"

# Main exports for public API
__all__ = [
    "SheetScraperApplication",
    "run_price_update_automation",
    "Config",
    "AutomationOrchestrator",
    "ProductData",
    "SupplierResult",
    "get_logger",
    "setup_logging_directories",
]
