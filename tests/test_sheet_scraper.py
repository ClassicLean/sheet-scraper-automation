import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from src.sheet_scraper import truncate_log_file, scrape_product_details, run_price_update_automation
from src.connect import get_service

# Test for truncate_log_file
@pytest.fixture
def setup_log_file(tmp_path):
    log_file = tmp_path / "test_log.txt"
    with open(log_file, "w") as f:
        for i in range(200):
            f.write(f"Line {i+1}\n")
    return log_file

def test_truncate_log_file(setup_log_file):
    log_file = setup_log_file
    truncate_log_file(str(log_file), max_lines=100)
    with open(log_file, "r") as f:
        lines = f.readlines()
    assert len(lines) == 100
    assert lines[0] == "Line 101\n"
    assert lines[-1] == "Line 200\n"

def test_truncate_log_file_less_than_max_lines(tmp_path):
    log_file = tmp_path / "test_log_small.txt"
    with open(log_file, "w") as f:
        for i in range(50):
            f.write(f"Line {i+1}\n")
    truncate_log_file(str(log_file), max_lines=100)
    with open(log_file, "r") as f:
        lines = f.readlines()
    assert len(lines) == 50

def test_truncate_log_file_non_existent(tmp_path):
    log_file = tmp_path / "non_existent.txt"
    # Should not raise an error
    truncate_log_file(str(log_file), max_lines=100)
    assert not log_file.exists()

@pytest.fixture
def mock_sheets_service():
    with patch('src.sheet_scraper.get_service') as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Mock the chain: service.spreadsheets().values().batchGet().execute()
        mock_batch_get_execute = MagicMock()
        mock_batch_get_execute.return_value = {'valueRanges': [{'values': [
            # Header rows (skipped)
            ['VA Notes', 'Product ID', 'Price', 'Last stock check'],
            ['Header2', 'Header2', 'Header2', 'Header2'],
            ['Header3', 'Header3', 'Header3', 'Header3'],
            ['Header4', 'Header4', 'Header4', 'Header4'],
            # Product row (index 4, actual row 5)
            ['', 'Product1', '10.00', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '10.00', '', '', '', '', '', '', '', 'http://example.com/product1']
        ]}]}

        mock_batch_get_method = MagicMock()
        mock_batch_get_method.execute = mock_batch_get_execute

        mock_values_method = MagicMock()
        mock_values_method.batchGet.return_value = mock_batch_get_method

        mock_spreadsheets_method = MagicMock()
        mock_spreadsheets_method.values.return_value = mock_values_method

        mock_service.spreadsheets.return_value = mock_spreadsheets_method

        # Mock the batchUpdate chain: service.spreadsheets().batchUpdate().execute()
        mock_batch_update_execute = MagicMock()
        mock_batch_update_execute.return_value = None

        mock_batch_update_method = MagicMock()
        mock_batch_update_method.execute = mock_batch_update_execute

        mock_spreadsheets_method.batchUpdate.return_value = mock_batch_update_method
        yield mock_service

# Tests for scrape_product_details
@pytest.fixture
def mock_page():
    mock = MagicMock()
    mock.content.return_value = """<html><body><span class=\"a-price-whole\">12</span><span class=\"a-price-fraction\">.99</span> in stock</body></html>"""
    mock.query_selector.return_value = MagicMock(inner_text=lambda: "$12.99")
    mock.inner_text.return_value = "some text for fallback"
    mock.wait_for_selector.return_value = None
    mock.goto.return_value = None
    return mock

def test_scrape_product_details_blocked(mock_page):
    mock_page.content.return_value = "robot or human activate and hold the button to confirm that you’re human. thank you"
    mock_page.goto.return_value = None # Simulate successful page load
    result = scrape_product_details("http://example.com", mock_page)
    assert result["price"] is None
    assert result["in_stock"] is False
    assert "Blocked" in result["error"]

def test_scrape_product_details_out_of_stock_404(mock_page):
    mock_page.content.return_value = "404 page not found the page you requested does not exist."
    mock_page.goto.return_value = None
    result = scrape_product_details("http://example.com/404", mock_page)
    assert result["price"] is None
    assert result["in_stock"] is False
    assert "Out of Stock" in result["error"]

def test_scrape_product_details_out_of_stock_unavailable(mock_page):
    mock_page.content.return_value = "currently unavailable. we don't know when or if this item will be back in stock."
    mock_page.goto.return_value = None
    result = scrape_product_details("http://example.com/unavailable", mock_page)
    assert result["price"] is None
    assert result["in_stock"] is False
    assert "Out of Stock" in result["error"]

def test_scrape_product_details_valid_price_and_in_stock(mock_page):
    mock_page.content.return_value = """<html><body><span class=\"a-price-whole\">12</span><span class=\"a-price-fraction\">.99</span> in stock</body></html>"""
    mock_page.query_selector.return_value = MagicMock(inner_text=lambda: "$12.99")
    mock_page.wait_for_selector.return_value = None
    mock_page.goto.return_value = None

    result = scrape_product_details("http://example.com/product", mock_page)
    assert result["price"] == 12.99
    assert result["in_stock"] is True
    assert result["error"] == ""

def test_scrape_product_details_no_price_but_in_stock(mock_page):
    mock_page.content.return_value = "in stock"
    mock_page.query_selector.return_value = None # No price selector found
    mock_page.inner_text.return_value = "" # Ensure inner_text("body") doesn't raise an error
    mock_page.wait_for_selector.side_effect = Exception("Simulated timeout") # Simulate price selector timeout
    mock_page.goto.return_value = None

    result = scrape_product_details("http://example.com/no-price", mock_page)
    assert result["price"] is None
    assert result["in_stock"] is False # Should be False if no price found and no clear positive indicator
    assert result["error"] == "Scraping error: Simulated timeout"

def test_run_price_update_automation_colors_available_row_white(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    

    # Mock scrape_product_details to return a successful result
    with patch('src.sheet_scraper.scrape_product_details') as mock_scrape_product_details:
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": 12.99, "in_stock": True, "error": ""}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768} # Mock viewport_size for mouse movements
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000 # Mock scrollHeight
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = MagicMock(inner_text=lambda: "$12.99")
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page)

            # Assert that batchUpdate was called with the correct request for white background
            mock_sheets_service.spreadsheets.return_value.batchUpdate.assert_called_once()
            call_args = mock_sheets_service.spreadsheets.return_value.batchUpdate.call_args[1]
            requests = call_args['body']['requests']

            # Find the repeatCell request for coloring
            color_request = None
            for req in requests:
                if 'repeatCell' in req:
                    color_request = req
                    break

            assert color_request is not None, "RepeatCell request for coloring not found"
            assert color_request['repeatCell']['cell']['userEnteredFormat']['backgroundColor'] == {'red': 1.0, 'green': 1.0, 'blue': 1.0}
            assert color_request['repeatCell']['cell']['userEnteredFormat']['textFormat']['foregroundColor'] == {'red': 0.0, 'green': 0.0, 'blue': 0.0}