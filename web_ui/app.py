#!/usr/bin/env python3
"""
Web UI for Sheet Scraper - Simple interface for row range specification and script execution
"""

import os
import sys
import threading
import time
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

app = Flask(__name__)

# Comprehensive cache-busting configuration
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['DEBUG'] = True

# Force Jinja2 cache clearing
app.jinja_env.auto_reload = True
app.jinja_env.cache = {}

# Additional template debugging
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

# Disable caching for development
@app.before_request
def before_request():
    """Clear template cache before each request to ensure fresh templates."""
    app.jinja_env.cache = {}

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    return response

# Global variables for tracking script execution
script_status = {
    'running': False,
    'progress': 0,
    'message': 'Ready',
    'log_messages': [],
    'start_time': None,
    'current_row': None,
    'total_rows': None
}

# Global variable to store the running process
current_process = None

@app.route('/')
def index():
    """Main page with the UI interface."""
    # Add timestamp for cache busting
    import time
    cache_buster = str(int(time.time()))
    return render_template('index.html', cache_buster=cache_buster)

@app.route('/start_script', methods=['POST'])
def start_script():
    """Start the sheet scraper script with specified row range."""
    global script_status

    if script_status['running']:
        return jsonify({'error': 'Script is already running'}), 400

    data = request.get_json()
    start_row = data.get('start_row')
    end_row = data.get('end_row')
    show_browser = data.get('show_browser', False)

    # Validate input
    try:
        if start_row:
            start_row = int(start_row)
            if start_row < 1:
                return jsonify({'error': 'Start row must be greater than 0'}), 400

        if end_row:
            end_row = int(end_row)
            if end_row < 1:
                return jsonify({'error': 'End row must be greater than 0'}), 400

        if start_row and end_row and start_row > end_row:
            return jsonify({'error': 'Start row cannot be greater than end row'}), 400

    except ValueError:
        return jsonify({'error': 'Row numbers must be valid integers'}), 400

    # Reset status
    script_status.update({
        'running': True,
        'progress': 0,
        'message': 'Starting script...',
        'log_messages': [],
        'start_time': datetime.now(),
        'current_row': None,
        'total_rows': None
    })

    # Start script in background thread
    thread = threading.Thread(target=run_scraper_script, args=(start_row, end_row, show_browser))
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': 'Script started successfully'})

@app.route('/status')
def get_status():
    """Get current script execution status."""
    return jsonify(script_status)

@app.route('/stop_script', methods=['POST'])
def stop_script():
    """Stop the running script and close the browser."""
    global script_status, current_process

    if not script_status['running']:
        return jsonify({'error': 'No script is currently running'}), 400

    try:
        # Terminate the subprocess if it exists
        if current_process and current_process.poll() is None:  # Process is still running
            script_status['log_messages'].append('Terminating script process...')
            current_process.terminate()

            # Give the process a moment to terminate gracefully
            try:
                current_process.wait(timeout=5)
                script_status['log_messages'].append('Script process terminated successfully')
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                script_status['log_messages'].append('Force killing script process...')
                current_process.kill()
                current_process.wait()
                script_status['log_messages'].append('Script process force killed')

        # Update status
        script_status.update({
            'running': False,
            'progress': 100,
            'message': 'Script stopped by user - browser should close automatically',
        })

        return jsonify({'success': True, 'message': 'Script stopped and browser closed'})

    except Exception as e:
        script_status['log_messages'].append(f'Error stopping script: {str(e)}')
        script_status.update({
            'running': False,
            'message': f'Error stopping script: {str(e)}',
        })
        return jsonify({'error': f'Error stopping script: {str(e)}'}), 500

def run_scraper_script(start_row, end_row, show_browser=False):
    """Run the sheet scraper script in a subprocess."""
    global script_status, current_process

    try:
        # Build command using standard Python module execution
        project_dir = os.path.dirname(os.path.dirname(__file__))

        cmd = [sys.executable, '-m', 'src.sheet_scraper']

        if start_row:
            cmd.extend(['--start-row', str(start_row)])
        if end_row:
            cmd.extend(['--end-row', str(end_row)])

        # Set up environment for browser visibility
        env = os.environ.copy()
        if show_browser:
            env['HEADFUL_BROWSER'] = 'true'

        # Enable debug mode for enhanced Column X debugging
        env['DEBUG_MODE'] = 'true'

        script_status['message'] = f'Running script with rows {start_row or "default"} to {end_row or "default"}'
        script_status['log_messages'].append(f'Command: {" ".join(cmd)}')
        if show_browser:
            script_status['log_messages'].append('Browser visibility: ENABLED')
        else:
            script_status['log_messages'].append('Browser visibility: DISABLED (headless mode)')

        script_status['log_messages'].append(f'Working directory: {project_dir}')
        script_status['log_messages'].append('Using standard Python module execution: python -m src.sheet_scraper')

        # Run the script
        current_process = subprocess.Popen(
            cmd,
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env
        )

        # Monitor progress
        total_rows = (end_row - start_row + 1) if (start_row and end_row) else 1
        script_status['total_rows'] = total_rows
        current_processed = 0

        # Read output line by line
        for line in iter(current_process.stdout.readline, ''):
            if not script_status['running']:
                script_status['log_messages'].append('Stop signal received, terminating process...')
                current_process.terminate()
                break

            line = line.strip()
            if line:
                script_status['log_messages'].append(line)                # Try to extract progress information from output
                if 'Processing rows' in line:
                    script_status['message'] = line
                elif 'Row_' in line or 'Processing' in line:
                    current_processed += 1
                    script_status['current_row'] = current_processed
                    progress = min(100, (current_processed / total_rows) * 100)
                    script_status['progress'] = round(progress, 1)
                    script_status['message'] = f'Processing row {current_processed} of {total_rows}'
                elif 'Script run finished' in line:
                    script_status['progress'] = 100
                    script_status['message'] = 'Script completed successfully'
                elif 'Enhanced Playwright browser closed' in line:
                    script_status['log_messages'].append('Browser closed successfully')
                elif 'COLUMN X DEBUG' in line:
                    script_status['message'] = 'Column X Update - See logs for details'
                elif 'PRICE EXTRACTION DEBUG' in line:
                    script_status['message'] = 'Price Extraction - See logs for details'
                elif 'SHEET OPERATION DEBUG' in line:
                    script_status['message'] = 'Sheet Operation - See logs for details'
                elif 'Error' in line or 'Failed' in line:
                    script_status['message'] = f'Error: {line}'

        # Wait for process to complete
        return_code = current_process.wait()

        if return_code == 0:
            script_status['progress'] = 100
            script_status['message'] = 'Script completed successfully'
        elif return_code == -15:  # SIGTERM
            script_status['message'] = 'Script terminated by user'
        else:
            script_status['message'] = f'Script finished with errors (exit code: {return_code})'

    except Exception as e:
        script_status['message'] = f'Error running script: {str(e)}'
        script_status['log_messages'].append(f'Exception: {str(e)}')

    finally:
        script_status['running'] = False
        current_process = None

@app.route('/logs')
def get_logs():
    """Get recent log messages."""
    return jsonify({
        'logs': script_status['log_messages'][-100:],  # Return last 100 log messages
        'running': script_status['running']
    })

if __name__ == '__main__':
    print("Starting Sheet Scraper Web UI...")
    print("Open your browser to http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
