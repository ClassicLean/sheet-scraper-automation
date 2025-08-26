# Sheet Scraper Automation Tool

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-141%20passing-green.svg)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-PEP%208-blue.svg)](https://www.python.org/dev/peps/pep-0008/)

A sophisticated automated web scraping tool that monitors product prices across multiple supplier websites and updates Google Sheets with real-time data. Features comprehensive site support, intelligent blocking detection, automated retries, and a modern Flask web interface.

## ✨ Features

- **Multi-Site Support**: Amazon, Walmart, Kohls, Vivo, Wayfair with intelligent site detection
- **Smart Price Extraction**: Handles dynamic pricing, shipping costs, stock status detection
- **Robust Automation**: Anti-detection measures, CAPTCHA solving, proxy rotation
- **Excel Integration**: Real-time Google Sheets updates with formatting and color coding
- **Web Interface**: Modern Flask UI with live progress tracking and browser management
- **Enterprise-Grade**: Comprehensive logging, error handling, and performance monitoring
- **Modular Architecture**: Clean, maintainable codebase following Python best practices

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ClassicLean/sheet-scraper-automation.git
   cd sheet-scraper-automation
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Set up Google Sheets API credentials** (see [Configuration](#configuration) section)

### Basic Usage

**Command Line Interface:**
```bash
# Process default row range (recommended)
python -m src.sheet_scraper

# Process specific rows (1-based indexing)
python -m src.sheet_scraper --start-row 1 --end-row 10

# Process single row for testing
python -m src.sheet_scraper --start-row 66 --end-row 66

# Alternative (legacy) method - may show RuntimeWarning
python -m src.sheet_scraper.sheet_scraper
```

**Web Interface:**
```bash
# Launch Flask web UI
python web_ui/start_ui.py
# Open browser to http://localhost:5000
```

## 📋 Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--start-row N` | Starting row number (1-based) | `--start-row 5` |
| `--end-row N` | Ending row number (1-based, inclusive) | `--end-row 20` |
| `--help` | Show help message and examples | `--help` |

**Legacy Environment Variables** (for backward compatibility):
```bash
set PROCESS_START_ROW=5    # 0-based index
set PROCESS_END_ROW=10     # 0-based index
```
*Note: Command-line arguments take priority over environment variables.*

## ⚙️ Configuration

### Required Environment Variables

```bash
# Google Sheets integration
SPREADSHEET_ID=your_google_sheet_id_here

# Optional: Row processing (legacy support)
PROCESS_START_ROW=0    # 0-based index
PROCESS_END_ROW=100    # 0-based index
```

### Google Sheets API Setup

1. Create a Google Cloud Project
2. Enable the Google Sheets API
3. Create service account credentials
4. Share your Google Sheet with the service account email
5. Download credentials JSON and place in project root

## 🏗️ Architecture

The project follows a modern modular architecture with clear separation of concerns:

```
src/sheet_scraper/
├── automation/          # High-level automation orchestration
├── core/               # Business logic & main automation
├── infrastructure/     # External services (browser, API, proxy)
├── config/            # Configuration management
├── logging/           # Enhanced logging & monitoring
└── utils/             # Shared utilities (pricing, data processing)
```

## 🧪 Testing

**Run the comprehensive test suite:**
```bash
# Run all tests (141 passing tests)
pytest tests/ -v

# Run specific test categories
pytest tests/test_web_scraping.py -v
pytest tests/test_configuration.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Test Categories:**
- Configuration & Site Detection
- Core Functionality & Row Range Processing
- Feature Testing (shipping, highlighting, blocking)
- Formatting & Excel Integration
- Infrastructure & Project Structure
- Web Scraping & Price Extraction
- Web UI Integration

## 🚀 Development

**Project Structure:**
```bash
# Run code quality checks
ruff check --fix                    # Linting
python dev_tools/cleanup.py        # Codebase cleanup

# Development tools
python dev_tools/selector_research.py    # CSS selector testing
python dev_tools/debug_blocking.py       # Debug detection issues
```

**Available Tasks:**
```bash
# Build & test
python -m pytest tests/ -v          # Run tests
python -m src.sheet_scraper.sheet_scraper    # Run main script

# Code quality
ruff check --fix                    # Lint code
python dev_tools/cleanup.py        # Clean codebase
```
