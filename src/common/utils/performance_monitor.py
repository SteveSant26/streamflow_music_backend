"""
Simple performance monitoring utility for tracking search improvements
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


class PerformanceMonitor:
    """Simple performance monitoring for music search operations"""

    def __init__(self, log_file: str = "performance_metrics.json"):
        self.log_file = log_file
        self.current_metrics: Dict[str, Any] = {}
        self.load_existing_metrics()

    def load_existing_metrics(self):
        """Load existing performance metrics if they exist"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    self.current_metrics = json.load(f)
        except Exception:
            self.current_metrics = {"searches": [], "summary": {}}

    def start_search(self, query: str, operation: str = "search") -> str:
        """Start tracking a search operation"""
        search_id = f"{operation}_{int(time.time() * 1000)}"
        self.current_metrics[search_id] = {
            "query": query,
            "operation": operation,
            "start_time": time.time(),
            "timestamp": datetime.now().isoformat(),
        }
        return search_id

    def end_search(
        self,
        search_id: str,
        result_count: int = 0,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """End tracking a search operation"""
        if search_id in self.current_metrics:
            search_data = self.current_metrics[search_id]
            search_data.update(
                {
                    "end_time": time.time(),
                    "duration": time.time() - search_data["start_time"],
                    "result_count": result_count,
                    "success": success,
                    "error": error,
                }
            )

            # Move to searches list
            if "searches" not in self.current_metrics:
                self.current_metrics["searches"] = []

            self.current_metrics["searches"].append(search_data)
            del self.current_metrics[search_id]

            # Update summary statistics
            self.update_summary()

            # Save to file
            self.save_metrics()

    def update_summary(self):
        """Update summary statistics"""
        searches = self.current_metrics.get("searches", [])

        if not searches:
            return

        successful_searches = [s for s in searches if s.get("success", False)]

        summary = {
            "total_searches": len(searches),
            "successful_searches": len(successful_searches),
            "success_rate": len(successful_searches) / len(searches) * 100,
            "last_updated": datetime.now().isoformat(),
        }

        if successful_searches:
            durations = [s["duration"] for s in successful_searches]
            result_counts = [s.get("result_count", 0) for s in successful_searches]

            summary.update(
                {
                    "avg_duration": sum(durations) / len(durations),
                    "max_duration": max(durations),
                    "min_duration": min(durations),
                    "avg_results": sum(result_counts) / len(result_counts),
                    "total_results_found": sum(result_counts),
                }
            )

        self.current_metrics["summary"] = summary

    def save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.log_file, "w") as f:
                json.dump(self.current_metrics, f, indent=2)
        except Exception as e:
            print(f"Failed to save performance metrics: {e}")

    def get_recent_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search performance data"""
        searches = self.current_metrics.get("searches", [])
        return searches[-limit:] if searches else []

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return self.current_metrics.get("summary", {})

    def clear_old_data(self, days: int = 7):
        """Clear performance data older than specified days"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        searches = self.current_metrics.get("searches", [])

        filtered_searches = [
            s for s in searches if s.get("start_time", 0) > cutoff_time
        ]

        self.current_metrics["searches"] = filtered_searches
        self.update_summary()
        self.save_metrics()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
