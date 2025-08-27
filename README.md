# Sheet Scraper Automation Tool

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-149%20discovered-green.svg)](tests/)
[![Performance](https://img.shields.io/badge/benchmarks-pytest--benchmark-orange.svg)](tests/)
[![Parallel Testing](https://img.shields.io/badge/parallel-pytest--xdist-purple.svg)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-PEP%208-blue.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Security](https://img.shields.io/badge/security-bandit-yellow.svg)](https://bandit.readthedocs.io/)
[![Type Hints](https://img.shields.io/badge/typing-enabled-blue.svg)](https://docs.python.org/3/library/typing.html)

An intelligent automation tool that monitors product prices across multiple supplier websites and maintains accurate pricing data in Google Sheets. Features advanced web scraping, automated price comparison, anti-detection technology, and comprehensive inventory management.

## ✨ Key Features

- **🤖 Automated Price Discovery** - Monitor prices across Amazon, Wayfair, Vevor, and more
- **🧠 Intelligent Comparison** - Find lowest in-stock prices with smart tie-breaking
- **📊 Google Sheets Integration** - Real-time updates with visual formatting and audit trails
- **🛡️ Anti-Detection Technology** - Stealth browsing with advanced blocking countermeasures
- **🎨 Visual Status Indicators** - Color-coded formatting for inventory status and price changes
- **🔧 Flexible Processing** - Configurable row ranges, batch operations, and environment controls
- **🌐 Web Interface** - Modern Flask UI with live progress tracking and configuration management
- **⚡ Performance Testing** - Built-in benchmarking with pytest-benchmark (346K+ ops/sec)
- **🚀 Parallel Execution** - Multi-worker test processing with 3-4x speed improvements
- **🧪 Professional Testing** - 149 tests with industry-leading best practices compliance

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Google Cloud Service Account with Sheets API access
- Google Sheet with proper column structure

### 30-Second Setup

```bash
# 1. Clone and install
git clone https://github.com/ClassicLean/sheet-scraper-automation.git
cd sheet-scraper-automation
pip install -e .
playwright install

# 2. Configure authentication (place service account JSON in config/)
cp your-service-account.json config/sheet-scraper-as.json

# 3. Run the scraper
python -m src.sheet_scraper.sheet_scraper
```

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| **[User Guide](docs/USER_GUIDE.md)** | Complete setup, configuration, and usage instructions |
| **[Developer Guide](docs/DEVELOPER_GUIDE.md)** | Technical reference, API documentation, and development |
| **[VS Code Setup](.vscode/README.md)** | VS Code-specific development configuration |

## 📋 Quick Examples

### Basic Operations

```bash
# Process default row range (starts at row 5)
python -m src.sheet_scraper.sheet_scraper

# Process specific row range
python -m src.sheet_scraper.sheet_scraper --start-row 1 --end-row 10

# Process single row for testing
python -m src.sheet_scraper.sheet_scraper --start-row 20 --end-row 20

# Launch web interface
python web_ui/start_ui.py
# Open browser to http://localhost:5000
```

### Development Tasks

Use VS Code tasks or run directly:

```bash
# Run tests
python -m pytest tests/ -v

# Code quality check
ruff check --fix

# Clean development artifacts
python dev_tools/cleanup.py
```

## 🔧 Configuration Overview

The tool requires minimal configuration to get started:

1. **Google Cloud Service Account** - For Sheets API access
2. **Selector Configuration** - CSS selectors for price extraction (`config/selectors.json`)
3. **Automation Settings** - Processing behavior (`config/settings.json`)

**Quick Configuration:**
PROCESS_START_ROW=0    # 0-based index
PROCESS_END_ROW=100    # 0-based index
```

```bash
# Place service account JSON in config/
cp your-service-account.json config/sheet-scraper-as.json

# Share Google Sheet with service account email
# (found in the JSON file)

# Customize selectors if needed
# Edit config/selectors.json for site-specific CSS selectors

# Adjust automation settings
# Edit config/settings.json for processing behavior
```

For detailed configuration, see the **[User Guide](docs/USER_GUIDE.md)**.

## 🎯 Key Capabilities

### Automation Features

- ✅ **Multi-Supplier Price Monitoring** - Amazon, Wayfair, Vevor, and more
- ✅ **Intelligent Price Comparison** - Automatic lowest price selection with tie-breaking
- ✅ **Stock Status Tracking** - Real-time availability monitoring across suppliers
- ✅ **Visual Status Indicators** - Color-coded formatting for price changes and inventory
- ✅ **Audit Trail Logging** - Complete history of all price updates and changes
- ✅ **Error Recovery** - Graceful handling of blocked sites and extraction failures

### Technical Features

- 🛡️ **Anti-Detection Technology** - Stealth browsing with advanced countermeasures
- 🔄 **Flexible Processing** - Configurable row ranges and batch operations
- 📊 **Google Sheets Integration** - Real-time updates with automatic formatting
- 🌐 **Web Interface** - Modern Flask UI with live progress tracking
- 🧪 **Comprehensive Testing** - 149 tests with extensive coverage
- 🔧 **Developer-Friendly** - Clean architecture with extensive documentation

## 🧪 Testing & Quality

```bash
# Run all tests (149 discovered)
python -m pytest tests/ -v

# Code quality check
ruff check --fix

# Type checking
mypy src/

# Security scan
bandit -r src/
```

**Test Coverage:** 96% across all modules with comprehensive integration testing.

## 🚀 Getting Help

- 📖 **Complete Documentation**: [User Guide](docs/USER_GUIDE.md) | [Developer Guide](docs/DEVELOPER_GUIDE.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/ClassicLean/sheet-scraper-automation/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ClassicLean/sheet-scraper-automation/discussions)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Developed with ❤️ for automated e-commerce price monitoring**
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

## 🔒 Security

This project follows security best practices for 2025:

- **Service Account Authentication**: Google Sheets API access via secure service accounts
- **Environment Variables**: Sensitive data stored in environment variables, not code
- **Input Validation**: All user inputs and web data are validated and sanitized
- **Rate Limiting**: Built-in protection against API abuse and blocking
- **Error Handling**: Secure error messages that don't expose internal information

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** PEP 8 coding standards
4. **Add** type hints to all new functions
5. **Write** tests for new functionality (minimum 90% coverage)
6. **Run** the test suite: `pytest tests/ -v`
7. **Commit** your changes (`git commit -m 'Add amazing feature'`)
8. **Push** to the branch (`git push origin feature/amazing-feature`)
9. **Open** a Pull Request

### Code Quality Standards

- **Type Hints**: All functions must include proper type annotations
- **Documentation**: Follow Google-style docstrings
- **Testing**: New features require comprehensive test coverage
- **Linting**: Code must pass `ruff check` without errors

## 📚 API Documentation

For detailed API documentation and advanced usage:

- [Automation API Reference](docs/automation_tool_documentation.md)
- [Row Range Functionality](docs/row_range_functionality.md)
- [Google Sheets Integration Guide](docs/sheets_integration.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Playwright**: For robust browser automation
- **Google Sheets API**: For seamless spreadsheet integration
- **pytest**: For comprehensive testing framework
- **ruff**: For modern Python linting
