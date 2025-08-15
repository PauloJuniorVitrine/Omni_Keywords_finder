"""
Data Sensitivity Matrix - Sistema de Classificação de Dados Sensíveis
Tracing ID: METRICS-002
Data/Hora: 2024-12-20 02:00:00 UTC
Versão: 1.0
Status: IMPLEMENTAÇÃO INICIAL

Sistema enterprise para classificação e monitoramento de dados sensíveis
em integrações externas, incluindo compliance com LGPD, GDPR e outras regulamentações.
"""

import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import redis
from collections import defaultdict

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSensitivityLevel(Enum):
    """Níveis de sensibilidade de dados"""
    PUBLIC = "public"           # Dados públicos
    INTERNAL = "internal"       # Dados internos
    CONFIDENTIAL = "confidential"  # Dados confidenciais
    RESTRICTED = "restricted"   # Dados restritos
    HIGHLY_SENSITIVE = "highly_sensitive"  # Dados altamente sensíveis

class DataCategory(Enum):
    """Categorias de dados"""
    PERSONAL_INFO = "personal_info"
    FINANCIAL = "financial"
    HEALTH = "health"
    LEGAL = "legal"
    TECHNICAL = "technical"
    BUSINESS = "business"
    AUTHENTICATION = "authentication"

@dataclass
class DataField:
    """Definição de campo de dados"""
    field_name: str
    field_path: str
    sensitivity_level: DataSensitivityLevel
    category: DataCategory
    description: str
    encryption_required: bool
    retention_days: int
    compliance_frameworks: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            **asdict(self),
            'sensitivity_level': self.sensitivity_level.value,
            'category': self.category.value
        }

@dataclass
class IntegrationDataMap:
    """Mapeamento de dados por integração"""
    integration_name: str
    fields: List[DataField]
    last_audit: datetime
    compliance_score: float
    risk_level: str
    encryption_status: Dict[str, bool]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            **asdict(self),
            'last_audit': self.last_audit.isoformat(),
            'fields': [field.to_dict() for field in self.fields]
        }

@dataclass
class ComplianceReport:
    """Relatório de compliance"""
    report_id: str
    timestamp: datetime
    integration_name: str
    overall_score: float
    compliance_frameworks: List[str]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

