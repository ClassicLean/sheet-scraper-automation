"""
Automation Logging Module

This module provides centralized logging functionality for the automation system.
It handles log formatting, file management, error tracking, and performance monitoring.

Best Practices Implemented:
- Centralized Logging: Single point for all logging operations
- Log Levels: Support for different log levels and filtering
- Error Tracking: Dedicated error logging and aggregation
- Performance Monitoring: Timing and metrics tracking
- File Management: Automatic log rotation and cleanup
"""

import json
import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from ..scraping_utils import debug_print


@dataclass
class PerformanceMetrics:
    """Track performance metrics for automation operations."""
    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    duration: float | None = None
    success: bool = False
    error_message: str | None = None

    def finish(self, success: bool = True, error_message: str | None = None):
        """Mark the operation as finished."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message


@dataclass
class LogSummary:
    """Summary of logging activity."""
    total_entries: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    debug_count: int = 0
    recent_errors: list[str] = field(default_factory=list)
    performance_metrics: list[PerformanceMetrics] = field(default_factory=list)


class AutomationLogger:
    """Centralized logging system for automation operations."""

    def __init__(self, log_dir: str = "logs", max_log_size: int = 10*1024*1024, backup_count: int = 5):
        """
        Initialize the automation logger.

        Args:
            log_dir: Directory to store log files
            max_log_size: Maximum size per log file in bytes
            backup_count: Number of backup log files to keep
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.max_log_size = max_log_size
        self.backup_count = backup_count

        # Initialize logging components
        self.summary = LogSummary()
        self.active_metrics: dict[str, PerformanceMetrics] = {}

        # Setup loggers
        self._setup_loggers()

    def _setup_loggers(self):
        """Setup different loggers for different purposes."""

        # Main automation logger
        self.main_logger = logging.getLogger('automation')
        self.main_logger.setLevel(logging.DEBUG)

        # Error logger
        self.error_logger = logging.getLogger('automation.errors')
        self.error_logger.setLevel(logging.ERROR)

        # Performance logger
        self.perf_logger = logging.getLogger('automation.performance')
        self.perf_logger.setLevel(logging.INFO)

        # Clear any existing handlers
        for logger in [self.main_logger, self.error_logger, self.perf_logger]:
            logger.handlers.clear()

        # Setup file handlers
        self._setup_file_handlers()

        # Setup console handler if needed
        self._setup_console_handler()

    def _setup_file_handlers(self):
        """Setup rotating file handlers for different log types."""

        # Main log file handler
        main_handler = RotatingFileHandler(
            self.log_dir / "automation.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        main_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        main_handler.setFormatter(main_formatter)
        self.main_logger.addHandler(main_handler)

        # Error log file handler
        error_handler = RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n'
        )
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)

        # Performance log file handler
        perf_handler = RotatingFileHandler(
            self.log_dir / "performance.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        perf_formatter = logging.Formatter(
            '%(asctime)s - PERF - %(message)s'
        )
        perf_handler.setFormatter(perf_formatter)
        self.perf_logger.addHandler(perf_handler)

    def _setup_console_handler(self):
        """Setup console handler for important messages."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.main_logger.addHandler(console_handler)

    def info(self, message: str, **kwargs):
        """Log an info message."""
        self.main_logger.info(message, **kwargs)
        self.summary.info_count += 1
        self.summary.total_entries += 1
        debug_print(f"INFO: {message}")

    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self.main_logger.warning(message, **kwargs)
        self.summary.warning_count += 1
        self.summary.total_entries += 1
        debug_print(f"WARNING: {message}")

    def error(self, message: str, exception: Exception | None = None, **kwargs):
        """Log an error message with optional exception details."""
        error_details = message

        if exception:
            error_details += f"\nException: {str(exception)}"
            error_details += f"\nTraceback: {traceback.format_exc()}"

        self.main_logger.error(message, **kwargs)
        self.error_logger.error(error_details, **kwargs)

        self.summary.error_count += 1
        self.summary.total_entries += 1
        self.summary.recent_errors.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")

        # Keep only last 10 errors
        if len(self.summary.recent_errors) > 10:
            self.summary.recent_errors = self.summary.recent_errors[-10:]

        debug_print(f"ERROR: {message}")

    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self.main_logger.debug(message, **kwargs)
        self.summary.debug_count += 1
        self.summary.total_entries += 1

    def start_operation(self, operation_name: str) -> str:
        """
        Start tracking a timed operation.

        Args:
            operation_name: Name of the operation to track

        Returns:
            Operation ID for referencing the operation
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        metrics = PerformanceMetrics(operation_name)
        self.active_metrics[operation_id] = metrics

        self.info(f"Started operation: {operation_name}")
        return operation_id

    def end_operation(self, operation_id: str, success: bool = True,
                     error_message: str | None = None):
        """
        End tracking of a timed operation.

        Args:
            operation_id: ID of the operation to end
            success: Whether the operation was successful
            error_message: Error message if operation failed
        """
        if operation_id not in self.active_metrics:
            self.warning(f"Unknown operation ID: {operation_id}")
            return

        metrics = self.active_metrics.pop(operation_id)
        metrics.finish(success, error_message)

        # Log performance
        status = "SUCCESS" if success else "FAILED"
        perf_message = f"{metrics.operation_name} - {status} - Duration: {metrics.duration:.2f}s"

        if error_message:
            perf_message += f" - Error: {error_message}"

        self.perf_logger.info(perf_message)
        self.summary.performance_metrics.append(metrics)

        # Log to main logger
        if success:
            self.info(f"Completed operation: {metrics.operation_name} in {metrics.duration:.2f}s")
        else:
            error_msg = f"Failed operation: {metrics.operation_name} after {metrics.duration:.2f}s"
            if error_message:
                error_msg += f" - Error: {error_message}"
            self.error(error_msg)

    def log_price_update(self, product_name: str, old_price: str | None,
                        new_price: str | None, row_number: int):
        """
        Log a price update operation.

        Args:
            product_name: Name of the product
            old_price: Previous price
            new_price: New price
            row_number: Row number in the sheet
        """
        message = f"Price update - Row {row_number}: {product_name}"

        if old_price and new_price:
            message += f" - {old_price} -> {new_price}"
        elif new_price:
            message += f" - New price: {new_price}"
        else:
            message += " - No price found"

        self.info(message)

    def log_scraping_result(self, url: str, success: bool, price: str | None = None,
                          error: str | None = None):
        """
        Log the result of a web scraping operation.

        Args:
            url: URL that was scraped
            success: Whether scraping was successful
            price: Extracted price if successful
            error: Error message if failed
        """
        if success and price:
            self.info(f"Scraping SUCCESS: {url} - Price: {price}")
        elif success:
            self.warning(f"Scraping PARTIAL: {url} - No price found")
        else:
            self.error(f"Scraping FAILED: {url} - {error or 'Unknown error'}")

    def log_batch_summary(self, total_items: int, successful: int, failed: int,
                         duration: float):
        """
        Log a summary of batch processing.

        Args:
            total_items: Total number of items processed
            successful: Number of successful operations
            failed: Number of failed operations
            duration: Total duration in seconds
        """
        success_rate = (successful / total_items * 100) if total_items > 0 else 0

        summary_message = (
            f"Batch Summary - Total: {total_items}, "
            f"Success: {successful}, Failed: {failed}, "
            f"Success Rate: {success_rate:.1f}%, "
            f"Duration: {duration:.2f}s"
        )

        self.info(summary_message)

    def export_logs_summary(self, output_file: str | None = None) -> dict[str, Any]:
        """
        Export a summary of logging activity.

        Args:
            output_file: Optional file to save the summary

        Returns:
            Dictionary containing log summary
        """
        summary_data = {
            'timestamp': datetime.now().isoformat(),
            'total_entries': self.summary.total_entries,
            'counts_by_level': {
                'error': self.summary.error_count,
                'warning': self.summary.warning_count,
                'info': self.summary.info_count,
                'debug': self.summary.debug_count
            },
            'recent_errors': self.summary.recent_errors,
            'performance_summary': {
                'total_operations': len(self.summary.performance_metrics),
                'average_duration': self._calculate_average_duration(),
                'success_rate': self._calculate_success_rate()
            }
        }

        if output_file:
            output_path = self.log_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)

            self.info(f"Log summary exported to: {output_path}")

        return summary_data

    def _calculate_average_duration(self) -> float:
        """Calculate average operation duration."""
        if not self.summary.performance_metrics:
            return 0.0

        total_duration = sum(
            m.duration for m in self.summary.performance_metrics
            if m.duration is not None
        )

        return total_duration / len(self.summary.performance_metrics)

    def _calculate_success_rate(self) -> float:
        """Calculate success rate of operations."""
        if not self.summary.performance_metrics:
            return 0.0

        successful = sum(1 for m in self.summary.performance_metrics if m.success)
        return (successful / len(self.summary.performance_metrics)) * 100

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up log files older than specified days.

        Args:
            days_to_keep: Number of days to keep log files
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_timestamp = cutoff_date.timestamp()

        cleaned_count = 0

        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_timestamp:
                try:
                    log_file.unlink()
                    cleaned_count += 1
                except OSError as e:
                    self.warning(f"Failed to delete old log file {log_file}: {e}")

        if cleaned_count > 0:
            self.info(f"Cleaned up {cleaned_count} old log files")

    def get_recent_errors(self, count: int = 5) -> list[str]:
        """
        Get recent error messages.

        Args:
            count: Number of recent errors to return

        Returns:
            List of recent error messages
        """
        return self.summary.recent_errors[-count:] if self.summary.recent_errors else []


