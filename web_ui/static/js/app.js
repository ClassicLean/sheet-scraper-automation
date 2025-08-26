/**
 * Sheet Scraper Web UI JavaScript
 * Handles form submission, script control, and real-time updates
 * Updated: August 2025 with enhanced spinner functionality
 */

// Global variables for interval management
let statusUpdateInterval;
let logsUpdateInterval;

/**
 * Initialize event handlers when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function () {
    // Form submission handler
    document.getElementById('scraperForm').addEventListener('submit', function (e) {
        e.preventDefault();
        startScript();
    });

    // Stop button handler
    document.getElementById('stopBtn').addEventListener('click', stopScript);

    // Initial status check
    updateStatus();
});

/**
 * Start the scraping script with optional row range parameters
 */
function startScript() {
    const startRow = document.getElementById('startRow').value;
    const endRow = document.getElementById('endRow').value;
    const showBrowser = document.getElementById('showBrowser').checked;

    // Validation: ensure start row is not greater than end row
    if (startRow && endRow && parseInt(startRow) > parseInt(endRow)) {
        alert('Start row cannot be greater than end row');
        return;
    }

    // Prepare request data
    const data = {};
    if (startRow) data.start_row = parseInt(startRow);
    if (endRow) data.end_row = parseInt(endRow);
    data.show_browser = showBrowser;

    // Send start request to server
    fetch('/start_script', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI for running state
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;

                // Start periodic updates
                startStatusUpdates();
                startLogsUpdates();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error starting script');
        });
}

/**
 * Stop the currently running script
 */
function stopScript() {
    fetch('/stop_script', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Status updates will handle the UI changes
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error stopping script');
        });
}

/**
 * Start periodic status updates
 */
function startStatusUpdates() {
    statusUpdateInterval = setInterval(updateStatus, 1000);
}

/**
 * Start periodic logs updates
 */
function startLogsUpdates() {
    logsUpdateInterval = setInterval(updateLogs, 2000);
}

/**
 * Update the status display and UI elements
 */
function updateStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            // Get UI elements
            const loadingContainer = document.getElementById('loadingContainer');
            const loadingText = document.getElementById('loadingText');
            const statusMessage = document.getElementById('statusMessage');
            const statusIndicator = document.getElementById('statusIndicator');

            // Handle loading spinner animation
            if (data.running) {
                loadingContainer.classList.add('show');
                loadingText.textContent = 'Processing...';
            } else {
                loadingContainer.classList.remove('show');
                if (data.message.includes('Error') || data.message.includes('Failed')) {
                    loadingText.textContent = 'Error';
                } else if (data.message.includes('completed') || data.message.includes('finished')) {
                    loadingText.textContent = 'Complete';
                } else {
                    loadingText.textContent = 'Ready';
                }
            }

            // Update status message
            statusMessage.textContent = data.message;

            // Update status indicator color
            statusIndicator.className = 'status-indicator';
            if (data.running) {
                statusIndicator.classList.add('running');
            } else if (data.message.includes('Error') || data.message.includes('Failed')) {
                statusIndicator.classList.add('error');
            }

            // Update button states
            if (!data.running) {
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;

                // Hide loading spinner after delay when not running
                if (!data.running) {
                    setTimeout(() => {
                        loadingContainer.classList.remove('show');
                    }, 2000); // Wait 2 seconds before hiding
                }

                // Stop periodic updates
                if (statusUpdateInterval) {
                    clearInterval(statusUpdateInterval);
                }
                if (logsUpdateInterval) {
                    clearInterval(logsUpdateInterval);
                }
            }
        })
        .catch(error => console.error('Error updating status:', error));
}

/**
 * Update the logs display with latest script output
 */
function updateLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            const logsContent = document.getElementById('logsContent');
            logsContent.innerHTML = '';

            // Add each log entry
            data.logs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                logEntry.textContent = log;
                logsContent.appendChild(logEntry);
            });

            // Auto-scroll to bottom to show latest logs
            logsContent.scrollTop = logsContent.scrollHeight;
        })
        .catch(error => console.error('Error updating logs:', error));
}

/**
 * Clear the logs display
 */
function clearLogs() {
    const logsContent = document.getElementById('logsContent');
    logsContent.innerHTML = '<div class="log-entry">Logs cleared...</div>';
}
