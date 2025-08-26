"""
Infrastructure package for external services and system interactions.

This package contains modules for managing external services and integrations
such as browser automation, proxy management, CAPTCHA solving, and connections.
"""

from .browser_manager import EnhancedBrowserManager
from .captcha_solver import *
from .connect import *
from .proxy_manager import *

# Import key classes for easy access
from .browser_manager import *
from .captcha_solver import *
from .proxy_manager import *
from .connect import *

__all__ = ['EnhancedBrowserManager']
