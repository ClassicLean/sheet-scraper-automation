"""
Configuration management and application settings.

This package contains modules for managing application configuration,
constants, and settings across different environments.
"""

# Import key classes for easy access
from .config_manager import Config

# Re-export all constants for easy access (suppressing linting warnings)
# ruff: noqa: F403, F401
from .constants import *

__all__ = ['Config']
