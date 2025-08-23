# Sheet-Scraper Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Shifted execution strategy from GitHub Workflow to local machine for enhanced anti-bot evasion.
- Configured Playwright to run in headful mode (`headless=False`) for more human-like browsing.
- Disabled GitHub Actions workflow (`scrape.yml` renamed to `scrape.yml.disabled`).

### Fixed
- Resolved issue where items appeared unavailable due to incorrect location by setting Playwright locale to `en-US`.
- Fixed Google Sheets `batchUpdate` not sending updates (including coloring, price, VA notes, and last stock check) by correctly populating the `requests` list.

### Added

### Deprecated

### Removed
- Removed desktop notification pop-up (tkinter) due to test suite hanging issues.

### Security

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
