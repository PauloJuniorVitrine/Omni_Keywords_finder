"""
Memory Profiler
==============

This module implements memory profiling and leak detection for the Omni Keywords Finder system.

Author: Omni Keywords Finder Team
Date: 2025-01-27
Tracing ID: MEMORY_PROFILER_20250127_001
"""

import psutil
import gc
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """Represents a memory snapshot."""
    timestamp: datetime
    total_memory: int
    available_memory: int
    used_memory: int
    memory_percent: float
    cpu_percent: float
    gc_stats: Dict[str, Any]
    process_memory: Dict[str, Any]


@dataclass
class MemoryLeak:
    """Represents a detected memory leak."""
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    memory_growth: float  # MB
    growth_rate: float  # MB/hour
    severity: str  # "low", "medium", "high", "critical"
    description: str
    status: str = "active"  # "active", "resolved", "investigating"


class MemoryProfiler:
    """
    Memory profiler with leak detection and monitoring.
    
    Features:
    - Continuous memory monitoring
    - Memory leak detection
    - GC statistics tracking
    - Process memory analysis
    - Performance impact monitoring
    """
    
    def __init__(self, 
                 monitoring_interval: float = 60.0,
                 leak_threshold: float = 100.0,  # MB
                 max_snapshots: int = 1000):
        """Initialize memory profiler."""
        self.monitoring_interval = monitoring_interval
        self.leak_threshold = leak_threshold
        self.max_snapshots = max_snapshots
        
        # Memory snapshots
        self.snapshots: deque = deque(maxlen=max_snapshots)
        self.memory_history: deque = deque(maxlen=max_snapshots)
        
        # Leak detection
        self.detected_leaks: Dict[str, MemoryLeak] = {}
        self.leak_counter = 0
        
        # Statistics
        self.stats = defaultdict(int)
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        logger.info("Memory profiler initialized")
    
    def start_monitoring(self) -> None:
        """Start memory monitoring."""
        if self.is_monitoring:
            logger.warning("Memory monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_memory,
            daemon=True,
            name="MemoryProfiler"
        )
        self.monitor_thread.start()
        
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        self.is_monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Memory monitoring stopped")
    
    def _monitor_memory(self) -> None:
        """Main memory monitoring loop."""
        while self.is_monitoring:
            try:
                # Take memory snapshot
                snapshot = self._take_snapshot()
                self.snapshots.append(snapshot)
                self.memory_history.append(snapshot.used_memory)
                
                # Check for memory leaks
                self._check_for_leaks()
                
                # Log memory usage
                if len(self.snapshots) % 10 == 0:  # Log every 10 snapshots
                    logger.info(f"Memory usage: {snapshot.used_memory / 1024 / 1024:.1f}MB "
                              f"({snapshot.memory_percent:.1f}%)")
                
                # Wait for next monitoring cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in memory monitoring: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot."""
        # System memory
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        
        # GC statistics
        gc_stats = {
            "collections": gc.get_stats(),
            "counts": gc.get_count(),
            "thresholds": gc.get_threshold()
        }
        
        # Process memory
        process = psutil.Process()
        process_memory = {
            "rss": process.memory_info().rss,
            "vms": process.memory_info().vms,
            "percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0
        }
        
        return MemorySnapshot(
            timestamp=datetime.now(),
            total_memory=memory.total,
            available_memory=memory.available,
            used_memory=memory.used,
            memory_percent=memory.percent,
            cpu_percent=cpu,
            gc_stats=gc_stats,
            process_memory=process_memory
        )
    
    def _check_for_leaks(self) -> None:
        """Check for potential memory leaks."""
        if len(self.snapshots) < 10:  # Need at least 10 snapshots
            return
        
        # Calculate memory growth over time
        recent_snapshots = list(self.snapshots)[-10:]
        first_memory = recent_snapshots[0].used_memory
        last_memory = recent_snapshots[-1].used_memory
        
        memory_growth = last_memory - first_memory
        time_diff = (recent_snapshots[-1].timestamp - recent_snapshots[0].timestamp).total_seconds()
        growth_rate = (memory_growth / 1024 / 1024) / (time_diff / 3600)  # MB/hour
        
        # Check if growth exceeds threshold
        if memory_growth > self.leak_threshold * 1024 * 1024:  # Convert MB to bytes
            self._detect_leak(memory_growth, growth_rate, recent_snapshots)
    
    def _detect_leak(self, memory_growth: float, growth_rate: float, snapshots: List[MemorySnapshot]) -> None:
        """Detect and record a memory leak."""
        leak_id = f"leak_{self.leak_counter}"
        self.leak_counter += 1
        
        # Determine severity
        if growth_rate < 10:
            severity = "low"
        elif growth_rate < 50:
            severity = "medium"
        elif growth_rate < 100:
            severity = "high"
        else:
            severity = "critical"
        
        leak = MemoryLeak(
            id=leak_id,
            start_time=snapshots[0].timestamp,
            end_time=None,
            memory_growth=memory_growth / 1024 / 1024,  # Convert to MB
            growth_rate=growth_rate,
            severity=severity,
            description=f"Memory growth of {memory_growth / 1024 / 1024:.1f}MB "
                       f"detected over {len(snapshots)} snapshots"
        )
        
        self.detected_leaks[leak_id] = leak
        self.stats["leaks_detected"] += 1
        
        logger.warning(f"Memory leak detected: {leak.description} (severity: {severity})")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        
        # Calculate memory trends
        if len(self.snapshots) >= 10:
            recent_snapshots = list(self.snapshots)[-10:]
            memory_trend = (recent_snapshots[-1].used_memory - recent_snapshots[0].used_memory) / 1024 / 1024
        else:
            memory_trend = 0.0
        
        return {
            "current_memory_mb": latest.used_memory / 1024 / 1024,
            "memory_percent": latest.memory_percent,
            "available_memory_mb": latest.available_memory / 1024 / 1024,
            "total_memory_mb": latest.total_memory / 1024 / 1024,
            "cpu_percent": latest.cpu_percent,
            "memory_trend_mb": memory_trend,
            "snapshots_count": len(self.snapshots),
            "active_leaks": len([l for l in self.detected_leaks.values() if l.status == "active"]),
            "total_leaks_detected": self.stats["leaks_detected"]
        }
    
    def get_gc_stats(self) -> Dict[str, Any]:
        """Get garbage collection statistics."""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        return {
            "gc_collections": latest.gc_stats["collections"],
            "gc_counts": latest.gc_stats["counts"],
            "gc_thresholds": latest.gc_stats["thresholds"]
        }
    
    def get_process_stats(self) -> Dict[str, Any]:
        """Get process memory statistics."""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        return {
            "process_rss_mb": latest.process_memory["rss"] / 1024 / 1024,
            "process_vms_mb": latest.process_memory["vms"] / 1024 / 1024,
            "process_memory_percent": latest.process_memory["percent"],
            "num_threads": latest.process_memory["num_threads"],
            "num_fds": latest.process_memory["num_fds"]
        }
    
    def get_leak_report(self) -> List[Dict[str, Any]]:
        """Get report of detected memory leaks."""
        return [
            {
                "id": leak.id,
                "start_time": leak.start_time.isoformat(),
                "end_time": leak.end_time.isoformat() if leak.end_time else None,
                "memory_growth_mb": leak.memory_growth,
                "growth_rate_mb_per_hour": leak.growth_rate,
                "severity": leak.severity,
                "description": leak.description,
                "status": leak.status
            }
            for leak in self.detected_leaks.values()
        ]
    
    def force_gc(self) -> Dict[str, Any]:
        """Force garbage collection and return statistics."""
        logger.info("Forcing garbage collection")
        
        # Take snapshot before GC
        before_snapshot = self._take_snapshot()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Take snapshot after GC
        after_snapshot = self._take_snapshot()
        
        # Calculate memory freed
        memory_freed = before_snapshot.used_memory - after_snapshot.used_memory
        
        result = {
            "objects_collected": collected,
            "memory_freed_mb": memory_freed / 1024 / 1024,
            "before_memory_mb": before_snapshot.used_memory / 1024 / 1024,
            "after_memory_mb": after_snapshot.used_memory / 1024 / 1024
        }
        
        logger.info(f"GC completed: {collected} objects collected, "
                   f"{memory_freed / 1024 / 1024:.1f}MB freed")
        
        return result
    
    def get_memory_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get memory history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        history = []
        for snapshot in self.snapshots:
            if snapshot.timestamp >= cutoff_time:
                history.append({
                    "timestamp": snapshot.timestamp.isoformat(),
                    "memory_mb": snapshot.used_memory / 1024 / 1024,
                    "memory_percent": snapshot.memory_percent,
                    "cpu_percent": snapshot.cpu_percent
                })
        
        return history


