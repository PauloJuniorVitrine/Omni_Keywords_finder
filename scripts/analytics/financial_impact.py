#!/usr/bin/env python3
"""
Sistema de Estimação de Impacto Financeiro - Omni Keywords Finder
Tracing ID: OBS_004_20241219_001
Data: 2024-12-19
Versão: 1.0

Implementa análise financeira com:
- Cálculo de custos de falhas
- Análise de ROI de integrações
- Simulação de cenários
- Relatórios executivos
- Métricas de negócio
- Análise de tendências financeiras
- Dashboard de impacto financeiro
"""

import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path

class ImpactType(Enum):
    """Tipos de impacto financeiro"""
    COST_AVOIDANCE = "cost_avoidance"
    REVENUE_LOSS = "revenue_loss"
    OPERATIONAL_COST = "operational_cost"
    COMPLIANCE_PENALTY = "compliance_penalty"
    CUSTOMER_CHURN = "customer_churn"

class IntegrationTier(Enum):
    """Tiers de integração por criticidade"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class FinancialImpact:
    """Impacto financeiro de uma integração"""
    integration_name: str
    impact_type: ImpactType
    amount: float
    currency: str
    period_start: datetime
    period_end: datetime
    description: str
    confidence_level: float  # 0.0 a 1.0
    source: str

@dataclass
class ROIAnalysis:
    """Análise de ROI de integração"""
    integration_name: str
    initial_investment: float
    operational_costs: float
    revenue_generated: float
    cost_savings: float
    roi_percentage: float
    payback_period_months: float
    net_present_value: float
    internal_rate_of_return: float

@dataclass
class FailureCost:
    """Custo de falha de integração"""
    integration_name: str
    failure_type: str
    downtime_minutes: int
    revenue_loss_per_minute: float
    operational_cost_per_minute: float
    customer_impact_score: float  # 0.0 a 1.0
    total_cost: float
    mitigation_cost: float
    net_impact: float

@dataclass
class FinancialReport:
    """Relatório financeiro executivo"""
    period_start: datetime
    period_end: datetime
    total_revenue_impact: float
    total_cost_impact: float
    net_financial_impact: float
    roi_by_integration: Dict[str, ROIAnalysis]
    failure_costs: List[FailureCost]
    recommendations: List[str]
    risk_assessment: Dict[str, float]

class FinancialImpactAnalyzer:
    """
    Sistema de análise de impacto financeiro com cálculos
    de ROI, custos de falhas e simulações de cenários.
    """
    
    def __init__(self, db_path: str = "financial_impact.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Configurações financeiras por integração
        self.financial_configs = {
            "google_trends": {
                "tier": IntegrationTier.CRITICAL,
                "revenue_per_request": 0.50,  # USD
                "operational_cost_per_request": 0.10,
                "customer_impact_weight": 0.8,
                "compliance_penalty_per_violation": 1000.0,
                "initial_investment": 50000.0,
                "monthly_operational_cost": 5000.0
            },
            "amazon_api": {
                "tier": IntegrationTier.HIGH,
                "revenue_per_request": 1.00,
                "operational_cost_per_request": 0.20,
                "customer_impact_weight": 0.6,
                "compliance_penalty_per_violation": 500.0,
                "initial_investment": 30000.0,
                "monthly_operational_cost": 3000.0
            },
            "webhook_system": {
                "tier": IntegrationTier.MEDIUM,
                "revenue_per_request": 0.25,
                "operational_cost_per_request": 0.05,
                "customer_impact_weight": 0.4,
                "compliance_penalty_per_violation": 200.0,
                "initial_investment": 15000.0,
                "monthly_operational_cost": 1500.0
            },
            "database_operations": {
                "tier": IntegrationTier.CRITICAL,
                "revenue_per_request": 0.75,
                "operational_cost_per_request": 0.15,
                "customer_impact_weight": 0.9,
                "compliance_penalty_per_violation": 2000.0,
                "initial_investment": 25000.0,
                "monthly_operational_cost": 2500.0
            }
        }
        
        # Configurações de análise
        self.analysis_config = {
            "discount_rate": 0.10,  # 10% ao ano
            "inflation_rate": 0.02,  # 2% ao ano
            "risk_free_rate": 0.03,  # 3% ao ano
            "market_risk_premium": 0.07,  # 7%
            "analysis_period_months": 12,
            "confidence_interval": 0.95
        }
        
        # Inicializar banco de dados
        self._init_database()
    
    def _init_database(self) -> None:
        """Inicializa banco de dados para análise financeira."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de impactos financeiros
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS financial_impacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        integration_name TEXT NOT NULL,
                        impact_type TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        period_start DATETIME NOT NULL,
                        period_end DATETIME NOT NULL,
                        description TEXT NOT NULL,
                        confidence_level REAL NOT NULL,
                        source TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de custos de falhas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS failure_costs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        integration_name TEXT NOT NULL,
                        failure_type TEXT NOT NULL,
                        downtime_minutes INTEGER NOT NULL,
                        revenue_loss_per_minute REAL NOT NULL,
                        operational_cost_per_minute REAL NOT NULL,
                        customer_impact_score REAL NOT NULL,
                        total_cost REAL NOT NULL,
                        mitigation_cost REAL NOT NULL,
                        net_impact REAL NOT NULL,
                        occurred_at DATETIME NOT NULL
                    )
                """)
                
                # Tabela de análises de ROI
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS roi_analyses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        integration_name TEXT NOT NULL,
                        initial_investment REAL NOT NULL,
                        operational_costs REAL NOT NULL,
                        revenue_generated REAL NOT NULL,
                        cost_savings REAL NOT NULL,
                        roi_percentage REAL NOT NULL,
                        payback_period_months REAL NOT NULL,
                        net_present_value REAL NOT NULL,
                        internal_rate_of_return REAL NOT NULL,
                        analysis_date DATETIME NOT NULL
                    )
                """)
                
                # Índices para performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_impacts_integration_time 
                    ON financial_impacts(integration_name, period_start)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_failures_integration_time 
                    ON failure_costs(integration_name, occurred_at)
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados financeiro: {e}")
            raise
    
    def calculate_failure_cost(self, integration_name: str, downtime_minutes: int,
                              failure_type: str = "outage") -> FailureCost:
        """
        Calcula custo de falha de uma integração.
        
        Args:
            integration_name: Nome da integração
            downtime_minutes: Tempo de indisponibilidade em minutos
            failure_type: Tipo da falha
            
        Returns:
            Objeto FailureCost com cálculos
        """
        try:
            if integration_name not in self.financial_configs:
                raise ValueError(f"Configuração financeira não encontrada para {integration_name}")
            
            config = self.financial_configs[integration_name]
            
            # Calcular perda de receita por minuto
            revenue_per_minute = config["revenue_per_request"] * 60  # Assumindo 60 requests/min
            revenue_loss = revenue_per_minute * downtime_minutes
            
            # Calcular custo operacional por minuto
            operational_cost_per_minute = config["operational_cost_per_request"] * 60
            operational_cost = operational_cost_per_minute * downtime_minutes
            
            # Calcular custo total
            total_cost = revenue_loss + operational_cost
            
            # Calcular custo de mitigação (baseado no tier)
            mitigation_multiplier = {
                IntegrationTier.CRITICAL: 0.5,
                IntegrationTier.HIGH: 0.3,
                IntegrationTier.MEDIUM: 0.2,
                IntegrationTier.LOW: 0.1
            }
            
            mitigation_cost = total_cost * mitigation_multiplier[config["tier"]]
            
            # Calcular impacto líquido
            net_impact = total_cost - mitigation_cost
            
            # Criar objeto de custo de falha
            failure_cost = FailureCost(
                integration_name=integration_name,
                failure_type=failure_type,
                downtime_minutes=downtime_minutes,
                revenue_loss_per_minute=revenue_per_minute,
                operational_cost_per_minute=operational_cost_per_minute,
                customer_impact_score=config["customer_impact_weight"],
                total_cost=total_cost,
                mitigation_cost=mitigation_cost,
                net_impact=net_impact
            )
            
            # Salvar no banco
            self._save_failure_cost(failure_cost)
            
            return failure_cost
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular custo de falha: {e}")
            raise
    
    def _save_failure_cost(self, failure_cost: FailureCost) -> None:
        """Salva custo de falha no banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO failure_costs 
                    (integration_name, failure_type, downtime_minutes, revenue_loss_per_minute,
                     operational_cost_per_minute, customer_impact_score, total_cost, 
                     mitigation_cost, net_impact, occurred_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    failure_cost.integration_name,
                    failure_cost.failure_type,
                    failure_cost.downtime_minutes,
                    failure_cost.revenue_loss_per_minute,
                    failure_cost.operational_cost_per_minute,
                    failure_cost.customer_impact_score,
                    failure_cost.total_cost,
                    failure_cost.mitigation_cost,
                    failure_cost.net_impact,
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar custo de falha: {e}")
    
    def calculate_roi(self, integration_name: str, 
                     period_months: int = 12) -> ROIAnalysis:
        """
        Calcula ROI de uma integração.
        
        Args:
            integration_name: Nome da integração
            period_months: Período de análise em meses
            
        Returns:
            Objeto ROIAnalysis com cálculos
        """
        try:
            if integration_name not in self.financial_configs:
                raise ValueError(f"Configuração financeira não encontrada para {integration_name}")
            
            config = self.financial_configs[integration_name]
            
            # Dados de investimento
            initial_investment = config["initial_investment"]
            monthly_operational_cost = config["monthly_operational_cost"]
            operational_costs = monthly_operational_cost * period_months
            
            # Calcular receita gerada (baseado em requests estimados)
            estimated_requests_per_month = 100000  # Estimativa
            revenue_per_request = config["revenue_per_request"]
            revenue_generated = estimated_requests_per_month * revenue_per_request * period_months
            
            # Calcular economia de custos (comparado com alternativa manual)
            manual_cost_per_request = revenue_per_request * 2  # Custo manual é 2x maior
            cost_savings = (manual_cost_per_request - config["operational_cost_per_request"]) * estimated_requests_per_month * period_months
            
            # Calcular ROI
            total_investment = initial_investment + operational_costs
            total_return = revenue_generated + cost_savings
            roi_percentage = ((total_return - total_investment) / total_investment) * 100
            
            # Calcular período de payback
            monthly_return = (revenue_generated + cost_savings) / period_months
            payback_period_months = initial_investment / monthly_return if monthly_return > 0 else float('inf')
            
            # Calcular NPV (Net Present Value)
            discount_rate_monthly = self.analysis_config["discount_rate"] / 12
            npv = -initial_investment
            
            for month in range(1, period_months + 1):
                monthly_cash_flow = monthly_return - monthly_operational_cost
                npv += monthly_cash_flow / ((1 + discount_rate_monthly) ** month)
            
            # Calcular IRR (Internal Rate of Return) - aproximação
            irr = (total_return / total_investment) ** (1 / period_months) - 1
            
            # Criar objeto de análise ROI
            roi_analysis = ROIAnalysis(
                integration_name=integration_name,
                initial_investment=initial_investment,
                operational_costs=operational_costs,
                revenue_generated=revenue_generated,
                cost_savings=cost_savings,
                roi_percentage=roi_percentage,
                payback_period_months=payback_period_months,
                net_present_value=npv,
                internal_rate_of_return=irr
            )
            
            # Salvar no banco
            self._save_roi_analysis(roi_analysis)
            
            return roi_analysis
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular ROI: {e}")
            raise
    
    def _save_roi_analysis(self, roi_analysis: ROIAnalysis) -> None:
        """Salva análise de ROI no banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO roi_analyses 
                    (integration_name, initial_investment, operational_costs, revenue_generated,
                     cost_savings, roi_percentage, payback_period_months, net_present_value,
                     internal_rate_of_return, analysis_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    roi_analysis.integration_name,
                    roi_analysis.initial_investment,
                    roi_analysis.operational_costs,
                    roi_analysis.revenue_generated,
                    roi_analysis.cost_savings,
                    roi_analysis.roi_percentage,
                    roi_analysis.payback_period_months,
                    roi_analysis.net_present_value,
                    roi_analysis.internal_rate_of_return,
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar análise ROI: {e}")
    
    def record_financial_impact(self, integration_name: str, impact_type: ImpactType,
                               amount: float, description: str, 
                               period_start: datetime, period_end: datetime,
                               confidence_level: float = 0.8, source: str = "manual") -> None:
        """
        Registra impacto financeiro.
        
        Args:
            integration_name: Nome da integração
            impact_type: Tipo do impacto
            amount: Valor do impacto
            description: Descrição do impacto
            period_start: Início do período
            period_end: Fim do período
            confidence_level: Nível de confiança (0.0 a 1.0)
            source: Fonte dos dados
        """
        try:
            financial_impact = FinancialImpact(
                integration_name=integration_name,
                impact_type=impact_type,
                amount=amount,
                currency="USD",
                period_start=period_start,
                period_end=period_end,
                description=description,
                confidence_level=confidence_level,
                source=source
            )
            
            # Salvar no banco
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO financial_impacts 
                    (integration_name, impact_type, amount, currency, period_start, period_end,
                     description, confidence_level, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    financial_impact.integration_name,
                    financial_impact.impact_type.value,
                    financial_impact.amount,
                    financial_impact.currency,
                    financial_impact.period_start.isoformat(),
                    financial_impact.period_end.isoformat(),
                    financial_impact.description,
                    financial_impact.confidence_level,
                    financial_impact.source
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao registrar impacto financeiro: {e}")
    
    def generate_financial_report(self, period_months: int = 12) -> FinancialReport:
        """
        Gera relatório financeiro executivo.
        
        Args:
            period_months: Período de análise em meses
            
        Returns:
            Relatório financeiro completo
        """
        try:
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(days=period_months * 30)
            
            # Calcular ROI para todas as integrações
            roi_by_integration = {}
            for integration_name in self.financial_configs.keys():
                roi_analysis = self.calculate_roi(integration_name, period_months)
                roi_by_integration[integration_name] = roi_analysis
            
            # Buscar custos de falhas do período
            failure_costs = self._get_failure_costs_period(period_start, period_end)
            
            # Calcular impactos totais
            total_revenue_impact = sum(roi.revenue_generated for roi in roi_by_integration.values())
            total_cost_impact = sum(roi.operational_costs for roi in roi_by_integration.values())
            net_financial_impact = total_revenue_impact - total_cost_impact
            
            # Calcular risco por integração
            risk_assessment = self._calculate_risk_assessment(roi_by_integration, failure_costs)
            
            # Gerar recomendações
            recommendations = self._generate_financial_recommendations(
                roi_by_integration, failure_costs, risk_assessment
            )
            
            return FinancialReport(
                period_start=period_start,
                period_end=period_end,
                total_revenue_impact=total_revenue_impact,
                total_cost_impact=total_cost_impact,
                net_financial_impact=net_financial_impact,
                roi_by_integration=roi_by_integration,
                failure_costs=failure_costs,
                recommendations=recommendations,
                risk_assessment=risk_assessment
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório financeiro: {e}")
            raise
    
    def _get_failure_costs_period(self, period_start: datetime, 
                                 period_end: datetime) -> List[FailureCost]:
        """Busca custos de falhas de um período."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT integration_name, failure_type, downtime_minutes, 
                           revenue_loss_per_minute, operational_cost_per_minute,
                           customer_impact_score, total_cost, mitigation_cost, net_impact, occurred_at
                    FROM failure_costs 
                    WHERE occurred_at BETWEEN ? AND ?
                    ORDER BY occurred_at DESC
                """, (period_start.isoformat(), period_end.isoformat()))
                
                failure_costs = []
                for row in cursor.fetchall():
                    failure_costs.append(FailureCost(
                        integration_name=row[0],
                        failure_type=row[1],
                        downtime_minutes=row[2],
                        revenue_loss_per_minute=row[3],
                        operational_cost_per_minute=row[4],
                        customer_impact_score=row[5],
                        total_cost=row[6],
                        mitigation_cost=row[7],
                        net_impact=row[8]
                    ))
                
                return failure_costs
                
        except Exception as e:
            self.logger.error(f"Erro ao buscar custos de falhas: {e}")
            return []
    
    def _calculate_risk_assessment(self, roi_by_integration: Dict[str, ROIAnalysis],
                                  failure_costs: List[FailureCost]) -> Dict[str, float]:
        """Calcula avaliação de risco por integração."""
        risk_assessment = {}
        
        for integration_name in self.financial_configs.keys():
            # Fator de risco baseado no ROI
            roi = roi_by_integration.get(integration_name)
            roi_risk = 1.0 - min(roi.roi_percentage / 100, 1.0) if roi else 1.0
            
            # Fator de risco baseado em falhas
            integration_failures = [fc for fc in failure_costs if fc.integration_name == integration_name]
            failure_risk = len(integration_failures) * 0.1  # 10% por falha
            
            # Fator de risco baseado no tier
            tier = self.financial_configs[integration_name]["tier"]
            tier_risk = {
                IntegrationTier.CRITICAL: 0.8,
                IntegrationTier.HIGH: 0.6,
                IntegrationTier.MEDIUM: 0.4,
                IntegrationTier.LOW: 0.2
            }[tier]
            
            # Risco total (média ponderada)
            total_risk = (roi_risk * 0.4 + failure_risk * 0.3 + tier_risk * 0.3)
            risk_assessment[integration_name] = min(total_risk, 1.0)
        
        return risk_assessment
    
    def _generate_financial_recommendations(self, roi_by_integration: Dict[str, ROIAnalysis],
                                           failure_costs: List[FailureCost],
                                           risk_assessment: Dict[str, float]) -> List[str]:
        """Gera recomendações financeiras."""
        recommendations = []
        
        # Análise de ROI
        low_roi_integrations = [
            name for name, roi in roi_by_integration.items() 
            if roi.roi_percentage < 50
        ]
        
        if low_roi_integrations:
            recommendations.append(f"Revisar integrações com baixo ROI: {', '.join(low_roi_integrations)}")
        
        # Análise de falhas
        if failure_costs:
            total_failure_cost = sum(fc.net_impact for fc in failure_costs)
            recommendations.append(f"Implementar medidas de mitigação para reduzir custos de falhas (${total_failure_cost:,.2f})")
        
        # Análise de risco
        high_risk_integrations = [
            name for name, risk in risk_assessment.items() 
            if risk > 0.7
        ]
        
        if high_risk_integrations:
            recommendations.append(f"Priorizar redução de risco nas integrações: {', '.join(high_risk_integrations)}")
        
        # Recomendações gerais
        recommendations.append("Considerar investimento em redundância para integrações críticas")
        recommendations.append("Implementar monitoramento proativo para reduzir tempo de detecção de falhas")
        
        return recommendations
    
    def simulate_scenario(self, scenario_name: str, 
                         changes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simula cenário financeiro com mudanças específicas.
        
        Args:
            scenario_name: Nome do cenário
            changes: Mudanças a serem aplicadas
            
        Returns:
            Resultados da simulação
        """
        try:
            # Criar cópia das configurações para simulação
            simulated_configs = self.financial_configs.copy()
            
            # Aplicar mudanças
            for integration_name, changes_dict in changes.items():
                if integration_name in simulated_configs:
                    simulated_configs[integration_name].update(changes_dict)
            
            # Calcular ROI com configurações simuladas
            simulated_roi = {}
            for integration_name in simulated_configs.keys():
                # Temporariamente substituir configurações
                original_config = self.financial_configs[integration_name]
                self.financial_configs[integration_name] = simulated_configs[integration_name]
                
                try:
                    roi_analysis = self.calculate_roi(integration_name)
                    simulated_roi[integration_name] = roi_analysis
                finally:
                    # Restaurar configurações originais
                    self.financial_configs[integration_name] = original_config
            
            # Calcular diferenças
            baseline_roi = {}
            for integration_name in self.financial_configs.keys():
                baseline_roi[integration_name] = self.calculate_roi(integration_name)
            
            # Comparar resultados
            comparison = {}
            for integration_name in simulated_roi.keys():
                baseline = baseline_roi[integration_name]
                simulated = simulated_roi[integration_name]
                
                comparison[integration_name] = {
                    "baseline_roi": baseline.roi_percentage,
                    "simulated_roi": simulated.roi_percentage,
                    "roi_change": simulated.roi_percentage - baseline.roi_percentage,
                    "baseline_npv": baseline.net_present_value,
                    "simulated_npv": simulated.net_present_value,
                    "npv_change": simulated.net_present_value - baseline.net_present_value
                }
            
            return {
                "scenario_name": scenario_name,
                "changes_applied": changes,
                "comparison": comparison,
                "simulated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao simular cenário: {e}")
            raise


def get_financial_analyzer() -> FinancialImpactAnalyzer:
    """Retorna instância singleton do Financial Impact Analyzer."""
    if not hasattr(get_financial_analyzer, '_instance'):
        get_financial_analyzer._instance = FinancialImpactAnalyzer()
    return get_financial_analyzer._instance


if __name__ == '__main__':
    # Exemplo de uso
    analyzer = get_financial_analyzer()
    
    # Calcular custo de falha
    failure_cost = analyzer.calculate_failure_cost("google_trends", 30)  # 30 min downtime
    print(f"Custo de falha: ${failure_cost.net_impact:,.2f}")
    
    # Calcular ROI
    roi_analysis = analyzer.calculate_roi("google_trends")
    print(f"ROI: {roi_analysis.roi_percentage:.2f}%")
    
    # Gerar relatório
    report = analyzer.generate_financial_report()
    print(f"Impacto financeiro líquido: ${report.net_financial_impact:,.2f}")
    
    # Simular cenário
    scenario = analyzer.simulate_scenario("redução_custos", {
        "google_trends": {"operational_cost_per_request": 0.05}  # Reduzir custo operacional
    })
    print(f"Simulação: {scenario['scenario_name']}") 