import sys
import os

# Add the parent directory of 'src' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from sheet_scraper import truncate_log_file
    print("Successfully imported truncate_log_file from src.sheet_scraper")
except ImportError as e:
    print(f"ImportError: {e}")
    print(f"sys.path: {sys.path}")