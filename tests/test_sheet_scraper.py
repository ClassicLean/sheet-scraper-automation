import pytest
from unittest.mock import MagicMock, patch
from sheet_scraper.sheet_scraper import run_price_update_automation
from sheet_scraper.constants import (
    COLOR_RED,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COL_AG,
    COL_AB,
    COL_AE,
    COLOR_WHITE,
)

@pytest.fixture
def mock_sheets_service():
    with patch('sheet_scraper.sheet_scraper.get_service') as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Default mock data
        mock_data = {'valueRanges': [{'values': [
            # Header rows (skipped)
            ['VA Notes', 'Product ID', 'Price', 'Last stock check'],
            ['Header2', 'Header2', 'Header2', 'Header2'],
            ['Header3', 'Header3', 'Header3', 'Header3'],
            ['Header4', 'Header4', 'Header4', 'Header4'],
            # Product row (index 4, actual row 5)
            ['', 'Product1', '10.00', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '10.00', '', '', '', '', '', '', '', '', 'http://example.com/product1']
        ]}]}

        def set_sheet_data(data):
            mock_batch_get_execute = MagicMock()
            mock_batch_get_execute.return_value = data
            mock_values_method = MagicMock()
            mock_values_method.batchGet.return_value.execute = mock_batch_get_execute
            mock_spreadsheets_method = MagicMock()
            mock_spreadsheets_method.values.return_value = mock_values_method
            mock_service.spreadsheets.return_value = mock_spreadsheets_method

        mock_service.set_sheet_data = set_sheet_data
        set_sheet_data(mock_data)


        # Mock the batchUpdate chain: service.spreadsheets().batchUpdate().execute()
        mock_batch_update_execute = MagicMock()
        mock_batch_update_execute.return_value = None

        mock_batch_update_method = MagicMock()
        mock_batch_update_method.execute = mock_batch_update_execute

        mock_spreadsheets_method = mock_service.spreadsheets.return_value
        mock_spreadsheets_method.batchUpdate.return_value = mock_batch_update_method
        yield mock_service

def test_run_price_update_automation_va_notes_price_up(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    mock_data = {'valueRanges': [{'values': [
        ['VA Notes', 'Product ID', 'Price', 'Last stock check'],
        ['Header2', 'Header2', 'Header2', 'Header2'],
        ['Header3', 'Header3', 'Header3', 'Header3'],
        ['Header4', 'Header4', 'Header4', 'Header4'],
        ['', 'Product1', '10.00', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '10.00', '', '', '', '', '', '', '', '', 'http://example.com/product1']
    ]}]}
    mock_sheets_service.set_sheet_data(mock_data)

    # Mock scrape_product_details to return a successful result with a higher price
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details, \
         patch('os.environ.get', return_value='test_spreadsheet_id'):
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": 15.00, "in_stock": True, "error": ""}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768}
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = MagicMock(inner_text=lambda: "$15.00")
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page, MagicMock())

            # Assert that batchUpdate was called with the correct requests for VA Notes
            call_args = mock_sheets_service.spreadsheets.return_value.batchUpdate.call_args[1]
            requests = call_args['body']['requests']
            
            # Find the request that updates the VA Notes
            va_notes_update_request = None
            for req in requests:
                if 'updateCells' in req and req['updateCells']['range']['startColumnIndex'] == 0:
                    va_notes_update_request = req
                    break
            
            assert va_notes_update_request is not None
            assert va_notes_update_request['updateCells']['rows'][0]['values'][0]['userEnteredValue']['stringValue'] == 'Up'