# Global logger instance
_global_logger: AutomationLogger | None = None


def get_logger() -> AutomationLogger:
    """Get the global logger instance, creating it if necessary."""
    global _global_logger
    if _global_logger is None:
        # Use absolute path to ensure logs are created in the correct location
        # From automation_logging.py, go up 4 levels to reach project root
        project_root = Path(__file__).parent.parent.parent.parent
        logs_dir = str(project_root / "logs")
        _global_logger = AutomationLogger(logs_dir)
    return _global_logger


def init_logging(log_dir: str = "logs", max_log_size: int = 10*1024*1024,
                backup_count: int = 5) -> AutomationLogger:
    """
    Initialize the global logging system.

    Args:
        log_dir: Directory to store log files
        max_log_size: Maximum size per log file in bytes
        backup_count: Number of backup log files to keep

    Returns:
        Initialized AutomationLogger instance
    """
    global _global_logger
    _global_logger = AutomationLogger(log_dir, max_log_size, backup_count)
    return _global_logger


# Convenience functions for common logging operations
def log_info(message: str, **kwargs):
    """Log an info message using the global logger."""
    get_logger().info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log a warning message using the global logger."""
    get_logger().warning(message, **kwargs)


def log_error(message: str, exception: Exception | None = None, **kwargs):
    """Log an error message using the global logger."""
    get_logger().error(message, exception, **kwargs)


def log_debug(message: str, **kwargs):
    """Log a debug message using the global logger."""
    get_logger().debug(message, **kwargs)


def setup_logging_directories():
    """
    Set up logging directories and ensure they exist.

    This function creates the necessary directory structure for logging
    and initializes the logging environment.
    """
    try:
        # Define the logs directory path
        # From automation_logging.py, go up 4 levels to reach project root
        project_root = Path(__file__).parent.parent.parent.parent
        logs_dir = project_root / "logs"

        # Create logs directory if it doesn't exist
        logs_dir.mkdir(exist_ok=True)

        # Ensure all required log files exist
        required_log_files = [
            "automation.log",
            "price_update_log.txt",
            "performance.log",
            "errors.log"
        ]

        for log_file in required_log_files:
            log_path = logs_dir / log_file
            if not log_path.exists():
                log_path.touch()

        return True

    except Exception as e:
        print(f"Failed to setup logging directories: {e}")
        return False
