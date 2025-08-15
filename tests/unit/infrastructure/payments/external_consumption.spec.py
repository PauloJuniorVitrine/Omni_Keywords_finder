"""
Testes Unitários para Validação de Consumo Externo - Omni Keywords Finder
Testes abrangentes para schemas e validação de APIs externas
Prompt: Validação de consumo externo
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import re
from datetime import datetime, timedelta
from pydantic import ValidationError
from unittest.mock import Mock, patch

from app.schemas.external_consumption_schemas import (
    ExternalEndpointSchema,
    ExternalRequestSchema,
    ExternalResponseSchema,
    ExternalFilterSchema,
    ExternalHealthSchema,
    ExternalConfigSchema,
    ExternalMetricsSchema
)

class TestExternalEndpointSchema:
    """Testes para validação de endpoints externos"""
    
    def test_valid_endpoint(self):
        """Testa endpoint válido"""
        data = {"endpoint": "/api/users"}
        schema = ExternalEndpointSchema(**data)
        assert schema.endpoint == "/api/users"
        assert schema.method == "GET"
    
    def test_endpoint_with_method(self):
        """Testa endpoint com método específico"""
        data = {"endpoint": "/api/users", "method": "POST"}
        schema = ExternalEndpointSchema(**data)
        assert schema.method == "POST"
    
    def test_endpoint_with_timeout(self):
        """Testa endpoint com timeout"""
        data = {"endpoint": "/api/users", "timeout": 30}
        schema = ExternalEndpointSchema(**data)
        assert schema.timeout == 30
    
    def test_endpoint_with_retry_count(self):
        """Testa endpoint com número de tentativas"""
        data = {"endpoint": "/api/users", "retry_count": 3}
        schema = ExternalEndpointSchema(**data)
        assert schema.retry_count == 3
    
    def test_invalid_endpoint_empty(self):
        """Testa endpoint vazio"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalEndpointSchema(endpoint="")
        assert "ensure this value has at least 1 characters" in str(exc_info.value)
    
    def test_invalid_endpoint_too_long(self):
        """Testa endpoint muito longo"""
        long_endpoint = "/" + "a" * 501
        with pytest.raises(ValidationError) as exc_info:
            ExternalEndpointSchema(endpoint=long_endpoint)
        assert "ensure this value has at most 500 characters" in str(exc_info.value)
    
    def test_endpoint_with_dangerous_characters(self):
        """Testa endpoint com caracteres perigosos"""
        dangerous_endpoints = [
            "/api/users<script>alert('xss')</script>",
            "/api/users' OR 1=1--",
            "/api/users\"; DROP TABLE users; --",
            "/api/users<>&\"'"
        ]
        
        for endpoint in dangerous_endpoints:
            schema = ExternalEndpointSchema(endpoint=endpoint)
            # Verifica se caracteres perigosos foram removidos
            assert "<" not in schema.endpoint
            assert ">" not in schema.endpoint
            assert '"' not in schema.endpoint
            assert "'" not in schema.endpoint
    
    def test_endpoint_path_traversal_prevention(self):
        """Testa prevenção de path traversal"""
        traversal_endpoints = [
            "/api/users/../../../etc/passwd",
            "/api/users//etc/passwd",
            "/api/users/..\\windows\\system32\\config\\sam"
        ]
        
        for endpoint in traversal_endpoints:
            with pytest.raises(ValidationError) as exc_info:
                ExternalEndpointSchema(endpoint=endpoint)
            assert "sequências perigosas" in str(exc_info.value)
    
    def test_invalid_method(self):
        """Testa método HTTP inválido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalEndpointSchema(endpoint="/api/users", method="INVALID")
        assert "Método HTTP inválido" in str(exc_info.value)
    
    def test_timeout_out_of_range(self):
        """Testa timeout fora do range permitido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalEndpointSchema(endpoint="/api/users", timeout=0)
        assert "ensure this value is greater than or equal to 1" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ExternalEndpointSchema(endpoint="/api/users", timeout=301)
        assert "ensure this value is less than or equal to 300" in str(exc_info.value)
    
    def test_retry_count_out_of_range(self):
        """Testa número de tentativas fora do range permitido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalEndpointSchema(endpoint="/api/users", retry_count=-1)
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ExternalEndpointSchema(endpoint="/api/users", retry_count=6)
        assert "ensure this value is less than or equal to 5" in str(exc_info.value)

class TestExternalRequestSchema:
    """Testes para validação de requisições externas"""
    
    def test_valid_request(self):
        """Testa requisição válida"""
        data = {
            "endpoint": "/api/users",
            "method": "POST",
            "params": {"page": 1},
            "headers": {"Content-Type": "application/json"},
            "body": {"name": "John Doe"}
        }
        schema = ExternalRequestSchema(**data)
        assert schema.endpoint == "/api/users"
        assert schema.method == "POST"
        assert schema.params == {"page": 1}
        assert schema.headers == {"Content-Type": "application/json"}
        assert schema.body == {"name": "John Doe"}
    
    def test_request_with_dangerous_params(self):
        """Testa requisição com parâmetros perigosos"""
        data = {
            "endpoint": "/api/users",
            "params": {
                "name": "<script>alert('xss')</script>",
                "query": "'; DROP TABLE users; --"
            }
        }
        schema = ExternalRequestSchema(**data)
        # Verifica se caracteres perigosos foram removidos
        assert "<" not in schema.params["name"]
        assert ">" not in schema.params["name"]
        assert "'" not in schema.params["query"]
    
    def test_request_with_dangerous_headers(self):
        """Testa requisição com headers perigosos"""
        data = {
            "endpoint": "/api/users",
            "headers": {
                "X-Custom-Header": "<script>alert('xss')</script>",
                "Authorization": "Bearer <script>alert('xss')</script>"
            }
        }
        schema = ExternalRequestSchema(**data)
        # Verifica se caracteres perigosos foram removidos
        for value in schema.headers.values():
            assert "<" not in value
            assert ">" not in value
    
    def test_request_with_dangerous_body(self):
        """Testa requisição com corpo perigoso"""
        data = {
            "endpoint": "/api/users",
            "body": {
                "name": "<script>alert('xss')</script>",
                "email": "user@example.com<script>alert('xss')</script>"
            }
        }
        schema = ExternalRequestSchema(**data)
        # Verifica se caracteres perigosos foram removidos
        assert "<" not in schema.body["name"]
        assert ">" not in schema.body["name"]
        assert "<" not in schema.body["email"]
        assert ">" not in schema.body["email"]
    
    def test_timeout_validation(self):
        """Testa validação de timeout"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalRequestSchema(endpoint="/api/users", timeout=0)
        assert "ensure this value is greater than or equal to 1" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ExternalRequestSchema(endpoint="/api/users", timeout=301)
        assert "ensure this value is less than or equal to 300" in str(exc_info.value)

