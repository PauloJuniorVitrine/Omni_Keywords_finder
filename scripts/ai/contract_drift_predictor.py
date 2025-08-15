"""
Contract Drift Predictor System
Tracing ID: ARCH-003
Prompt: INTEGRATION_EXTERNAL_CHECKLIST_V2.md
Ruleset: enterprise_control_layer.yaml
Data/Hora: 2024-12-20 01:30:00 UTC

Sistema de predição de drift de contratos usando IA para análise de mudanças
em APIs e predição de breaking changes para integrações externas enterprise.
"""

import json
import logging
import time
import hashlib
import difflib
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import aiohttp
from pathlib import Path
import yaml
import re
from collections import defaultdict
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Tipos de mudanças em APIs"""
    ADDITION = "addition"
    REMOVAL = "removal"
    MODIFICATION = "modification"
    DEPRECATION = "deprecation"
    BREAKING = "breaking"


class RiskLevel(Enum):
    """Níveis de risco"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DriftStatus(Enum):
    """Status do drift"""
    STABLE = "stable"
    WARNING = "warning"
    CRITICAL = "critical"
    PREDICTED = "predicted"


@dataclass
class APIContract:
    """Contrato de API"""
    name: str
    version: str
    base_url: str
    endpoints: Dict[str, Dict]
    schemas: Dict[str, Dict]
    headers: Dict[str, str]
    authentication: Dict[str, Any]
    rate_limits: Dict[str, Any]
    documentation_url: Optional[str] = None
    last_updated: Optional[datetime] = None
    hash: Optional[str] = None
    
    def __post_init__(self):
        """Calcula hash do contrato após inicialização"""
        if self.hash is None:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calcula hash SHA-256 do contrato"""
        contract_data = {
            "name": self.name,
            "version": self.version,
            "base_url": self.base_url,
            "endpoints": self.endpoints,
            "schemas": self.schemas,
            "headers": self.headers,
            "authentication": self.authentication,
            "rate_limits": self.rate_limits
        }
        
        contract_str = json.dumps(contract_data, sort_keys=True)
        return hashlib.sha256(contract_str.encode()).hexdigest()


@dataclass
class APIChange:
    """Mudança detectada em API"""
    change_type: ChangeType
    risk_level: RiskLevel
    endpoint: Optional[str] = None
    field: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    description: str = ""
    impact_analysis: str = ""
    recommendations: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0


@dataclass
class DriftPrediction:
    """Predição de drift"""
    api_name: str
    current_version: str
    predicted_version: str
    predicted_changes: List[APIChange]
    confidence_score: float
    risk_score: float
    predicted_date: datetime
    impact_analysis: str
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DriftReport:
    """Relatório de drift"""
    api_name: str
    current_contract: APIContract
    previous_contract: Optional[APIContract]
    detected_changes: List[APIChange]
    predictions: List[DriftPrediction]
    overall_risk: RiskLevel
    stability_score: float
    last_check: datetime
    next_check: datetime
    recommendations: List[str]


class ContractAnalyzer:
    """Analisador de contratos de API"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o analisador de contratos
        
        Args:
            config: Configuração opcional
        """
        self.config = config or {}
        self.breaking_patterns = self.config.get("breaking_patterns", [
            r"value\data+\.0\.0",  # Major version changes
            r"deprecated",
            r"removed",
            r"breaking",
            r"incompatible"
        ])
        self.warning_patterns = self.config.get("warning_patterns", [
            r"value\data+\.\data+\.0",  # Minor version changes
            r"new",
            r"added",
            r"enhanced"
        ])
    
    def analyze_contract_changes(self, old_contract: APIContract, new_contract: APIContract) -> List[APIChange]:
        """
        Analisa mudanças entre contratos
        
        Args:
            old_contract: Contrato antigo
            new_contract: Contrato novo
            
        Returns:
            List[APIChange]: Lista de mudanças detectadas
        """
        changes = []
        
        # Analisar mudanças em endpoints
        changes.extend(self._analyze_endpoint_changes(old_contract, new_contract))
        
        # Analisar mudanças em schemas
        changes.extend(self._analyze_schema_changes(old_contract, new_contract))
        
        # Analisar mudanças em headers
        changes.extend(self._analyze_header_changes(old_contract, new_contract))
        
        # Analisar mudanças em autenticação
        changes.extend(self._analyze_auth_changes(old_contract, new_contract))
        
        # Analisar mudanças em rate limits
        changes.extend(self._analyze_rate_limit_changes(old_contract, new_contract))
        
        return changes
    
    def _analyze_endpoint_changes(self, old_contract: APIContract, new_contract: APIContract) -> List[APIChange]:
        """Analisa mudanças em endpoints"""
        changes = []
        old_endpoints = old_contract.endpoints
        new_endpoints = new_contract.endpoints
        
        # Endpoints removidos
        for endpoint in old_endpoints:
            if endpoint not in new_endpoints:
                changes.append(APIChange(
                    change_type=ChangeType.REMOVAL,
                    risk_level=RiskLevel.CRITICAL,
                    endpoint=endpoint,
                    description=f"Endpoint {endpoint} foi removido",
                    impact_analysis="Integrações que usam este endpoint irão falhar",
                    recommendations=[
                        "Implementar fallback para este endpoint",
                        "Migrar para endpoint alternativo",
                        "Contatar provedor da API"
                    ],
                    confidence=1.0
                ))
        
        # Endpoints adicionados
        for endpoint in new_endpoints:
            if endpoint not in old_endpoints:
                changes.append(APIChange(
                    change_type=ChangeType.ADDITION,
                    risk_level=RiskLevel.LOW,
                    endpoint=endpoint,
                    description=f"Novo endpoint {endpoint} adicionado",
                    impact_analysis="Nova funcionalidade disponível",
                    recommendations=[
                        "Avaliar uso do novo endpoint",
                        "Atualizar documentação"
                    ],
                    confidence=1.0
                ))
        
        # Mudanças em endpoints existentes
        for endpoint in old_endpoints:
            if endpoint in new_endpoints:
                old_endpoint = old_endpoints[endpoint]
                new_endpoint = new_endpoints[endpoint]
                
                # Mudanças em métodos HTTP
                if old_endpoint.get("methods") != new_endpoint.get("methods"):
                    changes.append(APIChange(
                        change_type=ChangeType.MODIFICATION,
                        risk_level=RiskLevel.HIGH,
                        endpoint=endpoint,
                        field="methods",
                        old_value=old_endpoint.get("methods"),
                        new_value=new_endpoint.get("methods"),
                        description=f"Métodos HTTP alterados para {endpoint}",
                        impact_analysis="Requisições podem falhar se método não suportado",
                        recommendations=[
                            "Verificar métodos suportados",
                            "Atualizar implementação se necessário"
                        ],
                        confidence=0.9
                    ))
                
                # Mudanças em parâmetros
                if old_endpoint.get("parameters") != new_endpoint.get("parameters"):
                    changes.append(APIChange(
                        change_type=ChangeType.MODIFICATION,
                        risk_level=RiskLevel.MEDIUM,
                        endpoint=endpoint,
                        field="parameters",
                        old_value=old_endpoint.get("parameters"),
                        new_value=new_endpoint.get("parameters"),
                        description=f"Parâmetros alterados para {endpoint}",
                        impact_analysis="Requisições podem falhar se parâmetros incorretos",
                        recommendations=[
                            "Revisar parâmetros obrigatórios",
                            "Atualizar documentação"
                        ],
                        confidence=0.8
                    ))
        
        return changes
    
    def _analyze_schema_changes(self, old_contract: APIContract, new_contract: APIContract) -> List[APIChange]:
        """Analisa mudanças em schemas"""
        changes = []
        old_schemas = old_contract.schemas
        new_schemas = new_contract.schemas
        
        # Schemas removidos
        for schema_name in old_schemas:
            if schema_name not in new_schemas:
                changes.append(APIChange(
                    change_type=ChangeType.REMOVAL,
                    risk_level=RiskLevel.CRITICAL,
                    field=schema_name,
                    description=f"Schema {schema_name} foi removido",
                    impact_analysis="Validação de dados pode falhar",
                    recommendations=[
                        "Atualizar validação de dados",
                        "Implementar fallback"
                    ],
                    confidence=1.0
                ))
        
        # Mudanças em schemas existentes
        for schema_name in old_schemas:
            if schema_name in new_schemas:
                old_schema = old_schemas[schema_name]
                new_schema = new_schemas[schema_name]
                
                # Mudanças em campos obrigatórios
                old_required = old_schema.get("required", [])
                new_required = new_schema.get("required", [])
                
                if old_required != new_required:
                    added_required = set(new_required) - set(old_required)
                    removed_required = set(old_required) - set(new_required)
                    
                    if added_required:
                        changes.append(APIChange(
                            change_type=ChangeType.MODIFICATION,
                            risk_level=RiskLevel.HIGH,
                            field=f"{schema_name}.required",
                            old_value=list(old_required),
                            new_value=list(new_required),
                            description=f"Campos obrigatórios adicionados em {schema_name}: {list(added_required)}",
                            impact_analysis="Requisições podem falhar se campos obrigatórios não fornecidos",
                            recommendations=[
                                "Adicionar campos obrigatórios nas requisições",
                                "Atualizar validação de dados"
                            ],
                            confidence=0.9
                        ))
                    
                    if removed_required:
                        changes.append(APIChange(
                            change_type=ChangeType.MODIFICATION,
                            risk_level=RiskLevel.LOW,
                            field=f"{schema_name}.required",
                            old_value=list(old_required),
                            new_value=list(new_required),
                            description=f"Campos obrigatórios removidos em {schema_name}: {list(removed_required)}",
                            impact_analysis="Campos não são mais obrigatórios",
                            recommendations=[
                                "Revisar validação de dados",
                                "Atualizar documentação"
                            ],
                            confidence=0.8
                        ))
        
        return changes
    
    def _analyze_header_changes(self, old_contract: APIContract, new_contract: APIContract) -> List[APIChange]:
        """Analisa mudanças em headers"""
        changes = []
        old_headers = old_contract.headers
        new_headers = new_contract.headers
        
        # Headers removidos
        for header in old_headers:
            if header not in new_headers:
                changes.append(APIChange(
                    change_type=ChangeType.REMOVAL,
                    risk_level=RiskLevel.MEDIUM,
                    field=header,
                    description=f"Header {header} foi removido",
                    impact_analysis="Requisições podem falhar se header obrigatório",
                    recommendations=[
                        "Verificar se header é obrigatório",
                        "Remover header das requisições se não necessário"
                    ],
                    confidence=0.8
                ))
        
        # Headers adicionados
        for header in new_headers:
            if header not in old_headers:
                changes.append(APIChange(
                    change_type=ChangeType.ADDITION,
                    risk_level=RiskLevel.LOW,
                    field=header,
                    description=f"Novo header {header} adicionado",
                    impact_analysis="Novo header disponível",
                    recommendations=[
                        "Avaliar uso do novo header",
                        "Atualizar documentação"
                    ],
                    confidence=0.7
                ))
        
        return changes
    
    def _analyze_auth_changes(self, old_contract: APIContract, new_contract: APIContract) -> List[APIChange]:
        """Analisa mudanças em autenticação"""
        changes = []
        old_auth = old_contract.authentication
        new_auth = new_contract.authentication
        
        if old_auth != new_auth:
            changes.append(APIChange(
                change_type=ChangeType.MODIFICATION,
                risk_level=RiskLevel.CRITICAL,
                field="authentication",
                old_value=old_auth,
                new_value=new_auth,
                description="Método de autenticação alterado",
                impact_analysis="Todas as requisições podem falhar",
                recommendations=[
                    "Atualizar método de autenticação",
                    "Gerar novas credenciais se necessário",
                    "Testar autenticação"
                ],
                confidence=1.0
            ))
        
        return changes
    
    def _analyze_rate_limit_changes(self, old_contract: APIContract, new_contract: APIContract) -> List[APIChange]:
        """Analisa mudanças em rate limits"""
        changes = []
        old_limits = old_contract.rate_limits
        new_limits = new_contract.rate_limits
        
        if old_limits != new_limits:
            changes.append(APIChange(
                change_type=ChangeType.MODIFICATION,
                risk_level=RiskLevel.MEDIUM,
                field="rate_limits",
                old_value=old_limits,
                new_value=new_limits,
                description="Rate limits alterados",
                impact_analysis="Requisições podem ser limitadas",
                recommendations=[
                    "Ajustar estratégia de rate limiting",
                    "Monitorar limites de requisições",
                    "Implementar retry com backoff"
                ],
                confidence=0.8
            ))
        
        return changes


class DriftPredictor:
    """Preditor de drift usando IA"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o preditor de drift
        
        Args:
            config: Configuração opcional
        """
        self.config = config or {}
        self.historical_data = []
        self.prediction_models = {}
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.prediction_horizon = self.config.get("prediction_horizon", 30)  # dias
    
    def add_historical_data(self, contract: APIContract, changes: List[APIChange]):
        """Adiciona dados históricos para análise"""
        self.historical_data.append({
            "contract": contract,
            "changes": changes,
            "timestamp": datetime.now()
        })
    
    def analyze_change_patterns(self) -> Dict[str, Any]:
        """Analisa padrões de mudanças históricas"""
        if len(self.historical_data) < 2:
            return {"error": "Dados históricos insuficientes"}
        
        patterns = {
            "change_frequency": self._calculate_change_frequency(),
            "risk_distribution": self._calculate_risk_distribution(),
            "endpoint_volatility": self._calculate_endpoint_volatility(),
            "version_patterns": self._analyze_version_patterns(),
            "seasonal_patterns": self._analyze_seasonal_patterns()
        }
        
        return patterns
    
    def _calculate_change_frequency(self) -> Dict[str, float]:
        """Calcula frequência de mudanças"""
        if len(self.historical_data) < 2:
            return {}
        
        total_days = (self.historical_data[-1]["timestamp"] - self.historical_data[0]["timestamp"]).days
        total_changes = sum(len(data["changes"]) for data in self.historical_data)
        
        return {
            "changes_per_day": total_changes / total_days if total_days > 0 else 0,
            "changes_per_version": total_changes / len(self.historical_data),
            "total_changes": total_changes,
            "total_versions": len(self.historical_data)
        }
    
    def _calculate_risk_distribution(self) -> Dict[str, int]:
        """Calcula distribuição de riscos"""
        risk_counts = defaultdict(int)
        
        for data in self.historical_data:
            for change in data["changes"]:
                risk_counts[change.risk_level.value] += 1
        
        return dict(risk_counts)
    
    def _calculate_endpoint_volatility(self) -> Dict[str, float]:
        """Calcula volatilidade dos endpoints"""
        endpoint_changes = defaultdict(int)
        
        for data in self.historical_data:
            for change in data["changes"]:
                if change.endpoint:
                    endpoint_changes[change.endpoint] += 1
        
        if not endpoint_changes:
            return {}
        
        changes_list = list(endpoint_changes.values())
        return {
            "mean_changes": statistics.mean(changes_list),
            "std_changes": statistics.stdev(changes_list) if len(changes_list) > 1 else 0,
            "most_volatile": max(endpoint_changes.items(), key=lambda value: value[1])[0],
            "least_volatile": min(endpoint_changes.items(), key=lambda value: value[1])[0]
        }
    
    def _analyze_version_patterns(self) -> Dict[str, Any]:
        """Analisa padrões de versionamento"""
        versions = [data["contract"].version for data in self.historical_data]
        
        if len(versions) < 2:
            return {}
        
        # Análise de padrões de versionamento semântico
        major_versions = [value.split('.')[0] for value in versions]
        minor_versions = [value.split('.')[1] if len(value.split('.')) > 1 else '0' for value in versions]
        
        return {
            "major_version_changes": len(set(major_versions)),
            "minor_version_changes": len(set(minor_versions)),
            "version_sequence": versions,
            "breaking_changes_frequency": self._count_breaking_changes()
        }
    
    def _count_breaking_changes(self) -> int:
        """Conta mudanças breaking"""
        breaking_count = 0
        
        for data in self.historical_data:
            for change in data["changes"]:
                if change.risk_level == RiskLevel.CRITICAL:
                    breaking_count += 1
        
        return breaking_count
    
    def _analyze_seasonal_patterns(self) -> Dict[str, Any]:
        """Analisa padrões sazonais"""
        if len(self.historical_data) < 4:
            return {}
        
        # Análise simples de padrões por mês
        monthly_changes = defaultdict(int)
        
        for data in self.historical_data:
            month = data["timestamp"].strftime("%Y-%m")
            monthly_changes[month] += len(data["changes"])
        
        return {
            "monthly_patterns": dict(monthly_changes),
            "peak_month": max(monthly_changes.items(), key=lambda value: value[1])[0],
            "quiet_month": min(monthly_changes.items(), key=lambda value: value[1])[0]
        }
    
    def predict_drift(self, current_contract: APIContract) -> DriftPrediction:
        """
        Prediz drift baseado em dados históricos
        
        Args:
            current_contract: Contrato atual
            
        Returns:
            DriftPrediction: Predição de drift
        """
        if len(self.historical_data) < 2:
            return DriftPrediction(
                api_name=current_contract.name,
                current_version=current_contract.version,
                predicted_version="unknown",
                predicted_changes=[],
                confidence_score=0.0,
                risk_score=0.0,
                predicted_date=datetime.now() + timedelta(days=self.prediction_horizon),
                impact_analysis="Dados históricos insuficientes para predição",
                recommendations=["Coletar mais dados históricos"]
            )
        
        # Análise de padrões
        patterns = self.analyze_change_patterns()
        
        # Predição baseada em padrões históricos
        predicted_changes = self._predict_changes_based_on_patterns(patterns)
        
        # Calcular scores
        confidence_score = self._calculate_confidence_score(patterns)
        risk_score = self._calculate_risk_score(predicted_changes)
        
        # Predizer próxima versão
        predicted_version = self._predict_next_version(current_contract.version, patterns)
        
        # Predizer data
        predicted_date = self._predict_next_change_date(patterns)
        
        return DriftPrediction(
            api_name=current_contract.name,
            current_version=current_contract.version,
            predicted_version=predicted_version,
            predicted_changes=predicted_changes,
            confidence_score=confidence_score,
            risk_score=risk_score,
            predicted_date=predicted_date,
            impact_analysis=self._generate_impact_analysis(predicted_changes),
            recommendations=self._generate_recommendations(predicted_changes, patterns)
        )
    
    def _predict_changes_based_on_patterns(self, patterns: Dict[str, Any]) -> List[APIChange]:
        """Prediz mudanças baseado em padrões"""
        predicted_changes = []
        
        # Predizer mudanças baseado na frequência histórica
        change_frequency = patterns.get("change_frequency", {})
        avg_changes_per_version = change_frequency.get("changes_per_version", 0)
        
        if avg_changes_per_version > 0:
            # Predizer número de mudanças
            predicted_change_count = int(avg_changes_per_version)
            
            # Distribuir por tipo de risco
            risk_distribution = patterns.get("risk_distribution", {})
            total_historical_changes = sum(risk_distribution.values())
            
            if total_historical_changes > 0:
                for risk_level, count in risk_distribution.items():
                    probability = count / total_historical_changes
                    predicted_count = int(predicted_change_count * probability)
                    
                    for _ in range(predicted_count):
                        predicted_changes.append(APIChange(
                            change_type=ChangeType.MODIFICATION,
                            risk_level=RiskLevel(risk_level),
                            description=f"Predicted {risk_level} risk change",
                            confidence=0.6
                        ))
        
        return predicted_changes
    
    def _calculate_confidence_score(self, patterns: Dict[str, Any]) -> float:
        """Calcula score de confiança da predição"""
        if not patterns:
            return 0.0
        
        # Fatores que aumentam confiança
        confidence_factors = []
        
        # Quantidade de dados históricos
        total_versions = patterns.get("change_frequency", {}).get("total_versions", 0)
        if total_versions >= 5:
            confidence_factors.append(0.3)
        elif total_versions >= 3:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
        
        # Padrões consistentes
        volatility = patterns.get("endpoint_volatility", {})
        if volatility.get("std_changes", 0) < 2:
            confidence_factors.append(0.2)
        
        # Padrões sazonais
        seasonal = patterns.get("seasonal_patterns", {})
        if len(seasonal.get("monthly_patterns", {})) >= 6:
            confidence_factors.append(0.2)
        
        return min(sum(confidence_factors), 1.0)
    
    def _calculate_risk_score(self, predicted_changes: List[APIChange]) -> float:
        """Calcula score de risco da predição"""
        if not predicted_changes:
            return 0.0
        
        risk_weights = {
            RiskLevel.LOW: 0.1,
            RiskLevel.MEDIUM: 0.3,
            RiskLevel.HIGH: 0.6,
            RiskLevel.CRITICAL: 1.0
        }
        
        total_risk = sum(risk_weights[change.risk_level] for change in predicted_changes)
        return min(total_risk / len(predicted_changes), 1.0)
    
    def _predict_next_version(self, current_version: str, patterns: Dict[str, Any]) -> str:
        """Prediz próxima versão"""
        try:
            version_parts = current_version.split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            patch = int(version_parts[2]) if len(version_parts) > 2 else 0
            
            # Análise de padrões de versionamento
            version_patterns = patterns.get("version_patterns", {})
            breaking_frequency = version_patterns.get("breaking_changes_frequency", 0)
            
            if breaking_frequency > 0:
                # Predizer major version bump
                return f"{major + 1}.0.0"
            else:
                # Predizer minor version bump
                return f"{major}.{minor + 1}.0"
                
        except (ValueError, IndexError):
            return f"{current_version}+1"
    
    def _predict_next_change_date(self, patterns: Dict[str, Any]) -> datetime:
        """Prediz data da próxima mudança"""
        change_frequency = patterns.get("change_frequency", {})
        changes_per_day = change_frequency.get("changes_per_day", 0)
        
        if changes_per_day > 0:
            days_until_next = 1 / changes_per_day
        else:
            days_until_next = self.prediction_horizon
        
        return datetime.now() + timedelta(days=min(days_until_next, self.prediction_horizon))
    
    def _generate_impact_analysis(self, predicted_changes: List[APIChange]) -> str:
        """Gera análise de impacto das mudanças preditas"""
        if not predicted_changes:
            return "Nenhuma mudança significativa predita"
        
        critical_changes = [c for c in predicted_changes if c.risk_level == RiskLevel.CRITICAL]
        high_changes = [c for c in predicted_changes if c.risk_level == RiskLevel.HIGH]
        
        impact = []
        
        if critical_changes:
            impact.append(f"{len(critical_changes)} mudanças críticas preditas")
        
        if high_changes:
            impact.append(f"{len(high_changes)} mudanças de alto risco preditas")
        
        if impact:
            return f"Impacto esperado: {'; '.join(impact)}"
        else:
            return "Impacto baixo esperado"
    
    def _generate_recommendations(self, predicted_changes: List[APIChange], patterns: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nas predições"""
        recommendations = []
        
        if predicted_changes:
            recommendations.append("Implementar monitoramento de mudanças em tempo real")
            recommendations.append("Preparar planos de contingência para mudanças críticas")
        
        critical_changes = [c for c in predicted_changes if c.risk_level == RiskLevel.CRITICAL]
        if critical_changes:
            recommendations.append("Implementar fallbacks para funcionalidades críticas")
            recommendations.append("Estabelecer comunicação com provedor da API")
        
        # Recomendações baseadas em padrões
        change_frequency = patterns.get("change_frequency", {})
        if change_frequency.get("changes_per_version", 0) > 5:
            recommendations.append("Considerar implementar versionamento de API")
        
        return recommendations


