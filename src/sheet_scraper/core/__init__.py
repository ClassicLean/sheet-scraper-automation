"""
Core business logic and main application functionality.

This package contains the primary business logic for the sheet scraper application,
including automation orchestration, product processing, and sheet operations.
"""

# Import key classes for easy access
# Note: automation_core import is commented out to avoid circular imports
# from .automation_core import *

# Re-export core components (suppressing linting warnings for unused imports)
# ruff: noqa: F403, F401
from .product_processing import *
from .sheet_operations import *

__all__ = []  # Will be populated based on actual exports