class TestExternalResponseSchema:
    """Testes para validação de respostas externas"""
    
    def test_valid_response(self):
        """Testa resposta válida"""
        data = {
            "status_code": 200,
            "data": {"users": []},
            "headers": {"Content-Type": "application/json"},
            "response_time": 0.5
        }
        schema = ExternalResponseSchema(**data)
        assert schema.status_code == 200
        assert schema.data == {"users": []}
        assert schema.headers == {"Content-Type": "application/json"}
        assert schema.response_time == 0.5
    
    def test_response_with_malicious_data(self):
        """Testa resposta com dados maliciosos"""
        data = {
            "status_code": 200,
            "data": "<script>alert('xss')</script>"
        }
        schema = ExternalResponseSchema(**data)
        # Verifica se scripts foram removidos
        assert "<script>" not in schema.data
        assert "</script>" not in schema.data
    
    def test_invalid_status_code(self):
        """Testa código de status inválido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalResponseSchema(status_code=99)
        assert "ensure this value is greater than or equal to 100" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ExternalResponseSchema(status_code=600)
        assert "ensure this value is less than or equal to 599" in str(exc_info.value)
    
    def test_negative_response_time(self):
        """Testa tempo de resposta negativo"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalResponseSchema(status_code=200, response_time=-1.0)
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)

