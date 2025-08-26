"""
Configuration management for the sheet scraper.
Provides centralized access to selectors, settings, and other configuration data.
"""

import json
from pathlib import Path
from typing import Any


class Config:
    """Centralized configuration management."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.config_dir = self.project_root / "config"
        self._selectors = None
        self._settings = None
        self._validate_config()

    @property
    def selectors(self) -> dict[str, Any]:
        """Load and cache selector configuration."""
        if self._selectors is None:
            selector_file = self.config_dir / "selectors.json"
            try:
                with open(selector_file, encoding="utf-8") as f:
                    self._selectors = json.load(f)
            except FileNotFoundError:
                print(f"Warning: Selector config file not found at {selector_file}")
                self._selectors = self._get_default_selectors()
        return self._selectors

    def _get_default_selectors(self) -> dict[str, Any]:
        """Fallback selector configuration."""
        return {
            "price_selectors": {
                "generic": [".price", ".product-price", "[itemprop='price']"]
            },
            "stock_selectors": {
                "in_stock": {"generic": [".add-to-cart", ".in-stock"]},
                "out_of_stock": {"generic": [".out-of-stock", ".unavailable"]},
            },
            "blocking_indicators": ["captcha", "blocked", "access denied"],
        }

    def get_price_selectors(self, site: str = "generic") -> list[str]:
        """Get price selectors for a specific site."""
        selectors = self.selectors.get("price_selectors", {})
        return selectors.get(site, selectors.get("generic", []))

    def get_stock_selectors(
        self, site: str = "generic", stock_type: str = "in_stock"
    ) -> list[str]:
        """Get stock selectors for a specific site and stock type."""
        selectors = self.selectors.get("stock_selectors", {}).get(stock_type, {})
        return selectors.get(site, selectors.get("generic", []))

    def get_blocking_indicators(self) -> list[str]:
        """Get list of blocking indicators."""
        return self.selectors.get("blocking_indicators", [])

    def detect_site(self, url: str) -> str:
        """Detect site type from URL."""
        url_lower = url.lower()
        if "amazon.com" in url_lower:
            return "amazon"
        elif "walmart.com" in url_lower:
            return "walmart"
        elif "kohls.com" in url_lower:
            return "kohls"
        elif "vivo-us.com" in url_lower:
            return "vivo"
        elif "wayfair.com" in url_lower:
            return "wayfair"
        else:
            return "generic"

    def get_spreadsheet_id(self) -> str:
        """Get spreadsheet ID from configuration."""
        if self._settings is None:
            self._load_settings()
        return self._settings.get("spreadsheet_id", "")

    def get_range_name(self) -> str:
        """Get range name from configuration."""
        if self._settings is None:
            self._load_settings()
        return self._settings.get("range_name", "FBMP!A1:AQ1000")  # Use AQ to get more columns

    def _load_settings(self) -> None:
        """Load settings from settings.json file."""
        # Try settings.json first (new format)
        settings_file = self.config_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, encoding="utf-8") as f:
                    self._settings = json.load(f)
                return
            except Exception as e:
                print(f"Warning: Could not load settings from {settings_file}: {e}")

        # Fallback to sheet-scraper-as.json (service account file format - not recommended)
        fallback_file = self.config_dir / "sheet-scraper-as.json"
        try:
            with open(fallback_file, encoding="utf-8") as f:
                data = json.load(f)
                # Extract only non-credential settings if they exist
                self._settings = {
                    "spreadsheet_id": data.get("spreadsheet_id", ""),
                    "range_name": data.get("range_name", "FBMP!A1:AQ1000")
                }
        except FileNotFoundError:
            print(f"Warning: No settings config files found at {settings_file} or {fallback_file}")
            self._settings = {"spreadsheet_id": "", "range_name": "FBMP!A1:AQ1000"}  # Use AQ for broader range

    def _validate_config(self) -> None:
        """Validate configuration files and directories exist."""
        if not self.config_dir.exists():
            print(f"Warning: Config directory not found at {self.config_dir}")
            self.config_dir.mkdir(parents=True, exist_ok=True)

        selector_file = self.config_dir / "selectors.json"
        if not selector_file.exists():
            print(f"Warning: Selector config file not found at {selector_file}")
            # Create a basic config file
            default_config = self._get_default_selectors()
            with open(selector_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
            print("Created default selector configuration.")


# Global config instance
config = Config()
