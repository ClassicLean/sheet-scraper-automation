#!/usr/bin/env python3
"""
Main entry point for the Sheet Scraper application.

This module allows the package to be executed with 'python -m src.sheet_scraper'
instead of 'python -m src.sheet_scraper.sheet_scraper', which avoids the
RuntimeWarning about double imports.

Usage:
    python -m src.sheet_scraper
"""

from .sheet_scraper import main

if __name__ == "__main__":
    main()
