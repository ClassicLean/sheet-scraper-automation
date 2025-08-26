#!/usr/bin/env python3
"""
Startup script for Sheet Scraper Web UI
"""

import os
import subprocess
import sys
import time
import webbrowser


def check_flask_installed():
    """Check if Flask is installed."""
    try:
        import flask  # noqa: F401
        return True
    except ImportError:
        return False

def install_flask():
    """Install Flask if not already installed."""
    print("Flask not found. Installing Flask...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask>=2.3.0'])
        print("Flask installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install Flask. Please install it manually:")
        print("pip install flask>=2.3.0")
        return False

def main():
    """Main startup function."""
    print("=" * 60)
    print("      SHEET SCRAPER WEB UI")
    print("=" * 60)

    # Check and install Flask if needed
    if not check_flask_installed():
        if not install_flask():
            sys.exit(1)

    # Change to web_ui directory
    web_ui_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_ui_dir)

    # Import and configure Flask app
    from app import app

    # Force template reloading and disable caching
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['DEBUG'] = True

    # Additional cache-busting measures
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}

    # Get template directory for monitoring
    template_dir = os.path.join(web_ui_dir, 'templates')
    template_files = []
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))

    print(f"Starting web server from: {web_ui_dir}")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)

    # Start the Flask app
    try:
        # Give a moment for the message to be displayed
        time.sleep(1)

        # Open browser automatically only once (not during reloader restart)
        # Check if this is the main process, not the reloader subprocess
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            def open_browser():
                time.sleep(1.5)  # Wait a bit for server to start
                webbrowser.open('http://localhost:5000')

            import threading
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()

        # Import and run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True, extra_files=template_files)

    except KeyboardInterrupt:
        print("\nShutting down web server...")
    except Exception as e:
        print(f"Error starting web server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
