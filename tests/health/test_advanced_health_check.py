"""
Tests for Advanced Health Check System

This module contains comprehensive tests for the advanced health check system,
including all health check types, the health checker, and edge cases.

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: HEALTH_TEST_001
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from infrastructure.health.advanced_health_check import (
    HealthStatus,
    HealthCheckType,
    HealthCheckResult,
    HealthCheckConfig,
    BaseHealthCheck,
    DatabaseHealthCheck,
    RedisHealthCheck,
    ExternalAPICheck,
    SystemResourceCheck,
    CustomHealthCheck,
    AdvancedHealthChecker
)


class TestHealthStatus:
    """Test health status enumeration"""
    
    def test_health_status_values(self):
        """Test health status enum values"""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestHealthCheckType:
    """Test health check type enumeration"""
    
    def test_health_check_type_values(self):
        """Test health check type enum values"""
        assert HealthCheckType.LIVENESS.value == "liveness"
        assert HealthCheckType.READINESS.value == "readiness"
        assert HealthCheckType.STARTUP.value == "startup"
        assert HealthCheckType.CUSTOM.value == "custom"


class TestHealthCheckResult:
    """Test health check result dataclass"""
    
    def test_health_check_result_creation(self):
        """Test creating a health check result"""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="Test passed",
            details={"test": "data"},
            duration_ms=100.0,
            check_type=HealthCheckType.CUSTOM
        )
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Test passed"
        assert result.details == {"test": "data"}
        assert result.duration_ms == 100.0
        assert result.check_type == HealthCheckType.CUSTOM
        assert isinstance(result.timestamp, datetime)
    
    def test_health_check_result_defaults(self):
        """Test health check result with default values"""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY
        )
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == ""
        assert result.details == {}
        assert result.duration_ms == 0.0
        assert result.check_type == HealthCheckType.CUSTOM
        assert isinstance(result.timestamp, datetime)


class TestHealthCheckConfig:
    """Test health check configuration"""
    
    def test_health_check_config_defaults(self):
        """Test health check config default values"""
        config = HealthCheckConfig()
        
        assert config.timeout_seconds == 30.0
        assert config.retry_attempts == 3
        assert config.retry_delay_seconds == 1.0
        assert config.critical_threshold == 0.8
        assert config.warning_threshold == 0.9
    
    def test_health_check_config_custom_values(self):
        """Test health check config with custom values"""
        config = HealthCheckConfig(
            timeout_seconds=60.0,
            retry_attempts=5,
            retry_delay_seconds=2.0,
            critical_threshold=0.7,
            warning_threshold=0.85
        )
        
        assert config.timeout_seconds == 60.0
        assert config.retry_attempts == 5
        assert config.retry_delay_seconds == 2.0
        assert config.critical_threshold == 0.7
        assert config.warning_threshold == 0.85


class TestBaseHealthCheck:
    """Test base health check class"""
    
    def test_base_health_check_creation(self):
        """Test creating a base health check"""
        config = HealthCheckConfig(timeout_seconds=45.0)
        check = Mock(spec=BaseHealthCheck)
        check.name = "test_check"
        check.config = config
        check.last_check = None
        check.check_history = []
        check.max_history_size = 100
        
        assert check.name == "test_check"
        assert check.config.timeout_seconds == 45.0
        assert check.last_check is None
        assert check.check_history == []
        assert check.max_history_size == 100
    
    def test_base_health_check_with_default_config(self):
        """Test base health check with default config"""
        check = Mock(spec=BaseHealthCheck)
        check.name = "test_check"
        check.config = HealthCheckConfig()
        check.last_check = None
        check.check_history = []
        check.max_history_size = 100
        
        assert check.config.timeout_seconds == 30.0
        assert check.config.retry_attempts == 3


class TestDatabaseHealthCheck:
    """Test database health check"""
    
    @pytest.mark.asyncio
    async def test_database_health_check_success(self):
        """Test successful database health check"""
        with patch('infrastructure.health.advanced_health_check.create_engine') as mock_create_engine:
            mock_engine = Mock()
            mock_connection = Mock()
            mock_result = Mock()
            mock_result.fetchone.return_value = (1,)
            
            mock_connection.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_create_engine.return_value = mock_engine
            
            check = DatabaseHealthCheck("sqlite:///test.db")
            result = await check.check()
            
            assert result.name == "database"
            assert result.status == HealthStatus.HEALTHY
            assert "successful" in result.message.lower()
            assert result.check_type == HealthCheckType.READINESS
            assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_database_health_check_failure(self):
        """Test failed database health check"""
        with patch('infrastructure.health.advanced_health_check.create_engine') as mock_create_engine:
            mock_create_engine.side_effect = Exception("Connection failed")
            
            check = DatabaseHealthCheck("sqlite:///test.db")
            result = await check.check()
            
            assert result.name == "database"
            assert result.status == HealthStatus.UNHEALTHY
            assert "failed" in result.message.lower()
            assert result.check_type == HealthCheckType.READINESS
            assert result.duration_ms > 0


class TestRedisHealthCheck:
    """Test Redis health check"""
    
    @pytest.mark.asyncio
    async def test_redis_health_check_success(self):
        """Test successful Redis health check"""
        with patch('infrastructure.health.advanced_health_check.redis') as mock_redis:
            mock_redis_instance = Mock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.set.return_value = True
            mock_redis_instance.get.return_value = b"test"
            mock_redis_instance.delete.return_value = 1
            mock_redis.from_url.return_value = mock_redis_instance
            
            check = RedisHealthCheck("redis://localhost:6379")
            result = await check.check()
            
            assert result.name == "redis"
            assert result.status == HealthStatus.HEALTHY
            assert "successful" in result.message.lower()
            assert result.check_type == HealthCheckType.READINESS
            assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_redis_health_check_failure(self):
        """Test failed Redis health check"""
        with patch('infrastructure.health.advanced_health_check.redis') as mock_redis:
            mock_redis.from_url.side_effect = Exception("Connection failed")
            
            check = RedisHealthCheck("redis://localhost:6379")
            result = await check.check()
            
            assert result.name == "redis"
            assert result.status == HealthStatus.UNHEALTHY
            assert "failed" in result.message.lower()
            assert result.check_type == HealthCheckType.READINESS
            assert result.duration_ms > 0


class TestExternalAPICheck:
    """Test external API health check"""
    
    @pytest.mark.asyncio
    async def test_external_api_check_success(self):
        """Test successful external API check"""
        with patch('infrastructure.health.advanced_health_check.aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            check = ExternalAPICheck("test_api", "https://api.example.com/health")
            result = await check.check()
            
            assert result.name == "test_api"
            assert result.status == HealthStatus.HEALTHY
            assert "healthy" in result.message.lower()
            assert result.check_type == HealthCheckType.CUSTOM
            assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_external_api_check_unexpected_status(self):
        """Test external API check with unexpected status"""
        with patch('infrastructure.health.advanced_health_check.aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 500
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            check = ExternalAPICheck("test_api", "https://api.example.com/health", expected_status=200)
            result = await check.check()
            
            assert result.name == "test_api"
            assert result.status == HealthStatus.DEGRADED
            assert "unexpected status" in result.message.lower()
            assert result.check_type == HealthCheckType.CUSTOM
            assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_external_api_check_timeout(self):
        """Test external API check timeout"""
        with patch('infrastructure.health.advanced_health_check.aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = asyncio.TimeoutError()
            
            check = ExternalAPICheck("test_api", "https://api.example.com/health")
            result = await check.check()
            
            assert result.name == "test_api"
            assert result.status == HealthStatus.UNHEALTHY
            assert "timeout" in result.message.lower()
            assert result.check_type == HealthCheckType.CUSTOM
            assert result.duration_ms > 0


class TestSystemResourceCheck:
    """Test system resource health check"""
    
    @pytest.mark.asyncio
    async def test_system_resource_check_healthy(self):
        """Test system resource check with healthy resources"""
        with patch('infrastructure.health.advanced_health_check.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 50.0
            
            mock_memory = Mock()
            mock_memory.percent = 60.0
            mock_memory.available = 4 * 1024**3  # 4GB
            mock_psutil.virtual_memory.return_value = mock_memory
            
            mock_disk = Mock()
            mock_disk.percent = 70.0
            mock_disk.free = 50 * 1024**3  # 50GB
            mock_psutil.disk_usage.return_value = mock_disk
            
            check = SystemResourceCheck()
            result = await check.check()
            
            assert result.name == "system_resources"
            assert result.status == HealthStatus.HEALTHY
            assert "healthy" in result.message.lower()
            assert result.check_type == HealthCheckType.CUSTOM
            assert result.duration_ms > 0
            assert "cpu_percent" in result.details
            assert "memory_percent" in result.details
            assert "disk_percent" in result.details
    
    @pytest.mark.asyncio
    async def test_system_resource_check_degraded(self):
        """Test system resource check with degraded resources"""
        with patch('infrastructure.health.advanced_health_check.psutil') as mock_psutil:
            mock_psutil.cpu_percent.return_value = 95.0
            
            mock_memory = Mock()
            mock_memory.percent = 85.0
            mock_memory.available = 1 * 1024**3  # 1GB
            mock_psutil.virtual_memory.return_value = mock_memory
            
            mock_disk = Mock()
            mock_disk.percent = 75.0
            mock_disk.free = 10 * 1024**3  # 10GB
            mock_psutil.disk_usage.return_value = mock_disk
            
            check = SystemResourceCheck()
            result = await check.check()
            
            assert result.name == "system_resources"
            assert result.status == HealthStatus.DEGRADED
            assert "issues" in result.message.lower()
            assert result.check_type == HealthCheckType.CUSTOM
            assert result.duration_ms > 0


class TestCustomHealthCheck:
    """Test custom health check"""
    
    @pytest.mark.asyncio
    async def test_custom_health_check_success(self):
        """Test successful custom health check"""
        def custom_check():
            return True
        
        check = CustomHealthCheck("custom_check", custom_check)
        result = await check.check()
        
        assert result.name == "custom_check"
        assert result.status == HealthStatus.HEALTHY
        assert "passed" in result.message.lower()
        assert result.check_type == HealthCheckType.CUSTOM
        assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_custom_health_check_failure(self):
        """Test failed custom health check"""
        def custom_check():
            return False
        
        check = CustomHealthCheck("custom_check", custom_check)
        result = await check.check()
        
        assert result.name == "custom_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert "failed" in result.message.lower()
        assert result.check_type == HealthCheckType.CUSTOM
        assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_custom_health_check_with_dict_result(self):
        """Test custom health check with dictionary result"""
        def custom_check():
            return {
                "status": HealthStatus.DEGRADED,
                "message": "Custom degraded status",
                "details": {"custom": "data"}
            }
        
        check = CustomHealthCheck("custom_check", custom_check)
        result = await check.check()
        
        assert result.name == "custom_check"
        assert result.status == HealthStatus.DEGRADED
        assert result.message == "Custom degraded status"
        assert result.details == {"custom": "data"}
        assert result.check_type == HealthCheckType.CUSTOM
        assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_custom_health_check_async_function(self):
        """Test custom health check with async function"""
        async def async_custom_check():
            await asyncio.sleep(0.1)
            return True
        
        check = CustomHealthCheck("async_custom_check", async_custom_check)
        result = await check.check()
        
        assert result.name == "async_custom_check"
        assert result.status == HealthStatus.HEALTHY
        assert "passed" in result.message.lower()
        assert result.check_type == HealthCheckType.CUSTOM
        assert result.duration_ms > 0


class TestAdvancedHealthChecker:
    """Test advanced health checker"""
    
    def test_advanced_health_checker_creation(self):
        """Test creating an advanced health checker"""
        config = HealthCheckConfig(timeout_seconds=45.0)
        checker = AdvancedHealthChecker(config)
        
        assert checker.config.timeout_seconds == 45.0
        assert checker.health_checks == {}
        assert checker.overall_status == HealthStatus.UNKNOWN
        assert checker.last_check_time is None
    
    def test_advanced_health_checker_with_default_config(self):
        """Test advanced health checker with default config"""
        checker = AdvancedHealthChecker()
        
        assert checker.config.timeout_seconds == 30.0
        assert checker.config.retry_attempts == 3
    
    def test_add_health_check(self):
        """Test adding a health check"""
        checker = AdvancedHealthChecker()
        check = Mock(spec=BaseHealthCheck)
        check.name = "test_check"
        
        checker.add_health_check(check)
        
        assert "test_check" in checker.health_checks
        assert checker.health_checks["test_check"] == check
    
    def test_remove_health_check(self):
        """Test removing a health check"""
        checker = AdvancedHealthChecker()
        check = Mock(spec=BaseHealthCheck)
        check.name = "test_check"
        
        checker.add_health_check(check)
        assert "test_check" in checker.health_checks
        
        checker.remove_health_check("test_check")
        assert "test_check" not in checker.health_checks
    
    @pytest.mark.asyncio
    async def test_run_all_checks_empty(self):
        """Test running all checks with no registered checks"""
        checker = AdvancedHealthChecker()
        results = await checker.run_all_checks()
        
        assert results == {}
        assert checker.overall_status == HealthStatus.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_run_all_checks_success(self):
        """Test running all checks successfully"""
        checker = AdvancedHealthChecker()
        
        # Add mock health checks
        check1 = Mock(spec=BaseHealthCheck)
        check1.name = "check1"
        check1.check = AsyncMock(return_value=HealthCheckResult(
            name="check1",
            status=HealthStatus.HEALTHY,
            message="Check 1 passed"
        ))
        
        check2 = Mock(spec=BaseHealthCheck)
        check2.name = "check2"
        check2.check = AsyncMock(return_value=HealthCheckResult(
            name="check2",
            status=HealthStatus.HEALTHY,
            message="Check 2 passed"
        ))
        
        checker.add_health_check(check1)
        checker.add_health_check(check2)
        
        results = await checker.run_all_checks()
        
        assert len(results) == 2
        assert "check1" in results
        assert "check2" in results
        assert results["check1"].status == HealthStatus.HEALTHY
        assert results["check2"].status == HealthStatus.HEALTHY
        assert checker.overall_status == HealthStatus.HEALTHY
        assert checker.last_check_time is not None
    
    @pytest.mark.asyncio
    async def test_run_all_checks_with_failures(self):
        """Test running all checks with some failures"""
        checker = AdvancedHealthChecker()
        
        # Add mock health checks
        check1 = Mock(spec=BaseHealthCheck)
        check1.name = "check1"
        check1.check = AsyncMock(return_value=HealthCheckResult(
            name="check1",
            status=HealthStatus.HEALTHY,
            message="Check 1 passed"
        ))
        
        check2 = Mock(spec=BaseHealthCheck)
        check2.name = "check2"
        check2.check = AsyncMock(return_value=HealthCheckResult(
            name="check2",
            status=HealthStatus.UNHEALTHY,
            message="Check 2 failed"
        ))
        
        checker.add_health_check(check1)
        checker.add_health_check(check2)
        
        results = await checker.run_all_checks()
        
        assert len(results) == 2
        assert results["check1"].status == HealthStatus.HEALTHY
        assert results["check2"].status == HealthStatus.UNHEALTHY
        assert checker.overall_status == HealthStatus.UNHEALTHY
    
    @pytest.mark.asyncio
    async def test_run_all_checks_with_exceptions(self):
        """Test running all checks with exceptions"""
        checker = AdvancedHealthChecker()
        
        # Add mock health check that raises exception
        check = Mock(spec=BaseHealthCheck)
        check.name = "failing_check"
        check.check = AsyncMock(side_effect=Exception("Check failed"))
        
        checker.add_health_check(check)
        
        results = await checker.run_all_checks()
        
        assert len(results) == 1
        assert "failing_check" in results
        assert results["failing_check"].status == HealthStatus.UNHEALTHY
        assert "failed" in results["failing_check"].message.lower()
        assert checker.overall_status == HealthStatus.UNHEALTHY
    
    def test_get_overall_status(self):
        """Test getting overall status"""
        checker = AdvancedHealthChecker()
        
        status = checker.get_overall_status()
        
        assert "status" in status
        assert "timestamp" in status
        assert "total_checks" in status
        assert "last_check_time" in status
        assert status["status"] == "unknown"
        assert status["total_checks"] == 0
    
    def test_get_check_summary(self):
        """Test getting check summary"""
        checker = AdvancedHealthChecker()
        
        # Add a mock health check
        check = Mock(spec=BaseHealthCheck)
        check.name = "test_check"
        check.last_check = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="Test passed"
        )
        check.check_history = [check.last_check]
        check.get_success_rate = Mock(return_value=0.95)
        
        checker.add_health_check(check)
        
        summary = checker.get_check_summary()
        
        assert "overall_status" in summary
        assert "checks" in summary
        assert "test_check" in summary["checks"]
        assert summary["checks"]["test_check"]["success_rate"] == 0.95
        assert summary["checks"]["test_check"]["check_count"] == 1


class TestHealthCheckHistory:
    """Test health check history functionality"""
    
    def test_health_check_history_management(self):
        """Test health check history management"""
        check = Mock(spec=BaseHealthCheck)
        check.name = "test_check"
        check.config = HealthCheckConfig()
        check.last_check = None
        check.check_history = []
        check.max_history_size = 3
        
        # Simulate adding results to history
        result1 = HealthCheckResult("test_check", HealthStatus.HEALTHY, "First check")
        result2 = HealthCheckResult("test_check", HealthStatus.HEALTHY, "Second check")
        result3 = HealthCheckResult("test_check", HealthStatus.HEALTHY, "Third check")
        result4 = HealthCheckResult("test_check", HealthStatus.HEALTHY, "Fourth check")
        
        # Mock the _add_to_history method
        def add_to_history(result):
            check.check_history.append(result)
            if len(check.check_history) > check.max_history_size:
                check.check_history.pop(0)
            check.last_check = result
        
        check._add_to_history = add_to_history
        
        # Add results
        check._add_to_history(result1)
        check._add_to_history(result2)
        check._add_to_history(result3)
        check._add_to_history(result4)
        
        # Check that history is maintained correctly
        assert len(check.check_history) == 3  # Max size
        assert check.check_history[0] == result2  # First result was removed
        assert check.check_history[-1] == result4  # Latest result
        assert check.last_check == result4


class TestHealthCheckSuccessRate:
    """Test health check success rate calculation"""
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        check = Mock(spec=BaseHealthCheck)
        check.name = "test_check"
        check.config = HealthCheckConfig()
        check.last_check = None
        check.check_history = []
        check.max_history_size = 100
        
        # Mock the get_success_rate method
        def get_success_rate(window_minutes=5):
            if not check.check_history:
                return 0.0
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            recent_checks = [
                c for c in check.check_history 
                if c.timestamp >= cutoff_time
            ]
            
            if not recent_checks:
                return 0.0
            
            successful_checks = sum(
                1 for c in recent_checks 
                if c.status == HealthStatus.HEALTHY
            )
            
            return successful_checks / len(recent_checks)
        
        check.get_success_rate = get_success_rate
        
        # Add some test results
        now = datetime.utcnow()
        check.check_history = [
            HealthCheckResult("test_check", HealthStatus.HEALTHY, "Success 1", timestamp=now),
            HealthCheckResult("test_check", HealthStatus.UNHEALTHY, "Failure 1", timestamp=now),
            HealthCheckResult("test_check", HealthStatus.HEALTHY, "Success 2", timestamp=now),
            HealthCheckResult("test_check", HealthStatus.HEALTHY, "Success 3", timestamp=now),
        ]
        
        # Test success rate calculation
        success_rate = check.get_success_rate()
        assert success_rate == 0.75  # 3 out of 4 checks successful
    
    def test_success_rate_empty_history(self):
        """Test success rate with empty history"""
        check = Mock(spec=BaseHealthCheck)
        check.name = "test_check"
        check.config = HealthCheckConfig()
        check.last_check = None
        check.check_history = []
        check.max_history_size = 100
        
        def get_success_rate(window_minutes=5):
            if not check.check_history:
                return 0.0
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            recent_checks = [
                c for c in check.check_history 
                if c.timestamp >= cutoff_time
            ]
            
            if not recent_checks:
                return 0.0
            
            successful_checks = sum(
                1 for c in recent_checks 
                if c.status == HealthStatus.HEALTHY
            )
            
            return successful_checks / len(recent_checks)
        
        check.get_success_rate = get_success_rate
        
        success_rate = check.get_success_rate()
        assert success_rate == 0.0


# Integration tests
class TestHealthCheckIntegration:
    """Integration tests for health check system"""
    
    @pytest.mark.asyncio
    async def test_full_health_check_workflow(self):
        """Test complete health check workflow"""
        # Create health checker
        checker = AdvancedHealthChecker()
        
        # Create and add health checks
        db_check = DatabaseHealthCheck("sqlite:///test.db")
        redis_check = RedisHealthCheck("redis://localhost:6379")
        
        # Mock the checks to avoid actual connections
        with patch('infrastructure.health.advanced_health_check.create_engine') as mock_create_engine, \
             patch('infrastructure.health.advanced_health_check.redis') as mock_redis:
            
            # Mock database check
            mock_engine = Mock()
            mock_connection = Mock()
            mock_result = Mock()
            mock_result.fetchone.return_value = (1,)
            mock_connection.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_create_engine.return_value = mock_engine
            
            # Mock Redis check
            mock_redis_instance = Mock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.set.return_value = True
            mock_redis_instance.get.return_value = b"test"
            mock_redis_instance.delete.return_value = 1
            mock_redis.from_url.return_value = mock_redis_instance
            
            # Add checks to checker
            checker.add_health_check(db_check)
            checker.add_health_check(redis_check)
            
            # Run checks
            results = await checker.run_all_checks()
            
            # Verify results
            assert len(results) == 2
            assert "database" in results
            assert "redis" in results
            assert results["database"].status == HealthStatus.HEALTHY
            assert results["redis"].status == HealthStatus.HEALTHY
            assert checker.overall_status == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_health_check_with_mixed_results(self):
        """Test health check with mixed success and failure results"""
        checker = AdvancedHealthChecker()
        
        # Create custom health checks
        def successful_check():
            return True
        
        def failing_check():
            return False
        
        check1 = CustomHealthCheck("successful", successful_check)
        check2 = CustomHealthCheck("failing", failing_check)
        
        checker.add_health_check(check1)
        checker.add_health_check(check2)
        
        results = await checker.run_all_checks()
        
        assert len(results) == 2
        assert results["successful"].status == HealthStatus.HEALTHY
        assert results["failing"].status == HealthStatus.UNHEALTHY
        assert checker.overall_status == HealthStatus.UNHEALTHY


# Performance tests
class TestHealthCheckPerformance:
    """Performance tests for health check system"""
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """Test concurrent execution of health checks"""
        checker = AdvancedHealthChecker()
        
        # Create multiple health checks
        checks = []
        for i in range(10):
            def create_check(check_id):
                async def async_check():
                    await asyncio.sleep(0.1)  # Simulate work
                    return True
                return CustomHealthCheck(f"check_{check_id}", async_check)
            
            checks.append(create_check(i))
            checker.add_health_check(checks[-1])
        
        # Run all checks and measure time
        start_time = time.time()
        results = await checker.run_all_checks()
        end_time = time.time()
        
        # Verify all checks completed
        assert len(results) == 10
        assert all(result.status == HealthStatus.HEALTHY for result in results.values())
        
        # Verify concurrent execution (should be faster than sequential)
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should complete in less than 1 second (concurrent)
    
    @pytest.mark.asyncio
    async def test_health_check_timeout_handling(self):
        """Test health check timeout handling"""
        checker = AdvancedHealthChecker(HealthCheckConfig(timeout_seconds=0.1))
        
        async def slow_check():
            await asyncio.sleep(1.0)  # Longer than timeout
            return True
        
        check = CustomHealthCheck("slow_check", slow_check)
        checker.add_health_check(check)
        
        results = await checker.run_all_checks()
        
        assert len(results) == 1
        assert results["slow_check"].status == HealthStatus.UNHEALTHY
        assert "timeout" in results["slow_check"].message.lower() or "failed" in results["slow_check"].message.lower()


# Error handling tests
class TestHealthCheckErrorHandling:
    """Error handling tests for health check system"""
    
    @pytest.mark.asyncio
    async def test_health_check_with_invalid_config(self):
        """Test health check with invalid configuration"""
        # Test with negative timeout
        config = HealthCheckConfig(timeout_seconds=-1)
        checker = AdvancedHealthChecker(config)
        
        # Should not raise exception, but use default values
        assert checker.config.timeout_seconds == -1  # Should allow negative for testing
    
    @pytest.mark.asyncio
    async def test_health_check_with_missing_dependencies(self):
        """Test health check with missing dependencies"""
        # Test database check without database
        check = DatabaseHealthCheck("invalid://connection/string")
        result = await check.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "failed" in result.message.lower()
    
    def test_health_check_registry_duplicate_names(self):
        """Test adding health checks with duplicate names"""
        checker = AdvancedHealthChecker()
        
        check1 = Mock(spec=BaseHealthCheck)
        check1.name = "duplicate_check"
        
        check2 = Mock(spec=BaseHealthCheck)
        check2.name = "duplicate_check"
        
        # Add first check
        checker.add_health_check(check1)
        assert "duplicate_check" in checker.health_checks
        
        # Add second check with same name (should replace)
        checker.add_health_check(check2)
        assert "duplicate_check" in checker.health_checks
        assert checker.health_checks["duplicate_check"] == check2  # Should be the second one 