# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Advanced Testing Infrastructure & Performance Optimization (2025-08-27)
- **✅ Performance Benchmarking** - Implemented `pytest-benchmark` with 4 comprehensive benchmark tests measuring microsecond-level performance
- **✅ Parallel Test Execution** - Added `pytest-xdist` for multi-worker parallel testing (6 workers on 12-core systems)
- **✅ Comprehensive Testing Suite** - Created unified testing workflows with `dev_tools/comprehensive_testing.py`
- **✅ Performance Testing Tools** - Added `dev_tools/performance_testing.py` for detailed performance analysis
- **✅ Browser Setup Validation** - Created `dev_tools/browser_validation.py` for diagnosing browser issues
- **✅ Enhanced Error Handling** - Robust browser page creation with detailed debug logging and validation
- **✅ Test Infrastructure Analysis** - Comprehensive review against Python best practices (Real Python, Python.org)

### Fixed - Critical Browser Management Issues (2025-08-27)
- **❌ → ✅ Resolved**: `'NoneType' object has no attribute 'goto'` errors in web scraping
- **❌ → ✅ Resolved**: Browser page creation failures causing automation crashes
- **❌ → ✅ Resolved**: Silent browser manager failures without proper error reporting
- **✅ Enhanced**: Browser context creation with comprehensive error handling and debug output

### Performance - Testing Speed Improvements (2025-08-27)
- **Parallel Execution**: 3-4x faster test execution on multi-core systems
- **Benchmark Results**: Price parsing at 346.7K ops/sec (2.88 μs per operation)
- **Intelligent Workers**: Auto-detection of optimal worker count (CPU cores / 2)
- **Performance Metrics**: Bulk processing at 75.1K ops/sec, stock detection at 26.5K ops/sec

### Configuration - Enhanced Testing Setup (2025-08-27)
- **pytest.ini**: Added benchmark marker configuration
- **pyproject.toml**: Enhanced with pytest-benchmark and pytest-xdist dependencies and settings
- **Test Markers**: Professional categorization with 8 comprehensive test markers
- **Quality Tools**: Updated tool stack with latest versions (pytest 8.4.1, ruff 0.8.4, etc.)

### Documentation - Testing Excellence Documentation (2025-08-27)
- **Developer Guide**: Comprehensive testing section with industry best practices analysis
- **Test Architecture**: Detailed documentation of 149-test modular structure
- **Performance Benchmarking**: Usage examples and interpretation guidelines
- **Quality Metrics**: Assessment against industry standards with compliance verification

## [2.1.0] - 2025-01-15

### Changed
- **Comprehensive Codebase Cleanup** - Completed systematic removal of 15 redundant files totaling over 1,000 lines of dead code
- **Project Structure Optimization** - Eliminated duplicate files, debug scripts, temporary tools, and legacy documentation for cleaner navigation
- **Test Suite Verification** - Maintained 100% test coverage with all 141 tests passing throughout cleanup process
- **Documentation Updates** - Updated README.md test count from 140 to 141 tests

### Removed
- **Debug Scripts** (6 files): `check_template.py`, `debug_template.py`, `direct_test.py`, `final_test.py`, `test_simple.py`, `verify_ui.py` - Development artifacts no longer needed
- **Individual Test Files** (8 files): Consolidated standalone test files (`test_blocking_detection.py`, `test_blocking_simple.py`, etc.) into main test suite structure
- **Legacy Documentation** (1 file): `backup/automation_core_backup.py` - Outdated backup file replaced by current modular architecture

### Security
- **Codebase Hardening** - Removed potential security risks from abandoned debug scripts and temporary files

### Added
- Comprehensive documentation update following Python best practices
- Modern README with badges, feature highlights, and structured documentation
- Complete package architecture documentation

## [2.0.0] - 2025-08-26

### Added - Project Structure Optimization & Empty File Cleanup
- **Empty file cleanup** - Removed 9 redundant empty duplicate files from root directory
- **File structure validation** - Confirmed all imports properly reference organized modular structure
- **Project optimization** - Cleaner project navigation with maintained functionality through organized packages

### Added - Test Suite Restructuring & Modernization (2025-08-25)
- **Modular test architecture** - Transformed monolithic 1,355-line test file into 8 focused, maintainable modules
- **Professional test organization** - Split tests into logical groups: configuration, core functionality, features, formatting, infrastructure, web scraping, web UI, and project structure
- **Enhanced maintainability** - Each test file now averages 200-300 lines with clear separation of concerns
- **Shared test infrastructure** - Centralized imports and fixtures in `conftest.py` reducing duplication
- **Modern pytest patterns** - Implemented best practices with logical grouping, clear naming, and comprehensive documentation
- **Test coverage expansion** - Maintained all 71 original tests and added 2 new infrastructure validation tests (73 total)
- **Team collaboration support** - Parallel development capabilities with reduced merge conflicts through focused file structure
- **Performance improvements** - Faster IDE loading, selective testing, and better test discovery through modular organization

