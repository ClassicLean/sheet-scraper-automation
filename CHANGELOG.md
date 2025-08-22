# Sheet-Scraper Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Deprecated

### Removed

### Security
