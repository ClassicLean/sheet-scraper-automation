# Sheet-Scraper Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `pyppeteer-stealth` library for enhanced browser fingerprinting.
- `2captcha-python` library for CAPTCHA solving.
- `ProxyManager` class for proxy rotation.
- `CaptchaSolver` class for CAPTCHA solving.
- `scraping_utils.py` module for helper functions.
- `twocaptcha` library for CAPTCHA solving.

### Changed
- Noted ongoing challenges with reliable item availability detection on dynamic websites (e.g., Amazon, Vivo), requiring further investigation.
- Refactored `sheet_scraper.py` for modularity and readability.
- Updated import paths due to project restructuring.
- Replaced `requirements.txt` with `pyproject.toml`.
- Shifted execution strategy from GitHub Workflow to local machine for enhanced anti-bot evasion.
- Configured Playwright to run in headful mode (`headless=False`) for more human-like browsing.
- Disabled GitHub Actions workflow (`scrape.yml` renamed to `scrape.yml.disabled`).
- Refactored `sheet_scraper.py` to fix linting errors by moving imports to the top, removing unused ones, and cleaning up constant imports.
- Corrected `undetected-playwright` import path in `sheet_scraper.py`.
- Removed incorrect `stealth(page, ...)` call from `sheet_scraper.py`.

### Fixed
- Corrected "VA Notes" update logic in `sheet_scraper.py`.
- Resolved `name 'requests' is not defined` error by adding `requests` to `requirements.txt`.

### Removed
- Removed `requirements.txt`.
- Removed `tests/test_sheet_scraper_refactored.py` (renamed).
- Removed desktop notification pop-up (tkinter) due to test suite hanging issues.

### Security
- Removed `config/sheet-scraper-as.json` from Git history.

## [0.1.2] - 2025-08-23

## [0.1.1] - 2025-08-22

### Added
- Implemented basic human-like mouse movements and scrolling.
- Set a realistic viewport size for Playwright browser context.

### Changed
- Switched anti-detection library from `playwright-stealth` to `undetected-playwright`.

### Fixed
- Corrected `undetected-playwright` import and usage.
- Removed `python-ghost-cursor` due to Python 3.13 incompatibility.

## [0.1.0] - 2025-08-22

### Added
- Integrated `playwright-stealth` for bot detection evasion.
- Implemented User-Agent rotation for each page request.
- Created `requirements.txt` for dependency management.

### Changed
- Modified delays between requests to be random (`random.uniform(2, 5)`).
- Increased GitHub Actions workflow timeout to 10 minutes.

### Fixed
- Corrected CSS selector syntax in `src/sheet_scraper.py`.
- Updated GitHub Actions workflow to install dependencies from `requirements.txt`.
