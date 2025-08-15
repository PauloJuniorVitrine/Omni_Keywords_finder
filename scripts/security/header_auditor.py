"""
Sistema de Auditoria de Headers Sensíveis - Omni Keywords Finder

Funcionalidades:
- Detectar headers que vazam informações
- Validar headers de integrações externas
- Configuração de headers permitidos
- Relatórios de compliance
- Integração com observabilidade
- Alertas automáticos para headers suspeitos
- Validação de headers em tempo real
- Análise de padrões de headers

Autor: Sistema de Auditoria de Headers
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: HEADER_AUDITOR_001
"""

import os
import re
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import yaml
import hashlib
from urllib.parse import urlparse

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeaderRiskLevel(Enum):
    """Níveis de risco dos headers"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HeaderCategory(Enum):
    """Categorias de headers"""
    SECURITY = "security"
    IDENTIFICATION = "identification"
    PERFORMANCE = "performance"
    DEBUGGING = "debugging"
    CUSTOM = "custom"
    INTERNAL = "internal"

@dataclass
class HeaderViolation:
    """Violação de header encontrada"""
    header_name: str
    header_value: str
    risk_level: HeaderRiskLevel
    category: HeaderCategory
    file_path: str
    line_number: int
    line_content: str
    description: str
    recommendation: str
    timestamp: datetime
    hash: str
    is_false_positive: bool = False
    remediation: Optional[str] = None

@dataclass
class AuditResult:
    """Resultado da auditoria"""
    audit_id: str
    timestamp: datetime
    files_scanned: int
    violations_found: int
    critical_violations: int
    audit_duration: float
    scan_path: str
    summary: Dict[str, Any]
    compliance_score: float

class HeaderAuditor:
    """Auditor de headers sensíveis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.sensitive_patterns = self._load_sensitive_patterns()
        self.allowed_headers = set(self.config['allowed_headers'])
        self.blocked_headers = set(self.config['blocked_headers'])
        self.audit_history: List[AuditResult] = []
        self.violation_cache: Dict[str, HeaderViolation] = {}
        
        # Métricas
        self.audits_performed = 0
        self.violations_detected = 0
        self.false_positives = 0
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão do auditor"""
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
            'allowed_headers': [
                'Content-Type', 'Accept', 'User-Agent', 'Authorization',
                'X-Requested-With', 'X-CSRF-Token', 'X-API-Key',
                'X-Webhook-Signature', 'X-Webhook-Event', 'X-Webhook-Timestamp'
            ],
            'blocked_headers': [
                'X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version',
                'X-Runtime', 'X-Version', 'Server', 'X-Server',
                'X-Application-Name', 'X-Application-Version',
                'X-Debug-Token', 'X-Debug-Token-Link'
            ],
            'enable_real_time_validation': True,
            'enable_compliance_reporting': True,
            'alert_on_critical': True,
            'auto_remediation': False
        }
    
    def _load_sensitive_patterns(self) -> Dict[HeaderCategory, List[Dict[str, Any]]]:
        """Carrega padrões sensíveis de headers"""
        return {
            HeaderCategory.SECURITY: [
                {
                    'pattern': r'X-Powered-By["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.HIGH,
                    'description': 'Header X-Powered-By expõe tecnologia do servidor',
                    'recommendation': 'Remover header X-Powered-By para ocultar tecnologia'
                },
                {
                    'pattern': r'Server["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.MEDIUM,
                    'description': 'Header Server expõe informações do servidor',
                    'recommendation': 'Configurar header Server genérico ou removê-lo'
                }
            ],
            HeaderCategory.IDENTIFICATION: [
                {
                    'pattern': r'X-Application-Name["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.MEDIUM,
                    'description': 'Header X-Application-Name expõe nome da aplicação',
                    'recommendation': 'Remover ou usar nome genérico'
                },
                {
                    'pattern': r'X-Application-Version["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.MEDIUM,
                    'description': 'Header X-Application-Version expõe versão da aplicação',
                    'recommendation': 'Remover ou usar versão genérica'
                }
            ],
            HeaderCategory.DEBUGGING: [
                {
                    'pattern': r'X-Debug-Token["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.HIGH,
                    'description': 'Header X-Debug-Token expõe informações de debug',
                    'recommendation': 'Remover em produção'
                },
                {
                    'pattern': r'X-Runtime["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.LOW,
                    'description': 'Header X-Runtime expõe tempo de execução',
                    'recommendation': 'Considerar remoção em produção'
                }
            ],
            HeaderCategory.INTERNAL: [
                {
                    'pattern': r'X-Internal-([^\string_data"\']+)["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.CRITICAL,
                    'description': 'Header interno expõe informações sensíveis',
                    'recommendation': 'Remover headers internos de respostas externas'
                },
                {
                    'pattern': r'X-Server-([^\string_data"\']+)["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.HIGH,
                    'description': 'Header do servidor expõe informações internas',
                    'recommendation': 'Remover ou usar valores genéricos'
                }
            ],
            HeaderCategory.CUSTOM: [
                {
                    'pattern': r'X-Custom-([^\string_data"\']+)["\string_data]*[:=]["\string_data]*([^\string_data"\']+)',
                    'risk_level': HeaderRiskLevel.MEDIUM,
                    'description': 'Header customizado pode expor informações',
                    'recommendation': 'Revisar necessidade e conteúdo do header'
                }
            ]
        }
    
    def scan_file(self, file_path: str) -> List[HeaderViolation]:
        """Escaneia arquivo em busca de headers sensíveis"""
        violations = []
        
        try:
            if not self._should_scan_file(file_path):
                return violations
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_number, line in enumerate(file, 1):
                    line_violations = self._scan_line(line, file_path, line_number)
                    violations.extend(line_violations)
            
            logger.info(f"Arquivo {file_path} escaneado: {len(violations)} violações encontradas")
            
        except Exception as e:
            logger.error(f"Erro ao escanear arquivo {file_path}: {e}")
        
        return violations
    
    def _should_scan_file(self, file_path: str) -> bool:
        """Verifica se arquivo deve ser escaneado"""
        path = Path(file_path)
        
        # Verificar extensão
        if not any(str(path).endswith(ext) for ext in self.config['file_extensions']):
            return False
        
        # Verificar exclusões
        for excluded_path in self.config['excluded_paths']:
            if excluded_path in str(path):
                return False
        
        # Verificar padrões de exclusão
        for excluded_pattern in self.config['excluded_files']:
            if path.match(excluded_pattern):
                return False
        
        # Verificar tamanho
        try:
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config['max_file_size_mb']:
                return False
        except OSError:
            return False
        
        return True
    
    def _scan_line(self, line: str, file_path: str, line_number: int) -> List[HeaderViolation]:
        """Escaneia linha em busca de headers sensíveis"""
        violations = []
        
        for category, patterns in self.sensitive_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                matches = re.finditer(pattern, line, re.IGNORECASE)
                
                for match in matches:
                    header_name = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    header_value = match.group(2) if len(match.groups()) > 1 else ""
                    
                    # Verificar se é header permitido
                    if header_name in self.allowed_headers:
                        continue
                    
                    # Verificar se é header bloqueado
                    if header_name in self.blocked_headers:
                        violations.append(self._create_violation(
                            header_name, header_value, pattern_info, category,
                            file_path, line_number, line, match
                        ))
                        continue
                    
                    # Verificar padrões sensíveis
                    violations.append(self._create_violation(
                        header_name, header_value, pattern_info, category,
                        file_path, line_number, line, match
                    ))
        
        return violations
    
    def _create_violation(self, header_name: str, header_value: str, 
                         pattern_info: Dict[str, Any], category: HeaderCategory,
                         file_path: str, line_number: int, line: str, match) -> HeaderViolation:
        """Cria violação de header"""
        return HeaderViolation(
            header_name=header_name,
            header_value=header_value,
            risk_level=pattern_info['risk_level'],
            category=category,
            file_path=file_path,
            line_number=line_number,
            line_content=line.strip(),
            description=pattern_info['description'],
            recommendation=pattern_info['recommendation'],
            timestamp=datetime.now(),
            hash=self._generate_hash(file_path, line_number, header_name)
        )
    
    def _generate_hash(self, file_path: str, line_number: int, header_name: str) -> str:
        """Gera hash único para violação"""
        content = f"{file_path}:{line_number}:{header_name}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def scan_directory(self, directory: str) -> AuditResult:
        """Escaneia diretório completo"""
        start_time = time.time()
        all_violations = []
        files_scanned = 0
        
        logger.info(f"Iniciando auditoria de headers em: {directory}")
        
        for root, dirs, files in os.walk(directory):
            # Filtrar diretórios excluídos
            dirs[:] = [data for data in dirs if data not in self.config['excluded_paths']]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if self._should_scan_file(file_path):
                    violations = self.scan_file(file_path)
                    all_violations.extend(violations)
                    files_scanned += 1
        
        audit_duration = time.time() - start_time
        
        # Calcular estatísticas
        critical_violations = len([value for value in all_violations if value.risk_level == HeaderRiskLevel.CRITICAL])
        summary = self._get_risk_breakdown(all_violations)
        compliance_score = self._calculate_compliance_score(all_violations, files_scanned)
        
        # Criar resultado
        result = AuditResult(
            audit_id=f"header_audit_{int(time.time())}",
            timestamp=datetime.now(),
            files_scanned=files_scanned,
            violations_found=len(all_violations),
            critical_violations=critical_violations,
            audit_duration=audit_duration,
            scan_path=directory,
            summary=summary,
            compliance_score=compliance_score
        )
        
        # Adicionar ao histórico
        self.audit_history.append(result)
        self.audits_performed += 1
        self.violations_detected += len(all_violations)
        
        # Alertar se necessário
        if self.config['alert_on_critical'] and critical_violations > 0:
            self._send_critical_alert(result, all_violations)
        
        logger.info(f"Auditoria concluída: {files_scanned} arquivos, {len(all_violations)} violações")
        
        return result
    
    def _get_risk_breakdown(self, violations: List[HeaderViolation]) -> Dict[str, int]:
        """Calcula breakdown por nível de risco"""
        breakdown = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for violation in violations:
            breakdown[violation.risk_level.value] += 1
        
        return breakdown
    
    def _calculate_compliance_score(self, violations: List[HeaderViolation], files_scanned: int) -> float:
        """Calcula score de compliance"""
        if files_scanned == 0:
            return 100.0
        
        # Penalizar por violações
        critical_penalty = len([value for value in violations if value.risk_level == HeaderRiskLevel.CRITICAL]) * 10
        high_penalty = len([value for value in violations if value.risk_level == HeaderRiskLevel.HIGH]) * 5
        medium_penalty = len([value for value in violations if value.risk_level == HeaderRiskLevel.MEDIUM]) * 2
        low_penalty = len([value for value in violations if value.risk_level == HeaderRiskLevel.LOW]) * 1
        
        total_penalty = critical_penalty + high_penalty + medium_penalty + low_penalty
        
        # Calcular score (máximo 100)
        score = max(0, 100 - total_penalty)
        
        return round(score, 2)
    
    def _send_critical_alert(self, result: AuditResult, violations: List[HeaderViolation]):
        """Envia alerta para violações críticas"""
        critical_violations = [value for value in violations if value.risk_level == HeaderRiskLevel.CRITICAL]
        
        alert_message = f"""