### Added - Web UI Enhancements & Cache-Busting (2025-08-25)
- **Animated loading spinner** - Replaced static progress bar with CSS animation for better visual feedback
- **Comprehensive Flask cache-busting** - HTTP headers, before_request cache clearing, template auto-reload, and Jinja environment configuration
- **Template monitoring** - Enhanced template file monitoring for automatic reload during development
- **Cache-busting meta tags** - Timestamp-based cache invalidation for browser cache prevention
- **Enhanced Web UI testing** - New `TestWebUIIntegration` class with 5 tests covering Flask imports, routes, cache-busting configuration, and template validation
- **Project structure validation** - New `TestProjectStructure` class with 4 tests ensuring Flask dependencies, .gitignore patterns, and cleanup verification

### Added - Wayfair Integration & Site Detection Enhancement (2025-08-25)
- **Wayfair site detection** - Added "wayfair.com" → "wayfair" mapping in config_manager.py for proper selector assignment
- **Wayfair price selectors** - Comprehensive selectors including `[data-test-id='PriceDisplay']` and `StandardPricingPrice-PRIMARY` for accurate price extraction
- **Enhanced selectors.json** - Updated configuration with site-specific Wayfair price and stock detection selectors
- **Corrected price extraction** - Fixed Wayfair scraping from incorrect $5.00 to accurate pricing

### Added - Package Architecture & Modular Refactoring (2025-08-25)
- **4-tier modular architecture** - Created organized package structure with `automation/`, `core/`, `infrastructure/`, `config/`, `logging/`, and `utils/` packages
- **Single responsibility principle** - Each module focused on specific functionality for better maintainability
- **Professional package organization** - Proper `__init__.py` files with exports and package documentation
- **Backwards compatibility** - Maintained all existing functionality through organized structure
- **Code size reduction** - Transformed 1,081-line monolithic file into focused modules (56 lines main + 8 organized modules)

### Added - Row Range Specification Feature (2025-08-25)
- **Command-line row range specification** - Users can specify which rows to process using `--start-row` and `--end-row` arguments
- **Flexible row processing** - Support for processing single rows, ranges, or custom selections for efficient testing and production workflows
- **Enhanced argument parsing** - Added argparse support with comprehensive help documentation and usage examples
- **1-based row numbering** - User-friendly row numbers matching Google Sheets display (automatically converted to 0-based indices internally)
- **Priority-based configuration** - Command-line arguments override environment variables, which override defaults
- **Backward compatibility** - Existing environment variable configuration (`PROCESS_START_ROW`, `PROCESS_END_ROW`) continues to work
- **Comprehensive testing** - Added `TestRowRangeFunctionality` test class with 7 new tests covering all argument parsing scenarios

### Added - Enhanced Features & Integrations (2025-08-25)
- **Column formatting improvements** - Column A: removed text for "Out of stock"/"Price not found" (red fill only), Column E: black text on light cyan background for available items
- **Noah supplier highlighting** - Dark purple text with light green fill for Noah suppliers in columns N/O when items are available
- **Enhanced blocking detection** - Blue text formatting for "Blocked" status, differentiated from out-of-stock items
- **Shipping fee integration** - Total price calculation (base + shipping), Column Z updates, row 66 testing mode
- **Stop script functionality** - Stop button properly terminates subprocess and closes headful browser automatically
- **Loading interface** - Replaced percentage progress bar with animated loading bar for better visual feedback

### Added - Core Infrastructure & Reliability (2025-08-25)
- **Configuration validation system** - Automatic config file creation for missing configurations
- **Enhanced Google Sheets API reliability** - Exponential backoff retry logic for quota exhaustion (HTTP 429 errors)
- **Rate limiting protection** - Between API calls to prevent quota abuse
- **Improved Vivo price selector targeting** - Specific product area selectors for accurate $119.99 extraction
- **Type hints** - For better code documentation and IDE support
- **Module-level imports optimization** - Removed inline imports for better performance
- **Enhanced CAPTCHA solving** - `2captcha-python` library integration
- **Proxy management** - `ProxyManager` class for proxy rotation
- **Browser fingerprinting protection** - `pyppeteer-stealth` library implementation

### Changed
- **BREAKING**: Updated to Python 3.13+ requirement for latest features and performance improvements
- **Code Quality**: Standardized import ordering with alphabetical organization for better maintainability
- **API Resilience**: Enhanced update_sheet() function with sophisticated retry logic and jitter for API quota management
- **Configuration Management**: Added automatic validation and creation of missing config files on startup
- **Test Suite**: Fixed failing tests with proper environment variable mocking and configurable row processing
- **Vivo Integration**: Improved price selector specificity to target main product area (.product__price) avoiding related product prices
- **Function signatures**: Fixed critical bugs in `extract_price()` and `is_in_stock()` functions to properly handle config parameters
- **Blocking detection logic**: Refined to eliminate false positives while maintaining security
- **Processing logic**: Better distinction between "price not found", "out of stock", and successful updates
- **Logging system**: Clearer, more informative messages and better error categorization
- **Project structure**: Moved development tools to `dev_tools/` directory
- **Build system**: Replaced `requirements.txt` with `pyproject.toml` for modern Python packaging
- **Execution strategy**: Shifted from GitHub Workflow to local machine for enhanced anti-bot evasion
- **Browser configuration**: Playwright runs in headful mode (`headless=False`) for more human-like browsing

