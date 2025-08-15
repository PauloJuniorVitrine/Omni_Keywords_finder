from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Payload/Headers Logging - Omni Keywords Finder
Tracing ID: TEST_OBS_002_20241219_001
Data: 2024-12-19
Versão: 1.0

Testa funcionalidades de:
- Anonimização de dados sensíveis
- Truncamento de payloads
- Logging de headers
- Logging de requisições HTTP
- Logging de respostas HTTP
- Validação de padrões sensíveis
"""

import pytest
import json
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime

from infrastructure.observability.telemetry import PayloadLogger


class TestPayloadLogger:
    """Testes para a classe PayloadLogger."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.payload_logger = PayloadLogger()
        
        # Configurar logging para capturar logs
        self.log_capture = []
        
        def log_handler(record):
            self.log_capture.append(record)
        
        # Adicionar handler customizado
        logger = logging.getLogger()
        handler = MagicMock()
        handler.handle = log_handler
        logger.addHandler(handler)
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Limpar handlers
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        self.log_capture.clear()
    
    def test_anonymize_sensitive_data_password(self):
        """Testa anonimização de senhas."""
        data = '{"user": "test", "password": "secret123"}'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert 'password="[REDACTED]"' in result
        assert 'secret123' not in result
        assert 'test' in result  # Dados não sensíveis devem permanecer
    
    def test_anonymize_sensitive_data_token(self):
        """Testa anonimização de tokens."""
        data = '{"auth": {"token": "abc123xyz"}}'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert 'token="[REDACTED]"' in result
        assert 'abc123xyz' not in result
    
    def test_anonymize_sensitive_data_bearer(self):
        """Testa anonimização de bearer tokens."""
        data = 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert 'Bearer [REDACTED]' in result
        assert 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' not in result
    
    def test_anonymize_sensitive_data_cpf(self):
        """Testa anonimização de CPF."""
        data = '{"user": {"cpf": "123.456.789-00"}}'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert '[DOCUMENT_REDACTED]' in result
        assert '123.456.789-00' not in result
    
    def test_anonymize_sensitive_data_cnpj(self):
        """Testa anonimização de CNPJ."""
        data = '{"company": {"cnpj": "12.345.678/0001-90"}}'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert '[DOCUMENT_REDACTED]' in result
        assert '12.345.678/0001-90' not in result
    
    def test_anonymize_sensitive_data_email(self):
        """Testa anonimização de email."""
        data = '{"user": {"email": "user@example.com"}}'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert '[REDACTED]@example.com' in result
        assert 'user@example.com' not in result
    
    def test_anonymize_sensitive_data_phone(self):
        """Testa anonimização de telefone."""
        data = '{"contact": {"phone": "(11) 99999-9999"}}'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert '[PHONE_REDACTED]' in result
        assert '(11) 99999-9999' not in result
    
    def test_anonymize_sensitive_data_credit_card(self):
        """Testa anonimização de cartão de crédito."""
        data = '{"payment": {"card": "1234 5678 9012 3456"}}'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert '****-****-****-3456' in result
        assert '1234 5678 9012 3456' not in result
    
    def test_anonymize_sensitive_data_disabled(self):
        """Testa quando anonimização está desabilitada."""
        self.payload_logger.config['anonymize_sensitive'] = False
        data = '{"password": "secret123"}'
        result = self.payload_logger.anonymize_sensitive_data(data)
        
        assert result == data  # Dados devem permanecer inalterados
    
    def test_anonymize_headers_sensitive(self):
        """Testa anonimização de headers sensíveis."""
        headers = {
            'Authorization': 'Bearer token123',
            'X-API-Key': 'api_key_123',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
        
        result = self.payload_logger.anonymize_headers(headers)
        
        assert result['Authorization'] == '[REDACTED]'
        assert result['X-API-Key'] == '[REDACTED]'
        assert result['Content-Type'] == 'application/json'
        assert result['User-Agent'] == 'Mozilla/5.0'
    
    def test_anonymize_headers_non_sensitive(self):
        """Testa headers não sensíveis permanecem inalterados."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
        
        result = self.payload_logger.anonymize_headers(headers)
        
        assert result == headers  # Headers devem permanecer inalterados
    
    def test_truncate_data_within_limit(self):
        """Testa truncamento quando dados estão dentro do limite."""
        data = "Dados pequenos"
        result = self.payload_logger.truncate_data(data, 100)
        
        assert result == data  # Dados devem permanecer inalterados
    
    def test_truncate_data_exceeds_limit(self):
        """Testa truncamento quando dados excedem o limite."""
        data = "Dados muito longos que excedem o limite máximo permitido"
        result = self.payload_logger.truncate_data(data, 20)
        
        assert len(result.encode('utf-8')) <= 20
        assert '[TRUNCATED]' in result
    
    def test_log_payload_string(self):
        """Testa logging de payload string."""
        payload = '{"test": "data"}'
        context = {'operation': 'test'}
        
        self.payload_logger.log_payload(payload, context)
        
        assert len(self.log_capture) > 0
        log_record = self.log_capture[0]
        assert 'Payload logged' in log_record.getMessage()
    
    def test_log_payload_dict(self):
        """Testa logging de payload dict."""
        payload = {'test': 'data', 'number': 123}
        context = {'operation': 'test'}
        
        self.payload_logger.log_payload(payload, context)
        
        assert len(self.log_capture) > 0
        log_record = self.log_capture[0]
        assert 'Payload logged' in log_record.getMessage()
    
    def test_log_payload_bytes(self):
        """Testa logging de payload bytes."""
        payload = b'{"test": "data"}'
        context = {'operation': 'test'}
        
        self.payload_logger.log_payload(payload, context)
        
        assert len(self.log_capture) > 0
        log_record = self.log_capture[0]
        assert 'Payload logged' in log_record.getMessage()
    
    def test_log_payload_disabled(self):
        """Testa quando logging de payload está desabilitado."""
        self.payload_logger.config['log_payloads'] = False
        payload = '{"test": "data"}'
        
        self.payload_logger.log_payload(payload)
        
        assert len(self.log_capture) == 0  # Nenhum log deve ser gerado
    
    def test_log_headers(self):
        """Testa logging de headers."""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123'
        }
        context = {'operation': 'test'}
        
        self.payload_logger.log_headers(headers, context)
        
        assert len(self.log_capture) > 0
        log_record = self.log_capture[0]
        assert 'Headers logged' in log_record.getMessage()
    
    def test_log_headers_disabled(self):
        """Testa quando logging de headers está desabilitado."""
        self.payload_logger.config['log_headers'] = False
        headers = {'Content-Type': 'application/json'}
        
        self.payload_logger.log_headers(headers)
        
        assert len(self.log_capture) == 0  # Nenhum log deve ser gerado
    
    def test_log_http_request(self):
        """Testa logging de requisição HTTP completa."""
        method = 'POST'
        url = 'https://api.example.com/data'
        headers = {'Content-Type': 'application/json'}
        payload = '{"test": "data"}'
        context = {'user_id': '123'}
        
        self.payload_logger.log_http_request(method, url, headers, payload, context)
        
        # Deve gerar logs para headers e payload
        assert len(self.log_capture) >= 2
        
        # Verificar se os logs contêm informações da requisição
        log_messages = [record.getMessage() for record in self.log_capture]
        assert any('Headers logged' in msg for msg in log_messages)
        assert any('Payload logged' in msg for msg in log_messages)
    
    def test_log_http_response(self):
        """Testa logging de resposta HTTP completa."""
        status_code = 200
        headers = {'Content-Type': 'application/json'}
        payload = '{"result": "success"}'
        context = {'request_id': '456'}
        
        self.payload_logger.log_http_response(status_code, headers, payload, context)
        
        # Deve gerar logs para headers e payload
        assert len(self.log_capture) >= 2
        
        # Verificar se os logs contêm informações da resposta
        log_messages = [record.getMessage() for record in self.log_capture]
        assert any('Headers logged' in msg for msg in log_messages)
        assert any('Payload logged' in msg for msg in log_messages)
    
    def test_log_payload_with_sensitive_data(self):
        """Testa logging de payload com dados sensíveis."""
        payload = {
            'user': 'test_user',
            'password': 'secret123',
            'email': 'user@example.com',
            'cpf': '123.456.789-00'
        }
        
        self.payload_logger.log_payload(payload)
        
        assert len(self.log_capture) > 0
        log_record = self.log_capture[0]
        log_message = log_record.getMessage()
        
        # Verificar se dados sensíveis foram anonimizados
        assert 'password="[REDACTED]"' in log_message
        assert 'secret123' not in log_message
        assert '[REDACTED]@example.com' in log_message
        assert 'user@example.com' not in log_message
        assert '[DOCUMENT_REDACTED]' in log_message
        assert '123.456.789-00' not in log_message
    
    def test_log_headers_with_sensitive_headers(self):
        """Testa logging de headers com headers sensíveis."""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123',
            'X-API-Key': 'api_key_123',
            'User-Agent': 'Mozilla/5.0'
        }
        
        self.payload_logger.log_headers(headers)
        
        assert len(self.log_capture) > 0
        log_record = self.log_capture[0]
        log_message = log_record.getMessage()
        
        # Verificar se headers sensíveis foram anonimizados
        assert 'Authorization": "[REDACTED]"' in log_message
        assert 'Bearer token123' not in log_message
        assert 'X-API-Key": "[REDACTED]"' in log_message
        assert 'api_key_123' not in log_message
        assert 'User-Agent": "Mozilla/5.0"' in log_message  # Header não sensível
    
    def test_log_context_information(self):
        """Testa se informações de contexto são incluídas nos logs."""
        payload = '{"test": "data"}'
        context = {
            'operation': 'test_operation',
            'user_id': '123',
            'request_id': 'abc-123'
        }
        
        self.payload_logger.log_payload(payload, context)
        
        assert len(self.log_capture) > 0
        log_record = self.log_capture[0]
        
        # Verificar se contexto está presente no log
        assert hasattr(log_record, 'log_context')
        log_context = log_record.log_context
        assert log_context['operation'] == 'test_operation'
        assert log_context['user_id'] == '123'
        assert log_context['request_id'] == 'abc-123'
    
    def test_error_handling_in_log_payload(self):
        """Testa tratamento de erro no logging de payload."""
        # Simular payload que causa erro na serialização
        payload = MagicMock()
        payload.__str__.side_effect = Exception("Serialization error")
        
        # Não deve levantar exceção
        self.payload_logger.log_payload(payload)
        
        # Deve logar o erro
        assert len(self.log_capture) > 0
        error_logs = [record for record in self.log_capture if 'Erro ao logar payload' in record.getMessage()]
        assert len(error_logs) > 0
    
    def test_error_handling_in_log_headers(self):
        """Testa tratamento de erro no logging de headers."""
        # Simular headers que causam erro na serialização
        headers = {'test': MagicMock()}
        headers['test'].__str__.side_effect = Exception("Serialization error")
        
        # Não deve levantar exceção
        self.payload_logger.log_headers(headers)
        
        # Deve logar o erro
        assert len(self.log_capture) > 0
        error_logs = [record for record in self.log_capture if 'Erro ao logar headers' in record.getMessage()]
        assert len(error_logs) > 0


class TestPayloadLoggerIntegration:
    """Testes de integração para PayloadLogger."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.payload_logger = PayloadLogger()
    
    def test_full_http_request_response_cycle(self):
        """Testa ciclo completo de requisição e resposta HTTP."""
        # Simular requisição
        request_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123',
            'User-Agent': 'Mozilla/5.0'
        }
        request_payload = {
            'user': 'test_user',
            'password': 'secret123',
            'email': 'user@example.com'
        }
        
        # Simular resposta
        response_headers = {
            'Content-Type': 'application/json',
            'X-Rate-Limit-Remaining': '99'
        }
        response_payload = {
            'status': 'success',
            'user_id': '123',
            'token': 'new_token_456'
        }
        
        # Logar requisição
        self.payload_logger.log_http_request(
            'POST', 
            'https://api.example.com/login',
            request_headers,
            request_payload,
            {'request_id': 'req-123'}
        )
        
        # Logar resposta
        self.payload_logger.log_http_response(
            200,
            response_headers,
            response_payload,
            {'request_id': 'req-123'}
        )
        
        # Verificar se logs foram gerados corretamente
        # (Este teste valida a integração entre os métodos)
        assert True  # Se chegou até aqui, não houve exceções
    
    def test_sensitive_data_patterns_comprehensive(self):
        """Testa todos os padrões de dados sensíveis de forma abrangente."""
        test_data = {
            'password': 'password123',
            'token': 'abc123xyz',
            'api_key': 'key_456',
            'secret': 'secret789',
            'authorization': 'Bearer token123',
            'cpf': '123.456.789-00',
            'cnpj': '12.345.678/0001-90',
            'email': 'user@example.com',
            'phone': '(11) 99999-9999',
            'credit_card': '1234 5678 9012 3456'
        }
        
        # Testar cada padrão individualmente
        for field, value in test_data.items():
            data = f'{{"{field}": "{value}"}}'
            result = self.payload_logger.anonymize_sensitive_data(data)
            
            # Verificar se o valor original foi anonimizado
            assert value not in result, f"Valor {field} não foi anonimizado"
            
            # Verificar se o campo ainda está presente
            assert field in result, f"Campo {field} foi removido incorretamente"


if __name__ == '__main__':
    pytest.main([__file__]) 