class ContractDriftPredictor:
    """
    Sistema principal de predição de drift de contratos
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o preditor de drift
        
        Args:
            config: Configuração opcional
        """
        self.config = config or {}
        self.analyzer = ContractAnalyzer(config.get("analyzer", {}))
        self.predictor = DriftPredictor(config.get("predictor", {}))
        self.contracts_history = {}
        self.reports = []
    
    async def analyze_api_contract(self, api_name: str, contract_data: Dict) -> APIContract:
        """
        Analisa contrato de API
        
        Args:
            api_name: Nome da API
            contract_data: Dados do contrato
            
        Returns:
            APIContract: Contrato analisado
        """
        contract = APIContract(
            name=api_name,
            version=contract_data.get("version", "1.0.0"),
            base_url=contract_data.get("base_url", ""),
            endpoints=contract_data.get("endpoints", {}),
            schemas=contract_data.get("schemas", {}),
            headers=contract_data.get("headers", {}),
            authentication=contract_data.get("authentication", {}),
            rate_limits=contract_data.get("rate_limits", {}),
            documentation_url=contract_data.get("documentation_url"),
            last_updated=datetime.now()
        )
        
        return contract
    
    async def detect_changes(self, api_name: str, new_contract: APIContract) -> List[APIChange]:
        """
        Detecta mudanças em contrato
        
        Args:
            api_name: Nome da API
            new_contract: Novo contrato
            
        Returns:
            List[APIChange]: Mudanças detectadas
        """
        if api_name not in self.contracts_history:
            # Primeira análise
            self.contracts_history[api_name] = new_contract
            return []
        
        old_contract = self.contracts_history[api_name]
        changes = self.analyzer.analyze_contract_changes(old_contract, new_contract)
        
        # Atualizar histórico
        self.contracts_history[api_name] = new_contract
        
        # Adicionar dados históricos para predição
        self.predictor.add_historical_data(new_contract, changes)
        
        return changes
    
    async def predict_drift(self, api_name: str) -> DriftPrediction:
        """
        Prediz drift para API
        
        Args:
            api_name: Nome da API
            
        Returns:
            DriftPrediction: Predição de drift
        """
        if api_name not in self.contracts_history:
            return DriftPrediction(
                api_name=api_name,
                current_version="unknown",
                predicted_version="unknown",
                predicted_changes=[],
                confidence_score=0.0,
                risk_score=0.0,
                predicted_date=datetime.now() + timedelta(days=30),
                impact_analysis="Dados insuficientes para predição",
                recommendations=["Coletar dados históricos da API"]
            )
        
        current_contract = self.contracts_history[api_name]
        return self.predictor.predict_drift(current_contract)
    
    async def generate_drift_report(self, api_name: str) -> DriftReport:
        """
        Gera relatório completo de drift
        
        Args:
            api_name: Nome da API
            
        Returns:
            DriftReport: Relatório de drift
        """
        current_contract = self.contracts_history.get(api_name)
        if not current_contract:
            raise ValueError(f"Contrato não encontrado para API: {api_name}")
        
        # Obter contrato anterior se disponível
        previous_contract = None
        if len(self.predictor.historical_data) > 1:
            previous_data = self.predictor.historical_data[-2]
            if previous_data["contract"].name == api_name:
                previous_contract = previous_data["contract"]
        
        # Detectar mudanças recentes
        recent_changes = []
        if len(self.predictor.historical_data) > 0:
            recent_data = self.predictor.historical_data[-1]
            if recent_data["contract"].name == api_name:
                recent_changes = recent_data["changes"]
        
        # Predizer drift
        prediction = await self.predict_drift(api_name)
        
        # Calcular scores
        stability_score = self._calculate_stability_score(recent_changes, prediction)
        overall_risk = self._calculate_overall_risk(recent_changes, prediction)
        
        # Gerar recomendações
        recommendations = self._generate_overall_recommendations(recent_changes, prediction)
        
        report = DriftReport(
            api_name=api_name,
            current_contract=current_contract,
            previous_contract=previous_contract,
            detected_changes=recent_changes,
            predictions=[prediction],
            overall_risk=overall_risk,
            stability_score=stability_score,
            last_check=datetime.now(),
            next_check=datetime.now() + timedelta(days=7),
            recommendations=recommendations
        )
        
        self.reports.append(report)
        return report
    
    def _calculate_stability_score(self, changes: List[APIChange], prediction: DriftPrediction) -> float:
        """Calcula score de estabilidade"""
        if not changes and prediction.confidence_score < 0.5:
            return 1.0  # Muito estável
        
        # Penalizar por mudanças recentes
        change_penalty = len(changes) * 0.1
        
        # Penalizar por predições de alto risco
        risk_penalty = prediction.risk_score * 0.3
        
        stability = 1.0 - change_penalty - risk_penalty
        return max(stability, 0.0)
    
    def _calculate_overall_risk(self, changes: List[APIChange], prediction: DriftPrediction) -> RiskLevel:
        """Calcula risco geral"""
        # Verificar mudanças críticas recentes
        critical_changes = [c for c in changes if c.risk_level == RiskLevel.CRITICAL]
        if critical_changes:
            return RiskLevel.CRITICAL
        
        # Verificar predições de alto risco
        if prediction.risk_score > 0.7:
            return RiskLevel.HIGH
        
        # Verificar mudanças de alto risco
        high_changes = [c for c in changes if c.risk_level == RiskLevel.HIGH]
        if high_changes:
            return RiskLevel.HIGH
        
        # Verificar predições de médio risco
        if prediction.risk_score > 0.4:
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _generate_overall_recommendations(self, changes: List[APIChange], prediction: DriftPrediction) -> List[str]:
        """Gera recomendações gerais"""
        recommendations = []
        
        # Recomendações baseadas em mudanças recentes
        if changes:
            recommendations.append("Implementar monitoramento contínuo de mudanças")
            recommendations.append("Atualizar integrações afetadas pelas mudanças")
        
        # Recomendações baseadas em predições
        if prediction.confidence_score > 0.7:
            recommendations.append("Preparar para mudanças preditas")
            recommendations.append("Implementar testes para cenários preditos")
        
        if prediction.risk_score > 0.6:
            recommendations.append("Estabelecer comunicação com provedor da API")
            recommendations.append("Desenvolver planos de contingência")
        
        # Recomendações gerais
        recommendations.append("Manter documentação atualizada")
        recommendations.append("Implementar testes automatizados")
        
        return list(set(recommendations))  # Remove duplicatas
    
    def get_historical_analysis(self, api_name: str) -> Dict[str, Any]:
        """Obtém análise histórica da API"""
        if api_name not in self.contracts_history:
            return {"error": "API não encontrada"}
        
        return {
            "api_name": api_name,
            "current_version": self.contracts_history[api_name].version,
            "patterns": self.predictor.analyze_change_patterns(),
            "total_historical_changes": len(self.predictor.historical_data),
            "last_updated": self.contracts_history[api_name].last_updated.isoformat()
        }