class DataSensitivityMatrix:
    """
    Sistema de matriz de sensibilidade de dados
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Inicializa o sistema de matriz de sensibilidade
        
        Args:
            redis_client: Cliente Redis para cache (opcional)
        """
        self.redis_client = redis_client
        self.integration_maps: Dict[str, IntegrationDataMap] = {}
        self.compliance_frameworks = {
            'lgpd': {
                'name': 'Lei Geral de Proteção de Dados',
                'country': 'Brazil',
                'requirements': ['consent', 'purpose_limitation', 'data_minimization']
            },
            'gdpr': {
                'name': 'General Data Protection Regulation',
                'country': 'EU',
                'requirements': ['consent', 'purpose_limitation', 'data_minimization', 'right_to_erasure']
            },
            'ccpa': {
                'name': 'California Consumer Privacy Act',
                'country': 'USA',
                'requirements': ['disclosure', 'opt_out', 'data_portability']
            },
            'sox': {
                'name': 'Sarbanes-Oxley Act',
                'country': 'USA',
                'requirements': ['financial_reporting', 'internal_controls', 'audit_trails']
            }
        }
        
        # Padrões de detecção de dados sensíveis
        self.sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-data]{2,}\b',
            'cpf': r'\b\data{3}\.?\data{3}\.?\data{3}-?\data{2}\b',
            'cnpj': r'\b\data{2}\.?\data{3}\.?\data{3}/?0001-?\data{2}\b',
            'credit_card': r'\b\data{4}[-\string_data]?\data{4}[-\string_data]?\data{4}[-\string_data]?\data{4}\b',
            'phone': r'\b\(\data{2}\)\string_data?\data{4,5}-?\data{4}\b',
            'address': r'\bRua|Avenida|Av\.|Street|Avenue\b',
            'ip_address': r'\b\data{1,3}\.\data{1,3}\.\data{1,3}\.\data{1,3}\b',
            'api_key': r'\b[A-Za-z0-9]{32,}\b',
            'token': r'\b[A-Za-z0-9]{20,}\b'
        }
        
        logger.info("[DATA_SENSITIVITY] Sistema de matriz de sensibilidade inicializado")
    
    def classify_field_sensitivity(self, field_name: str, 
                                 field_path: str,
                                 sample_data: Optional[str] = None) -> DataField:
        """
        Classifica a sensibilidade de um campo
        
        Args:
            field_name: Nome do campo
            field_path: Caminho do campo (ex: user.personal.email)
            sample_data: Dados de exemplo para análise
            
        Returns:
            Campo classificado
        """
        try:
            # Análise baseada no nome do campo
            field_lower = field_name.lower()
            path_lower = field_path.lower()
            
            # Determina categoria e sensibilidade
            category, sensitivity_level = self._analyze_field_patterns(field_lower, path_lower)
            
            # Análise de dados de exemplo se disponível
            if sample_data:
                category, sensitivity_level = self._analyze_sample_data(
                    sample_data, category, sensitivity_level
                )
            
            # Configurações baseadas na sensibilidade
            encryption_required = sensitivity_level in [
                DataSensitivityLevel.CONFIDENTIAL,
                DataSensitivityLevel.RESTRICTED,
                DataSensitivityLevel.HIGHLY_SENSITIVE
            ]
            
            retention_days = self._get_retention_days(sensitivity_level)
            compliance_frameworks = self._get_compliance_frameworks(category, sensitivity_level)
            
            field = DataField(
                field_name=field_name,
                field_path=field_path,
                sensitivity_level=sensitivity_level,
                category=category,
                description=self._generate_field_description(field_name, category),
                encryption_required=encryption_required,
                retention_days=retention_days,
                compliance_frameworks=compliance_frameworks
            )
            
            logger.info(f"[DATA_SENSITIVITY] Campo {field_path} classificado como {sensitivity_level.value}")
            return field
            
        except Exception as e:
            logger.error(f"[DATA_SENSITIVITY] Erro ao classificar campo {field_name}: {e}")
            # Retorna classificação padrão segura
            return DataField(
                field_name=field_name,
                field_path=field_path,
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL,
                category=DataCategory.PERSONAL_INFO,
                description="Campo com classificação padrão de segurança",
                encryption_required=True,
                retention_days=365,
                compliance_frameworks=['lgpd', 'gdpr']
            )
    
    def _analyze_field_patterns(self, field_name: str, field_path: str) -> Tuple[DataCategory, DataSensitivityLevel]:
        """
        Analisa padrões no nome do campo para determinar categoria e sensibilidade
        """
        # Padrões de dados pessoais
        personal_patterns = ['email', 'name', 'phone', 'address', 'cpf', 'cnpj', 'rg', 'passport']
        if any(pattern in field_name for pattern in personal_patterns):
            return DataCategory.PERSONAL_INFO, DataSensitivityLevel.CONFIDENTIAL
        
        # Padrões financeiros
        financial_patterns = ['credit_card', 'bank_account', 'balance', 'transaction', 'payment', 'invoice']
        if any(pattern in field_name for pattern in financial_patterns):
            return DataCategory.FINANCIAL, DataSensitivityLevel.RESTRICTED
        
        # Padrões de saúde
        health_patterns = ['medical', 'health', 'diagnosis', 'treatment', 'prescription']
        if any(pattern in field_name for pattern in health_patterns):
            return DataCategory.HEALTH, DataSensitivityLevel.HIGHLY_SENSITIVE
        
        # Padrões legais
        legal_patterns = ['contract', 'legal', 'court', 'case', 'document']
        if any(pattern in field_name for pattern in legal_patterns):
            return DataCategory.LEGAL, DataSensitivityLevel.RESTRICTED
        
        # Padrões de autenticação
        auth_patterns = ['password', 'token', 'api_key', 'secret', 'key']
        if any(pattern in field_name for pattern in auth_patterns):
            return DataCategory.AUTHENTICATION, DataSensitivityLevel.HIGHLY_SENSITIVE
        
        # Padrões técnicos
        technical_patterns = ['ip', 'user_agent', 'session', 'log', 'debug']
        if any(pattern in field_name for pattern in technical_patterns):
            return DataCategory.TECHNICAL, DataSensitivityLevel.INTERNAL
        
        # Padrões de negócio
        business_patterns = ['company', 'organization', 'department', 'role', 'title']
        if any(pattern in field_name for pattern in business_patterns):
            return DataCategory.BUSINESS, DataSensitivityLevel.INTERNAL
        
        # Padrão padrão
        return DataCategory.PERSONAL_INFO, DataSensitivityLevel.CONFIDENTIAL
    
    def _analyze_sample_data(self, sample_data: str, 
                           current_category: DataCategory,
                           current_sensitivity: DataSensitivityLevel) -> Tuple[DataCategory, DataSensitivityLevel]:
        """
        Analisa dados de exemplo para refinar classificação
        """
        sample_lower = sample_data.lower()
        
        # Verifica padrões de dados sensíveis
        for pattern_name, pattern in self.sensitive_patterns.items():
            if re.search(pattern, sample_data):
                if pattern_name in ['email', 'cpf', 'cnpj']:
                    return DataCategory.PERSONAL_INFO, DataSensitivityLevel.CONFIDENTIAL
                elif pattern_name in ['credit_card']:
                    return DataCategory.FINANCIAL, DataSensitivityLevel.RESTRICTED
                elif pattern_name in ['api_key', 'token']:
                    return DataCategory.AUTHENTICATION, DataSensitivityLevel.HIGHLY_SENSITIVE
        
        return current_category, current_sensitivity
    
    def _get_retention_days(self, sensitivity_level: DataSensitivityLevel) -> int:
        """Retorna dias de retenção baseado na sensibilidade"""
        retention_map = {
            DataSensitivityLevel.PUBLIC: 2555,  # 7 anos
            DataSensitivityLevel.INTERNAL: 1825,  # 5 anos
            DataSensitivityLevel.CONFIDENTIAL: 1095,  # 3 anos
            DataSensitivityLevel.RESTRICTED: 730,  # 2 anos
            DataSensitivityLevel.HIGHLY_SENSITIVE: 365  # 1 ano
        }
        return retention_map.get(sensitivity_level, 1095)
    
    def _get_compliance_frameworks(self, category: DataCategory, 
                                 sensitivity_level: DataSensitivityLevel) -> List[str]:
        """Retorna frameworks de compliance aplicáveis"""
        frameworks = []
        
        if category in [DataCategory.PERSONAL_INFO, DataCategory.HEALTH]:
            frameworks.extend(['lgpd', 'gdpr'])
        
        if category == DataCategory.FINANCIAL:
            frameworks.extend(['sox'])
        
        if sensitivity_level in [DataSensitivityLevel.RESTRICTED, DataSensitivityLevel.HIGHLY_SENSITIVE]:
            frameworks.extend(['lgpd', 'gdpr'])
        
        return list(set(frameworks))
    
    def _generate_field_description(self, field_name: str, category: DataCategory) -> str:
        """Gera descrição do campo baseada na categoria"""
        descriptions = {
            DataCategory.PERSONAL_INFO: f"Informação pessoal: {field_name}",
            DataCategory.FINANCIAL: f"Dado financeiro: {field_name}",
            DataCategory.HEALTH: f"Dado de saúde: {field_name}",
            DataCategory.LEGAL: f"Dado legal: {field_name}",
            DataCategory.TECHNICAL: f"Dado técnico: {field_name}",
            DataCategory.BUSINESS: f"Dado de negócio: {field_name}",
            DataCategory.AUTHENTICATION: f"Dado de autenticação: {field_name}"
        }
        return descriptions.get(category, f"Campo: {field_name}")
    
    def create_integration_data_map(self, integration_name: str, 
                                  field_definitions: List[Dict[str, Any]]) -> IntegrationDataMap:
        """
        Cria mapeamento de dados para uma integração
        
        Args:
            integration_name: Nome da integração
            field_definitions: Lista de definições de campos
            
        Returns:
            Mapeamento de dados da integração
        """
        try:
            fields = []
            encryption_status = {}
            
            for field_def in field_definitions:
                field = self.classify_field_sensitivity(
                    field_name=field_def['name'],
                    field_path=field_def.get('path', field_def['name']),
                    sample_data=field_def.get('sample_data')
                )
                fields.append(field)
                encryption_status[field.field_path] = field.encryption_required
            
            # Calcula score de compliance
            compliance_score = self._calculate_compliance_score(fields)
            risk_level = self._calculate_risk_level(fields)
            
            data_map = IntegrationDataMap(
                integration_name=integration_name,
                fields=fields,
                last_audit=datetime.utcnow(),
                compliance_score=compliance_score,
                risk_level=risk_level,
                encryption_status=encryption_status
            )
            
            # Armazena o mapeamento
            self.integration_maps[integration_name] = data_map
            
            # Cache no Redis se disponível
            if self.redis_client:
                cache_key = f"data_map:{integration_name}"
                self.redis_client.setex(
                    cache_key,
                    3600,  # 1 hora
                    json.dumps(data_map.to_dict())
                )
            
            logger.info(f"[DATA_SENSITIVITY] Mapeamento criado para {integration_name}")
            return data_map
            
        except Exception as e:
            logger.error(f"[DATA_SENSITIVITY] Erro ao criar mapeamento para {integration_name}: {e}")
            raise
    
    def _calculate_compliance_score(self, fields: List[DataField]) -> float:
        """Calcula score de compliance baseado nos campos"""
        if not fields:
            return 0.0
        
        total_score = 0.0
        max_score = len(fields) * 100
        
        for field in fields:
            field_score = 100.0
            
            # Deduz pontos por falta de criptografia
            if field.encryption_required and not field.encryption_required:
                field_score -= 30
            
            # Deduz pontos por alta sensibilidade
            if field.sensitivity_level in [DataSensitivityLevel.RESTRICTED, DataSensitivityLevel.HIGHLY_SENSITIVE]:
                field_score -= 20
            
            # Adiciona pontos por frameworks de compliance
            field_score += len(field.compliance_frameworks) * 10
            
            total_score += max(0, field_score)
        
        return (total_score / max_score) * 100
    
    def _calculate_risk_level(self, fields: List[DataField]) -> str:
        """Calcula nível de risco baseado nos campos"""
        if not fields:
            return "low"
        
        high_sensitive_count = sum(
            1 for field in fields 
            if field.sensitivity_level in [DataSensitivityLevel.RESTRICTED, DataSensitivityLevel.HIGHLY_SENSITIVE]
        )
        
        total_fields = len(fields)
        risk_percentage = (high_sensitive_count / total_fields) * 100
        
        if risk_percentage >= 50:
            return "high"
        elif risk_percentage >= 25:
            return "medium"
        else:
            return "low"
    
    def scan_data_for_sensitive_content(self, data: Dict[str, Any], 
                                      integration_name: str) -> List[Dict[str, Any]]:
        """
        Escaneia dados em busca de conteúdo sensível
        
        Args:
            data: Dados a serem escaneados
            integration_name: Nome da integração
            
        Returns:
            Lista de violações encontradas
        """
        try:
            violations = []
            data_map = self.integration_maps.get(integration_name)
            
            if not data_map:
                logger.warning(f"[DATA_SENSITIVITY] Mapeamento não encontrado para {integration_name}")
                return violations
            
            # Converte dados para string para análise
            data_str = json.dumps(data, default=str)
            
            # Verifica padrões sensíveis
            for pattern_name, pattern in self.sensitive_patterns.items():
                matches = re.findall(pattern, data_str)
                if matches:
                    violation = {
                        'pattern_type': pattern_name,
                        'matches_count': len(matches),
                        'sample_matches': matches[:3],  # Primeiros 3 matches
                        'severity': 'high' if pattern_name in ['credit_card', 'api_key', 'token'] else 'medium',
                        'timestamp': datetime.utcnow().isoformat(),
                        'recommendation': f"Remover ou mascarar dados {pattern_name}"
                    }
                    violations.append(violation)
            
            # Verifica campos não mapeados
            unmapped_fields = self._find_unmapped_fields(data, data_map)
            for field in unmapped_fields:
                violation = {
                    'pattern_type': 'unmapped_field',
                    'field_name': field,
                    'severity': 'medium',
                    'timestamp': datetime.utcnow().isoformat(),
                    'recommendation': f"Mapear campo {field} no sistema de sensibilidade"
                }
                violations.append(violation)
            
            logger.info(f"[DATA_SENSITIVITY] {len(violations)} violações encontradas em {integration_name}")
            return violations
            
        except Exception as e:
            logger.error(f"[DATA_SENSITIVITY] Erro ao escanear dados para {integration_name}: {e}")
            return []
    
    def _find_unmapped_fields(self, data: Dict[str, Any], 
                            data_map: IntegrationDataMap) -> List[str]:
        """Encontra campos não mapeados nos dados"""
        mapped_fields = {field.field_path for field in data_map.fields}
        unmapped = []
        
        def check_fields(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if current_path not in mapped_fields:
                        unmapped.append(current_path)
                    check_fields(value, current_path)
            elif isinstance(obj, list):
                for index, item in enumerate(obj):
                    current_path = f"{path}[{index}]"
                    check_fields(item, current_path)
        
        check_fields(data)
        return list(set(unmapped))
    
    def generate_compliance_report(self, integration_name: str) -> ComplianceReport:
        """
        Gera relatório de compliance para uma integração
        
        Args:
            integration_name: Nome da integração
            
        Returns:
            Relatório de compliance
        """
        try:
            data_map = self.integration_maps.get(integration_name)
            if not data_map:
                raise ValueError(f"Mapeamento não encontrado para {integration_name}")
            
            # Analisa violações
            violations = []
            recommendations = []
            
            # Verifica campos sem criptografia
            unencrypted_fields = [
                field for field in data_map.fields 
                if field.encryption_required and not data_map.encryption_status.get(field.field_path, False)
            ]
            
            for field in unencrypted_fields:
                violations.append({
                    'type': 'encryption_missing',
                    'field': field.field_path,
                    'severity': 'high',
                    'description': f"Campo {field.field_path} requer criptografia"
                })
                recommendations.append(f"Implementar criptografia para {field.field_path}")
            
            # Verifica compliance com frameworks
            for framework in ['lgpd', 'gdpr']:
                if framework in self.compliance_frameworks:
                    framework_violations = self._check_framework_compliance(data_map, framework)
                    violations.extend(framework_violations)
            
            # Avaliação de risco
            risk_assessment = {
                'overall_risk': data_map.risk_level,
                'high_sensitive_fields': len([
                    f for f in data_map.fields 
                    if f.sensitivity_level in [DataSensitivityLevel.RESTRICTED, DataSensitivityLevel.HIGHLY_SENSITIVE]
                ]),
                'encryption_coverage': len([
                    f for f in data_map.fields 
                    if data_map.encryption_status.get(f.field_path, False)
                ]) / len(data_map.fields) * 100,
                'compliance_frameworks': list(set([
                    framework for field in data_map.fields 
                    for framework in field.compliance_frameworks
                ]))
            }
            
            report = ComplianceReport(
                report_id=f"COMP_{integration_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.utcnow(),
                integration_name=integration_name,
                overall_score=data_map.compliance_score,
                compliance_frameworks=list(set([
                    framework for field in data_map.fields 
                    for framework in field.compliance_frameworks
                ])),
                violations=violations,
                recommendations=recommendations,
                risk_assessment=risk_assessment
            )
            
            logger.info(f"[DATA_SENSITIVITY] Relatório de compliance gerado para {integration_name}")
            return report
            
        except Exception as e:
            logger.error(f"[DATA_SENSITIVITY] Erro ao gerar relatório para {integration_name}: {e}")
            raise
    
    def _check_framework_compliance(self, data_map: IntegrationDataMap, 
                                  framework: str) -> List[Dict[str, Any]]:
        """Verifica compliance com framework específico"""
        violations = []
        
        if framework == 'lgpd':
            # Verifica princípios da LGPD
            for field in data_map.fields:
                if field.category == DataCategory.PERSONAL_INFO:
                    if field.retention_days > 2555:  # 7 anos
                        violations.append({
                            'type': 'lgpd_retention',
                            'field': field.field_path,
                            'severity': 'medium',
                            'description': f"Retenção de {field.retention_days} dias excede limite LGPD"
                        })
        
        elif framework == 'gdpr':
            # Verifica princípios do GDPR
            for field in data_map.fields:
                if field.category == DataCategory.PERSONAL_INFO:
                    if not field.encryption_required:
                        violations.append({
                            'type': 'gdpr_encryption',
                            'field': field.field_path,
                            'severity': 'high',
                            'description': f"Campo pessoal sem criptografia requerida pelo GDPR"
                        })
        
        return violations
    
    def get_integration_data_map(self, integration_name: str) -> Optional[IntegrationDataMap]:
        """Obtém mapeamento de dados de uma integração"""
        try:
            # Tenta cache primeiro
            if self.redis_client:
                cache_key = f"data_map:{integration_name}"
                cached = self.redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return IntegrationDataMap(**data)
            
            # Busca no mapeamento local
            return self.integration_maps.get(integration_name)
            
        except Exception as e:
            logger.error(f"[DATA_SENSITIVITY] Erro ao obter mapeamento para {integration_name}: {e}")
            return None
    
    def get_all_integrations_summary(self) -> Dict[str, Any]:
        """Obtém resumo de todas as integrações"""
        try:
            summary = {
                'total_integrations': len(self.integration_maps),
                'total_fields': sum(len(data_map.fields) for data_map in self.integration_maps.values()),
                'risk_distribution': defaultdict(int),
                'compliance_scores': [],
                'last_audits': []
            }
            
            for data_map in self.integration_maps.values():
                summary['risk_distribution'][data_map.risk_level] += 1
                summary['compliance_scores'].append(data_map.compliance_score)
                summary['last_audits'].append(data_map.last_audit.isoformat())
            
            if summary['compliance_scores']:
                summary['average_compliance_score'] = sum(summary['compliance_scores']) / len(summary['compliance_scores'])
            
            summary['risk_distribution'] = dict(summary['risk_distribution'])
            
            return summary
            
        except Exception as e:
            logger.error(f"[DATA_SENSITIVITY] Erro ao gerar resumo: {e}")
            return {}


# Instância global
data_sensitivity_matrix = DataSensitivityMatrix()

# Funções de conveniência
def classify_field_sensitivity(field_name: str, field_path: str, sample_data: Optional[str] = None) -> DataField:
    """Função de conveniência para classificar campo"""
    return data_sensitivity_matrix.classify_field_sensitivity(field_name, field_path, sample_data)

def create_integration_data_map(integration_name: str, field_definitions: List[Dict[str, Any]]) -> IntegrationDataMap:
    """Função de conveniência para criar mapeamento"""
    return data_sensitivity_matrix.create_integration_data_map(integration_name, field_definitions)

def scan_data_for_sensitive_content(data: Dict[str, Any], integration_name: str) -> List[Dict[str, Any]]:
    """Função de conveniência para escanear dados"""
    return data_sensitivity_matrix.scan_data_for_sensitive_content(data, integration_name)

def generate_compliance_report(integration_name: str) -> ComplianceReport:
    """Função de conveniência para gerar relatório"""
    return data_sensitivity_matrix.generate_compliance_report(integration_name) 