"""
Sistema de Secrets Scanning Avançado - Omni Keywords Finder

Funcionalidades:
- Detectar padrões de API keys (Stripe, Google, etc.)
- Scan de arquivos de configuração
- Integração com Git hooks
- Relatórios de segurança
- Configuração de padrões customizados
- Integração com CI/CD
- Validação de secrets em tempo real
- Alertas automáticos

Autor: Sistema de Secrets Scanning Avançado
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: SECRETS_SCANNER_001
"""

import os
import re
import json
import hashlib
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import subprocess
import yaml
import base64

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecretType(Enum):
    """Tipos de secrets detectados"""
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    PRIVATE_KEY = "private_key"
    DATABASE_URL = "database_url"
    AWS_CREDENTIALS = "aws_credentials"
    GOOGLE_CREDENTIALS = "google_credentials"
    STRIPE_KEY = "stripe_key"
    JWT_SECRET = "jwt_secret"
    ENCRYPTION_KEY = "encryption_key"
    CUSTOM = "custom"

class SeverityLevel(Enum):
    """Níveis de severidade"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecretMatch:
    """Match de secret encontrado"""
    secret_type: SecretType
    pattern: str
    file_path: str
    line_number: int
    line_content: str
    severity: SeverityLevel
    confidence: float  # 0.0 a 1.0
    context: str
    timestamp: datetime
    hash: str
    is_false_positive: bool = False
    remediation: Optional[str] = None

@dataclass
class ScanResult:
    """Resultado de scan"""
    scan_id: str
    timestamp: datetime
    files_scanned: int
    secrets_found: int
    false_positives: int
    critical_secrets: int
    scan_duration: float
    patterns_used: List[str]
    scan_path: str
    summary: Dict[str, Any]

class SecretsScanner:
    """Scanner avançado de secrets"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.patterns = self._load_patterns()
        self.excluded_paths = set(self.config['excluded_paths'])
        self.excluded_files = set(self.config['excluded_files'])
        self.scan_history: List[ScanResult] = []
        self.secret_cache: Dict[str, SecretMatch] = {}
        
        # Métricas
        self.scans_performed = 0
        self.secrets_detected = 0
        self.false_positives = 0
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão do scanner"""
        return {
            'scan_paths': ['.'],
            'excluded_paths': [
                '.git', 'node_modules', '__pycache__', '.venv', 'venv',
                'coverage', 'htmlcov', 'logs', 'backups', 'uploads',
                '.pytest_cache', '.mypy_cache', '.tox'
            ],
            'excluded_files': [
                '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
                '*.log', '*.tmp', '*.temp', '*.cache', '*.lock'
            ],
            'file_extensions': [
                '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env',
                '.ini', '.cfg', '.conf', '.config', '.txt', '.md',
                '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat'
            ],
            'max_file_size_mb': 10,
            'confidence_threshold': 0.7,
            'enable_git_hooks': True,
            'enable_ci_integration': True,
            'alert_on_critical': True,
            'auto_remediation': False
        }
    
    def _load_patterns(self) -> Dict[SecretType, List[Dict[str, Any]]]:
        """Carrega padrões de detecção de secrets"""
        return {
            SecretType.API_KEY: [
                {
                    'pattern': r'api[_-]?key["\string_data]*[:=]["\string_data]*([a-zA-Z0-9]{32,})',
                    'confidence': 0.9,
                    'severity': SeverityLevel.HIGH
                },
                {
                    'pattern': r'api_key["\string_data]*[:=]["\string_data]*([a-zA-Z0-9]{20,})',
                    'confidence': 0.8,
                    'severity': SeverityLevel.MEDIUM
                }
            ],
            SecretType.PASSWORD: [
                {
                    'pattern': r'password["\string_data]*[:=]["\string_data]*([^\string_data"\']{8,})',
                    'confidence': 0.7,
                    'severity': SeverityLevel.MEDIUM
                },
                {
                    'pattern': r'passwd["\string_data]*[:=]["\string_data]*([^\string_data"\']{8,})',
                    'confidence': 0.7,
                    'severity': SeverityLevel.MEDIUM
                }
            ],
            SecretType.TOKEN: [
                {
                    'pattern': r'token["\string_data]*[:=]["\string_data]*([a-zA-Z0-9]{32,})',
                    'confidence': 0.8,
                    'severity': SeverityLevel.HIGH
                },
                {
                    'pattern': r'access_token["\string_data]*[:=]["\string_data]*([a-zA-Z0-9]{32,})',
                    'confidence': 0.9,
                    'severity': SeverityLevel.HIGH
                }
            ],
            SecretType.PRIVATE_KEY: [
                {
                    'pattern': r'-----BEGIN PRIVATE KEY-----',
                    'confidence': 0.95,
                    'severity': SeverityLevel.CRITICAL
                },
                {
                    'pattern': r'-----BEGIN RSA PRIVATE KEY-----',
                    'confidence': 0.95,
                    'severity': SeverityLevel.CRITICAL
                }
            ],
            SecretType.DATABASE_URL: [
                {
                    'pattern': r'(postgresql|mysql|mongodb)://[^\string_data"\']+',
                    'confidence': 0.8,
                    'severity': SeverityLevel.HIGH
                }
            ],
            SecretType.AWS_CREDENTIALS: [
                {
                    'pattern': r'AKIA[0-9A-Z]{16}',
                    'confidence': 0.95,
                    'severity': SeverityLevel.CRITICAL
                },
                {
                    'pattern': r'aws_access_key_id["\string_data]*[:=]["\string_data]*([A-Z0-9]{20})',
                    'confidence': 0.9,
                    'severity': SeverityLevel.HIGH
                }
            ],
            SecretType.GOOGLE_CREDENTIALS: [
                {
                    'pattern': r'AIza[0-9A-Za-data-_]{35}',
                    'confidence': 0.9,
                    'severity': SeverityLevel.HIGH
                },
                {
                    'pattern': r'google[_-]?api[_-]?key["\string_data]*[:=]["\string_data]*([A-Za-z0-9_-]{39})',
                    'confidence': 0.9,
                    'severity': SeverityLevel.HIGH
                }
            ],
            SecretType.STRIPE_KEY: [
                {
                    'pattern': r'sk_live_[0-9a-zA-Z]{24}',
                    'confidence': 0.95,
                    'severity': SeverityLevel.CRITICAL
                },
                {
                    'pattern': r'pk_live_[0-9a-zA-Z]{24}',
                    'confidence': 0.8,
                    'severity': SeverityLevel.MEDIUM
                }
            ],
            SecretType.JWT_SECRET: [
                {
                    'pattern': r'jwt[_-]?secret["\string_data]*[:=]["\string_data]*([^\string_data"\']{16,})',
                    'confidence': 0.8,
                    'severity': SeverityLevel.HIGH
                }
            ],
            SecretType.ENCRYPTION_KEY: [
                {
                    'pattern': r'encryption[_-]?key["\string_data]*[:=]["\string_data]*([^\string_data"\']{32,})',
                    'confidence': 0.9,
                    'severity': SeverityLevel.CRITICAL
                }
            ]
        }
    
    def scan_file(self, file_path: str) -> List[SecretMatch]:
        """Escaneia um arquivo em busca de secrets"""
        matches = []
        
        try:
            # Verificar se arquivo deve ser excluído
            if self._should_exclude_file(file_path):
                return matches
            
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(file_path)
            if file_size > self.config['max_file_size_mb'] * 1024 * 1024:
                logger.warning(f"Arquivo muito grande ignorado: {file_path}")
                return matches
            
            # Ler conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Escanear cada linha
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line_matches = self._scan_line(line, file_path, line_num)
                matches.extend(line_matches)
            
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao escanear arquivo {file_path}: {str(e)}")
            return matches
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """Verifica se arquivo deve ser excluído"""
        path = Path(file_path)
        
        # Verificar extensão
        if path.suffix not in self.config['file_extensions']:
            return True
        
        # Verificar caminhos excluídos
        for excluded in self.excluded_paths:
            if excluded in str(path):
                return True
        
        # Verificar padrões de arquivo excluído
        for pattern in self.excluded_files:
            if path.match(pattern):
                return True
        
        return False
    
    def _scan_line(self, line: str, file_path: str, line_number: int) -> List[SecretMatch]:
        """Escaneia uma linha em busca de secrets"""
        matches = []
        
        for secret_type, patterns in self.patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                confidence = pattern_info['confidence']
                severity = pattern_info['severity']
                
                # Procurar matches
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    if confidence >= self.config['confidence_threshold']:
                        secret_match = SecretMatch(
                            secret_type=secret_type,
                            pattern=pattern,
                            file_path=file_path,
                            line_number=line_number,
                            line_content=line.strip(),
                            severity=severity,
                            confidence=confidence,
                            context=self._get_context(line, match),
                            timestamp=datetime.utcnow(),
                            hash=self._generate_hash(file_path, line_number, match.group())
                        )
                        
                        # Verificar se é falso positivo
                        if self._is_false_positive(secret_match):
                            secret_match.is_false_positive = True
                        
                        matches.append(secret_match)
        
        return matches
    
    def _get_context(self, line: str, match) -> str:
        """Extrai contexto do match"""
        start = max(0, match.start() - 20)
        end = min(len(line), match.end() + 20)
        return line[start:end].strip()
    
    def _generate_hash(self, file_path: str, line_number: int, match_text: str) -> str:
        """Gera hash único para o secret"""
        content = f"{file_path}:{line_number}:{match_text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _is_false_positive(self, secret_match: SecretMatch) -> bool:
        """Verifica se é falso positivo"""
        # Verificar se está em comentário
        line = secret_match.line_content
        if line.strip().startswith('#') or line.strip().startswith('//'):
            return True
        
        # Verificar se está em string de exemplo
        if 'example' in line.lower() or 'sample' in line.lower():
            return True
        
        # Verificar se está em documentação
        if 'doc' in secret_match.file_path.lower():
            return True
        
        # Verificar se está em teste
        if 'test' in secret_match.file_path.lower():
            return True
        
        return False
    
    def scan_directory(self, directory: str) -> ScanResult:
        """Escaneia um diretório completo"""
        start_time = time.time()
        scan_id = f"scan_{int(start_time)}"
        
        all_matches = []
        files_scanned = 0
        
        logger.info(f"Iniciando scan do diretório: {directory}")
        
        # Percorrer arquivos recursivamente
        for root, dirs, files in os.walk(directory):
            # Remover diretórios excluídos
            dirs[:] = [data for data in dirs if data not in self.excluded_paths]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Escanear arquivo
                matches = self.scan_file(file_path)
                all_matches.extend(matches)
                files_scanned += 1
                
                if matches:
                    logger.warning(f"Secrets encontrados em {file_path}: {len(matches)}")
        
        # Calcular estatísticas
        scan_duration = time.time() - start_time
        secrets_found = len(all_matches)
        false_positives = len([m for m in all_matches if m.is_false_positive])
        critical_secrets = len([m for m in all_matches if m.severity == SeverityLevel.CRITICAL])
        
        # Criar resultado
        result = ScanResult(
            scan_id=scan_id,
            timestamp=datetime.utcnow(),
            files_scanned=files_scanned,
            secrets_found=secrets_found,
            false_positives=false_positives,
            critical_secrets=critical_secrets,
            scan_duration=scan_duration,
            patterns_used=list(self.patterns.keys()),
            scan_path=directory,
            summary={
                'total_secrets': secrets_found,
                'critical_secrets': critical_secrets,
                'false_positives': false_positives,
                'real_secrets': secrets_found - false_positives,
                'severity_breakdown': self._get_severity_breakdown(all_matches)
            }
        )
        
        # Salvar no histórico
        self.scan_history.append(result)
        
        # Atualizar métricas
        self.scans_performed += 1
        self.secrets_detected += secrets_found
        self.false_positives += false_positives
        
        # Alertar se há secrets críticos
        if critical_secrets > 0 and self.config['alert_on_critical']:
            self._send_critical_alert(result, all_matches)
        
        logger.info(f"Scan concluído: {files_scanned} arquivos, {secrets_found} secrets encontrados")
        
        return result
    
    def _get_severity_breakdown(self, matches: List[SecretMatch]) -> Dict[str, int]:
        """Calcula breakdown por severidade"""
        breakdown = {severity.value: 0 for severity in SeverityLevel}
        for match in matches:
            breakdown[match.severity.value] += 1
        return breakdown
    
    def _send_critical_alert(self, result: ScanResult, matches: List[SecretMatch]):
        """Envia alerta para secrets críticos"""
        critical_matches = [m for m in matches if m.severity == SeverityLevel.CRITICAL]
        
        alert_message = f"""
