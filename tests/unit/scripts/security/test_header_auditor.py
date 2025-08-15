from typing import Dict, List, Optional, Any
"""
Testes Unitários para Header Auditor - Omni Keywords Finder

Testes abrangentes para validação do sistema de auditoria de headers:
- Detecção de headers sensíveis
- Validação de padrões de headers
- Testes de compliance
- Integração com observabilidade
- Relatórios de auditoria
- Configuração de headers permitidos/bloqueados

Autor: Sistema de Testes de Segurança
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: TEST_HEADER_AUDITOR_001
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Importar o módulo a ser testado
import sys
sys.path.append('scripts/security')
from header_auditor import (
    HeaderAuditor, HeaderRiskLevel, HeaderCategory, 
    HeaderViolation, AuditResult, create_header_auditor
)

class TestHeaderAuditor:
    """Testes para o HeaderAuditor"""
    
    @pytest.fixture
    def auditor(self):
        """Fixture para criar auditor de teste"""
        config = {
            'scan_paths': ['.'],
            'excluded_paths': ['.git', 'node_modules'],
            'excluded_files': ['*.log', '*.tmp'],
            'file_extensions': ['.py', '.js', '.json', '.env'],
            'max_file_size_mb': 5,
            'allowed_headers': [
                'Content-Type', 'Accept', 'User-Agent', 'Authorization',
                'X-API-Key', 'X-Webhook-Signature'
            ],
            'blocked_headers': [
                'X-Powered-By', 'X-AspNet-Version', 'Server',
                'X-Application-Name', 'X-Debug-Token'
            ],
            'enable_real_time_validation': True,
            'enable_compliance_reporting': True,
            'alert_on_critical': True,
            'auto_remediation': False
        }
        return HeaderAuditor(config)
    
    @pytest.fixture
    def temp_dir(self):
        """Fixture para criar diretório temporário"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_auditor_initialization(self, auditor):
        """Teste de inicialização do auditor"""
        assert auditor is not None
        assert auditor.config is not None
        assert auditor.sensitive_patterns is not None
        assert len(auditor.sensitive_patterns) > 0
        assert auditor.allowed_headers is not None
        assert auditor.blocked_headers is not None
        assert auditor.audit_history == []
        assert auditor.violation_cache == {}
    
    def test_default_config_loading(self):
        """Teste de carregamento da configuração padrão"""
        auditor = HeaderAuditor()
        config = auditor.config
        
        assert 'scan_paths' in config
        assert 'excluded_paths' in config
        assert 'excluded_files' in config
        assert 'file_extensions' in config
        assert 'allowed_headers' in config
        assert 'blocked_headers' in config
        assert 'max_file_size_mb' in config
    
    def test_sensitive_patterns_loading(self, auditor):
        """Teste de carregamento de padrões sensíveis"""
        patterns = auditor.sensitive_patterns
        
        # Verificar se todas as categorias estão presentes
        expected_categories = [
            HeaderCategory.SECURITY,
            HeaderCategory.IDENTIFICATION,
            HeaderCategory.DEBUGGING,
            HeaderCategory.INTERNAL,
            HeaderCategory.CUSTOM
        ]
        
        for category in expected_categories:
            assert category in patterns
            assert len(patterns[category]) > 0
    
    def test_x_powered_by_detection(self, auditor, temp_dir):
        """Teste de detecção de header X-Powered-By"""
        # Criar arquivo de teste com X-Powered-By
        test_file = Path(temp_dir) / "test_config.py"
        test_content = '''
        headers = {
            "X-Powered-By": "Express/4.17.1",
            "Content-Type": "application/json"
        }
        '''
        test_file.write_text(test_content)
        
        # Executar scan
        violations = auditor.scan_file(str(test_file))
        
        # Verificar resultados
        assert len(violations) >= 1
        
        # Verificar se encontrou X-Powered-By
        x_powered_by_violations = [value for value in violations if "X-Powered-By" in value.header_name]
        assert len(x_powered_by_violations) >= 1
        
        # Verificar severidade
        for violation in x_powered_by_violations:
            assert violation.risk_level == HeaderRiskLevel.HIGH
            assert violation.category == HeaderCategory.SECURITY
    
    def test_server_header_detection(self, auditor, temp_dir):
        """Teste de detecção de header Server"""
        # Criar arquivo de teste com Server header
        test_file = Path(temp_dir) / "test_server.py"
        test_content = '''
        response_headers = {
            "Server": "nginx/1.18.0",
            "Content-Type": "text/html"
        }
        '''
        test_file.write_text(test_content)
        
        # Executar scan
        violations = auditor.scan_file(str(test_file))
        
        # Verificar resultados
        server_violations = [value for value in violations if "Server" in value.header_name]
        assert len(server_violations) >= 1
        
        # Verificar severidade
        for violation in server_violations:
            assert violation.risk_level == HeaderRiskLevel.MEDIUM
            assert violation.category == HeaderCategory.SECURITY
    
    def test_debug_token_detection(self, auditor, temp_dir):
        """Teste de detecção de header X-Debug-Token"""
        # Criar arquivo de teste com X-Debug-Token
        test_file = Path(temp_dir) / "test_debug.py"
        test_content = '''
        debug_headers = {
            "X-Debug-Token": "abc123def456",
            "X-Debug-Token-Link": "/_profiler/abc123def456"
        }
        '''
        test_file.write_text(test_content)
        
        # Executar scan
        violations = auditor.scan_file(str(test_file))
        
        # Verificar resultados
        debug_violations = [value for value in violations if "X-Debug-Token" in value.header_name]
        assert len(debug_violations) >= 2
        
        # Verificar severidade
        for violation in debug_violations:
            assert violation.risk_level == HeaderRiskLevel.HIGH
            assert violation.category == HeaderCategory.DEBUGGING
    
    def test_application_name_detection(self, auditor, temp_dir):
        """Teste de detecção de header X-Application-Name"""
        # Criar arquivo de teste com X-Application-Name
        test_file = Path(temp_dir) / "test_app.py"
        test_content = '''
        app_headers = {
            "X-Application-Name": "OmniKeywordsFinder",
            "X-Application-Version": "1.0.0"
        }
        '''
        test_file.write_text(test_content)
        
        # Executar scan
        violations = auditor.scan_file(str(test_file))
        
        # Verificar resultados
        app_violations = [value for value in violations if "X-Application" in value.header_name]
        assert len(app_violations) >= 2
        
        # Verificar severidade
        for violation in app_violations:
            assert violation.risk_level == HeaderRiskLevel.MEDIUM
            assert violation.category == HeaderCategory.IDENTIFICATION
    
    def test_internal_header_detection(self, auditor, temp_dir):
        """Teste de detecção de headers internos"""
        # Criar arquivo de teste com headers internos
        test_file = Path(temp_dir) / "test_internal.py"
        test_content = '''
        internal_headers = {
            "X-Internal-User": "admin",
            "X-Server-Instance": "prod-01"
        }
        '''
        test_file.write_text(test_content)
        
        # Executar scan
        violations = auditor.scan_file(str(test_file))
        
        # Verificar resultados
        internal_violations = [value for value in violations if "X-Internal" in value.header_name or "X-Server" in value.header_name]
        assert len(internal_violations) >= 2
        
        # Verificar severidade crítica para X-Internal
        critical_violations = [value for value in internal_violations if value.risk_level == HeaderRiskLevel.CRITICAL]
        assert len(critical_violations) >= 1
    
    def test_allowed_headers_ignored(self, auditor, temp_dir):
        """Teste de que headers permitidos são ignorados"""
        # Criar arquivo de teste com headers permitidos
        test_file = Path(temp_dir) / "test_allowed.py"
        test_content = '''
        allowed_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token123",
            "X-API-Key": "api_key_123"
        }
        '''
        test_file.write_text(test_content)
        
        # Executar scan
        violations = auditor.scan_file(str(test_file))
        
        # Verificar que headers permitidos não geram violações
        allowed_violations = [value for value in violations if value.header_name in auditor.allowed_headers]
        assert len(allowed_violations) == 0
    
    def test_blocked_headers_detected(self, auditor, temp_dir):
        """Teste de detecção de headers bloqueados"""
        # Criar arquivo de teste com headers bloqueados
        test_file = Path(temp_dir) / "test_blocked.py"
        test_content = '''
        blocked_headers = {
            "X-Powered-By": "Express",
            "Server": "nginx",
            "X-AspNet-Version": "4.0.30319"
        }
        '''
        test_file.write_text(test_content)
        
        # Executar scan
        violations = auditor.scan_file(str(test_file))
        
        # Verificar que headers bloqueados geram violações
        blocked_violations = [value for value in violations if value.header_name in auditor.blocked_headers]
        assert len(blocked_violations) >= 3
    
    def test_file_exclusion(self, auditor, temp_dir):
        """Teste de exclusão de arquivos"""
        # Criar arquivo que deve ser excluído
        excluded_file = Path(temp_dir) / "test.log"
        excluded_content = 'X-Powered-By: Express'
        excluded_file.write_text(excluded_content)
        
        # Criar arquivo que deve ser incluído
        included_file = Path(temp_dir) / "test.py"
        included_content = 'X-Powered-By: Express'
        included_file.write_text(included_content)
        
        # Executar scan no diretório
        result = auditor.scan_directory(temp_dir)
        
        # Verificar que apenas o arquivo incluído foi processado
        assert result.files_scanned == 1
        assert result.violations_found >= 1
    
    def test_scan_directory(self, auditor, temp_dir):
        """Teste de scan de diretório completo"""
        # Criar múltiplos arquivos de teste
        files = [
            ("config.py", 'X-Powered-By: "Express"'),
            ("headers.json", '{"Server": "nginx"}'),
            ("debug.env", "X-Debug-Token=abc123")
        ]
        
        for filename, content in files:
            file_path = Path(temp_dir) / filename
            file_path.write_text(content)
        
        # Executar scan
        result = auditor.scan_directory(temp_dir)
        
        # Verificar resultados
        assert result.files_scanned >= 3
        assert result.violations_found >= 3
        assert result.audit_duration > 0
        assert result.timestamp is not None
        assert result.compliance_score >= 0
    
    def test_compliance_score_calculation(self, auditor):
        """Teste de cálculo de score de compliance"""
        # Criar violações de diferentes níveis
        violations = [
            HeaderViolation(
                header_name="X-Powered-By",
                header_value="Express",
                risk_level=HeaderRiskLevel.HIGH,
                category=HeaderCategory.SECURITY,
                file_path="test.py",
                line_number=1,
                line_content="X-Powered-By: Express",
                description="Test",
                recommendation="Remove",
                timestamp=datetime.now(),
                hash="test_hash"
            ),
            HeaderViolation(
                header_name="X-Internal-User",
                header_value="admin",
                risk_level=HeaderRiskLevel.CRITICAL,
                category=HeaderCategory.INTERNAL,
                file_path="test.py",
                line_number=2,
                line_content="X-Internal-User: admin",
                description="Test",
                recommendation="Remove",
                timestamp=datetime.now(),
                hash="test_hash"
            )
        ]
        
        # Calcular score
        score = auditor._calculate_compliance_score(violations, 1)
        
        # Verificar score (deve ser menor que 100 devido às violações)
        assert score < 100
        assert score >= 0
    
    def test_risk_breakdown(self, auditor):
        """Teste de breakdown por nível de risco"""
        # Criar violações de diferentes níveis
        violations = [
            HeaderViolation(
                header_name="X-Powered-By",
                header_value="Express",
                risk_level=HeaderRiskLevel.HIGH,
                category=HeaderCategory.SECURITY,
                file_path="test.py",
                line_number=1,
                line_content="X-Powered-By: Express",
                description="Test",
                recommendation="Remove",
                timestamp=datetime.now(),
                hash="test_hash"
            ),
            HeaderViolation(
                header_name="X-Internal-User",
                header_value="admin",
                risk_level=HeaderRiskLevel.CRITICAL,
                category=HeaderCategory.INTERNAL,
                file_path="test.py",
                line_number=2,
                line_content="X-Internal-User: admin",
                description="Test",
                recommendation="Remove",
                timestamp=datetime.now(),
                hash="test_hash"
            )
        ]
        
        # Obter breakdown
        breakdown = auditor._get_risk_breakdown(violations)
        
        # Verificar breakdown
        assert breakdown['critical'] >= 1
        assert breakdown['high'] >= 1
        assert breakdown['medium'] >= 0
        assert breakdown['low'] >= 0
    
    def test_real_time_validation(self, auditor):
        """Teste de validação em tempo real"""
        # Headers de teste
        test_headers = {
            "Content-Type": "application/json",
            "X-Powered-By": "Express",
            "X-Internal-User": "admin",
            "Authorization": "Bearer token123"
        }
        
        # Executar validação
        violations = auditor.validate_headers_in_request(test_headers, "test_source")
        
        # Verificar resultados
        assert len(violations) >= 2  # X-Powered-By e X-Internal-User
        
        # Verificar que headers permitidos não geram violações
        allowed_violations = [value for value in violations if value.header_name in ["Content-Type", "Authorization"]]
        assert len(allowed_violations) == 0
    
    def test_custom_pattern_addition(self, auditor):
        """Teste de adição de padrões customizados"""
        # Adicionar padrão customizado
        auditor.add_custom_pattern(
            HeaderCategory.CUSTOM,
            r'X-Custom-Test["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
            HeaderRiskLevel.MEDIUM,
            "Header customizado de teste",
            "Revisar necessidade do header"
        )
        
        # Verificar se o padrão foi adicionado
        assert HeaderCategory.CUSTOM in auditor.sensitive_patterns
        custom_patterns = auditor.sensitive_patterns[HeaderCategory.CUSTOM]
        assert len(custom_patterns) >= 1
        
        # Verificar se o novo padrão funciona
        test_line = 'X-Custom-Test: "test_value"'
        violations = auditor._scan_line(test_line, "test.py", 1)
        
        custom_violations = [value for value in violations if "X-Custom-Test" in value.header_name]
        assert len(custom_violations) >= 1
    
    def test_audit_history(self, auditor, temp_dir):
        """Teste de histórico de auditorias"""
        # Executar múltiplas auditorias
        for index in range(3):
            test_file = Path(temp_dir) / f"test_{index}.py"
            test_file.write_text(f'X-Powered-By: "Express_{index}"')
            auditor.scan_directory(temp_dir)
        
        # Verificar histórico
        history = auditor.get_audit_history()
        assert len(history) >= 3
    
    def test_statistics(self, auditor, temp_dir):
        """Teste de estatísticas do auditor"""
        # Executar algumas auditorias
        test_file = Path(temp_dir) / "test_stats.py"
        test_file.write_text('X-Powered-By: "Express"')
        auditor.scan_directory(temp_dir)
        
        # Obter estatísticas
        stats = auditor.get_statistics()
        
        # Verificar estatísticas
        assert 'audits_performed' in stats
        assert 'violations_detected' in stats
        assert 'false_positives' in stats
        assert 'average_compliance_score' in stats
        assert stats['audits_performed'] >= 1
    
    def test_report_generation(self, auditor, temp_dir):
        """Teste de geração de relatórios"""
        # Criar arquivo de teste
        test_file = Path(temp_dir) / "test_report.py"
        test_file.write_text('X-Powered-By: "Express"')
        
        # Executar auditoria
        result = auditor.scan_directory(temp_dir)
        
        # Gerar relatório JSON
        json_report = auditor.generate_report(result, 'json')
        
        # Verificar relatório JSON
        assert json_report is not None
        assert len(json_report) > 0
        
        # Verificar formato JSON
        try:
            json_data = json.loads(json_report)
            assert 'audit_id' in json_data
            assert 'summary' in json_data
            assert 'compliance_score' in json_data['summary']
        except json.JSONDecodeError:
            pytest.fail("Relatório JSON não é válido")
        
        # Gerar relatório texto
        text_report = auditor.generate_report(result, 'text')
        
        # Verificar relatório texto
        assert text_report is not None
        assert len(text_report) > 0
        assert "RELATÓRIO DE AUDITORIA DE HEADERS" in text_report
    
    def test_create_header_auditor_function(self):
        """Teste da função factory create_header_auditor"""
        # Criar auditor usando função factory
        auditor = create_header_auditor()
        
        # Verificar que é uma instância válida
        assert isinstance(auditor, HeaderAuditor)
        assert auditor.config is not None
    
    def test_auditor_with_custom_config(self):
        """Teste do auditor com configuração customizada"""
        custom_config = {
            'scan_paths': ['/custom/path'],
            'excluded_paths': ['/custom/exclude'],
            'allowed_headers': ['Custom-Header'],
            'blocked_headers': ['Custom-Blocked'],
            'max_file_size_mb': 20
        }
        
        auditor = HeaderAuditor(custom_config)
        
        # Verificar que configuração customizada foi aplicada
        assert auditor.config['scan_paths'] == ['/custom/path']
        assert auditor.config['excluded_paths'] == ['/custom/exclude']
        assert 'Custom-Header' in auditor.allowed_headers
        assert 'Custom-Blocked' in auditor.blocked_headers
        assert auditor.config['max_file_size_mb'] == 20
    
    def test_hash_generation(self, auditor):
        """Teste de geração de hash único"""
        # Gerar hash
        hash1 = auditor._generate_hash("test.py", 1, "X-Powered-By")
        hash2 = auditor._generate_hash("test.py", 2, "X-Powered-By")
        hash3 = auditor._generate_hash("test.py", 1, "Server")
        
        # Verificar que hashes são únicos
        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3
        
        # Verificar que hash é consistente para mesma entrada
        hash1_again = auditor._generate_hash("test.py", 1, "X-Powered-By")
        assert hash1 == hash1_again

if __name__ == "__main__":
    pytest.main([__file__]) 