"""
Cache Invalidation Strategy
==========================

This module implements intelligent cache invalidation strategies based on:
- Data dependencies
- Update patterns
- User behavior
- System events

Author: Omni Keywords Finder Team
Date: 2025-01-27
Tracing ID: CACHE_INVALIDATION_20250127_001
"""

import time
import json
import logging
from typing import Dict, List, Set, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio

from .intelligent_cache import IntelligentCache

logger = logging.getLogger(__name__)


@dataclass
class DependencyNode:
    """Represents a dependency node in the cache dependency graph."""
    key: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    last_updated: Optional[datetime] = None
    update_frequency: float = 0.0
    invalidation_priority: int = 5  # 1-10, higher is more critical


@dataclass
class InvalidationRule:
    """Represents an invalidation rule."""
    name: str
    pattern: str
    trigger_conditions: List[str]
    invalidation_scope: str  # "exact", "pattern", "cascade"
    priority: int
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class InvalidationEvent:
    """Represents a cache invalidation event."""
    id: str
    trigger: str
    affected_keys: List[str]
    timestamp: datetime
    reason: str
    cascade_level: int = 0
    status: str = "pending"  # pending, running, completed, failed


class CacheInvalidationStrategy:
    """
    Intelligent cache invalidation strategy with dependency-aware invalidation.
    
    Features:
    - Dependency graph management
    - Pattern-based invalidation
    - Cascade invalidation
    - Selective invalidation
    - Performance monitoring
    """
    
    def __init__(self, cache: IntelligentCache):
        """Initialize cache invalidation strategy."""
        self.cache = cache
        self.dependency_graph: Dict[str, DependencyNode] = {}
        self.invalidation_rules: Dict[str, InvalidationRule] = {}
        self.invalidation_events: Dict[str, InvalidationEvent] = {}
        self.update_history = defaultdict(lambda: deque(maxlen=50))
        
        # Configuration
        self.max_cascade_depth = 3
        self.batch_invalidation_size = 100
        self.invalidation_delay = 1.0  # seconds
        
        # Statistics
        self.invalidation_stats = defaultdict(int)
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("Cache invalidation strategy initialized")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default invalidation rules."""
        default_rules = [
            InvalidationRule(
                name="user_profile_update",
                pattern="user_profile:*",
                trigger_conditions=["user_update", "profile_change"],
                invalidation_scope="exact",
                priority=8
            ),
            InvalidationRule(
                name="keyword_analysis_update",
                pattern="keyword_analysis:*",
                trigger_conditions=["new_analysis", "model_update"],
                invalidation_scope="pattern",
                priority=7
            ),
            InvalidationRule(
                name="dashboard_data_update",
                pattern="dashboard:*",
                trigger_conditions=["data_refresh", "metrics_update"],
                invalidation_scope="cascade",
                priority=6
            ),
            InvalidationRule(
                name="global_config_update",
                pattern="config:*",
                trigger_conditions=["config_change", "system_update"],
                invalidation_scope="cascade",
                priority=9
            )
        ]
        
        for rule in default_rules:
            self.add_invalidation_rule(rule)
    
    def add_invalidation_rule(self, rule: InvalidationRule) -> None:
        """Add an invalidation rule."""
        self.invalidation_rules[rule.name] = rule
        logger.info(f"Added invalidation rule: {rule.name}")
    
    def add_dependency(self, key: str, depends_on: str) -> None:
        """Add a dependency relationship between cache keys."""
        # Ensure nodes exist
        if key not in self.dependency_graph:
            self.dependency_graph[key] = DependencyNode(key=key)
        if depends_on not in self.dependency_graph:
            self.dependency_graph[depends_on] = DependencyNode(key=depends_on)
        
        # Add dependency
        self.dependency_graph[key].dependencies.add(depends_on)
        self.dependency_graph[depends_on].dependents.add(key)
        
        logger.debug(f"Added dependency: {key} depends on {depends_on}")
    
    def remove_dependency(self, key: str, depends_on: str) -> None:
        """Remove a dependency relationship."""
        if key in self.dependency_graph:
            self.dependency_graph[key].dependencies.discard(depends_on)
        if depends_on in self.dependency_graph:
            self.dependency_graph[depends_on].dependents.discard(key)
    
    def track_update(self, key: str, update_type: str = "general") -> None:
        """Track a cache key update for invalidation analysis."""
        current_time = datetime.now()
        
        # Update dependency node
        if key in self.dependency_graph:
            node = self.dependency_graph[key]
            node.last_updated = current_time
            
            # Update frequency calculation
            self.update_history[key].append(current_time)
            if len(self.update_history[key]) >= 2:
                intervals = []
                history_list = list(self.update_history[key])
                for i in range(1, len(history_list)):
                    interval = (history_list[i] - history_list[i-1]).total_seconds()
                    intervals.append(interval)
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    node.update_frequency = 3600 / avg_interval if avg_interval > 0 else 0
        
        # Check invalidation rules
        self._check_invalidation_rules(key, update_type)
    
    def _check_invalidation_rules(self, key: str, update_type: str) -> None:
        """Check if any invalidation rules should be triggered."""
        for rule in self.invalidation_rules.values():
            if not rule.enabled:
                continue
            
            # Check if key matches pattern
            if not self._matches_pattern(key, rule.pattern):
                continue
            
            # Check trigger conditions
            if update_type in rule.trigger_conditions:
                self._trigger_invalidation(rule, key, update_type)
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches invalidation pattern."""
        # Simple pattern matching - can be extended with regex
        return pattern in key or key.startswith(pattern.replace("*", ""))
    
    def _trigger_invalidation(self, rule: InvalidationRule, key: str, trigger: str) -> None:
        """Trigger cache invalidation based on rule."""
        rule.last_triggered = datetime.now()
        rule.trigger_count += 1
        
        # Determine affected keys based on scope
        affected_keys = self._get_affected_keys(rule, key)
        
        # Create invalidation event
        event_id = f"invalidation_{rule.name}_{int(time.time())}"
        event = InvalidationEvent(
            id=event_id,
            trigger=trigger,
            affected_keys=affected_keys,
            timestamp=datetime.now(),
            reason=f"Rule '{rule.name}' triggered by {trigger}"
        )
        
        self.invalidation_events[event_id] = event
        
        # Execute invalidation asynchronously
        asyncio.create_task(self._execute_invalidation(event))
        
        logger.info(f"Triggered invalidation: {rule.name} -> {len(affected_keys)} keys")
    
    def _get_affected_keys(self, rule: InvalidationRule, trigger_key: str) -> List[str]:
        """Get keys affected by invalidation based on scope."""
        affected_keys = []
        
        if rule.invalidation_scope == "exact":
            # Invalidate only the exact key
            affected_keys = [trigger_key]
        
        elif rule.invalidation_scope == "pattern":
            # Invalidate all keys matching the pattern
            pattern_prefix = rule.pattern.replace("*", "")
            affected_keys = [
                key for key in self.dependency_graph.keys()
                if self._matches_pattern(key, rule.pattern)
            ]
        
        elif rule.invalidation_scope == "cascade":
            # Invalidate key and all dependents
            affected_keys = self._get_cascade_affected_keys(trigger_key)
        
        return affected_keys
    
    def _get_cascade_affected_keys(self, key: str, max_depth: int = None) -> List[str]:
        """Get all keys affected by cascade invalidation."""
        if max_depth is None:
            max_depth = self.max_cascade_depth
        
        affected_keys = set()
        to_process = [(key, 0)]  # (key, depth)
        
        while to_process:
            current_key, depth = to_process.pop(0)
            
            if depth > max_depth or current_key in affected_keys:
                continue
            
            affected_keys.add(current_key)
            
            # Add dependents to processing queue
            if current_key in self.dependency_graph:
                node = self.dependency_graph[current_key]
                for dependent in node.dependents:
                    to_process.append((dependent, depth + 1))
        
        return list(affected_keys)
    
    async def _execute_invalidation(self, event: InvalidationEvent) -> None:
        """Execute cache invalidation for an event."""
        event.status = "running"
        
        try:
            # Process keys in batches
            for i in range(0, len(event.affected_keys), self.batch_invalidation_size):
                batch = event.affected_keys[i:i + self.batch_invalidation_size]
                
                # Invalidate batch
                for key in batch:
                    success = self.cache.delete(key)
                    if success:
                        self.invalidation_stats["successful_invalidations"] += 1
                    else:
                        self.invalidation_stats["failed_invalidations"] += 1
                
                # Small delay between batches
                await asyncio.sleep(self.invalidation_delay)
            
            event.status = "completed"
            self.invalidation_stats["completed_events"] += 1
            
            logger.info(f"Invalidation event {event.id} completed: {len(event.affected_keys)} keys")
            
        except Exception as e:
            event.status = "failed"
            self.invalidation_stats["failed_events"] += 1
            logger.error(f"Invalidation event {event.id} failed: {e}")
    
    def invalidate_key(self, key: str, reason: str = "manual") -> bool:
        """Manually invalidate a specific key."""
        try:
            success = self.cache.delete(key)
            if success:
                self.invalidation_stats["manual_invalidations"] += 1
                logger.info(f"Manually invalidated key: {key} ({reason})")
            return success
        except Exception as e:
            logger.error(f"Failed to invalidate key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str, reason: str = "manual") -> int:
        """Invalidate all keys matching a pattern."""
        affected_keys = [
            key for key in self.dependency_graph.keys()
            if self._matches_pattern(key, pattern)
        ]
        
        invalidated_count = 0
        for key in affected_keys:
            if self.invalidate_key(key, reason):
                invalidated_count += 1
        
        logger.info(f"Pattern invalidation completed: {pattern} -> {invalidated_count} keys")
        return invalidated_count
    
    def get_invalidation_stats(self) -> Dict[str, Any]:
        """Get invalidation strategy statistics."""
        total_events = (self.invalidation_stats["completed_events"] + 
                       self.invalidation_stats["failed_events"])
        
        success_rate = (self.invalidation_stats["completed_events"] / total_events * 100 
                       if total_events > 0 else 0)
        
        return {
            "total_events": total_events,
            "completed_events": self.invalidation_stats["completed_events"],
            "failed_events": self.invalidation_stats["failed_events"],
            "success_rate": round(success_rate, 2),
            "successful_invalidations": self.invalidation_stats["successful_invalidations"],
            "failed_invalidations": self.invalidation_stats["failed_invalidations"],
            "manual_invalidations": self.invalidation_stats["manual_invalidations"],
            "active_rules": len([r for r in self.invalidation_rules.values() if r.enabled]),
            "dependency_nodes": len(self.dependency_graph),
            "pending_events": len([e for e in self.invalidation_events.values() if e.status == "pending"]),
            "running_events": len([e for e in self.invalidation_events.values() if e.status == "running"])
        }
    
    def optimize_rules(self) -> Dict[str, Any]:
        """Optimize invalidation rules based on performance."""
        optimization_stats = {
            "rules_analyzed": len(self.invalidation_rules),
            "rules_optimized": 0,
            "rules_disabled": 0
        }
        
        for rule in self.invalidation_rules.values():
            # Disable rules with very low trigger count
            if rule.trigger_count < 5 and rule.last_triggered:
                days_since_trigger = (datetime.now() - rule.last_triggered).days
                if days_since_trigger > 7:
                    rule.enabled = False
                    optimization_stats["rules_disabled"] += 1
            
            # Adjust priority based on trigger frequency
            if rule.trigger_count > 100:
                rule.priority = min(10, rule.priority + 1)
                optimization_stats["rules_optimized"] += 1
        
        logger.info(f"Rule optimization completed: {optimization_stats}")
        return optimization_stats
    
    def get_dependency_graph(self) -> Dict[str, Any]:
        """Get dependency graph information."""
        return {
            "total_nodes": len(self.dependency_graph),
            "nodes_with_dependencies": len([n for n in self.dependency_graph.values() if n.dependencies]),
            "nodes_with_dependents": len([n for n in self.dependency_graph.values() if n.dependents]),
            "max_dependency_depth": max(len(n.dependencies) for n in self.dependency_graph.values()) if self.dependency_graph else 0,
            "max_dependent_count": max(len(n.dependents) for n in self.dependency_graph.values()) if self.dependency_graph else 0
        }


# Example usage and testing
if __name__ == "__main__":
    async def test_invalidation_strategy():
        # Initialize cache and invalidation strategy
        cache = IntelligentCache()
        invalidation = CacheInvalidationStrategy(cache)
        
        # Add some dependencies
        invalidation.add_dependency("user_profile:123", "user_data:123")
        invalidation.add_dependency("dashboard:user:123", "user_profile:123")
        invalidation.add_dependency("keyword_analysis:456", "user_profile:123")
        
        # Track some updates
        invalidation.track_update("user_data:123", "user_update")
        invalidation.track_update("keyword_analysis:456", "new_analysis")
        
        # Wait for invalidation to complete
        await asyncio.sleep(5)
        
        # Get statistics
        stats = invalidation.get_invalidation_stats()
        print(f"Invalidation statistics: {stats}")
        
        # Get dependency graph info
        graph_info = invalidation.get_dependency_graph()
        print(f"Dependency graph: {graph_info}")
    
    # Run test
    asyncio.run(test_invalidation_strategy()) 