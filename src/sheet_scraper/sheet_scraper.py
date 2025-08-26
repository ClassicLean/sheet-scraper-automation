"""
Enhanced Sheet Scraper - Main Entry Point

A clean, modular automation framework for updating Google Sheets with product pricing data.
This module serves as the main orchestrator, coordinating all automation components while
maintaining a clean separation of concerns.

Architecture:
- Main orchestration logic (this file)
- Core automation classes (automation_core.py)
- Utility modules (sheet_operations.py, product_processing.py, automation_logging.py)
- Configuration and browser management
"""

import argparse
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from .config.config_manager import Config
from .config.constants import DEBUG_MODE, HEADFUL_BROWSER
from .core.automation_core import AutomationOrchestrator
from .infrastructure.browser_manager import EnhancedBrowserManager
from .infrastructure.captcha_solver import CaptchaSolver
from .infrastructure.proxy_manager import ProxyManager
from .logs_module.automation_logging import get_logger, setup_logging_directories


class SheetScraperApplication:
    """
    Main application facade that coordinates all automation components.

    This class follows the Facade pattern to provide a simplified interface
    to the complex automation subsystem, making it easy to use and maintain.
    """

    def __init__(self):
        """Initialize the application with default configuration."""
        self.logger = get_logger()
        self.config = None
        self.browser_manager = None
        self.captcha_solver = None
        self.orchestrator = None

    def setup(self) -> bool:
        """
        Set up all application components.

        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            # Initialize configuration
            self.config = Config()
            self.logger.info("Configuration manager initialized")

            # Initialize captcha solver
            api_key = os.environ.get("TWOCAPTCHA_API_KEY")
            self.captcha_solver = CaptchaSolver(api_key)
            if api_key:
                self.logger.info("Captcha solver initialized with API key")
            else:
                self.logger.info("Captcha solver initialized without API key")

            return True

        except Exception as e:
            self.logger.error(f"Failed to set up application: {e}")
            return False

    def setup_browser(self) -> bool:
        """
        Set up browser and proxy components.

        Returns:
            bool: True if browser setup successful, False otherwise
        """
        try:
            # Load proxies
            proxies = self._load_proxies()
            proxy_manager = ProxyManager(proxies)

            # Create browser manager with Playwright
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(
                headless=not (DEBUG_MODE or HEADFUL_BROWSER),
                args=self._get_browser_args()
            )

            self.browser_manager = EnhancedBrowserManager(browser, proxy_manager)
            self.logger.info("Browser and proxy components initialized")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set up browser: {e}")
            return False

    def run(self, start_row: int = None, end_row: int = None) -> bool:
        """
        Run the main automation process.

        Args:
            start_row: Starting row number (1-based)
            end_row: Ending row number (1-based)

        Returns:
            bool: True if automation completed successfully, False otherwise
        """
        try:
            # Create automation orchestrator
            self.orchestrator = AutomationOrchestrator(
                config=self.config,
                browser_manager=self.browser_manager,
                captcha_solver=self.captcha_solver
            )

            # Run automation with specified parameters
            success = self.orchestrator.execute_automation(start_row, end_row)

            if success:
                self.logger.info("Automation completed successfully")
            else:
                self.logger.error("Automation completed with errors")

            return success

        except Exception as e:
            self.logger.error(f"Failed to run automation: {e}")
            return False

    def cleanup(self):
        """Clean up all resources."""
        try:
            if self.browser_manager:
                self.browser_manager.close()
                self.logger.info("Browser resources cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def _load_proxies(self) -> list:
        """Load proxy list from configuration file."""
        try:
            proxy_file = Path("proxies.txt")
            if proxy_file.exists():
                with open(proxy_file) as f:
                    proxies = [line.strip() for line in f.readlines() if line.strip()]
                self.logger.info(f"Loaded {len(proxies)} proxies")
                return proxies
        except Exception as e:
            self.logger.warning(f"Could not load proxies: {e}")

        self.logger.info("Running without proxies")
        return []

    def _get_browser_args(self) -> list:
        """Get optimized browser arguments for stealth browsing."""
        return [
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor",
            "--disable-extensions-except",
            "--disable-extensions",
            "--no-first-run",
            "--disable-default-apps",
            "--disable-component-extensions-with-background-pages",
        ]


def setup_application_environment():
    """Set up the application environment and logging."""
    try:
        # Setup logging directories
        setup_logging_directories()

        # Clear startup logs for fresh run data
        log_files = [
            "price_update_log.txt",
            "automation.log",
            "errors.log",
            "performance.log"
        ]
        for log_file in log_files:
            log_path = Path.cwd() / "logs" / log_file
            log_path.parent.mkdir(exist_ok=True)
            log_path.write_text("")  # Clear the file for fresh run data

        return True
    except Exception as e:
        print(f"Failed to setup application environment: {e}")
        return False


def parse_command_line_arguments():
    """
    Parse and validate command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Enhanced Sheet Scraper - Automate price updates from supplier websites to Google Sheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.sheet_scraper.sheet_scraper                    # Default: process row 7 only
  python -m src.sheet_scraper.sheet_scraper --start-row 1     # Process from row 1 to default end
  python -m src.sheet_scraper.sheet_scraper --start-row 1 --end-row 10  # Process rows 1-10
  python -m src.sheet_scraper.sheet_scraper --end-row 5       # Process from default start to row 5

