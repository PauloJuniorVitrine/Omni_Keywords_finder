from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Detecção de Dados Sensíveis
Tracing ID: TEST_SENSITIVE_DATA_DETECTOR_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa testes unitários abrangentes para o sistema
de detecção de dados sensíveis, cobrindo todos os cenários de uso e
validações de segurança enterprise.
"""

import pytest
import tempfile
import shutil
import json
import re
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar o sistema a ser testado
from infrastructure.security.advanced_security_system import SensitiveDataDetector, SecurityLevel

class TestSensitiveDataDetector:
    """
    Testes para SensitiveDataDetector.
    
    Cobre todos os métodos públicos e cenários de erro.
    """
    
    @pytest.fixture
    def detector(self):
        """Cria instância do detector para testes."""
        return SensitiveDataDetector({
            'auto_sanitize': False,
            'max_incidents': 100
        })
    
    @pytest.fixture
    def sample_content_with_sensitive_data(self):
        """Conteúdo de exemplo com dados sensíveis para testes."""
        return """
# Documentação de Configuração

## Configurações AWS
AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_ARN=arn:aws:s3:::my-bucket

## Configurações Google
GOOGLE_API_KEY=AIzaSyB1234567890abcdefghijklmnopqrstuvwxyz
SERVICE_ACCOUNT=123456789012-abcdefghijklmnopqrstuvwxyz123456

## Configurações de Banco
DATABASE_URL=mysql://user:password123@localhost:3306/database
POSTGRES_URL=postgresql://admin:secret456@localhost:5432/postgres

## Configurações de Autenticação
JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
BEARER_TOKEN=Bearer sk-1234567890abcdefghijklmnopqrstuvwxyz

## Configurações de Senha
PASSWORD=minhasenha123
PASSWD=outrasenha456
SENHA=senha789

## Configurações de Secrets
SECRET_KEY=mysecretkey123
API_KEY=myapikey456
TOKEN=mygenerictoken789

## Dados Pessoais
CPF=123.456.789-00
CNPJ=12.345.678/0001-90
CREDIT_CARD=4111111111111111

## Chave Privada
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyz
-----END RSA PRIVATE KEY-----"
"""
    
    @pytest.fixture
    def sample_content_clean(self):
        """Conteúdo limpo sem dados sensíveis."""
        return """
# Documentação Limpa

## Configurações Gerais
DEBUG=True
ENVIRONMENT=production
LOG_LEVEL=INFO

## Configurações de Aplicação
APP_NAME=Omni Keywords Finder
VERSION=1.0.0
DESCRIPTION=Sistema de análise de keywords