🚨 ALERTA: Headers Críticos Detectados

Auditoria: {result.audit_id}
Arquivos escaneados: {result.files_scanned}
Violações críticas: {len(critical_violations)}

Headers críticos encontrados:
"""
        
        for violation in critical_violations[:5]:  # Mostrar apenas os primeiros 5
            alert_message += f"- {violation.header_name} em {violation.file_path}:{violation.line_number}\n"
        
        if len(critical_violations) > 5:
            alert_message += f"... e mais {len(critical_violations) - 5} violações críticas\n"
        
        logger.critical(alert_message)
    
    def validate_headers_in_request(self, headers: Dict[str, str], 
                                  source: str = "unknown") -> List[HeaderViolation]:
        """Valida headers em request em tempo real"""
        violations = []
        
        for header_name, header_value in headers.items():
            # Verificar headers bloqueados
            if header_name in self.blocked_headers:
                violations.append(HeaderViolation(
                    header_name=header_name,
                    header_value=header_value,
                    risk_level=HeaderRiskLevel.HIGH,
                    category=HeaderCategory.SECURITY,
                    file_path=f"request_{source}",
                    line_number=0,
                    line_content=f"{header_name}: {header_value}",
                    description=f"Header bloqueado detectado: {header_name}",
                    recommendation=f"Remover header {header_name}",
                    timestamp=datetime.now(),
                    hash=hashlib.sha256(f"{source}:{header_name}".encode()).hexdigest()
                ))
                continue
            
            # Verificar padrões sensíveis
            for category, patterns in self.sensitive_patterns.items():
                for pattern_info in patterns:
                    pattern = pattern_info['pattern']
                    if re.search(pattern, f"{header_name}: {header_value}", re.IGNORECASE):
                        violations.append(HeaderViolation(
                            header_name=header_name,
                            header_value=header_value,
                            risk_level=pattern_info['risk_level'],
                            category=category,
                            file_path=f"request_{source}",
                            line_number=0,
                            line_content=f"{header_name}: {header_value}",
                            description=pattern_info['description'],
                            recommendation=pattern_info['recommendation'],
                            timestamp=datetime.now(),
                            hash=hashlib.sha256(f"{source}:{header_name}:{header_value}".encode()).hexdigest()
                        ))
        
        return violations
    
    def add_custom_pattern(self, category: HeaderCategory, pattern: str, 
                          risk_level: HeaderRiskLevel, description: str, recommendation: str):
        """Adiciona padrão customizado"""
        if category not in self.sensitive_patterns:
            self.sensitive_patterns[category] = []
        
        self.sensitive_patterns[category].append({
            'pattern': pattern,
            'risk_level': risk_level,
            'description': description,
            'recommendation': recommendation
        })
        
        logger.info(f"Padrão customizado adicionado para categoria {category.value}")
    
    def get_audit_history(self) -> List[AuditResult]:
        """Retorna histórico de auditorias"""
        return self.audit_history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do auditor"""
        return {
            'audits_performed': self.audits_performed,
            'violations_detected': self.violations_detected,
            'false_positives': self.false_positives,
            'average_compliance_score': self._calculate_average_compliance_score(),
            'last_audit': self.audit_history[-1].timestamp if self.audit_history else None
        }
    
    def _calculate_average_compliance_score(self) -> float:
        """Calcula score médio de compliance"""
        if not self.audit_history:
            return 100.0
        
        total_score = sum(result.compliance_score for result in self.audit_history)
        return round(total_score / len(self.audit_history), 2)
    
    def generate_report(self, audit_result: AuditResult, output_format: str = 'json') -> str:
        """Gera relatório da auditoria"""
        if output_format == 'json':
            return self._generate_json_report(audit_result)
        else:
            return self._generate_text_report(audit_result)
    
    def _generate_json_report(self, audit_result: AuditResult) -> str:
        """Gera relatório em formato JSON"""
        report_data = {
            'audit_id': audit_result.audit_id,
            'timestamp': audit_result.timestamp.isoformat(),
            'summary': {
                'files_scanned': audit_result.files_scanned,
                'violations_found': audit_result.violations_found,
                'critical_violations': audit_result.critical_violations,
                'compliance_score': audit_result.compliance_score,
                'risk_breakdown': audit_result.summary
            },
            'scan_path': audit_result.scan_path,
            'audit_duration': audit_result.audit_duration
        }
        
        return json.dumps(report_data, indent=2)
    
    def _generate_text_report(self, audit_result: AuditResult) -> str:
        """Gera relatório em formato texto"""
        report = f"""
=== RELATÓRIO DE AUDITORIA DE HEADERS ===

ID da Auditoria: {audit_result.audit_id}
Data/Hora: {audit_result.timestamp.strftime('%Y-%m-%data %H:%M:%S')}
Diretório Escaneado: {audit_result.scan_path}

RESUMO:
- Arquivos escaneados: {audit_result.files_scanned}
- Violações encontradas: {audit_result.violations_found}
- Violações críticas: {audit_result.critical_violations}
- Score de compliance: {audit_result.compliance_score}/100
- Duração da auditoria: {audit_result.audit_duration:.2f}string_data

DISTRIBUIÇÃO POR RISCO:
- Crítico: {audit_result.summary['critical']}
- Alto: {audit_result.summary['high']}
- Médio: {audit_result.summary['medium']}
- Baixo: {audit_result.summary['low']}

RECOMENDAÇÕES:
"""
        
        if audit_result.critical_violations > 0:
            report += "- ⚠️ Violações críticas detectadas - ação imediata necessária\n"
        
        if audit_result.compliance_score < 80:
            report += "- 📉 Score de compliance baixo - revisar políticas de headers\n"
        
        if audit_result.violations_found == 0:
            report += "- ✅ Nenhuma violação encontrada - excelente compliance\n"
        
        return report

def create_header_auditor(config: Optional[Dict[str, Any]] = None) -> HeaderAuditor:
    """Função factory para criar auditor de headers"""
    return HeaderAuditor(config)

def main():
    """Função principal para execução via linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auditor de Headers Sensíveis')
    parser.add_argument('path', help='Caminho para escanear')
    parser.add_argument('--config', help='Arquivo de configuração')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Formato do relatório')
    parser.add_argument('--output', help='Arquivo de saída')
    
    args = parser.parse_args()
    
    # Carregar configuração se fornecida
    config = None
    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    
    # Criar auditor
    auditor = create_header_auditor(config)
    
    # Executar auditoria
    result = auditor.scan_directory(args.path)
    
    # Gerar relatório
    report = auditor.generate_report(result, args.format)
    
    # Salvar ou exibir relatório
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Relatório salvo em: {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main() 