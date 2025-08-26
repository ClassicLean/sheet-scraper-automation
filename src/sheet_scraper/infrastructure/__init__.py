"""
Infrastructure package for external services and system interactions.

This package contains modules for managing external services and integrations
such as browser automation, proxy management, CAPTCHA solving, and connections.
"""

# Import key classes for easy access
from .browser_manager import EnhancedBrowserManager

# Note: Other imports commented out to avoid star import issues
# from .captcha_solver import *
# from .connect import *
# from .proxy_manager import *

__all__ = ['EnhancedBrowserManager']