class TestExternalFilterSchema:
    """Testes para validação de filtros"""
    
    def test_valid_filters(self):
        """Testa filtros válidos"""
        data = {
            "endpoint": "/api/users",
            "method": "GET",
            "status_code": 200,
            "min_response_time": 0.1,
            "max_response_time": 2.0,
            "limit": 100,
            "offset": 0
        }
        schema = ExternalFilterSchema(**data)
        assert schema.endpoint == "/api/users"
        assert schema.method == "GET"
        assert schema.status_code == 200
        assert schema.min_response_time == 0.1
        assert schema.max_response_time == 2.0
        assert schema.limit == 100
        assert schema.offset == 0
    
    def test_invalid_method(self):
        """Testa método inválido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalFilterSchema(method="INVALID")
        assert "Método HTTP inválido" in str(exc_info.value)
    
    def test_invalid_status_code(self):
        """Testa código de status inválido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalFilterSchema(status_code=99)
        assert "ensure this value is greater than or equal to 100" in str(exc_info.value)
    
    def test_invalid_response_time_range(self):
        """Testa range de tempo de resposta inválido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalFilterSchema(min_response_time=2.0, max_response_time=1.0)
        assert "Tempo mínimo não pode ser maior que tempo máximo" in str(exc_info.value)
    
    def test_invalid_date_range(self):
        """Testa range de datas inválido"""
        start_date = datetime.utcnow()
        end_date = start_date - timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc_info:
            ExternalFilterSchema(start_date=start_date, end_date=end_date)
        assert "Data inicial não pode ser posterior à data final" in str(exc_info.value)
    
    def test_limit_out_of_range(self):
        """Testa limite fora do range permitido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalFilterSchema(limit=0)
        assert "ensure this value is greater than or equal to 1" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ExternalFilterSchema(limit=1001)
        assert "ensure this value is less than or equal to 1000" in str(exc_info.value)
    
    def test_negative_offset(self):
        """Testa offset negativo"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalFilterSchema(offset=-1)
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)

class TestExternalHealthSchema:
    """Testes para validação de health check"""
    
    def test_valid_health_data(self):
        """Testa dados de health válidos"""
        data = {
            "endpoint": "/api/users",
            "status": "healthy",
            "response_time": 0.5
        }
        schema = ExternalHealthSchema(**data)
        assert schema.endpoint == "/api/users"
        assert schema.status == "healthy"
        assert schema.response_time == 0.5
    
    def test_invalid_status(self):
        """Testa status inválido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalHealthSchema(endpoint="/api/users", status="invalid", response_time=0.5)
        assert "Status inválido" in str(exc_info.value)
    
    def test_negative_response_time(self):
        """Testa tempo de resposta negativo"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalHealthSchema(endpoint="/api/users", status="healthy", response_time=-1.0)
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)
    
    def test_malicious_error_message(self):
        """Testa mensagem de erro maliciosa"""
        data = {
            "endpoint": "/api/users",
            "status": "unhealthy",
            "response_time": 0.5,
            "error_message": "<script>alert('xss')</script>"
        }
        schema = ExternalHealthSchema(**data)
        # Verifica se caracteres perigosos foram removidos
        assert "<" not in schema.error_message
        assert ">" not in schema.error_message

class TestExternalConfigSchema:
    """Testes para validação de configuração"""
    
    def test_valid_config(self):
        """Testa configuração válida"""
        data = {
            "base_url": "https://api.example.com",
            "api_key": "sk_test_123456789",
            "timeout": 30,
            "max_retries": 3,
            "rate_limit": 100,
            "allowed_endpoints": ["/api/users", "/api/posts"]
        }
        schema = ExternalConfigSchema(**data)
        assert str(schema.base_url) == "https://api.example.com"
        assert schema.api_key == "sk_test_123456789"
        assert schema.timeout == 30
        assert schema.max_retries == 3
        assert schema.rate_limit == 100
        assert schema.allowed_endpoints == ["/api/users", "/api/posts"]
    
    def test_malicious_api_key(self):
        """Testa chave de API maliciosa"""
        data = {
            "base_url": "https://api.example.com",
            "api_key": "<script>alert('xss')</script>"
        }
        schema = ExternalConfigSchema(**data)
        # Verifica se caracteres perigosos foram removidos
        assert "<" not in schema.api_key
        assert ">" not in schema.api_key
    
    def test_malicious_allowed_endpoints(self):
        """Testa endpoints permitidos maliciosos"""
        data = {
            "base_url": "https://api.example.com",
            "allowed_endpoints": [
                "/api/users<script>alert('xss')</script>",
                "/api/posts' OR 1=1--"
            ]
        }
        schema = ExternalConfigSchema(**data)
        # Verifica se caracteres perigosos foram removidos
        for endpoint in schema.allowed_endpoints:
            assert "<" not in endpoint
            assert ">" not in endpoint
            assert "'" not in endpoint
    
    def test_timeout_out_of_range(self):
        """Testa timeout fora do range permitido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalConfigSchema(base_url="https://api.example.com", timeout=0)
        assert "ensure this value is greater than or equal to 1" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ExternalConfigSchema(base_url="https://api.example.com", timeout=301)
        assert "ensure this value is less than or equal to 300" in str(exc_info.value)
    
    def test_max_retries_out_of_range(self):
        """Testa número máximo de tentativas fora do range permitido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalConfigSchema(base_url="https://api.example.com", max_retries=-1)
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ExternalConfigSchema(base_url="https://api.example.com", max_retries=11)
        assert "ensure this value is less than or equal to 10" in str(exc_info.value)

class TestExternalMetricsSchema:
    """Testes para validação de métricas"""
    
    def test_valid_metrics(self):
        """Testa métricas válidas"""
        data = {
            "total_requests": 100,
            "successful_requests": 95,
            "failed_requests": 5,
            "avg_response_time": 0.5,
            "max_response_time": 2.0,
            "min_response_time": 0.1,
            "error_rate": 0.05
        }
        schema = ExternalMetricsSchema(**data)
        assert schema.total_requests == 100
        assert schema.successful_requests == 95
        assert schema.failed_requests == 5
        assert schema.avg_response_time == 0.5
        assert schema.max_response_time == 2.0
        assert schema.min_response_time == 0.1
        assert schema.error_rate == 0.05
    
    def test_inconsistent_metrics(self):
        """Testa métricas inconsistentes"""
        data = {
            "total_requests": 100,
            "successful_requests": 95,
            "failed_requests": 10,  # Deveria ser 5
            "avg_response_time": 0.5,
            "max_response_time": 2.0,
            "min_response_time": 0.1,
            "error_rate": 0.05
        }
        with pytest.raises(ValidationError) as exc_info:
            ExternalMetricsSchema(**data)
        assert "Total de requisições deve ser igual à soma de sucessos e falhas" in str(exc_info.value)
    
    def test_negative_values(self):
        """Testa valores negativos"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalMetricsSchema(
                total_requests=-1,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0.5,
                max_response_time=2.0,
                min_response_time=0.1,
                error_rate=0.05
            )
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)
    
    def test_error_rate_out_of_range(self):
        """Testa taxa de erro fora do range permitido"""
        with pytest.raises(ValidationError) as exc_info:
            ExternalMetricsSchema(
                total_requests=100,
                successful_requests=95,
                failed_requests=5,
                avg_response_time=0.5,
                max_response_time=2.0,
                min_response_time=0.1,
                error_rate=1.5  # Deveria ser <= 1.0
            )
        assert "ensure this value is less than or equal to 1" in str(exc_info.value)