# Funções de conveniência para uso global
async def create_drift_predictor(config: Optional[Dict] = None) -> ContractDriftPredictor:
    """
    Função de conveniência para criar preditor de drift
    
    Args:
        config: Configuração opcional
        
    Returns:
        ContractDriftPredictor: Preditor configurado
    """
    return ContractDriftPredictor(config)


async def analyze_api_changes(api_name: str, old_contract: Dict, new_contract: Dict, config: Optional[Dict] = None) -> List[APIChange]:
    """
    Função de conveniência para analisar mudanças em API
    
    Args:
        api_name: Nome da API
        old_contract: Contrato antigo
        new_contract: Contrato novo
        config: Configuração opcional
        
    Returns:
        List[APIChange]: Mudanças detectadas
    """
    predictor = ContractDriftPredictor(config)
    
    old_api_contract = await predictor.analyze_api_contract(api_name, old_contract)
    new_api_contract = await predictor.analyze_api_contract(api_name, new_contract)
    
    return predictor.analyzer.analyze_contract_changes(old_api_contract, new_api_contract)


async def predict_api_drift(api_name: str, contract_data: Dict, config: Optional[Dict] = None) -> DriftPrediction:
    """
    Função de conveniência para predizer drift de API
    
    Args:
        api_name: Nome da API
        contract_data: Dados do contrato
        config: Configuração opcional
        
    Returns:
        DriftPrediction: Predição de drift
    """
    predictor = ContractDriftPredictor(config)
    
    contract = await predictor.analyze_api_contract(api_name, contract_data)
    await predictor.detect_changes(api_name, contract)
    
    return await predictor.predict_drift(api_name)


