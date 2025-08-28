"""
Geolocation logging utilities for the Sheet Scraper automation.

This module provides centralized geolocation logging functionality,
following the project's best practices for logging.
"""

import logging
import logging.config
import os
from pathlib import Path


class GeolocationLogger:
    """Centralized geolocation logger that clears the log file on initialization."""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        """Setup the geolocation logger with file clearing."""
        # Get the project root directory (go up 3 levels from this file)
        project_root = Path(__file__).parent.parent.parent.parent
        logging_config_path = project_root / "logging.conf"

        # Clear the geolocation log file at startup
        log_file_path = project_root / "logs" / "geolocation.log"
        if log_file_path.exists():
            try:
                log_file_path.unlink()  # Delete the file to clear it
            except (PermissionError, OSError):
                # If file is in use, just truncate it instead
                try:
                    with open(log_file_path, 'w') as f:
                        pass  # Truncate the file
                except Exception:
                    pass  # If we can't clear it, continue anyway

        # Ensure logs directory exists
        log_file_path.parent.mkdir(exist_ok=True)

        # Configure logging manually if config file doesn't work
        try:
            if logging_config_path.exists():
                logging.config.fileConfig(str(logging_config_path))
            else:
                # Fallback manual configuration
                self._setup_manual_logger(log_file_path)

            # Get the geolocation logger
            self._logger = logging.getLogger('geolocation')

            # If logger has no handlers, set up manual configuration
            if not self._logger.handlers:
                self._setup_manual_logger(log_file_path)

        except Exception as e:
            # Fallback to manual configuration
            print(f"Warning: Could not configure logging from config file: {e}")
            self._setup_manual_logger(log_file_path)

        # Log the initialization
        self._logger.info("=== Geolocation logging initialized - log file cleared ===")

    def _setup_manual_logger(self, log_file_path):
        """Setup logger manually when config file fails."""
        # Create logger
        self._logger = logging.getLogger('geolocation')
        self._logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self._logger.handlers.clear()

        # Create file handler
        file_handler = logging.FileHandler(str(log_file_path), mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self._logger.addHandler(file_handler)

        # Prevent propagation to avoid console output
        self._logger.propagate = False

    def debug(self, message: str):
        """Log a debug message to the geolocation log."""
        if self._logger:
            self._logger.debug(message)

    def info(self, message: str):
        """Log an info message to the geolocation log."""
        if self._logger:
            self._logger.info(message)

    def warning(self, message: str):
        """Log a warning message to the geolocation log."""
        if self._logger:
            self._logger.warning(message)

    def error(self, message: str):
        """Log an error message to the geolocation log."""
        if self._logger:
            self._logger.error(message)


# Global instance for easy importing
geo_logger = GeolocationLogger()


def log_geolocation_debug(message: str):
    """Convenience function for logging geolocation debug messages."""
    geo_logger.debug(message)


def log_geolocation_info(message: str):
    """Convenience function for logging geolocation info messages."""
    geo_logger.info(message)


def log_geolocation_warning(message: str):
    """Convenience function for logging geolocation warning messages."""
    geo_logger.warning(message)


def log_geolocation_error(message: str):
    """Convenience function for logging geolocation error messages."""
    geo_logger.error(message)