Note: Row numbers are 1-based (as shown in Google Sheets).
        """
    )

    parser.add_argument(
        "--start-row",
        type=int,
        metavar="N",
        help="Starting row number (1-based, as shown in Google Sheets). Default: 7"
    )

    parser.add_argument(
        "--end-row",
        type=int,
        metavar="N",
        help="Ending row number (1-based, inclusive). Default: 7"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.start_row is not None and args.start_row < 1:
        parser.error("Start row must be >= 1")
    if args.end_row is not None and args.end_row < 1:
        parser.error("End row must be >= 1")
    if (args.start_row is not None and args.end_row is not None and
        args.start_row > args.end_row):
        parser.error("Start row must be <= end row")

    return args


def main():
    """
    Main entry point following the Template Method pattern.

    This function defines the skeleton of the automation algorithm,
    allowing subcomponents to override specific steps while maintaining
    the overall structure.
    """
    # Step 1: Setup environment
    if not setup_application_environment():
        sys.exit(1)

    # Step 2: Parse arguments
    args = parse_command_line_arguments()

    # Step 3: Display execution plan
    logger = get_logger()
    start_display = args.start_row or "default (7)"
    end_display = args.end_row or "default (7)"
    logger.info(f"Starting Sheet Scraper - Processing rows {start_display} to {end_display}")

    # Step 4: Initialize and run application
    app = SheetScraperApplication()
    success = False

    try:
        # Setup phase
        if not app.setup():
            logger.error("Application setup failed")
            sys.exit(1)

        if not app.setup_browser():
            logger.error("Browser setup failed")
            sys.exit(1)

        # Execution phase
        success = app.run(args.start_row, args.end_row)

    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
    finally:
        # Cleanup phase
        app.cleanup()

    # Step 5: Exit with appropriate code
    exit_code = 0 if success else 1
    logger.info(f"Application finished with exit code {exit_code}")
    sys.exit(exit_code)


# Legacy support functions for backwards compatibility
def scrape_product_details(url, page, captcha_solver, config=None):
    """
    Legacy function for backwards compatibility.

    This function is maintained for compatibility with existing tests
    but delegates to the new modular architecture.
    """
    from .automation_core import ProductScraper

    scraper = ProductScraper(page, captcha_solver, config)
    return scraper.scrape_product(url)


def run_price_update_automation(page, captcha_solver, config=None, browser_manager=None,
                                start_row=None, end_row=None):
    """
    Legacy function for backwards compatibility.

    This function is maintained for compatibility with existing tests
    but delegates to the new modular architecture.
    """
    from .core.automation_core import AutomationOrchestrator

    orchestrator = AutomationOrchestrator(
        config=config or Config(),
        browser_manager=browser_manager,
        captcha_solver=captcha_solver
    )

    return orchestrator.execute_automation(start_row, end_row)


def parse_arguments():
    """
    Legacy function for backwards compatibility.

    This function is maintained for compatibility with existing tests
    but delegates to the new argument parsing logic.
    """
    return parse_command_line_arguments()


# Additional backwards compatibility imports
def get_service():
    """Legacy function for backwards compatibility."""
    from .infrastructure.connect import get_service as _get_service
    return _get_service()


def read_sheet_data(*args, **kwargs):
    """Legacy function for backwards compatibility."""
    from .scraping_utils import read_sheet_data as _read_sheet_data
    return _read_sheet_data(*args, **kwargs)


def update_sheet(sheet, range_name, values):
    """Legacy function for backwards compatibility."""
    from .sheet_operations import update_sheet as _update_sheet
    return _update_sheet(sheet, range_name, values)


def log_update(product_name, old_price, new_price, status, message, row_num):
    """Legacy function for backwards compatibility."""
    from .logs_module.automation_logging import log_update as _log_update
    return _log_update(product_name, old_price, new_price, status, message, row_num)


if __name__ == "__main__":
    main()