# Global memory profiler instance
memory_profiler: Optional[MemoryProfiler] = None


def get_memory_profiler() -> MemoryProfiler:
    """Get the global memory profiler instance."""
    global memory_profiler
    if memory_profiler is None:
        memory_profiler = MemoryProfiler()
    return memory_profiler


# Example usage and testing
if __name__ == "__main__":
    def test_memory_profiler():
        # Initialize memory profiler
        profiler = MemoryProfiler(monitoring_interval=5.0)  # 5 second intervals for testing
        
        # Start monitoring
        profiler.start_monitoring()
        
        # Simulate some memory usage
        print("Simulating memory usage...")
        large_list = []
        for i in range(100000):
            large_list.append([i] * 100)  # Create some memory pressure
        
        # Let it run for a bit
        time.sleep(30)
        
        # Get statistics
        memory_stats = profiler.get_memory_stats()
        print(f"Memory Statistics: {memory_stats}")
        
        # Force garbage collection
        gc_stats = profiler.force_gc()
        print(f"GC Statistics: {gc_stats}")
        
        # Get leak report
        leak_report = profiler.get_leak_report()
        print(f"Leak Report: {leak_report}")
        
        # Stop monitoring
        profiler.stop_monitoring()
    
    # Run test
    test_memory_profiler() 