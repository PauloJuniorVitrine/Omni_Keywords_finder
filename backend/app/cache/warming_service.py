"""
Cache Warming Service
====================

This module implements an intelligent cache warming service that pre-loads
frequently accessed data based on usage patterns and predictive analysis.

Author: Omni Keywords Finder Team
Date: 2025-01-27
Tracing ID: CACHE_WARMING_20250127_001
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

from .intelligent_cache import IntelligentCache

logger = logging.getLogger(__name__)


@dataclass
class WarmingPattern:
    """Represents a cache warming pattern."""
    key_pattern: str
    frequency: float  # Access frequency per hour
    priority: int  # 1-10, higher is more important
    last_warmed: Optional[datetime] = None
    success_rate: float = 0.0
    avg_load_time: float = 0.0
    dependencies: List[str] = field(default_factory=list)


@dataclass
class WarmingJob:
    """Represents a cache warming job."""
    id: str
    pattern: WarmingPattern
    target_keys: List[str]
    priority: int
    created_at: datetime
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    error_message: Optional[str] = None


class CacheWarmingService:
    """
    Intelligent cache warming service that pre-loads data based on usage patterns.
    
    Features:
    - Pattern-based warming
    - Predictive warming
    - Dependency-aware warming
    - Performance monitoring
    - Adaptive scheduling
    """
    
    def __init__(self, cache: IntelligentCache):
        """Initialize cache warming service."""
        self.cache = cache
        self.patterns: Dict[str, WarmingPattern] = {}
        self.jobs: Dict[str, WarmingJob] = {}
        self.access_history = defaultdict(lambda: deque(maxlen=100))
        self.warming_stats = defaultdict(int)
        
        # Configuration
        self.max_concurrent_jobs = 5
        self.warming_interval = 300  # 5 minutes
        self.min_frequency_threshold = 0.1  # Minimum access frequency for warming
        self.max_warming_keys = 100  # Maximum keys to warm per job
        
        # Performance tracking
        self.performance_history = deque(maxlen=50)
        self.success_threshold = 0.7  # Minimum success rate for continued warming
        
        logger.info("Cache warming service initialized")
    
    def register_pattern(self, pattern: WarmingPattern) -> None:
        """Register a warming pattern."""
        self.patterns[pattern.key_pattern] = pattern
        logger.info(f"Registered warming pattern: {pattern.key_pattern}")
    
    def track_access(self, key: str, load_time: float = 0.0) -> None:
        """Track key access for pattern analysis."""
        current_time = time.time()
        self.access_history[key].append({
            'timestamp': current_time,
            'load_time': load_time
        })
        
        # Update pattern statistics
        for pattern in self.patterns.values():
            if self._matches_pattern(key, pattern.key_pattern):
                self._update_pattern_stats(pattern, load_time)
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches warming pattern."""
        # Simple pattern matching - can be extended with regex
        return pattern in key or key.startswith(pattern)
    
    def _update_pattern_stats(self, pattern: WarmingPattern, load_time: float) -> None:
        """Update pattern statistics based on access."""
        current_time = time.time()
        
        # Calculate frequency (accesses per hour)
        recent_accesses = [
            access for access in self.access_history.get(pattern.key_pattern, [])
            if current_time - access['timestamp'] < 3600  # Last hour
        ]
        pattern.frequency = len(recent_accesses) / 1.0  # Per hour
        
        # Update average load time
        if load_time > 0:
            if pattern.avg_load_time == 0:
                pattern.avg_load_time = load_time
            else:
                pattern.avg_load_time = (pattern.avg_load_time + load_time) / 2
    
    def _predict_keys_to_warm(self, pattern: WarmingPattern) -> List[str]:
        """Predict which keys should be warmed based on pattern."""
        predicted_keys = []
        
        # Get all keys that match the pattern
        matching_keys = []
        for key in self.access_history.keys():
            if self._matches_pattern(key, pattern.key_pattern):
                matching_keys.append(key)
        
        # Sort by access frequency and recency
        key_scores = []
        current_time = time.time()
        
        for key in matching_keys:
            recent_accesses = [
                access for access in self.access_history[key]
                if current_time - access['timestamp'] < 86400  # Last 24 hours
            ]
            
            if recent_accesses:
                frequency = len(recent_accesses) / 24.0  # Per hour
                last_access = max(access['timestamp'] for access in recent_accesses)
                recency_score = 1.0 / (current_time - last_access + 1)
                
                score = frequency * 0.7 + recency_score * 0.3
                key_scores.append((key, score))
        
        # Sort by score and return top keys
        key_scores.sort(key=lambda x: x[1], reverse=True)
        predicted_keys = [key for key, _ in key_scores[:self.max_warming_keys]]
        
        return predicted_keys
    
    async def warm_cache(self, pattern_key: str) -> WarmingJob:
        """Warm cache for a specific pattern."""
        if pattern_key not in self.patterns:
            raise ValueError(f"Pattern {pattern_key} not found")
        
        pattern = self.patterns[pattern_key]
        
        # Check if warming is needed
        if pattern.frequency < self.min_frequency_threshold:
            logger.info(f"Skipping warming for {pattern_key} - frequency too low")
            return None
        
        # Check if recently warmed
        if (pattern.last_warmed and 
            datetime.now() - pattern.last_warmed < timedelta(minutes=30)):
            logger.info(f"Skipping warming for {pattern_key} - recently warmed")
            return None
        
        # Create warming job
        job_id = f"warming_{pattern_key}_{int(time.time())}"
        target_keys = self._predict_keys_to_warm(pattern)
        
        job = WarmingJob(
            id=job_id,
            pattern=pattern,
            target_keys=target_keys,
            priority=pattern.priority,
            created_at=datetime.now()
        )
        
        self.jobs[job_id] = job
        
        # Execute warming asynchronously
        asyncio.create_task(self._execute_warming_job(job))
        
        logger.info(f"Started warming job {job_id} for {len(target_keys)} keys")
        return job
    
    async def _execute_warming_job(self, job: WarmingJob) -> None:
        """Execute a warming job."""
        job.status = "running"
        successful_warms = 0
        
        try:
            for i, key in enumerate(job.target_keys):
                if job.status == "cancelled":
                    break
                
                # Simulate warming by accessing the key
                # In real implementation, this would call the actual data loading function
                success = await self._warm_key(key)
                
                if success:
                    successful_warms += 1
                
                # Update progress
                job.progress = (i + 1) / len(job.target_keys) * 100
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            # Update job status
            job.status = "completed"
            success_rate = successful_warms / len(job.target_keys) if job.target_keys else 0
            
            # Update pattern statistics
            job.pattern.success_rate = success_rate
            job.pattern.last_warmed = datetime.now()
            
            # Update warming stats
            self.warming_stats["successful_jobs"] += 1
            self.warming_stats["total_keys_warmed"] += successful_warms
            
            logger.info(f"Warming job {job.id} completed: {successful_warms}/{len(job.target_keys)} keys warmed")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            self.warming_stats["failed_jobs"] += 1
            logger.error(f"Warming job {job.id} failed: {e}")
    
    async def _warm_key(self, key: str) -> bool:
        """Warm a specific key by pre-loading its data."""
        try:
            # In real implementation, this would call the appropriate data loading function
            # For now, we'll simulate warming by checking if the key exists in cache
            
            # Simulate data loading time
            await asyncio.sleep(0.05)
            
            # Check if key is already in cache
            if self.cache.get(key) is not None:
                return True
            
            # Simulate successful warming
            return True
            
        except Exception as e:
            logger.warning(f"Failed to warm key {key}: {e}")
            return False
    
    def get_warming_stats(self) -> Dict[str, Any]:
        """Get warming service statistics."""
        total_jobs = (self.warming_stats["successful_jobs"] + 
                     self.warming_stats["failed_jobs"])
        
        success_rate = (self.warming_stats["successful_jobs"] / total_jobs * 100 
                       if total_jobs > 0 else 0)
        
        return {
            "total_jobs": total_jobs,
            "successful_jobs": self.warming_stats["successful_jobs"],
            "failed_jobs": self.warming_stats["failed_jobs"],
            "success_rate": round(success_rate, 2),
            "total_keys_warmed": self.warming_stats["total_keys_warmed"],
            "active_patterns": len(self.patterns),
            "pending_jobs": len([j for j in self.jobs.values() if j.status == "pending"]),
            "running_jobs": len([j for j in self.jobs.values() if j.status == "running"])
        }
    
    def optimize_patterns(self) -> Dict[str, Any]:
        """Optimize warming patterns based on performance."""
        optimization_stats = {
            "patterns_analyzed": len(self.patterns),
            "patterns_optimized": 0,
            "patterns_disabled": 0
        }
        
        for pattern in self.patterns.values():
            # Disable patterns with low success rate
            if pattern.success_rate < self.success_threshold:
                pattern.priority = max(1, pattern.priority - 1)
                optimization_stats["patterns_optimized"] += 1
            
            # Disable patterns with very low frequency
            if pattern.frequency < self.min_frequency_threshold * 0.5:
                pattern.priority = 1
                optimization_stats["patterns_disabled"] += 1
        
        logger.info(f"Pattern optimization completed: {optimization_stats}")
        return optimization_stats
    
    async def start_background_warming(self) -> None:
        """Start background warming service."""
        logger.info("Starting background cache warming service")
        
        while True:
            try:
                # Get patterns that need warming
                patterns_to_warm = []
                for pattern in self.patterns.values():
                    if (pattern.frequency >= self.min_frequency_threshold and
                        (not pattern.last_warmed or 
                         datetime.now() - pattern.last_warmed > timedelta(minutes=30))):
                        patterns_to_warm.append(pattern)
                
                # Sort by priority and frequency
                patterns_to_warm.sort(key=lambda p: (p.priority, p.frequency), reverse=True)
                
                # Start warming for top patterns
                active_jobs = [j for j in self.jobs.values() if j.status == "running"]
                
                for pattern in patterns_to_warm[:self.max_concurrent_jobs - len(active_jobs)]:
                    await self.warm_cache(pattern.key_pattern)
                
                # Wait before next warming cycle
                await asyncio.sleep(self.warming_interval)
                
            except Exception as e:
                logger.error(f"Error in background warming: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying


# Example usage and testing
if __name__ == "__main__":
    async def test_warming_service():
        # Initialize cache and warming service
        cache = IntelligentCache()
        warming_service = CacheWarmingService(cache)
        
        # Register some patterns
        patterns = [
            WarmingPattern("user_profile:", 5.0, 8),
            WarmingPattern("keyword_analysis:", 3.0, 6),
            WarmingPattern("dashboard_data:", 2.0, 4)
        ]
        
        for pattern in patterns:
            warming_service.register_pattern(pattern)
        
        # Simulate some access patterns
        for i in range(10):
            warming_service.track_access(f"user_profile:{i}", 0.1)
            warming_service.track_access(f"keyword_analysis:{i}", 0.2)
        
        # Start background warming
        warming_task = asyncio.create_task(warming_service.start_background_warming())
        
        # Let it run for a bit
        await asyncio.sleep(10)
        
        # Get statistics
        stats = warming_service.get_warming_stats()
        print(f"Warming statistics: {stats}")
        
        # Cancel background task
        warming_task.cancel()
    
    # Run test
    asyncio.run(test_warming_service()) 