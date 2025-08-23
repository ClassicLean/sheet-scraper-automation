import sys
import os

# Add the parent directory of 'src' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    pass # No specific import to check here, just testing path setup
except ImportError as e:
    print(f"ImportError: {e}")
    print(f"sys.path: {sys.path}")