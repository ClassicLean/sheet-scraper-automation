"""
Statistics tracking for automation processes.

This module provides the AutomationStats class for tracking
metrics and performance data during automation runs.
"""

from datetime import datetime
from typing import Dict, Any


class AutomationStats:
    """Tracks automation statistics and metrics."""

    def __init__(self):
        self.total_processed = 0
        self.successful_updates = 0
        self.failed_updates = 0
        self.blocked_updates = 0
        self.out_of_stock_count = 0
        self.start_time = datetime.now()

    def record_success(self):
        """Record a successful update."""
        self.successful_updates += 1
        self.total_processed += 1

    def record_failure(self):
        """Record a failed update."""
        self.failed_updates += 1
        self.total_processed += 1

    def record_blocked(self):
        """Record a blocked update."""
        self.blocked_updates += 1
        self.total_processed += 1

    def record_out_of_stock(self):
        """Record an out of stock item."""
        self.out_of_stock_count += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get automation statistics summary."""
        runtime = datetime.now() - self.start_time
        return {
            "total_processed": self.total_processed,
            "successful_updates": self.successful_updates,
            "failed_updates": self.failed_updates,
            "blocked_updates": self.blocked_updates,
            "out_of_stock_count": self.out_of_stock_count,
            "success_rate": (self.successful_updates / max(1, self.total_processed)) * 100,
            "runtime_seconds": runtime.total_seconds(),
            "avg_time_per_item": runtime.total_seconds() / max(1, self.total_processed)
        }
