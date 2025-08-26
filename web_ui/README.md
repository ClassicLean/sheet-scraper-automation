# Sheet Scraper Web UI

A simple and intuitive web interface for the Enhanced Sheet Scraper, allowing users to specify row ranges and monitor script execution through a modern web browser interface.

## Features

- **🎯 Row Range Specification**: Easy input fields for start and end rows
- **▶️ One-Click Execution**: Start the scraper script with a single button click
- **�️ Browser Visibility Control**: Toggle between headless and headful browser modes
- **�📊 Real-Time Progress**: Live progress bar showing current processing status
- **📝 Live Logs**: Real-time display of script output and execution logs
- **🛑 Script Control**: Stop running scripts if needed
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🎨 Modern UI**: Clean, professional interface with smooth animations

## Quick Start

### Option 1: Windows Batch File (Easiest)
1. Double-click `start_ui.bat` in the `web_ui` folder
2. The web interface will open automatically in your browser
3. If it doesn't open automatically, go to `http://localhost:5000`

### Option 2: Python Script
1. Open terminal/command prompt in the `web_ui` folder
2. Run: `python start_ui.py`
3. Open your browser to `http://localhost:5000`

### Option 3: Manual Flask Execution
1. Install Flask: `pip install flask>=2.3.0`
2. Navigate to the `web_ui` folder
3. Run: `python app.py`
4. Open your browser to `http://localhost:5000`

## Usage Guide

### Starting the Script

1. **Access the Web Interface**: Open `http://localhost:5000` in your browser
2. **Specify Row Range** (optional):
   - **Start Row**: Enter the first row to process (1-based numbering)
   - **End Row**: Enter the last row to process (1-based numbering)
   - Leave fields empty to use default settings
3. **Click "Start Scraping"**: Begin script execution
4. **Monitor Progress**: Watch the real-time progress bar and logs

### Row Range Examples

| Start Row | End Row | Result |
|-----------|---------|--------|
| (empty) | (empty) | Default behavior (row 66) |
| 1 | 10 | Process rows 1 through 10 |
| 5 | (empty) | Process from row 5 to default end |
| (empty) | 20 | Process from default start to row 20 |
| 66 | 66 | Process only row 66 |

### Monitoring Execution

- **Status Indicator**:
  - 🟢 Green: Ready/Completed
  - 🟡 Yellow: Running
  - 🔴 Red: Error occurred

- **Progress Bar**: Shows percentage completion of current operation

- **Live Logs**: Real-time output from the scraper script

- **Control Buttons**:
  - **Start Scraping**: Begin script execution (disabled when running)
  - **Stop Script**: Terminate running script (enabled when running)

## Technical Details

### Architecture

- **Backend**: Flask web server (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Communication**: RESTful API with JSON responses
- **Process Management**: Subprocess execution with real-time monitoring

### API Endpoints

- `GET /`: Main web interface
- `POST /start_script`: Start scraper with row range parameters
- `GET /status`: Get current execution status and progress
- `POST /stop_script`: Stop running script
- `GET /logs`: Retrieve recent log messages

### File Structure

```
web_ui/
├── app.py                 # Flask application (main backend)
├── start_ui.py           # Startup script with auto-installation
├── start_ui.bat          # Windows batch launcher
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main web interface
└── static/               # (Reserved for additional assets)
```

## Configuration

### Port Configuration
Default port is `5000`. To change:
1. Edit `app.py`, line: `app.run(debug=False, host='0.0.0.0', port=5000)`
2. Change `5000` to your desired port
3. Restart the web UI

### Host Configuration
Default accepts connections from any IP (`0.0.0.0`). For localhost only:
1. Edit `app.py`, change `host='0.0.0.0'` to `host='127.0.0.1'`
2. Restart the web UI

## Troubleshooting

### Common Issues

**1. "Flask not found" Error**
- Solution: Install Flask with `pip install flask>=2.3.0`
- Or use the startup script which auto-installs dependencies

**2. "Port already in use" Error**
- Solution: Change the port in `app.py` or stop other services using port 5000
- Common culprits: Other development servers, AirPlay (macOS)

**3. Script doesn't start**
- Check that the main `sheet_scraper.py` exists in the correct location
- Verify Python path and project structure
- Check logs for detailed error messages

**4. Progress bar doesn't update**
- This is normal for very short-running scripts
- Progress tracking works best with larger row ranges

**5. Browser doesn't open automatically**
- Manually navigate to `http://localhost:5000`
- Check firewall settings if accessing from another device

**6. Browser window doesn't appear when "Show Browser Window" is checked**
- Ensure you have a compatible browser installed (Chrome/Chromium)
- Check that Playwright browsers are installed: `playwright install chromium`
- Verify the option is checked before clicking "Start Scraping"

### Performance Notes

- **Memory Usage**: Logs are limited to the last 100 entries to prevent memory buildup
- **Refresh Rate**: Status updates every 1 second, logs every 2 seconds
- **Browser Compatibility**: Tested with Chrome, Firefox, Safari, Edge (modern versions)

## Security Considerations

- **Local Network Only**: Web UI is designed for local/development use
- **No Authentication**: No login system (suitable for single-user local development)
- **Process Control**: Limited ability to forcefully terminate subprocess

## Development

### Adding Features

1. **Backend Changes**: Modify `app.py` for new API endpoints
2. **Frontend Changes**: Edit `templates/index.html` for UI updates
3. **Styling**: CSS is embedded in the HTML file for simplicity

### Testing

1. Start the web UI: `python start_ui.py`
2. Test with different row ranges
3. Monitor console output for any errors
4. Check browser developer tools for frontend issues

## Integration with Main Project

The web UI is designed as a standalone component that:
- ✅ Calls the existing command-line interface
- ✅ Maintains full compatibility with all existing features
- ✅ Requires no changes to the main scraper code
- ✅ Works with all existing configurations and environment variables

## Future Enhancements

Potential improvements for future versions:
- 📋 Configuration file editing through web interface
- 📈 Historical execution reports and analytics
- 🔐 Optional authentication system
- 💾 Job scheduling and automation
- 📊 Advanced progress tracking with row-level details
- 🌐 Multi-user support with session management

---

**Note**: This web UI is a convenience tool for easier interaction with the Sheet Scraper. All core functionality remains available through the command-line interface.
