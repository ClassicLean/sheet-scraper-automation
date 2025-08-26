"""
Core automation classes for the Sheet Scraper project.

DEPRECATION NOTICE: This module has been refactored into a modular package
structure following Python best practices. The original 1,081-line file
violated code organization principles and has been split into logical modules.

New structure:
- automation.data_models: Data classes and type definitions
- automation.stats: Statistics tracking and metrics
- automation.processors: Product processing and supplier handling
- automation.formatters: Sheet formatting and styling
- automation.sheet_managers: Google Sheets operations
- automation.orchestrators: High-level automation coordination
- automation.scrapers: Individual product scraping operations

For backward compatibility, this module re-exports the main classes.
New code should import directly from the automation package modules.
"""

"""
Core automation module with backward compatibility.

This module provides access to automation classes while maintaining
backward compatibility with the previous module structure.
"""

def get_automation_classes():
    """Lazy import of automation classes to avoid circular imports."""
    from ..automation import (
        # Data models
        ProductData,
        SupplierResult,
        PriceUpdateResult,

        # Core components
        AutomationStats,
        ProductProcessor,
        SheetFormatter,
        SheetManager,

        # Orchestrators
        SheetScraperAutomation,
        AutomationOrchestrator,

        # Scrapers
        ProductScraper,
    )

    return {
        'ProductData': ProductData,
        'SupplierResult': SupplierResult,
        'PriceUpdateResult': PriceUpdateResult,
        'AutomationStats': AutomationStats,
        'ProductProcessor': ProductProcessor,
        'SheetFormatter': SheetFormatter,
        'SheetManager': SheetManager,
        'SheetScraperAutomation': SheetScraperAutomation,
        'AutomationOrchestrator': AutomationOrchestrator,
        'ProductScraper': ProductScraper,
    }

# For backward compatibility, expose classes when requested
def __getattr__(name):
    classes = get_automation_classes()
    if name in classes:
        return classes[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