class TestSecurityValidation:
    """Testes específicos de segurança"""
    
    def test_xss_prevention(self):
        """Testa prevenção de XSS"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            # Testa em endpoint
            with pytest.raises(ValidationError):
                ExternalEndpointSchema(endpoint=payload)
            
            # Testa em parâmetros
            schema = ExternalRequestSchema(
                endpoint="/api/users",
                params={"param": payload}
            )
            assert "<script>" not in schema.params["param"]
            assert "javascript:" not in schema.params["param"]
    
    def test_sql_injection_prevention(self):
        """Testa prevenção de SQL Injection"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR 1=1--",
            "' UNION SELECT * FROM users--",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for payload in sql_payloads:
            # Testa em endpoint
            with pytest.raises(ValidationError):
                ExternalEndpointSchema(endpoint=payload)
            
            # Testa em parâmetros
            schema = ExternalRequestSchema(
                endpoint="/api/users",
                params={"query": payload}
            )
            assert "'" not in schema.params["query"]
            assert ";" not in schema.params["query"]
    
    def test_path_traversal_prevention(self):
        """Testa prevenção de Path Traversal"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\windows\\system32\\config\\sam"
        ]
        
        for payload in traversal_payloads:
            with pytest.raises(ValidationError) as exc_info:
                ExternalEndpointSchema(endpoint=payload)
            assert "sequências perigosas" in str(exc_info.value)
    
    def test_command_injection_prevention(self):
        """Testa prevenção de Command Injection"""
        command_payloads = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& whoami",
            "`id`",
            "$(whoami)"
        ]
        
        for payload in command_payloads:
            with pytest.raises(ValidationError):
                ExternalEndpointSchema(endpoint=payload)

class TestEdgeCases:
    """Testes de casos extremos"""
    
    def test_empty_strings(self):
        """Testa strings vazias"""
        with pytest.raises(ValidationError):
            ExternalEndpointSchema(endpoint="")
        
        # Parâmetros vazios devem ser removidos
        schema = ExternalRequestSchema(
            endpoint="/api/users",
            params={"": "value", "key": ""}
        )
        assert "" not in schema.params
    
    def test_unicode_characters(self):
        """Testa caracteres Unicode"""
        unicode_endpoint = "/api/users/测试/中文"
        schema = ExternalEndpointSchema(endpoint=unicode_endpoint)
        assert schema.endpoint == unicode_endpoint
    
    def test_very_long_strings(self):
        """Testa strings muito longas"""
        long_string = "a" * 1000
        with pytest.raises(ValidationError):
            ExternalEndpointSchema(endpoint=long_string)
    
    def test_special_characters(self):
        """Testa caracteres especiais válidos"""
        special_endpoints = [
            "/api/users/123",
            "/api/users/user-name",
            "/api/users/user_name",
            "/api/users/user.name"
        ]
        
        for endpoint in special_endpoints:
            schema = ExternalEndpointSchema(endpoint=endpoint)
            assert schema.endpoint == endpoint
    
    def test_numeric_values(self):
        """Testa valores numéricos"""
        schema = ExternalRequestSchema(
            endpoint="/api/users",
            params={"page": 1, "limit": 10},
            timeout=30
        )
        assert schema.params["page"] == 1
        assert schema.params["limit"] == 10
        assert schema.timeout == 30

if __name__ == "__main__":
    pytest.main([__file__]) 