def test_run_price_update_automation_va_notes_price_down(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    mock_data = {'valueRanges': [{'values': [
        ['VA Notes', 'Product ID', 'Price', 'Last stock check'],
        ['Header2', 'Header2', 'Header2', 'Header2'],
        ['Header3', 'Header3', 'Header3', 'Header3'],
        ['Header4', 'Header4', 'Header4', 'Header4'],
        ['', 'Product1', '10.00', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '10.00', '', '', '', '', '', '', '', '', 'http://example.com/product1']
    ]}]}
    mock_sheets_service.set_sheet_data(mock_data)

    # Mock scrape_product_details to return a successful result with a lower price
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details, \
         patch('os.environ.get', return_value='test_spreadsheet_id'):
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": 5.00, "in_stock": True, "error": ""}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768}
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = MagicMock(inner_text=lambda: "$5.00")
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page, MagicMock())

            # Assert that batchUpdate was called with the correct requests for VA Notes
            call_args = mock_sheets_service.spreadsheets.return_value.batchUpdate.call_args[1]
            requests = call_args['body']['requests']
            
            # Find the request that updates the VA Notes
            va_notes_update_request = None
            for req in requests:
                if 'updateCells' in req and req['updateCells']['range']['startColumnIndex'] == 0:
                    va_notes_update_request = req
                    break
            
            assert va_notes_update_request is not None
            assert va_notes_update_request['updateCells']['rows'][0]['values'][0]['userEnteredValue']['stringValue'] == 'Down'

def test_run_price_update_automation_va_notes_price_same(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    mock_data = {'valueRanges': [{'values': [
        ['VA Notes', 'Product ID', 'Price', 'Last stock check'],
        ['Header2', 'Header2', 'Header2', 'Header2'],
        ['Header3', 'Header3', 'Header3', 'Header3'],
        ['Header4', 'Header4', 'Header4', 'Header4'],
        ['', 'Product1', '10.00', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '10.00', '', '', '', '', '', '', '', '', 'http://example.com/product1']
    ]}]}
    mock_sheets_service.set_sheet_data(mock_data)

    # Mock scrape_product_details to return a successful result with the same price
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details, \
         patch('os.environ.get', return_value='test_spreadsheet_id'):
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": 10.00, "in_stock": True, "error": ""}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768}
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = MagicMock(inner_text=lambda: "$10.00")
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page, MagicMock())

            # Assert that batchUpdate was called, but VA notes was not updated
            call_args = mock_sheets_service.spreadsheets.return_value.batchUpdate.call_args[1]
            requests = call_args['body']['requests']
            
            # Find the request that updates the VA Notes
            va_notes_update_request = None
            for req in requests:
                if 'updateCells' in req and req['updateCells']['range']['startColumnIndex'] == 0:
                    va_notes_update_request = req
                    break
            
            assert va_notes_update_request is not None
            assert va_notes_update_request['updateCells']['rows'][0]['values'][0]['userEnteredValue']['stringValue'] == ''

def test_run_price_update_automation_out_of_stock_colors_row_red(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    mock_data = {'valueRanges': [{'values': [
        ['VA Notes', 'Product ID', 'Price', 'Last stock check'],
        ['Header2', 'Header2', 'Header2', 'Header2'],
        ['Header3', 'Header3', 'Header3', 'Header3'],
        ['Header4', 'Header4', 'Header4', 'Header4'],
        ['', 'Product1', '10.00', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '10.00', '', '', '', '', '', '', '', '', 'http://example.com/product1']
    ]}]}
    mock_sheets_service.set_sheet_data(mock_data)

    # Mock scrape_product_details to return an out of stock result
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details, \
         patch('os.environ.get', return_value='test_spreadsheet_id'):
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": None, "in_stock": False, "error": "Out of Stock"}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768}
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = None
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page, MagicMock())

            # Assert that batchUpdate was called with the correct requests for row coloring
            call_args = mock_sheets_service.spreadsheets.return_value.batchUpdate.call_args[1]
            requests = call_args['body']['requests']

            # Expected column colors (from sheet_scraper.py)
            # Assert that the first request is to color the entire row red
            assert requests[0]['repeatCell']['range']['startRowIndex'] == 4
            assert 'endColumnIndex' not in requests[0]['repeatCell']['range'] # Entire row, so no endColumnIndex
            assert requests[0]['repeatCell']['cell']['userEnteredFormat']['backgroundColor'] == COLOR_RED


