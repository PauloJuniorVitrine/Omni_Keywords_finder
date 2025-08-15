"""
Schemas de Validação para Métricas de Negócio - Omni Keywords Finder
Validação robusta e estrutura de dados para métricas de negócio
Prompt: Implementação de sistema de métricas de negócio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator

class MetricType(Enum):
    """Tipos de métricas de negócio"""
    REVENUE = "revenue"
    USERS = "users"
    EXECUTIONS = "executions"
    CONVERSION = "conversion"
    RETENTION = "retention"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COSTS = "costs"
    GROWTH = "growth"

class MetricPeriod(Enum):
    """Períodos de métricas"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class MetricCategory(Enum):
    """Categorias de métricas"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    CUSTOMER = "customer"
    TECHNICAL = "technical"
    SECURITY = "security"
    GROWTH = "growth"

class BusinessMetric(BaseModel):
    """Schema para métrica de negócio"""
    
    # Identificação
    metric_id: str = Field(..., description="ID único da métrica")
    metric_type: str = Field(..., description="Tipo da métrica")
    metric_name: str = Field(..., description="Nome da métrica")
    category: str = Field(default="operational", description="Categoria da métrica")
    
    # Valores
    value: float = Field(..., description="Valor da métrica")
    previous_value: Optional[float] = Field(None, description="Valor anterior")
    target_value: Optional[float] = Field(None, description="Valor alvo")
    
    # Período
    period: str = Field(default="daily", description="Período da métrica")
    start_date: datetime = Field(..., description="Data inicial")
    end_date: datetime = Field(..., description="Data final")
    
    # Contexto
    user_id: Optional[str] = Field(None, description="ID do usuário")
    plan_type: Optional[str] = Field(None, description="Tipo de plano")
    region: Optional[str] = Field(None, description="Região")
    
    # Metadados
    source: str = Field(default="api", description="Origem da métrica")
    version: str = Field(default="1.0", description="Versão do schema")
    environment: str = Field(default="production", description="Ambiente")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Data de criação")
    
    @validator('metric_type')
    def validate_metric_type(cls, v):
        """Valida tipo da métrica"""
        valid_types = [metric.value for metric in MetricType]
        if v not in valid_types:
            raise ValueError(f'Tipo de métrica não suportado. Válidos: {", ".join(valid_types)}')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        """Valida categoria"""
        valid_categories = [category.value for category in MetricCategory]
        if v not in valid_categories:
            raise ValueError(f'Categoria inválida. Válidas: {", ".join(valid_categories)}')
        return v
    
    @validator('period')
    def validate_period(cls, v):
        """Valida período"""
        valid_periods = [period.value for period in MetricPeriod]
        if v not in valid_periods:
            raise ValueError(f'Período inválido. Válidos: {", ".join(valid_periods)}')
        return v
    
    @validator('metric_name')
    def validate_metric_name(cls, v):
        """Sanitiza nome da métrica"""
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        return sanitized
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Valida ID do usuário"""
        if v:
            sanitized = re.sub(r'[<>"\']', '', str(v).strip())
            return sanitized
        return v
    
    @validator('plan_type')
    def validate_plan_type(cls, v):
        """Valida tipo de plano"""
        if v:
            valid_plans = ['free', 'basic', 'premium', 'enterprise']
            if v not in valid_plans:
                raise ValueError(f'Tipo de plano inválido. Válidos: {", ".join(valid_plans)}')
        return v
    
    @root_validator
    def validate_date_range(cls, values):
        """Valida range de datas"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError('Data inicial não pode ser posterior à data final')
        
        return values

class MetricFilterSchema(BaseModel):
    """Schema para filtros de métricas"""
    
    # Filtros de tempo
    start_date: Optional[datetime] = Field(None, description="Data inicial")
    end_date: Optional[datetime] = Field(None, description="Data final")
    
    # Filtros de métrica
    metric_types: Optional[List[str]] = Field(None, description="Tipos de métrica")
    categories: Optional[List[str]] = Field(None, description="Categorias")
    periods: Optional[List[str]] = Field(None, description="Períodos")
    
    # Filtros de contexto
    user_id: Optional[str] = Field(None, description="ID do usuário")
    plan_type: Optional[str] = Field(None, description="Tipo de plano")
    region: Optional[str] = Field(None, description="Região")
    
    # Paginação
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Limite de resultados")
    offset: Optional[int] = Field(None, ge=0, description="Offset para paginação")
    
    # Ordenação
    sort_by: Optional[str] = Field(default="created_at", description="Campo para ordenação")
    sort_order: Optional[str] = Field(default="desc", description="Ordem de classificação")
    
    @validator('metric_types')
    def validate_metric_types(cls, v):
        """Valida tipos de métrica"""
        if v:
            valid_types = [metric.value for metric in MetricType]
            for metric_type in v:
                if metric_type not in valid_types:
                    raise ValueError(f'Tipo de métrica não suportado: {metric_type}')
        return v
    
    @validator('categories')
    def validate_categories(cls, v):
        """Valida categorias"""
        if v:
            valid_categories = [category.value for category in MetricCategory]
            for category in v:
                if category not in valid_categories:
                    raise ValueError(f'Categoria inválida: {category}')
        return v
    
    @validator('periods')
    def validate_periods(cls, v):
        """Valida períodos"""
        if v:
            valid_periods = [period.value for period in MetricPeriod]
            for period in v:
                if period not in valid_periods:
                    raise ValueError(f'Período inválido: {period}')
        return v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Valida ID do usuário"""
        if v:
            sanitized = re.sub(r'[<>"\']', '', str(v).strip())
            return sanitized
        return v
    
    @validator('plan_type')
    def validate_plan_type(cls, v):
        """Valida tipo de plano"""
        if v:
            valid_plans = ['free', 'basic', 'premium', 'enterprise']
            if v not in valid_plans:
                raise ValueError(f'Tipo de plano inválido. Válidos: {", ".join(valid_plans)}')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Valida campo de ordenação"""
        valid_fields = [
            'created_at', 'metric_type', 'category', 'period', 
            'value', 'user_id', 'plan_type', 'region'
        ]
        if v not in valid_fields:
            raise ValueError(f'Campo de ordenação inválido. Válidos: {", ".join(valid_fields)}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Valida ordem de classificação"""
        if v not in ['asc', 'desc']:
            raise ValueError('Ordem de classificação deve ser "asc" ou "desc"')
        return v
    
    @root_validator
    def validate_date_range(cls, values):
        """Valida range de datas"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValueError('Data inicial não pode ser posterior à data final')
        
        return values

class MetricAnalysisSchema(BaseModel):
    """Schema para análise de métricas"""
    
    # Identificação
    analysis_id: str = Field(..., description="ID único da análise")
    metric_type: str = Field(..., description="Tipo da métrica analisada")
    
    # Período de análise
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    # Estatísticas
    total_records: int = Field(..., description="Total de registros")
    average_value: float = Field(..., description="Valor médio")
    min_value: float = Field(..., description="Valor mínimo")
    max_value: float = Field(..., description="Valor máximo")
    median_value: float = Field(..., description="Valor mediano")
    standard_deviation: float = Field(..., description="Desvio padrão")
    
    # Tendências
    growth_rate: float = Field(..., description="Taxa de crescimento")
    trend_direction: str = Field(..., description="Direção da tendência")
    trend_strength: str = Field(..., description="Força da tendência")
    
    # Análise por segmento
    by_plan_type: Dict[str, float] = Field(default_factory=dict, description="Por tipo de plano")
    by_region: Dict[str, float] = Field(default_factory=dict, description="Por região")
    by_period: Dict[str, float] = Field(default_factory=dict, description="Por período")
    
    # Insights
    insights: List[str] = Field(default_factory=list, description="Insights identificados")
    recommendations: List[str] = Field(default_factory=list, description="Recomendações")
    alerts: List[str] = Field(default_factory=list, description="Alertas")
    
    # Metadados
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Data de geração")
    filters_applied: MetricFilterSchema = Field(..., description="Filtros aplicados")
    
    @validator('metric_type')
    def validate_metric_type(cls, v):
        """Valida tipo da métrica"""
        valid_types = [metric.value for metric in MetricType]
        if v not in valid_types:
            raise ValueError(f'Tipo de métrica não suportado. Válidos: {", ".join(valid_types)}')
        return v
    
    @validator('trend_direction')
    def validate_trend_direction(cls, v):
        """Valida direção da tendência"""
        valid_directions = ['up', 'down', 'stable', 'volatile']
        if v not in valid_directions:
            raise ValueError(f'Direção de tendência inválida. Válidas: {", ".join(valid_directions)}')
        return v
    
    @validator('trend_strength')
    def validate_trend_strength(cls, v):
        """Valida força da tendência"""
        valid_strengths = ['strong', 'moderate', 'weak', 'none']
        if v not in valid_strengths:
            raise ValueError(f'Força de tendência inválida. Válidas: {", ".join(valid_strengths)}')
        return v

class KPISchema(BaseModel):
    """Schema para KPIs de negócio"""
    
    # Identificação
    kpi_id: str = Field(..., description="ID único do KPI")
    kpi_name: str = Field(..., description="Nome do KPI")
    description: str = Field(..., description="Descrição do KPI")
    
    # Valores
    current_value: float = Field(..., description="Valor atual")
    target_value: float = Field(..., description="Valor alvo")
    previous_value: float = Field(..., description="Valor anterior")
    
    # Cálculos
    percentage_change: float = Field(..., description="Mudança percentual")
    target_achievement: float = Field(..., description="Atingimento do alvo (%)")
    status: str = Field(..., description="Status do KPI")
    
    # Período
    period: str = Field(..., description="Período do KPI")
    last_updated: datetime = Field(..., description="Última atualização")
    
    # Metadados
    category: str = Field(..., description="Categoria do KPI")
    priority: str = Field(..., description="Prioridade")
    owner: str = Field(..., description="Responsável")
    
    @validator('status')
    def validate_status(cls, v):
        """Valida status do KPI"""
        valid_statuses = ['on_track', 'at_risk', 'off_track', 'completed', 'not_started']
        if v not in valid_statuses:
            raise ValueError(f'Status inválido. Válidos: {", ".join(valid_statuses)}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        """Valida prioridade"""
        valid_priorities = ['high', 'medium', 'low']
        if v not in valid_priorities:
            raise ValueError(f'Prioridade inválida. Válidas: {", ".join(valid_priorities)}')
        return v
    
    @validator('kpi_name')
    def validate_kpi_name(cls, v):
        """Sanitiza nome do KPI"""
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        return sanitized

class DashboardSchema(BaseModel):
    """Schema para dashboard de métricas"""
    
    # Identificação
    dashboard_id: str = Field(..., description="ID único do dashboard")
    dashboard_name: str = Field(..., description="Nome do dashboard")
    description: str = Field(..., description="Descrição do dashboard")
    
    # Configuração
    layout: Dict[str, Any] = Field(default_factory=dict, description="Layout do dashboard")
    refresh_interval: int = Field(default=300, description="Intervalo de atualização (segundos)")
    auto_refresh: bool = Field(default=True, description="Atualização automática")
    
    # Métricas
    metrics: List[str] = Field(default_factory=list, description="IDs das métricas")
    kpis: List[str] = Field(default_factory=list, description="IDs dos KPIs")
    
    # Permissões
    is_public: bool = Field(default=False, description="Dashboard público")
    allowed_users: List[str] = Field(default_factory=list, description="Usuários permitidos")
    allowed_roles: List[str] = Field(default_factory=list, description="Roles permitidas")
    
    # Metadados
    created_by: str = Field(..., description="Criado por")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Data de criação")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Data de atualização")
    
    @validator('dashboard_name')
    def validate_dashboard_name(cls, v):
        """Sanitiza nome do dashboard"""
        sanitized = re.sub(r'[<>"\']', '', str(v).strip())
        return sanitized
    
    @validator('refresh_interval')
    def validate_refresh_interval(cls, v):
        """Valida intervalo de atualização"""
        if v < 30 or v > 3600:
            raise ValueError('Intervalo de atualização deve estar entre 30 e 3600 segundos')
        return v 