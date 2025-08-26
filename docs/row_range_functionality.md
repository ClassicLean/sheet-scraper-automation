# Row Range Functionality Documentation

## Overview

The Enhanced Sheet Scraper now supports specifying custom row ranges for processing, making it more flexible and efficient for testing and production use.

## Features

### Command-Line Arguments

The script now accepts the following command-line arguments:

- `--start-row N`: Starting row number (1-based, as shown in Google Sheets)
- `--end-row N`: Ending row number (1-based, inclusive)

### Usage Examples

```bash
# Default behavior (process row 66 only)
python -m src.sheet_scraper.sheet_scraper

# Process from row 1 to default end (row 66)
python -m src.sheet_scraper.sheet_scraper --start-row 1

# Process from default start to row 5
python -m src.sheet_scraper.sheet_scraper --end-row 5

# Process rows 1 through 10
python -m src.sheet_scraper.sheet_scraper --start-row 1 --end-row 10

# Process a specific range for testing
python -m src.sheet_scraper.sheet_scraper --start-row 65 --end-row 70
```

### Help Information

To see all available options:

```bash
python -m src.sheet_scraper.sheet_scraper --help
```

## Implementation Details

### Priority System

The row range is determined using the following priority:

1. **Command-line arguments** (highest priority)
2. **Environment variables** (`PROCESS_START_ROW`, `PROCESS_END_ROW`)
3. **Default values** (row 66, index 65)

### Row Number Conversion

- **User input**: 1-based row numbers (as displayed in Google Sheets)
- **Internal processing**: 0-based indices (for Python list slicing)
- **Automatic conversion**: The script handles the conversion transparently

### Backward Compatibility

The new functionality maintains full backward compatibility:

- Existing environment variable configuration continues to work
- Default behavior remains unchanged (processes row 66)
- No breaking changes to existing scripts or workflows

## Function Signature Changes

### `run_price_update_automation`

```python
def run_price_update_automation(
    page,
    captcha_solver,
    config: Config = None,
    browser_manager = None,
    start_row: int = None,
    end_row: int = None
) -> None:
```

**New Parameters:**
- `start_row`: Starting row index (0-based, optional)
- `end_row`: Ending row index (0-based, optional)

### `parse_arguments`

```python
def parse_arguments():
    """
    Parse command-line arguments for row range specification.

    Returns:
        argparse.Namespace: Parsed arguments containing start_row and end_row
    """
```

## Error Handling

- Invalid row numbers are handled by argparse with appropriate error messages
- Row ranges that exceed sheet bounds are processed without errors (empty ranges are handled gracefully)
- Missing or None parameters fall back to environment variables or defaults

## Testing

The functionality includes comprehensive tests:

- Argument parsing with various combinations
- Row range parameter passing
- Environment variable fallback behavior
- Command-line argument priority over environment variables

## Benefits

1. **Flexible Testing**: Easily test specific rows or ranges
2. **Efficient Processing**: Process only the rows you need
3. **Batch Operations**: Run large ranges for bulk updates
4. **Development Workflow**: Quick iteration on specific products
5. **Production Control**: Fine-tune processing scope for performance

## Migration Guide

### From Environment Variables

**Before:**
```bash
set PROCESS_START_ROW=5
set PROCESS_END_ROW=10
python -m src.sheet_scraper.sheet_scraper
```

**After:**
```bash
python -m src.sheet_scraper.sheet_scraper --start-row 6 --end-row 10
```

Note: Row numbers are now 1-based instead of 0-based indices.

### From Default Behavior

**Before:**
```bash
python -m src.sheet_scraper.sheet_scraper
# Always processed row 66
```

**After:**
```bash
# Same default behavior
python -m src.sheet_scraper.sheet_scraper

# Or explicitly specify
python -m src.sheet_scraper.sheet_scraper --start-row 66 --end-row 66
```

## Best Practices

1. **Start Small**: Test with a single row first (`--start-row 66 --end-row 66`)
2. **Use Ranges**: Process multiple rows efficiently (`--start-row 1 --end-row 50`)
3. **Verify Data**: Check your sheet to ensure the row range contains valid product data
4. **Monitor Output**: Watch the console output to confirm the correct rows are being processed
5. **Test Mode**: Use small ranges during development and testing

## Example Workflows

### Development Testing
```bash
# Test a specific product
python -m src.sheet_scraper.sheet_scraper --start-row 5 --end-row 5

# Test a small range
python -m src.sheet_scraper.sheet_scraper --start-row 65 --end-row 70
```

### Production Processing
```bash
# Process first 100 products
python -m src.sheet_scraper.sheet_scraper --start-row 1 --end-row 100

# Process a daily batch
python -m src.sheet_scraper.sheet_scraper --start-row 1 --end-row 500
```

### Error Recovery
```bash
# Resume from where processing failed
python -m src.sheet_scraper.sheet_scraper --start-row 250 --end-row 500
```
