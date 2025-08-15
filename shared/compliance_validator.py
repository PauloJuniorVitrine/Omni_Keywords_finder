"""
Validador de Compliance Enterprise
=================================

Tracing ID: COMPLIANCE_VALIDATOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação

Objetivo: Validar conformidade com padrões PCI-DSS, LGPD e gerar
relatórios de compliance para auditoria e certificação.
"""

import os
import json
import yaml
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict

# Adicionar diretório raiz ao path
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from infrastructure.security.advanced_security_system import SensitiveDataDetector
    from infrastructure.validation.doc_quality_score import DocQualityAnalyzer
    from shared.doc_generation_metrics import DocGenerationMetrics
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de que todos os módulos estão implementados")
    sys.exit(1)


@dataclass
class ComplianceRequirement:
    """Representa um requisito de compliance."""
    id: str
    name: str
    description: str
    severity: str
    documentation_required: bool
    audit_frequency: str
    status: str = "pending"
    last_audit: Optional[datetime] = None
    next_audit: Optional[datetime] = None
    compliance_score: float = 0.0
    issues: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


@dataclass
class ComplianceReport:
    """Relatório de compliance."""
    report_id: str
    timestamp: datetime
    framework: str  # 'pci_dss', 'lgpd', 'combined'
    overall_score: float
    requirements_count: int
    compliant_count: int
    non_compliant_count: int
    pending_count: int
    requirements: List[ComplianceRequirement]
    recommendations: List[str]
    next_audit_date: datetime
    generated_by: str = "ComplianceValidator"


@dataclass
class ComplianceViolation:
    """Violação de compliance detectada."""
    violation_id: str
    requirement_id: str
    severity: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    detected_at: datetime = None
    resolved: bool = False
    resolution_notes: str = ""
    
    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now()