## Configurações de Performance
MAX_CONNECTIONS=100
TIMEOUT=30
CACHE_TTL=3600
"""
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        detector = SensitiveDataDetector()
        
        assert detector.config == {}
        assert len(detector.sensitive_patterns) > 0
        assert detector.sanitization_config['replace_with'] == '[REDACTED]'
        assert detector.sanitization_config['preserve_format'] == True
        assert detector.sanitization_config['log_incidents'] == True
        assert detector.sanitization_config['auto_sanitize'] == False
        assert len(detector.incidents) == 0
        assert detector.max_incidents == 1000
    
    def test_init_custom_values(self):
        """Testa inicialização com valores customizados."""
        config = {
            'auto_sanitize': True,
            'max_incidents': 500
        }
        detector = SensitiveDataDetector(config)
        
        assert detector.config == config
        assert detector.sanitization_config['auto_sanitize'] == True
        assert detector.max_incidents == 500
    
    def test_scan_documentation_empty_content(self, detector):
        """Testa escaneamento com conteúdo vazio."""
        result = detector.scan_documentation("")
        
        assert result['sensitive_data_found'] == False
        assert result['incidents'] == []
        assert result['risk_level'] == SecurityLevel.LOW.value
        assert result['recommendations'] == ["Nenhum dado sensível encontrado. Documentação segura."]
        assert result['total_incidents'] == 0
    
    def test_scan_documentation_clean_content(self, detector, sample_content_clean):
        """Testa escaneamento com conteúdo limpo."""
        result = detector.scan_documentation(sample_content_clean)
        
        assert result['sensitive_data_found'] == False
        assert result['incidents'] == []
        assert result['risk_level'] == SecurityLevel.LOW.value
        assert result['total_incidents'] == 0
    
    def test_scan_documentation_aws_keys(self, detector):
        """Testa detecção de AWS keys."""
        content = """
        AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
        AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.CRITICAL.value
        assert result['total_incidents'] >= 2
        
        # Verificar se AWS keys foram detectadas
        aws_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'aws_keys']
        assert len(aws_incidents) >= 2
    
    def test_scan_documentation_google_api_keys(self, detector):
        """Testa detecção de Google API keys."""
        content = """
        GOOGLE_API_KEY=AIzaSyB1234567890abcdefghijklmnopqrstuvwxyz
        SERVICE_ACCOUNT=123456789012-abcdefghijklmnopqrstuvwxyz123456
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.CRITICAL.value
        assert result['total_incidents'] >= 2
        
        # Verificar se Google API keys foram detectadas
        google_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'google_api_keys']
        assert len(google_incidents) >= 2
    
    def test_scan_documentation_passwords(self, detector):
        """Testa detecção de passwords."""
        content = """
        PASSWORD=minhasenha123
        PASSWD=outrasenha456
        PWD=senha789
        SENHA=minhasenha
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.HIGH.value
        assert result['total_incidents'] >= 4
        
        # Verificar se passwords foram detectadas
        password_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'passwords']
        assert len(password_incidents) >= 4
    
    def test_scan_documentation_secrets(self, detector):
        """Testa detecção de secrets."""
        content = """
        SECRET_KEY=mysecretkey123
        API_KEY=myapikey456
        TOKEN=mygenerictoken789
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.HIGH.value
        assert result['total_incidents'] >= 3
        
        # Verificar se secrets foram detectadas
        secret_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'secrets']
        assert len(secret_incidents) >= 3
    
    def test_scan_documentation_tokens(self, detector):
        """Testa detecção de tokens."""
        content = """
        JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
        BEARER_TOKEN=Bearer sk-1234567890abcdefghijklmnopqrstuvwxyz
        GENERIC_TOKEN=abcdef1234567890abcdef1234567890
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.MEDIUM.value
        assert result['total_incidents'] >= 3
        
        # Verificar se tokens foram detectados
        token_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'tokens']
        assert len(token_incidents) >= 3
    
    def test_scan_documentation_database_connections(self, detector):
        """Testa detecção de conexões de banco."""
        content = """
        DATABASE_URL=mysql://user:password123@localhost:3306/database
        POSTGRES_URL=postgresql://admin:secret456@localhost:5432/postgres
        MONGODB_URL=mongodb://user:pass789@localhost:27017/db
        REDIS_URL=redis://user:redispass@localhost:6379
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.HIGH.value
        assert result['total_incidents'] >= 4
        
        # Verificar se conexões de banco foram detectadas
        db_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'database_connections']
        assert len(db_incidents) >= 4
    
    def test_scan_documentation_private_keys(self, detector):
        """Testa detecção de chaves privadas."""
        content = """
        PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyz
        -----END RSA PRIVATE KEY-----"
        
        SSH_KEY="-----BEGIN OPENSSH PRIVATE KEY-----
        b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
        -----END OPENSSH PRIVATE KEY-----"
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.CRITICAL.value
        assert result['total_incidents'] >= 2
        
        # Verificar se chaves privadas foram detectadas
        key_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'private_keys']
        assert len(key_incidents) >= 2
    
    def test_scan_documentation_credit_cards(self, detector):
        """Testa detecção de cartões de crédito."""
        content = """
        VISA=4111111111111111
        MASTERCARD=5555555555554444
        AMEX=378282246310005
        DINERS=3056930009020004
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.CRITICAL.value
        assert result['total_incidents'] >= 4
        
        # Verificar se cartões de crédito foram detectados
        cc_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'credit_cards']
        assert len(cc_incidents) >= 4
    
    def test_scan_documentation_cpf_cnpj(self, detector):
        """Testa detecção de CPF/CNPJ."""
        content = """
        CPF=123.456.789-00
        CNPJ=12.345.678/0001-90
        CPF_SEM_PONTOS=12345678900
        CNPJ_SEM_PONTOS=12345678000190
        """
        
        result = detector.scan_documentation(content)
        
        assert result['sensitive_data_found'] == True
        assert result['risk_level'] == SecurityLevel.HIGH.value
        assert result['total_incidents'] >= 4
        
        # Verificar se CPF/CNPJ foram detectados
        cpf_cnpj_incidents = [inc for inc in result['incidents'] if inc['data_type'] == 'cpf_cnpj']
        assert len(cpf_cnpj_incidents) >= 4
    
    def test_scan_documentation_with_file_path(self, detector):
        """Testa escaneamento com caminho de arquivo."""
        content = "AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF"
        file_path = "/path/to/config.md"
        
        result = detector.scan_documentation(content, file_path)
        
        assert result['sensitive_data_found'] == True
        assert result['incidents'][0]['file_path'] == file_path
    
    def test_sanitize_content_empty(self, detector):
        """Testa sanitização de conteúdo vazio."""
        sanitized_content, report = detector.sanitize_content("")
        
        assert sanitized_content == ""
        assert report['sanitized'] == False
        assert report['replacements_made'] == 0
        assert report['incidents'] == []
    
    def test_sanitize_content_clean(self, detector, sample_content_clean):
        """Testa sanitização de conteúdo limpo."""
        sanitized_content, report = detector.sanitize_content(sample_content_clean)
        
        assert sanitized_content == sample_content_clean
        assert report['sanitized'] == False
        assert report['replacements_made'] == 0
    
    def test_sanitize_content_aws_keys(self, detector):
        """Testa sanitização de AWS keys."""
        content = "AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF"
        
        sanitized_content, report = detector.sanitize_content(content)
        
        assert report['sanitized'] == True
        assert report['replacements_made'] >= 1
        assert "AKIA1234567890ABCDEF" not in sanitized_content
        assert "[REDACTED]" in sanitized_content or "AKIA[REDACTED]ABCDEF" in sanitized_content
    
    def test_sanitize_content_passwords(self, detector):
        """Testa sanitização de passwords."""
        content = "PASSWORD=minhasenha123"
        
        sanitized_content, report = detector.sanitize_content(content)
        
        assert report['sanitized'] == True
        assert report['replacements_made'] >= 1
        assert "minhasenha123" not in sanitized_content
        assert "[REDACTED]" in sanitized_content
    
    def test_sanitize_content_credit_cards(self, detector):
        """Testa sanitização de cartões de crédito."""
        content = "VISA=4111111111111111"
        
        sanitized_content, report = detector.sanitize_content(content)
        
        assert report['sanitized'] == True
        assert report['replacements_made'] >= 1
        assert "4111111111111111" not in sanitized_content
        # Deve manter formato mas substituir números por *
        assert "************1111" in sanitized_content or "[REDACTED]" in sanitized_content
    
    def test_sanitize_content_cpf_cnpj(self, detector):
        """Testa sanitização de CPF/CNPJ."""
        content = "CPF=123.456.789-00"
        
        sanitized_content, report = detector.sanitize_content(content)
        
        assert report['sanitized'] == True
        assert report['replacements_made'] >= 1
        assert "123.456.789-00" not in sanitized_content
        # Deve manter formato mas substituir números por *
        assert "***.***.***-**" in sanitized_content or "[REDACTED]" in sanitized_content
    
    def test_sanitize_content_multiple_types(self, detector):
        """Testa sanitização de múltiplos tipos de dados sensíveis."""
        content = """
        AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
        PASSWORD=minhasenha123
        VISA=4111111111111111
        """
        
        sanitized_content, report = detector.sanitize_content(content)
        
        assert report['sanitized'] == True
        assert report['replacements_made'] >= 3
        assert "AKIA1234567890ABCDEF" not in sanitized_content
        assert "minhasenha123" not in sanitized_content
        assert "4111111111111111" not in sanitized_content
    
    def test_sanitize_content_with_file_path(self, detector):
        """Testa sanitização com caminho de arquivo."""
        content = "PASSWORD=minhasenha123"
        file_path = "/path/to/config.md"
        
        sanitized_content, report = detector.sanitize_content(content, file_path)
        
        assert report['sanitized'] == True
        assert report['incidents'][0]['file_path'] == file_path
    
    def test_get_context(self, detector):
        """Testa obtenção de contexto."""
        content = "Este é um texto de teste com dados sensíveis: PASSWORD=senha123"
        
        # Encontrar posição da senha
        match = re.search(r'PASSWORD=senha123', content)
        start, end = match.span()
        
        context = detector._get_context(content, start, end, context_size=10)
        
        assert "PASSWORD=senha123" in context
        assert len(context) > 0
    
    def test_generate_replacement_preserve_format(self, detector):
        """Testa geração de substituição preservando formato."""
        # Testar AWS key
        replacement = detector._generate_replacement("AKIA1234567890ABCDEF", "aws_keys")
        assert "AKIA" in replacement or "[REDACTED]" in replacement
        
        # Testar cartão de crédito
        replacement = detector._generate_replacement("4111111111111111", "credit_cards")
        assert "************1111" in replacement or "[REDACTED]" in replacement
        
        # Testar CPF
        replacement = detector._generate_replacement("123.456.789-00", "cpf_cnpj")
        assert "***.***.***-**" in replacement or "[REDACTED]" in replacement
    
    def test_generate_recommendations_no_incidents(self, detector):
        """Testa geração de recomendações sem incidentes."""
        recommendations = detector._generate_recommendations([], SecurityLevel.LOW)
        
        assert len(recommendations) == 1
        assert "Nenhum dado sensível encontrado" in recommendations[0]
    
    def test_generate_recommendations_with_incidents(self, detector):
        """Testa geração de recomendações com incidentes."""
        incidents = [
            {'data_type': 'aws_keys', 'severity': SecurityLevel.CRITICAL.value},
            {'data_type': 'passwords', 'severity': SecurityLevel.HIGH.value}
        ]
        
        recommendations = detector._generate_recommendations(incidents, SecurityLevel.CRITICAL)
        
        assert len(recommendations) >= 3
        assert any("AWS Keys" in rec for rec in recommendations)
        assert any("senhas" in rec for rec in recommendations)
        assert any("AÇÃO IMEDIATA" in rec for rec in recommendations)
    
    def test_log_incidents(self, detector):
        """Testa registro de incidentes."""
        incidents = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'data_type': 'aws_keys',
                'severity': SecurityLevel.CRITICAL.value,
                'description': 'AWS Keys detectadas'
            }
        ]
        
        initial_count = len(detector.incidents)
        detector._log_incidents(incidents)
        
        assert len(detector.incidents) == initial_count + 1
        assert detector.incidents[-1]['data_type'] == 'aws_keys'
    
    def test_log_incidents_max_limit(self, detector):
        """Testa limite máximo de incidentes."""
        # Configurar limite baixo para teste
        detector.max_incidents = 2
        
        # Adicionar 3 incidentes
        incidents = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'data_type': 'test',
                'severity': SecurityLevel.LOW.value,
                'description': 'Test incident'
            }
        ]
        
        detector._log_incidents(incidents)  # Incidente 1
        detector._log_incidents(incidents)  # Incidente 2
        detector._log_incidents(incidents)  # Incidente 3 (deve remover o 1)
        
        assert len(detector.incidents) == 2
    
    def test_get_incident_report(self, detector):
        """Testa geração de relatório de incidentes."""
        # Adicionar alguns incidentes
        incidents = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'data_type': 'aws_keys',
                'severity': SecurityLevel.CRITICAL.value
            },
            {
                'timestamp': datetime.utcnow().isoformat(),
                'data_type': 'passwords',
                'severity': SecurityLevel.HIGH.value
            }
        ]
        detector._log_incidents(incidents)
        
        report = detector.get_incident_report()
        
        assert 'period' in report
        assert 'total_incidents' in report
        assert 'stats_by_type' in report
        assert 'stats_by_severity' in report
        assert 'incidents' in report
        assert report['total_incidents'] >= 2
    
    def test_get_incident_report_with_dates(self, detector):
        """Testa geração de relatório com datas específicas."""
        # Adicionar incidente antigo
        old_incident = {
            'timestamp': (datetime.utcnow() - timedelta(days=60)).isoformat(),
            'data_type': 'aws_keys',
            'severity': SecurityLevel.CRITICAL.value
        }
        detector._log_incidents([old_incident])
        
        # Adicionar incidente recente
        recent_incident = {
            'timestamp': datetime.utcnow().isoformat(),
            'data_type': 'passwords',
            'severity': SecurityLevel.HIGH.value
        }
        detector._log_incidents([recent_incident])
        
        # Relatório dos últimos 30 dias
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        report = detector.get_incident_report(start_date, end_date)
        
        # Deve incluir apenas o incidente recente
        assert report['total_incidents'] >= 1
        recent_incidents = [inc for inc in report['incidents'] if inc['data_type'] == 'passwords']
        assert len(recent_incidents) >= 1
    
    def test_is_healthy(self, detector):
        """Testa verificação de saúde do detector."""
        assert detector.is_healthy() == True
        
        # Testar com padrões vazios (não deve acontecer na prática)
        detector.sensitive_patterns = {}
        assert detector.is_healthy() == False

class TestSensitiveDataDetectorIntegration:
    """
    Testes de integração para SensitiveDataDetector.
    
    Testa cenários mais complexos e workflows completos.
    """
    
    @pytest.fixture
    def integration_detector(self):
        """Cria detector para testes de integração."""
        return SensitiveDataDetector({
            'auto_sanitize': True,
            'max_incidents': 1000
        })
    
    def test_full_workflow_scan_and_sanitize(self, integration_detector):
        """Testa workflow completo de escaneamento e sanitização."""
        content = """
        # Configuração de Produção
        
        ## AWS
        AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
        AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        
        ## Banco de Dados
        DATABASE_URL=mysql://user:password123@localhost:3306/prod
        
        ## Autenticação
        JWT_SECRET=mysecretkey123
        """
        
        # 1. Escanear conteúdo
        scan_result = integration_detector.scan_documentation(content, "config.md")
        
        assert scan_result['sensitive_data_found'] == True
        assert scan_result['risk_level'] == SecurityLevel.CRITICAL.value
        assert scan_result['total_incidents'] >= 4
        
        # 2. Sanitizar conteúdo
        sanitized_content, sanitize_report = integration_detector.sanitize_content(content, "config.md")
        
        assert sanitize_report['sanitized'] == True
        assert sanitize_report['replacements_made'] >= 4
        
        # 3. Verificar que dados sensíveis foram removidos
        assert "AKIA1234567890ABCDEF" not in sanitized_content
        assert "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" not in sanitized_content
        assert "password123" not in sanitized_content
        assert "mysecretkey123" not in sanitized_content
        
        # 4. Verificar que estrutura foi mantida
        assert "# Configuração de Produção" in sanitized_content
        assert "## AWS" in sanitized_content
        assert "## Banco de Dados" in sanitized_content
        assert "## Autenticação" in sanitized_content
    
    def test_multiple_file_processing(self, integration_detector):
        """Testa processamento de múltiplos arquivos."""
        files = {
            "config.md": "AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF",
            "secrets.env": "PASSWORD=minhasenha123",
            "docs/api.md": "JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "clean.md": "Este é um arquivo limpo sem dados sensíveis."
        }
        
        total_incidents = 0
        
        for file_path, content in files.items():
            result = integration_detector.scan_documentation(content, file_path)
            total_incidents += result['total_incidents']
        
        assert total_incidents >= 3  # 3 arquivos com dados sensíveis
        
        # Verificar relatório geral
        report = integration_detector.get_incident_report()
        assert report['total_incidents'] >= 3
    
    def test_error_handling_robustness(self, integration_detector):
        """Testa robustez no tratamento de erros."""
        # Testar com conteúdo que pode causar problemas de regex
        problematic_content = "PASSWORD=" + "a" * 10000  # String muito longa
        
        # Não deve falhar
        result = integration_detector.scan_documentation(problematic_content)
        assert isinstance(result, dict)
        assert 'sensitive_data_found' in result
        
        # Testar sanitização
        sanitized_content, report = integration_detector.sanitize_content(problematic_content)
        assert isinstance(sanitized_content, str)
        assert isinstance(report, dict)
    
    def test_performance_with_large_content(self, integration_detector):
        """Testa performance com conteúdo grande."""
        # Criar conteúdo grande com dados sensíveis espalhados
        large_content = []
        for index in range(1000):
            if index % 100 == 0:
                large_content.append(f"PASSWORD=senha{index}")
            else:
                large_content.append(f"Linha {index} sem dados sensíveis")
        
        content = "\n".join(large_content)
        
        # Medir tempo de escaneamento
        import time
        start_time = time.time()
        result = integration_detector.scan_documentation(content)
        scan_time = time.time() - start_time
        
        # Deve ser rápido (< 1 segundo para 1000 linhas)
        assert scan_time < 1.0
        assert result['sensitive_data_found'] == True
        assert result['total_incidents'] >= 10  # 10 senhas espalhadas
    
    def test_recommendations_quality(self, integration_detector):
        """Testa qualidade das recomendações geradas."""
        content = """
        AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
        PASSWORD=minhasenha123
        VISA=4111111111111111
        CPF=123.456.789-00
        """
        
        result = integration_detector.scan_documentation(content)
        recommendations = result['recommendations']
        
        # Verificar se recomendações específicas foram geradas
        aws_recommendation = any("AWS Keys" in rec for rec in recommendations)
        password_recommendation = any("senhas" in rec for rec in recommendations)
        credit_card_recommendation = any("cartão" in rec for rec in recommendations)
        cpf_recommendation = any("CPF/CNPJ" in rec for rec in recommendations)
        general_recommendation = any("CI/CD" in rec for rec in recommendations)
        
        assert aws_recommendation
        assert password_recommendation
        assert credit_card_recommendation
        assert cpf_recommendation
        assert general_recommendation 