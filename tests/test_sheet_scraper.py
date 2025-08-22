import pytest
from unittest.mock import MagicMock, patch
from src.sheet_scraper import truncate_log_file, scrape_product_details

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

# Tests for scrape_product_details
@pytest.fixture
def mock_page():
    return MagicMock()

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
    mock_page.content.return_value = "<span class=\"a-price-whole\">12</span><span class=\"a-price-fraction\">.99</span> in stock"
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