def test_read_sheet_data(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details,         patch('os.environ.get', return_value='test_spreadsheet_id'):
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
            run_price_update_automation(mock_page, MagicMock())

            # Assert that batchGet was called with the correct parameters
            mock_sheets_service.spreadsheets.return_value.values.return_value.batchGet.assert_called_once_with(
                spreadsheetId='test_spreadsheet_id',
                ranges=['FBMP!A:AQ']
            )

def test_run_price_update_automation_colors_available_row_white(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    

    # Mock scrape_product_details to return a successful result
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details:
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
            run_price_update_automation(mock_page, MagicMock())

            # Assert that batchUpdate was called with the correct requests for column coloring
            mock_sheets_service.spreadsheets.return_value.batchUpdate.assert_called_once()
            call_args = mock_sheets_service.spreadsheets.return_value.batchUpdate.call_args[1]
            requests = call_args['body']['requests']

            # Expected column colors (from sheet_scraper.py)
            COLOR_WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}

            # Assert that the first request is to color the entire row white
            assert requests[0]['repeatCell']['range']['startRowIndex'] == 4
            assert 'endColumnIndex' not in requests[0]['repeatCell']['range'] # Entire row, so no endColumnIndex
            assert requests[0]['repeatCell']['cell']['userEnteredFormat']['backgroundColor'] == COLOR_WHITE

def test_run_price_update_automation_handles_infinity_price(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    mock_data = {'valueRanges': [{'values': [
        ['VA Notes', 'Product ID', 'Price', 'Last stock check'],
        ['Header2', 'Header2', 'Header2', 'Header2'],
        ['Header3', 'Header3', 'Header3', 'Header3'],
        ['Header4', 'Header4', 'Header4', 'Header4'],
        ['', 'Product1', '10.00', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '10.00', '', '', '', '', '', '', '', '', 'http://example.com/product1']
    ]}]}
    mock_sheets_service.set_sheet_data(mock_data)

    # Mock scrape_product_details to return float("inf") as the price
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details, \
         patch('os.environ.get', return_value='test_spreadsheet_id'):
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": float("inf"), "in_stock": False, "error": "Price not found"}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768}
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = None
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page, MagicMock())

            # Assert that batchUpdate was called with the correct requests for PRICE_COL
            call_args = mock_sheets_service.spreadsheets.return_value.batchUpdate.call_args[1]
            requests = call_args['body']['requests']
            
            # Find the request that updates the PRICE_COL
            price_update_request = None
            for req in requests:
                if 'updateCells' in req and req['updateCells']['range']['startColumnIndex'] == 23: # PRICE_COL is 23
                    price_update_request = req
                    break
            
            assert price_update_request is not None
            assert price_update_request['updateCells']['rows'][0]['values'][0]['userEnteredValue']['numberValue'] == 10.0

            # Find the request that updates the VA Notes
            va_notes_update_request = None
            for req in requests:
                if 'updateCells' in req and req['updateCells']['range']['startColumnIndex'] == 0: # VA_NOTES_COL is 0
                    va_notes_update_request = req
                    break
            
            assert va_notes_update_request is not None
            assert va_notes_update_request['updateCells']['rows'][0]['values'][0]['userEnteredValue']['stringValue'] == 'Price not found / Out of stock'

def test_run_price_update_automation_unavailable_item_coloring(mock_sheets_service):
    # Mock the sheet data to be read by run_price_update_automation
    mock_data = {'valueRanges': [{'values': [
        ['VA Notes', 'Product ID', 'Price', 'Last stock check'],
        ['Header2', 'Header2', 'Header2', 'Header2'],
        ['Header3', 'Header3', 'Header3', 'Header3'],
        ['Header4', 'Header4', 'Header4', 'Header4'],
        ['', 'Product1', '10.00', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '10.00', '', '', '', '', '', '', '', '', 'http://example.com/product1']
    ]}]}
    mock_sheets_service.set_sheet_data(mock_data)

    # Mock scrape_product_details to return an unavailable item
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details, \
         patch('os.environ.get', return_value='test_spreadsheet_id'):
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": None, "in_stock": False, "error": "Out of Stock"}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768}
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = None
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page, MagicMock())

            # Assert that batchUpdate was called with the correct requests for coloring
            call_args = mock_sheets_service.spreadsheets.return_value.batchUpdate.call_args[1]
            requests = call_args['body']['requests']

            # Helper to find a specific color request
            def find_color_request(req_list, col_index=None):
                for req in req_list:
                    if 'repeatCell' in req:
                        if col_index is None and 'startColumnIndex' not in req['repeatCell']['range']:
                            return req # Entire row request
                        elif col_index is not None and req['repeatCell']['range'].get('startColumnIndex') == col_index:
                            return req # Specific column request
                return None

            # Assert entire row coloring (red background, white text)
            entire_row_request = find_color_request(requests)
            assert entire_row_request is not None
            assert entire_row_request['repeatCell']['cell']['userEnteredFormat']['backgroundColor'] == COLOR_RED
            assert entire_row_request['repeatCell']['cell']['userEnteredFormat']['textFormat']['foregroundColor'] == COLOR_WHITE

            # Assert column AG coloring (black background, white text)
            col_ag_request = find_color_request(requests, COL_AG)
            assert col_ag_request is not None
            assert col_ag_request['repeatCell']['cell']['userEnteredFormat']['backgroundColor'] == COLOR_BLACK
            assert col_ag_request['repeatCell']['cell']['userEnteredFormat']['textFormat']['foregroundColor'] == COLOR_WHITE

            # Assert column AB coloring (blue background, white text)
            col_ab_request = find_color_request(requests, COL_AB)
            assert col_ab_request is not None
            assert col_ab_request['repeatCell']['cell']['userEnteredFormat']['backgroundColor'] == COLOR_BLUE
            assert col_ab_request['repeatCell']['cell']['userEnteredFormat']['textFormat']['foregroundColor'] == COLOR_WHITE

            # Assert column AE coloring (green background, black text)
            col_ae_request = find_color_request(requests, COL_AE)
            assert col_ae_request is not None
            assert col_ae_request['repeatCell']['cell']['userEnteredFormat']['backgroundColor'] == COLOR_GREEN
            assert col_ae_request['repeatCell']['cell']['userEnteredFormat']['textFormat']['foregroundColor'] == COLOR_BLACK