### Fixed
- **Import organization**: Resolved inconsistent import styles and moved inline imports to module level
- **Exception handling**: Replaced generic `Exception` catching with specific exception types (`AttributeError`, `RuntimeError`, `ValueError`, `TypeError`)
- **Mock compatibility**: Functions now properly handle mock objects in tests with type checking
- **Package initialization**: Fixed empty `__init__.py` files with proper exports and public API access
- **Log file management**: Removed redundant log files, maintained centralized logging system

### Removed
- **GitHub Actions workflow**: Disabled `scrape.yml` to prevent automated execution conflicts
- **Redundant files**: Cleaned up 13 obsolete files from root directory for better organization
- **Empty duplicate files**: Removed 9 empty files that were duplicates of organized structure
- **Unused dependencies**: Removed legacy requirements and cleaned up import statements

### Security
- **Enhanced anti-detection**: Improved browser fingerprinting protection and human-like interaction patterns
- **Proxy rotation**: Added proxy management for distributed request patterns
- **CAPTCHA solving**: Integrated automated CAPTCHA resolution capabilities

## [1.0.0] - 2025-08-25

### Added
- Initial release with core web scraping functionality
- Google Sheets integration
- Basic price monitoring capabilities
- Support for major supplier websites
- Flask web interface
- Comprehensive logging system

[Unreleased]: https://github.com/ClassicLean/sheet-scraper-automation/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/ClassicLean/sheet-scraper-automation/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/ClassicLean/sheet-scraper-automation/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/ClassicLean/sheet-scraper-automation/releases/tag/v1.0.0
- Removed incorrect `stealth(page, ...)` call from `sheet_scraper.py`.
- Implemented extensive conditional styling rules in Google Sheets based on product stock status and price, enhancing visual feedback for in-stock items under $299.99.

### Fixed
- **CRITICAL**: Flask template caching completely resolved - templates now update immediately with comprehensive cache-busting strategy
- **CRITICAL**: Duplicate browser tabs eliminated - start_ui.py now properly checks WERKZEUG_RUN_MAIN environment variable to prevent subprocess duplication
- **CRITICAL**: Wayfair price scraping accuracy restored - corrected $5.00 error to proper $68.75 extraction through enhanced site detection
- **Template refresh issues**: Implemented before_request cache clearing, enhanced HTTP headers, and Jinja environment auto-reload for immediate template updates
- **Browser management**: Fixed start_ui.py opening multiple browser tabs by implementing Flask reloader subprocess detection
- **Site-specific scraping**: Enhanced config_manager.py site detection logic to properly assign Wayfair-specific selectors
- **CRITICAL**: Resolved function signature bugs that were causing AttributeError crashes when config=None parameter was passed.
- **CRITICAL**: Fixed CSS selector execution - selectors were working correctly but function crashes prevented their execution.
- Corrected blocking detection false positives by refining indicator patterns in `selectors.json`.
- Resolved browser context closure issues that were causing "Target page, context or browser has been closed" errors.
- Added missing `os` import in `scraping_utils.py` to resolve logging errors.
- Improved test consistency by removing try/catch blocks for legacy function signatures.
- Corrected "VA Notes" update logic in `sheet_scraper.py`.
- Resolved `name 'requests' is not defined` error by adding `requests` to `requirements.txt`.
- Improved `parse_price` function for more robust price extraction and comma validation.
- Fixed `extract_price` function to correctly combine whole and fractional price parts.
- Enhanced `is_in_stock` function for more accurate stock detection by prioritizing out-of-stock indicators.

### Removed
- **Comprehensive codebase cleanup** - Removed 8 temporary/debug files: check_template.py, final_test.py, test_simple.py, verify_ui.py, debug_template.py, direct_test.py, and redundant requirements.txt files
- **Test suite consolidation** - Enhanced test coverage to 70 total tests (up from 64) with comprehensive Web UI and project structure validation
- **Dependency consolidation** - Flask dependency moved to pyproject.toml, removed redundant web_ui/requirements.txt
- **Enhanced .gitignore patterns** - Added comprehensive patterns for temporary files, cache directories, and IDE files
- **Legacy automation files**: `automate.py`, `check_automation.py` (replaced by main module architecture)
- **Debug files**: `debug_blocking_issue.py`, `selector_research.py` (duplicate), `vivo.html` (static test file)
- **Standalone test files** (8 total): `test_blocking_detection.py`, `test_blocking_simple.py`, `test_enhanced_blocking.py`, `test_noah_highlighting.py`, `test_price_extraction.py`, `test_shipping_fees.py`, `test_temp_system.py`, `test_vivo_selectors.py` - Functionality consolidated into main test suite
- **Cache directories**: `.pytest_cache/`, `src/sheet_scraper/__pycache__/`, `tests/__pycache__/` - Generated files properly ignored
- Removed unused imports (`stealth_sync` from `undetected_playwright.ninja`).
- Removed cache directories (`__pycache__`, `.pytest_cache`, `.ruff_cache`, `*.egg-info`).
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