if __name__ == "__main__":
    # Exemplo de uso
    config = {
        "analyzer": {
            "breaking_patterns": [r"value\data+\.0\.0", r"deprecated"],
            "warning_patterns": [r"value\data+\.\data+\.0", r"new"]
        },
        "predictor": {
            "confidence_threshold": 0.7,
            "prediction_horizon": 30
        }
    }
    
    async def main():
        predictor = ContractDriftPredictor(config)
        
        # Exemplo de contrato
        contract_data = {
            "version": "1.0.0",
            "base_url": "https://api.example.com",
            "endpoints": {
                "/users": {
                    "methods": ["GET", "POST"],
                    "parameters": {"limit": "integer"}
                }
            },
            "schemas": {
                "User": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    }
                }
            },
            "headers": {"Authorization": "Bearer"},
            "authentication": {"type": "bearer"},
            "rate_limits": {"requests_per_minute": 100}
        }
        
        # Analisar contrato
        contract = await predictor.analyze_api_contract("example_api", contract_data)
        changes = await predictor.detect_changes("example_api", contract)
        
        # Predizer drift
        prediction = await predictor.predict_drift("example_api")
        
        # Gerar relatório
        report = await predictor.generate_drift_report("example_api")
        
        print(json.dumps({
            "contract_hash": contract.hash,
            "changes_detected": len(changes),
            "prediction_confidence": prediction.confidence_score,
            "prediction_risk": prediction.risk_score,
            "overall_risk": report.overall_risk.value,
            "stability_score": report.stability_score
        }, indent=2))
    
    asyncio.run(main()) 