class ComplianceValidator:
    """
    Validador principal de compliance enterprise.
    
    Valida conformidade com padrões PCI-DSS, LGPD e gera relatórios
    detalhados para auditoria e certificação.
    """
    
    def __init__(self, config_path: str = "config/compliance.yaml"):
        """
        Inicializa o validador de compliance.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Serviços
        self.security_detector = SensitiveDataDetector()
        self.quality_analyzer = DocQualityAnalyzer()
        self.metrics_collector = DocGenerationMetrics()
        
        # Estado interno
        self.requirements: Dict[str, ComplianceRequirement] = {}
        self.violations: List[ComplianceViolation] = []
        self.audit_history: List[ComplianceReport] = []
        
        # Configuração de logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Carregar requisitos
        self._load_requirements()
        
        self.logger.info(f"[COMPLIANCE_VALIDATOR] Inicializado com {len(self.requirements)} requisitos")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração de compliance."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error(f"[COMPLIANCE_VALIDATOR] Erro ao carregar configuração: {e}")
            return {}
    
    def _load_requirements(self) -> None:
        """Carrega requisitos de compliance da configuração."""
        try:
            # Carregar requisitos PCI-DSS
            if self.config.get('pci_dss', {}).get('enabled', False):
                for req_data in self.config['pci_dss']['requirements']:
                    requirement = ComplianceRequirement(
                        id=req_data['id'],
                        name=req_data['name'],
                        description=req_data['description'],
                        severity=req_data['severity'],
                        documentation_required=req_data['documentation_required'],
                        audit_frequency=req_data['audit_frequency']
                    )
                    self.requirements[req_data['id']] = requirement
            
            # Carregar requisitos LGPD
            if self.config.get('lgpd', {}).get('enabled', False):
                for req_data in self.config['lgpd']['requirements']:
                    requirement = ComplianceRequirement(
                        id=req_data['id'],
                        name=req_data['name'],
                        description=req_data['description'],
                        severity=req_data['severity'],
                        documentation_required=req_data['documentation_required'],
                        audit_frequency=req_data['audit_frequency']
                    )
                    self.requirements[req_data['id']] = requirement
            
            self.logger.info(f"[COMPLIANCE_VALIDATOR] Carregados {len(self.requirements)} requisitos")
            
        except Exception as e:
            self.logger.error(f"[COMPLIANCE_VALIDATOR] Erro ao carregar requisitos: {e}")
    
    def validate_pci_dss_compliance(self, scan_paths: List[str] = None) -> ComplianceReport:
        """
        Valida conformidade com PCI-DSS.
        
        Args:
            scan_paths: Lista de caminhos para escanear
            
        Returns:
            ComplianceReport com resultados da validação
        """
        self.logger.info("[COMPLIANCE_VALIDATOR] Iniciando validação PCI-DSS")
        
        scan_paths = scan_paths or ['docs/', 'backend/', 'infrastructure/']
        pci_requirements = [req for req in self.requirements.values() if req.id.startswith('PCI-DSS')]
        
        # Validar cada requisito
        for requirement in pci_requirements:
            self._validate_requirement(requirement, scan_paths)
        
        # Gerar relatório
        report = self._generate_compliance_report('pci_dss', pci_requirements)
        
        self.logger.info(f"[COMPLIANCE_VALIDATOR] Validação PCI-DSS concluída - Score: {report.overall_score:.2f}")
        return report
    
    def validate_lgpd_compliance(self, scan_paths: List[str] = None) -> ComplianceReport:
        """
        Valida conformidade com LGPD.
        
        Args:
            scan_paths: Lista de caminhos para escanear
            
        Returns:
            ComplianceReport com resultados da validação
        """
        self.logger.info("[COMPLIANCE_VALIDATOR] Iniciando validação LGPD")
        
        scan_paths = scan_paths or ['docs/', 'backend/', 'infrastructure/']
        lgpd_requirements = [req for req in self.requirements.values() if req.id.startswith('LGPD')]
        
        # Validar cada requisito
        for requirement in lgpd_requirements:
            self._validate_requirement(requirement, scan_paths)
        
        # Gerar relatório
        report = self._generate_compliance_report('lgpd', lgpd_requirements)
        
        self.logger.info(f"[COMPLIANCE_VALIDATOR] Validação LGPD concluída - Score: {report.overall_score:.2f}")
        return report
    
    def validate_combined_compliance(self, scan_paths: List[str] = None) -> ComplianceReport:
        """
        Valida conformidade combinada (PCI-DSS + LGPD).
        
        Args:
            scan_paths: Lista de caminhos para escanear
            
        Returns:
            ComplianceReport com resultados da validação
        """
        self.logger.info("[COMPLIANCE_VALIDATOR] Iniciando validação combinada")
        
        # Executar validações individuais
        pci_report = self.validate_pci_dss_compliance(scan_paths)
        lgpd_report = self.validate_lgpd_compliance(scan_paths)
        
        # Combinar resultados
        all_requirements = list(self.requirements.values())
        combined_report = self._generate_compliance_report('combined', all_requirements)
        
        # Calcular score combinado (média ponderada)
        pci_weight = 0.6  # PCI-DSS tem peso maior
        lgpd_weight = 0.4
        combined_report.overall_score = (pci_report.overall_score * pci_weight + 
                                        lgpd_report.overall_score * lgpd_weight)
        
        self.logger.info(f"[COMPLIANCE_VALIDATOR] Validação combinada concluída - Score: {combined_report.overall_score:.2f}")
        return combined_report
    
    def _validate_requirement(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """
        Valida um requisito específico de compliance.
        
        Args:
            requirement: Requisito a ser validado
            scan_paths: Caminhos para escanear
        """
        try:
            self.logger.debug(f"[COMPLIANCE_VALIDATOR] Validando requisito: {requirement.id}")
            
            # Resetar issues
            requirement.issues = []
            
            # Validar baseado no tipo de requisito
            if requirement.id.startswith('PCI-DSS'):
                self._validate_pci_requirement(requirement, scan_paths)
            elif requirement.id.startswith('LGPD'):
                self._validate_lgpd_requirement(requirement, scan_paths)
            
            # Calcular score de compliance
            requirement.compliance_score = self._calculate_requirement_score(requirement)
            
            # Atualizar status
            if requirement.compliance_score >= 0.95:
                requirement.status = "compliant"
            elif requirement.compliance_score >= 0.80:
                requirement.status = "partial"
            else:
                requirement.status = "non_compliant"
            
            # Atualizar datas de auditoria
            requirement.last_audit = datetime.now()
            requirement.next_audit = self._calculate_next_audit_date(requirement.audit_frequency)
            
        except Exception as e:
            self.logger.error(f"[COMPLIANCE_VALIDATOR] Erro ao validar requisito {requirement.id}: {e}")
            requirement.status = "error"
            requirement.issues.append({
                'type': 'validation_error',
                'description': str(e),
                'severity': 'high'
            })
    
    def _validate_pci_requirement(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida requisito específico do PCI-DSS."""
        if requirement.id == 'PCI-DSS-1':
            # Firewall configuration
            self._validate_firewall_configuration(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-2':
            # Default passwords
            self._validate_default_passwords(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-3':
            # Cardholder data protection
            self._validate_cardholder_data_protection(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-4':
            # Data transmission encryption
            self._validate_data_transmission_encryption(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-5':
            # Malware protection
            self._validate_malware_protection(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-6':
            # Secure development
            self._validate_secure_development(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-7':
            # Access restriction
            self._validate_access_restriction(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-8':
            # Authentication
            self._validate_authentication(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-9':
            # Physical access
            self._validate_physical_access(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-10':
            # Logging and monitoring
            self._validate_logging_monitoring(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-11':
            # Security testing
            self._validate_security_testing(requirement, scan_paths)
        elif requirement.id == 'PCI-DSS-12':
            # Security policy
            self._validate_security_policy(requirement, scan_paths)
    
    def _validate_lgpd_requirement(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida requisito específico da LGPD."""
        if requirement.id == 'LGPD-1':
            # Finalidade e boa-fé
            self._validate_purpose_good_faith(requirement, scan_paths)
        elif requirement.id == 'LGPD-2':
            # Adequação e necessidade
            self._validate_adequacy_necessity(requirement, scan_paths)
        elif requirement.id == 'LGPD-3':
            # Livre acesso
            self._validate_free_access(requirement, scan_paths)
        elif requirement.id == 'LGPD-4':
            # Qualidade dos dados
            self._validate_data_quality(requirement, scan_paths)
        elif requirement.id == 'LGPD-5':
            # Transparência
            self._validate_transparency(requirement, scan_paths)
        elif requirement.id == 'LGPD-6':
            # Segurança
            self._validate_lgpd_security(requirement, scan_paths)
        elif requirement.id == 'LGPD-7':
            # Não discriminação
            self._validate_non_discrimination(requirement, scan_paths)
        elif requirement.id == 'LGPD-8':
            # Responsabilização
            self._validate_accountability(requirement, scan_paths)
        elif requirement.id == 'LGPD-9':
            # Consentimento
            self._validate_consent(requirement, scan_paths)
        elif requirement.id == 'LGPD-10':
            # Legítimo interesse
            self._validate_legitimate_interest(requirement, scan_paths)
    
    def _validate_firewall_configuration(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida configuração de firewall (PCI-DSS-1)."""
        # Verificar se há documentação de firewall
        firewall_docs = self._find_files_with_pattern(scan_paths, ['firewall', 'network', 'security'])
        
        if not firewall_docs:
            requirement.issues.append({
                'type': 'missing_documentation',
                'description': 'Documentação de firewall não encontrada',
                'severity': 'high',
                'recommendation': 'Criar documentação de configuração de firewall'
            })
        else:
            # Verificar qualidade da documentação
            for doc_path in firewall_docs:
                quality_score = self.quality_analyzer.calculate_doc_quality_score(doc_path)
                if quality_score < 0.8:
                    requirement.issues.append({
                        'type': 'poor_documentation',
                        'description': f'Documentação de firewall com baixa qualidade: {doc_path}',
                        'severity': 'medium',
                        'file_path': doc_path,
                        'quality_score': quality_score
                    })
    
    def _validate_default_passwords(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida uso de senhas padrão (PCI-DSS-2)."""
        # Procurar por senhas padrão em arquivos de configuração
        default_password_patterns = [
            r'password["\string_data]*[:=]["\string_data]*["\']?(admin|root|password|123456|default)["\']?',
            r'passwd["\string_data]*[:=]["\string_data]*["\']?(admin|root|password|123456|default)["\']?'
        ]
        
        for pattern in default_password_patterns:
            matches = self._find_pattern_in_files(scan_paths, pattern)
            for match in matches:
                requirement.issues.append({
                    'type': 'default_password',
                    'description': f'Senha padrão detectada: {match["value"]}',
                    'severity': 'critical',
                    'file_path': match['file_path'],
                    'line_number': match['line_number']
                })
    
    def _validate_cardholder_data_protection(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida proteção de dados de cartão (PCI-DSS-3)."""
        # Verificar se há dados de cartão em texto plano
        card_patterns = [
            r'\b\data{4}[-\string_data]?\data{4}[-\string_data]?\data{4}[-\string_data]?\data{4}\b',  # 16 dígitos
            r'\b\data{4}[-\string_data]?\data{6}[-\string_data]?\data{5}\b'  # 15 dígitos (Amex)
        ]
        
        for pattern in card_patterns:
            matches = self._find_pattern_in_files(scan_paths, pattern)
            for match in matches:
                requirement.issues.append({
                    'type': 'cardholder_data_exposure',
                    'description': 'Dados de cartão em texto plano detectados',
                    'severity': 'critical',
                    'file_path': match['file_path'],
                    'line_number': match['line_number']
                })
    
    def _validate_data_transmission_encryption(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida criptografia de transmissão (PCI-DSS-4)."""
        # Verificar se há configurações de HTTPS/TLS
        encryption_patterns = [
            r'https://',
            r'tls[_-]?version',
            r'ssl[_-]?version',
            r'encryption[_-]?enabled["\string_data]*[:=]["\string_data]*true'
        ]
        
        encryption_found = False
        for pattern in encryption_patterns:
            matches = self._find_pattern_in_files(scan_paths, pattern)
            if matches:
                encryption_found = True
                break
        
        if not encryption_found:
            requirement.issues.append({
                'type': 'missing_encryption',
                'description': 'Configuração de criptografia de transmissão não encontrada',
                'severity': 'critical',
                'recommendation': 'Implementar HTTPS/TLS para transmissão de dados'
            })
    
    def _validate_malware_protection(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida proteção contra malware (PCI-DSS-5)."""
        # Verificar se há documentação de proteção contra malware
        malware_docs = self._find_files_with_pattern(scan_paths, ['antivirus', 'malware', 'security'])
        
        if not malware_docs:
            requirement.issues.append({
                'type': 'missing_malware_protection',
                'description': 'Documentação de proteção contra malware não encontrada',
                'severity': 'high',
                'recommendation': 'Implementar e documentar proteção contra malware'
            })
    
    def _validate_secure_development(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida desenvolvimento seguro (PCI-DSS-6)."""
        # Verificar se há documentação de desenvolvimento seguro
        secure_dev_docs = self._find_files_with_pattern(scan_paths, ['secure', 'development', 'sdlc'])
        
        if not secure_dev_docs:
            requirement.issues.append({
                'type': 'missing_secure_development',
                'description': 'Documentação de desenvolvimento seguro não encontrada',
                'severity': 'high',
                'recommendation': 'Implementar e documentar processo de desenvolvimento seguro'
            })
    
    def _validate_access_restriction(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida restrição de acesso (PCI-DSS-7)."""
        # Verificar se há documentação de controle de acesso
        access_docs = self._find_files_with_pattern(scan_paths, ['access', 'control', 'authorization'])
        
        if not access_docs:
            requirement.issues.append({
                'type': 'missing_access_control',
                'description': 'Documentação de controle de acesso não encontrada',
                'severity': 'high',
                'recommendation': 'Implementar e documentar controle de acesso'
            })
    
    def _validate_authentication(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida autenticação (PCI-DSS-8)."""
        # Verificar se há documentação de autenticação
        auth_docs = self._find_files_with_pattern(scan_paths, ['authentication', 'login', 'auth'])
        
        if not auth_docs:
            requirement.issues.append({
                'type': 'missing_authentication',
                'description': 'Documentação de autenticação não encontrada',
                'severity': 'high',
                'recommendation': 'Implementar e documentar sistema de autenticação'
            })
    
    def _validate_physical_access(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida acesso físico (PCI-DSS-9)."""
        # Verificar se há documentação de controle de acesso físico
        physical_docs = self._find_files_with_pattern(scan_paths, ['physical', 'security', 'facility'])
        
        if not physical_docs:
            requirement.issues.append({
                'type': 'missing_physical_security',
                'description': 'Documentação de segurança física não encontrada',
                'severity': 'medium',
                'recommendation': 'Documentar controles de segurança física'
            })
    
    def _validate_logging_monitoring(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida logging e monitoramento (PCI-DSS-10)."""
        # Verificar se há documentação de logging
        logging_docs = self._find_files_with_pattern(scan_paths, ['logging', 'monitoring', 'audit'])
        
        if not logging_docs:
            requirement.issues.append({
                'type': 'missing_logging',
                'description': 'Documentação de logging e monitoramento não encontrada',
                'severity': 'high',
                'recommendation': 'Implementar e documentar sistema de logging'
            })
    
    def _validate_security_testing(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida testes de segurança (PCI-DSS-11)."""
        # Verificar se há documentação de testes de segurança
        testing_docs = self._find_files_with_pattern(scan_paths, ['security', 'testing', 'penetration'])
        
        if not testing_docs:
            requirement.issues.append({
                'type': 'missing_security_testing',
                'description': 'Documentação de testes de segurança não encontrada',
                'severity': 'high',
                'recommendation': 'Implementar e documentar testes de segurança'
            })
    
    def _validate_security_policy(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida política de segurança (PCI-DSS-12)."""
        # Verificar se há documentação de política de segurança
        policy_docs = self._find_files_with_pattern(scan_paths, ['policy', 'security', 'compliance'])
        
        if not policy_docs:
            requirement.issues.append({
                'type': 'missing_security_policy',
                'description': 'Política de segurança não encontrada',
                'severity': 'high',
                'recommendation': 'Criar e documentar política de segurança'
            })
    
    # Métodos de validação LGPD
    def _validate_purpose_good_faith(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida finalidade e boa-fé (LGPD-1)."""
        purpose_docs = self._find_files_with_pattern(scan_paths, ['purpose', 'finalidade', 'consent'])
        
        if not purpose_docs:
            requirement.issues.append({
                'type': 'missing_purpose_documentation',
                'description': 'Documentação de finalidade do tratamento não encontrada',
                'severity': 'high',
                'recommendation': 'Documentar finalidade do tratamento de dados'
            })
    
    def _validate_adequacy_necessity(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida adequação e necessidade (LGPD-2)."""
        adequacy_docs = self._find_files_with_pattern(scan_paths, ['adequacy', 'necessity', 'adequação'])
        
        if not adequacy_docs:
            requirement.issues.append({
                'type': 'missing_adequacy_documentation',
                'description': 'Documentação de adequação e necessidade não encontrada',
                'severity': 'high',
                'recommendation': 'Documentar adequação e necessidade dos dados coletados'
            })
    
    def _validate_free_access(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida livre acesso (LGPD-3)."""
        access_docs = self._find_files_with_pattern(scan_paths, ['access', 'acesso', 'user_rights'])
        
        if not access_docs:
            requirement.issues.append({
                'type': 'missing_access_documentation',
                'description': 'Documentação de direitos de acesso não encontrada',
                'severity': 'high',
                'recommendation': 'Documentar direitos de acesso dos usuários'
            })
    
    def _validate_data_quality(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida qualidade dos dados (LGPD-4)."""
        quality_docs = self._find_files_with_pattern(scan_paths, ['quality', 'qualidade', 'accuracy'])
        
        if not quality_docs:
            requirement.issues.append({
                'type': 'missing_quality_documentation',
                'description': 'Documentação de qualidade dos dados não encontrada',
                'severity': 'medium',
                'recommendation': 'Documentar processos de garantia de qualidade dos dados'
            })
    
    def _validate_transparency(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida transparência (LGPD-5)."""
        transparency_docs = self._find_files_with_pattern(scan_paths, ['transparency', 'transparência', 'privacy'])
        
        if not transparency_docs:
            requirement.issues.append({
                'type': 'missing_transparency_documentation',
                'description': 'Documentação de transparência não encontrada',
                'severity': 'high',
                'recommendation': 'Documentar políticas de transparência'
            })
    
    def _validate_lgpd_security(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida segurança LGPD (LGPD-6)."""
        security_docs = self._find_files_with_pattern(scan_paths, ['security', 'segurança', 'protection'])
        
        if not security_docs:
            requirement.issues.append({
                'type': 'missing_security_documentation',
                'description': 'Documentação de segurança LGPD não encontrada',
                'severity': 'high',
                'recommendation': 'Documentar medidas de segurança para dados pessoais'
            })
    
    def _validate_non_discrimination(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida não discriminação (LGPD-7)."""
        discrimination_docs = self._find_files_with_pattern(scan_paths, ['discrimination', 'discriminação', 'fair'])
        
        if not discrimination_docs:
            requirement.issues.append({
                'type': 'missing_discrimination_documentation',
                'description': 'Documentação de não discriminação não encontrada',
                'severity': 'medium',
                'recommendation': 'Documentar políticas de não discriminação'
            })
    
    def _validate_accountability(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida responsabilização (LGPD-8)."""
        accountability_docs = self._find_files_with_pattern(scan_paths, ['accountability', 'responsabilização', 'governance'])
        
        if not accountability_docs:
            requirement.issues.append({
                'type': 'missing_accountability_documentation',
                'description': 'Documentação de responsabilização não encontrada',
                'severity': 'high',
                'recommendation': 'Documentar estrutura de responsabilização'
            })
    
    def _validate_consent(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida consentimento (LGPD-9)."""
        consent_docs = self._find_files_with_pattern(scan_paths, ['consent', 'consentimento', 'authorization'])
        
        if not consent_docs:
            requirement.issues.append({
                'type': 'missing_consent_documentation',
                'description': 'Documentação de consentimento não encontrada',
                'severity': 'critical',
                'recommendation': 'Documentar processos de consentimento'
            })
    
    def _validate_legitimate_interest(self, requirement: ComplianceRequirement, scan_paths: List[str]) -> None:
        """Valida legítimo interesse (LGPD-10)."""
        interest_docs = self._find_files_with_pattern(scan_paths, ['legitimate', 'legítimo', 'interest'])
        
        if not interest_docs:
            requirement.issues.append({
                'type': 'missing_legitimate_interest_documentation',
                'description': 'Documentação de legítimo interesse não encontrada',
                'severity': 'high',
                'recommendation': 'Documentar fundamentação de legítimo interesse'
            })
    
    def _find_files_with_pattern(self, scan_paths: List[str], keywords: List[str]) -> List[str]:
        """Encontra arquivos que contêm palavras-chave específicas."""
        found_files = []
        
        for scan_path in scan_paths:
            if not os.path.exists(scan_path):
                continue
            
            for root, dirs, files in os.walk(scan_path):
                for file in files:
                    if file.endswith(('.md', '.txt', '.rst', '.py', '.js', '.ts', '.yaml', '.yml')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read().lower()
                                if any(keyword.lower() in content for keyword in keywords):
                                    found_files.append(file_path)
                        except Exception:
                            continue
        
        return found_files
    
    def _find_pattern_in_files(self, scan_paths: List[str], pattern: str) -> List[Dict[str, Any]]:
        """Encontra padrões regex em arquivos."""
        matches = []
        
        for scan_path in scan_paths:
            if not os.path.exists(scan_path):
                continue
            
            for root, dirs, files in os.walk(scan_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.yaml', '.yml', '.json', '.md')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                for line_num, line in enumerate(f, 1):
                                    if re.search(pattern, line, re.IGNORECASE):
                                        matches.append({
                                            'file_path': file_path,
                                            'line_number': line_num,
                                            'value': line.strip()
                                        })
                        except Exception:
                            continue
        
        return matches
    
    def _calculate_requirement_score(self, requirement: ComplianceRequirement) -> float:
        """Calcula score de compliance para um requisito."""
        if not requirement.issues:
            return 1.0
        
        # Calcular score baseado na severidade dos issues
        total_weight = 0
        weighted_score = 0
        
        for issue in requirement.issues:
            if issue['severity'] == 'critical':
                weight = 1.0
            elif issue['severity'] == 'high':
                weight = 0.7
            elif issue['severity'] == 'medium':
                weight = 0.4
            else:
                weight = 0.1
            
            total_weight += weight
            weighted_score += weight * 0.0  # Issue = 0 pontos
        
        if total_weight == 0:
            return 1.0
        
        return max(0.0, 1.0 - (weighted_score / total_weight))
    
    def _calculate_next_audit_date(self, audit_frequency: str) -> datetime:
        """Calcula próxima data de auditoria."""
        now = datetime.now()
        
        if audit_frequency == 'daily':
            return now + timedelta(days=1)
        elif audit_frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif audit_frequency == 'monthly':
            return now + timedelta(days=30)
        elif audit_frequency == 'quarterly':
            return now + timedelta(days=90)
        elif audit_frequency == 'annually':
            return now + timedelta(days=365)
        else:
            return now + timedelta(days=30)  # Default mensal
    
    def _generate_compliance_report(self, framework: str, requirements: List[ComplianceRequirement]) -> ComplianceReport:
        """Gera relatório de compliance."""
        # Calcular estatísticas
        total_requirements = len(requirements)
        compliant_count = sum(1 for req in requirements if req.status == 'compliant')
        non_compliant_count = sum(1 for req in requirements if req.status == 'non_compliant')
        pending_count = sum(1 for req in requirements if req.status == 'pending')
        
        # Calcular score geral
        if total_requirements > 0:
            overall_score = sum(req.compliance_score for req in requirements) / total_requirements
        else:
            overall_score = 0.0
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(requirements)
        
        # Calcular próxima auditoria
        next_audit_date = min((req.next_audit for req in requirements if req.next_audit), default=datetime.now() + timedelta(days=30))
        
        report = ComplianceReport(
            report_id=f"COMPLIANCE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            framework=framework,
            overall_score=overall_score,
            requirements_count=total_requirements,
            compliant_count=compliant_count,
            non_compliant_count=non_compliant_count,
            pending_count=pending_count,
            requirements=requirements,
            recommendations=recommendations,
            next_audit_date=next_audit_date
        )
        
        # Salvar relatório
        self.audit_history.append(report)
        
        return report
    
    def _generate_recommendations(self, requirements: List[ComplianceRequirement]) -> List[str]:
        """Gera recomendações baseadas nos issues encontrados."""
        recommendations = []
        
        # Agrupar issues por tipo
        issue_types = defaultdict(list)
        for req in requirements:
            for issue in req.issues:
                issue_types[issue['type']].append(issue)
        
        # Gerar recomendações baseadas nos tipos mais comuns
        if issue_types['missing_documentation']:
            recommendations.append("Implementar documentação completa para todos os requisitos de compliance")
        
        if issue_types['default_password']:
            recommendations.append("Remover todas as senhas padrão e implementar senhas seguras")
        
        if issue_types['cardholder_data_exposure']:
            recommendations.append("Implementar criptografia para todos os dados de cartão")
        
        if issue_types['missing_encryption']:
            recommendations.append("Implementar criptografia de transmissão (HTTPS/TLS)")
        
        if issue_types['missing_security_policy']:
            recommendations.append("Criar e implementar política de segurança abrangente")
        
        if issue_types['missing_consent_documentation']:
            recommendations.append("Implementar processos de consentimento conforme LGPD")
        
        # Recomendações gerais
        if len(recommendations) == 0:
            recommendations.append("Manter monitoramento contínuo de compliance")
        else:
            recommendations.append("Realizar auditoria completa após implementação das correções")
        
        return recommendations
    
    def save_report(self, report: ComplianceReport, output_path: str = None) -> str:
        """Salva relatório de compliance em arquivo."""
        if output_path is None:
            output_path = f"reports/compliance/{report.report_id}.json"
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Converter para dict
        report_dict = asdict(report)
        report_dict['timestamp'] = report.timestamp.isoformat()
        report_dict['next_audit_date'] = report.next_audit_date.isoformat()
        
        # Salvar arquivo
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"[COMPLIANCE_VALIDATOR] Relatório salvo em: {output_path}")
        return output_path
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de compliance."""
        if not self.audit_history:
            return {'status': 'no_audits_performed'}
        
        latest_report = self.audit_history[-1]
        
        return {
            'latest_audit': latest_report.timestamp.isoformat(),
            'overall_score': latest_report.overall_score,
            'framework': latest_report.framework,
            'requirements_count': latest_report.requirements_count,
            'compliant_count': latest_report.compliant_count,
            'non_compliant_count': latest_report.non_compliant_count,
            'next_audit_date': latest_report.next_audit_date.isoformat(),
            'critical_issues': len([issue for req in latest_report.requirements 
                                  for issue in req.issues if issue['severity'] == 'critical'])
        }


# Função de conveniência
def validate_compliance(framework: str = 'combined', config_path: str = None) -> ComplianceReport:
    """
    Função de conveniência para validação de compliance.
    
    Args:
        framework: 'pci_dss', 'lgpd', ou 'combined'
        config_path: Caminho para arquivo de configuração
        
    Returns:
        ComplianceReport com resultados da validação
    """
    validator = ComplianceValidator(config_path)
    
    if framework == 'pci_dss':
        return validator.validate_pci_dss_compliance()
    elif framework == 'lgpd':
        return validator.validate_lgpd_compliance()
    else:
        return validator.validate_combined_compliance() 