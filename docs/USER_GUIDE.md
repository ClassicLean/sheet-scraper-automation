# Sheet Scraper User Guide

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Features](#features)
7. [Troubleshooting](#troubleshooting)
8. [Security](#security)

## Overview

The Enhanced Sheet Scraper is an intelligent automation tool that monitors product prices across multiple supplier websites and maintains accurate pricing data in Google Sheets. It features advanced web scraping capabilities, automated price comparison, and comprehensive inventory management.

### Key Capabilities

- **Automated Price Discovery** - Visit supplier websites and extract current pricing
- **Intelligent Price Comparison** - Find lowest in-stock prices across suppliers
- **Google Sheets Integration** - Seamless updates with audit trail logging
- **Anti-Detection Technology** - Stealth browsing with advanced blocking countermeasures
- **Visual Status Indicators** - Color-coded formatting for inventory status
- **Flexible Processing** - Configurable row ranges and batch operations

## Quick Start

### Prerequisites

- Python 3.13+
- Google Cloud Service Account with Sheets API access
- Google Sheet with proper column structure
- Internet connection for web scraping

### 30-Second Setup

```bash
# 1. Install dependencies
pip install -e .
playwright install

# 2. Configure authentication
# Place your service account JSON in config/sheet-scraper-as.json

# 3. Run the scraper
python -m src.sheet_scraper.sheet_scraper
```

## Installation & Setup

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/ClassicLean/sheet-scraper-automation.git
cd sheet-scraper-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e .[dev]

# Install browser binaries
playwright install
```

### 2. Google Cloud Authentication

#### Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin → Service Accounts**
3. Create new service account with **Google Sheets API Editor** role
4. Generate and download JSON key
5. Rename to `sheet-scraper-as.json` and place in `config/` directory

#### Share Your Sheet

Share your Google Sheet with the service account email address found in the JSON key file:
```
your-service-account@your-project.iam.gserviceaccount.com
```

### 3. Environment Variables

Create `.env` file in project root:

```bash
# Core Configuration
PROCESS_START_ROW=5                   # Default starting row
PROCESS_END_ROW=                      # End row (empty = process all)
GOOGLE_APPLICATION_CREDENTIALS=config/sheet-scraper-as.json

# Performance Settings
MAX_CONCURRENT_REQUESTS=5             # Parallel processing limit
REQUEST_TIMEOUT=30                    # Timeout per request (seconds)
RETRY_ATTEMPTS=3                      # Number of retry attempts

# Anti-Detection
USE_PROXY=false                       # Enable proxy rotation
STEALTH_MODE=true                     # Enable stealth browser features
```

## Configuration

### Google Sheets Structure

Your Google Sheet must follow this column structure:

| Column | Purpose | Index |
|--------|---------|-------|
| A | VA Notes | 0 |
| D | Last Stock Check | 3 |
| X | Supplier Price For ONE Unit | 23 |
| AF | Supplier in Use | 31 |
| AH-AQ | Supplier A-J URLs | 34-43 |

### Selector Configuration

Edit `config/selectors.json` to customize price and stock detection:

```json
{
  "amazon": {
    "price_selectors": [
      ".a-price-whole",
      ".a-offscreen",
      "#price_inside_buybox"
    ],
    "stock_selectors": [
      "#availability span",
      ".a-declarative .a-color-success"
    ],
    "blocking_indicators": [
      "Robot Check",
      "CAPTCHA",
      "Blocked"
    ]
  },
  "wayfair": {
    "price_selectors": [
      "[data-test-id='ProductPrice']",
      ".ProductPricing-sale"
    ],
    "stock_selectors": [
      "[data-test-id='ProductAvailability']"
    ]
  }
}
```

### Settings Configuration

Modify `config/settings.json` for automation behavior:

```json
{
  "automation": {
    "default_start_row": 5,
    "max_retries": 3,
    "request_timeout": 30,
    "rate_limit_delay": 2.5
  },
  "google_sheets": {
    "quota_retry_attempts": 5,
    "backoff_multiplier": 2.0,
    "max_backoff_seconds": 300
  },
  "browser": {
    "headless": false,
    "stealth_mode": true,
    "user_data_dir": "./browser_data"
  }
}
```

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Process default row range (starts at row 5)
python -m src.sheet_scraper.sheet_scraper

# Process specific row range
python -m src.sheet_scraper.sheet_scraper --start-row 1 --end-row 10

# Process single row for testing
python -m src.sheet_scraper.sheet_scraper --start-row 20 --end-row 20
```

#### Advanced Options

```bash
# Get help information
python -m src.sheet_scraper.sheet_scraper --help

# Use environment variables for row range (legacy support)
export PROCESS_START_ROW=1
export PROCESS_END_ROW=50
python -m src.sheet_scraper.sheet_scraper
```

#### Row Range Priority System

The row range is determined using the following priority:

1. **Command-line arguments** (highest priority)
2. **Environment variables** (`PROCESS_START_ROW`, `PROCESS_END_ROW`)
3. **Configuration defaults** (starts at row 5)

**Note:** Row numbers are 1-based (as shown in Google Sheets), but environment variables use 0-based indexing for backward compatibility.

### VS Code Tasks

Run predefined tasks from VS Code:

- **Run Main Script** - Execute automation with default settings
- **Run Tests** - Execute full test suite
- **Lint Code** - Check code quality with Ruff
- **Clean Codebase** - Remove temporary files

### Web UI Interface

Launch the web interface for easier management:

```bash
# Start web server
python web_ui/start_ui.py

# Access at http://localhost:5000
```

The web UI provides:
- Real-time automation status
- Interactive configuration
- Visual progress tracking
- Log file viewing

## Features

### Core Automation Features

#### Price Discovery & Comparison

- **Multi-Supplier Scraping** - Simultaneously check prices across all configured suppliers
- **Intelligent Tie-Breaking** - Select first supplier when prices are equal
- **Price Change Tracking** - Visual indicators for price movements (Up ↗️ / Down ↘️ / $$$ 💰)
- **Fallback Handling** - Graceful handling when all suppliers fail

#### Inventory Management

- **Stock Status Detection** - Identify in-stock vs out-of-stock products
- **Discontinuation Detection** - Special handling for discontinued items (Vevor)
- **Availability Indicators** - Clear status in VA Notes column
- **Best Supplier Tracking** - Automatic selection of optimal supplier

#### Data Integrity

- **Audit Trail Logging** - Complete history of all price updates
- **Separate Date Updates** - Last check date updated regardless of price success
- **Error State Handling** - Proper None values for failed extractions
- **Quota Management** - Automatic Google Sheets API quota handling

### Advanced Features

#### Anti-Detection Technology

- **Stealth Browsing** - Undetected browser fingerprinting
- **Human-like Behavior** - Random delays and mouse movements
- **User-Agent Rotation** - Dynamic browser identification
- **Error Page Detection** - Skip 404 and blocked pages
- **CAPTCHA Handling** - Integration with solving services

#### Visual Formatting

- **Status-Based Coloring** - Red highlighting for out-of-stock items
- **Column-Specific Formatting** - Different colors for different data types
- **Price Threshold Indicators** - Special formatting for premium items ($299.99+)
- **Conditional Styling** - Dynamic formatting based on content

#### Flexible Processing

- **Row Range Control** - Process specific rows or ranges
- **Environment Configuration** - Override settings via environment variables
- **Batch Operations** - Efficient processing of multiple products
- **Parallel Execution** - Concurrent supplier checking

### Site-Specific Enhancements

#### Amazon Integration
- Advanced price selector targeting
- Availability detection via multiple indicators
- Anti-blocking countermeasures

#### Wayfair Support
- Product price extraction
- Stock status determination
- Rate limiting compliance

#### Vevor Discontinuation Detection
- Schema.org structured data parsing
- Discontinued product identification
- Proper fallback handling

## Troubleshooting

### Common Issues

#### "Blocked by Website" Status

**Symptoms:** "Blocked" appears in VA Notes column

**Solutions:**
1. Enable stealth mode: `STEALTH_MODE=true`
2. Reduce request frequency: increase `rate_limit_delay`
3. Update User-Agent strings in browser configuration
4. Consider proxy rotation: `USE_PROXY=true`

#### Google Sheets API Quota Exceeded

**Symptoms:** HTTP 429 errors in logs

**Solutions:**
1. Built-in exponential backoff handles this automatically
2. Reduce concurrent requests: `MAX_CONCURRENT_REQUESTS=1`
3. Increase rate limiting: `rate_limit_delay=5.0`
4. Check Google Cloud Console for quota limits

#### Price Extraction Failures

**Symptoms:** "Price not found" in logs

**Solutions:**
1. Update CSS selectors in `config/selectors.json`
2. Check for website structure changes
3. Enable debug logging: `LOG_LEVEL=DEBUG`
4. Use `dev_tools/selector_research.py` for testing

#### Test Failures

**Symptoms:** pytest failures during development

**Solutions:**
```bash
pytest tests/ -v --tb=short          # Detailed error information
pytest tests/ -v --lf                # Run last failed tests only
pytest tests/ -v --collect-only      # Verify test discovery
```

### Debug Tools

```bash
# Test blocking detection on specific URL
python dev_tools/debug_blocking.py <url>

# Research CSS selectors for new sites
python dev_tools/selector_research.py <url>

# Clean development artifacts
python dev_tools/cleanup.py
```

### Log Analysis

Monitor automation progress through log files:

- `logs/automation.log` - General automation events
- `logs/errors.log` - Error details and stack traces
- `logs/performance.log` - Performance metrics
- `logs/price_update_log.txt` - Price update audit trail

### Performance Monitoring

```python
# Access built-in performance metrics
from src.sheet_scraper.automation.stats import AutomationStats

stats = automation.get_performance_metrics()
print(f"Success Rate: {stats.success_rate:.1%}")
print(f"Avg Processing Time: {stats.avg_processing_time:.2f}s")
print(f"API Quota Usage: {stats.api_quota_usage}")
```

## Security

### Authentication & Authorization

- **Service Account Security** - Google Cloud service accounts with minimal permissions
- **API Key Management** - Secure storage of external service credentials
- **Environment Variables** - No hardcoded secrets in source code
- **Input Validation** - Comprehensive sanitization of scraped data
- **HTTPS Enforcement** - All external communications encrypted

### Data Protection

```python
# Secure credential loading example
import os
from pathlib import Path

def load_credentials():
    """Securely load Google Service Account credentials"""
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not cred_path or not Path(cred_path).exists():
        raise SecurityError("Service account credentials not found")
    return cred_path
```

### Security Best Practices

- ✅ **Principle of Least Privilege** - Minimal Google Sheets API permissions
- ✅ **Error Message Sanitization** - No internal data exposure
- ✅ **Request Rate Limiting** - Built-in protection against abuse
- ✅ **Dependency Scanning** - Automated vulnerability checking
- ✅ **Secure Defaults** - Conservative security settings

### Configuration Security

**Environment Variables Only:**
```bash
# Never commit these to version control
GOOGLE_APPLICATION_CREDENTIALS=config/sheet-scraper-as.json
CAPTCHA_API_KEY=your_api_key_here
TWOCAPTCHA_API_KEY=your_api_key_here
```

**Service Account Permissions:**
- Google Sheets API: Editor role
- No additional permissions required
- Regular key rotation recommended

---

**Last Updated:** August 2025 | **Version:** 2.0.0 | **License:** MIT