🚨 ALERTA CRÍTICO: Secrets críticos detectados!

Scan ID: {result.scan_id}
Arquivos escaneados: {result.files_scanned}
Secrets críticos: {result.critical_secrets}

Arquivos com secrets críticos:
"""
        
        for match in critical_matches:
            alert_message += f"- {match.file_path}:{match.line_number} ({match.secret_type.value})\n"
        
        logger.error(alert_message)
        
        # Aqui você pode integrar com sistemas de alerta (Slack, email, etc.)
    
    def scan_git_commit(self, commit_hash: str) -> ScanResult:
        """Escaneia um commit específico do Git"""
        try:
            # Obter arquivos modificados no commit
            cmd = f"git show --name-only {commit_hash}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Erro ao obter arquivos do commit {commit_hash}")
                return None
            
            files = result.stdout.strip().split('\n')[1:]  # Pular primeira linha
            
            all_matches = []
            files_scanned = 0
            
            for file_path in files:
                if file_path and os.path.exists(file_path):
                    matches = self.scan_file(file_path)
                    all_matches.extend(matches)
                    files_scanned += 1
            
            # Criar resultado similar ao scan de diretório
            scan_id = f"git_scan_{commit_hash}"
            scan_duration = 0.0  # Não medimos tempo para git scan
            
            return ScanResult(
                scan_id=scan_id,
                timestamp=datetime.utcnow(),
                files_scanned=files_scanned,
                secrets_found=len(all_matches),
                false_positives=len([m for m in all_matches if m.is_false_positive]),
                critical_secrets=len([m for m in all_matches if m.severity == SeverityLevel.CRITICAL]),
                scan_duration=scan_duration,
                patterns_used=list(self.patterns.keys()),
                scan_path=f"git_commit:{commit_hash}",
                summary={'total_secrets': len(all_matches)}
            )
            
        except Exception as e:
            logger.error(f"Erro ao escanear commit {commit_hash}: {str(e)}")
            return None
    
    def add_custom_pattern(self, secret_type: SecretType, pattern: str, 
                          confidence: float, severity: SeverityLevel):
        """Adiciona padrão customizado"""
        if secret_type not in self.patterns:
            self.patterns[secret_type] = []
        
        self.patterns[secret_type].append({
            'pattern': pattern,
            'confidence': confidence,
            'severity': severity
        })
        
        logger.info(f"Padrão customizado adicionado: {secret_type.value}")
    
    def get_scan_history(self) -> List[ScanResult]:
        """Retorna histórico de scans"""
        return self.scan_history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do scanner"""
        return {
            'scans_performed': self.scans_performed,
            'secrets_detected': self.secrets_detected,
            'false_positives': self.false_positives,
            'accuracy_rate': (self.secrets_detected - self.false_positives) / max(self.secrets_detected, 1),
            'patterns_configured': len(self.patterns),
            'last_scan': self.scan_history[-1].timestamp if self.scan_history else None
        }
    
    def generate_report(self, scan_result: ScanResult, output_format: str = 'json') -> str:
        """Gera relatório do scan"""
        if output_format == 'json':
            return json.dumps(asdict(scan_result), indent=2, default=str)
        elif output_format == 'yaml':
            return yaml.dump(asdict(scan_result), default_flow_style=False)
        else:
            return self._generate_text_report(scan_result)
    
    def _generate_text_report(self, scan_result: ScanResult) -> str:
        """Gera relatório em texto"""
        report = f"""
=== RELATÓRIO DE SECRETS SCANNING ===

Scan ID: {scan_result.scan_id}
Data/Hora: {scan_result.timestamp}
Diretório: {scan_result.scan_path}
Duração: {scan_result.scan_duration:.2f} segundos

ESTATÍSTICAS:
- Arquivos escaneados: {scan_result.files_scanned}
- Secrets encontrados: {scan_result.secrets_found}
- Falsos positivos: {scan_result.false_positives}
- Secrets críticos: {scan_result.critical_secrets}
- Secrets reais: {scan_result.secrets_found - scan_result.false_positives}

BREAKDOWN POR SEVERIDADE:
"""
        
        for severity, count in scan_result.summary['severity_breakdown'].items():
            report += f"- {severity}: {count}\n"
        
        return report

def create_secrets_scanner(config: Optional[Dict[str, Any]] = None) -> SecretsScanner:
    """Factory para criar scanner de secrets"""
    return SecretsScanner(config)

def main():
    """Função principal para execução via linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scanner de Secrets')
    parser.add_argument('path', help='Caminho para escanear')
    parser.add_argument('--format', choices=['json', 'yaml', 'text'], default='text',
                       help='Formato do relatório')
    parser.add_argument('--config', help='Arquivo de configuração JSON')
    
    args = parser.parse_args()
    
    # Carregar configuração se fornecida
    config = None
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Criar scanner e executar
    scanner = create_secrets_scanner(config)
    result = scanner.scan_directory(args.path)
    
    # Gerar relatório
    report = scanner.generate_report(result, args.format)
    print(report)

if __name__ == "__main__":
    main() 