def test_log_status_reflects_price_found(mock_sheets_service):
    # Mock scrape_product_details to return an unavailable item
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details, \
         patch('os.environ.get', return_value='test_spreadsheet_id'), \
         patch('sheet_scraper.sheet_scraper.log_update') as mock_log_update, \
         patch('sheet_scraper.sheet_scraper.update_sheet', return_value=True): # Mock update_sheet to always succeed
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": None, "in_stock": False, "error": "Out of Stock"}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768}
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = None
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page, MagicMock())

            # Assert that log_update was called with "Failed" status and "Price not found / Out of stock" message
            mock_log_update.assert_called_once()
            args, kwargs = mock_log_update.call_args
            
            # Check the status and message arguments
            assert args[3] == "Failed" # Status
            assert args[4] == "Price not found / Out of stock" # Message

def test_log_update_includes_row_number(mock_sheets_service):
    # Mock scrape_product_details to return a successful item
    with patch('sheet_scraper.sheet_scraper.scrape_product_details') as mock_scrape_product_details, \
         patch('os.environ.get', return_value='test_spreadsheet_id'), \
         patch('sheet_scraper.sheet_scraper.log_update') as mock_log_update, \
         patch('sheet_scraper.sheet_scraper.update_sheet', return_value=True): # Mock update_sheet to always succeed
        with patch('time.sleep', return_value=None): # Mock time.sleep
            mock_scrape_product_details.return_value = {"price": 10.00, "in_stock": True, "error": ""}

            # Create a mock page object and mock its methods
            mock_page = MagicMock()
            mock_page.viewport_size = {'width': 1366, 'height': 768}
            mock_page.goto.return_value = None
            mock_page.evaluate.return_value = 1000
            mock_page.content.return_value = "mock page content"
            mock_page.query_selector.return_value = None
            mock_page.inner_text.return_value = "mock body text"
            mock_page.wait_for_selector.return_value = None
            mock_page.mouse.move.return_value = None

            # Run the automation
            run_price_update_automation(mock_page, MagicMock())

            # Assert that log_update was called with the correct row number
            mock_log_update.assert_called_once()
            args, kwargs = mock_log_update.call_args
            
            # Check the row_number argument (which is the last argument in the modified log_update)
            # The row_index in the loop starts from 4, so row_number should be 5 (4 + 1)
            assert kwargs['row_number'] == 5