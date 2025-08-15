"""
Exemplo Prático - Sistema de Analytics Avançado
==============================================

Este exemplo demonstra o uso completo do sistema de analytics avançado do Omni Keywords Finder,
incluindo analytics em tempo real, análise de funnels e análise de coortes.

Características demonstradas:
- Analytics em tempo real com métricas avançadas
- Análise de funnels de conversão
- Análise de coortes com predições ML
- Dashboards interativos
- Exportação de dados
- Integração com observabilidade

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: ANALYTICS_EXAMPLE_001
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import random

# Imports do sistema de analytics
from infrastructure.analytics.avancado.real_time_analytics import (
    RealTimeAnalytics, AnalyticsEvent, EventType, RealTimeMetric
)
from infrastructure.analytics.avancado.funnel_analyzer import (
    FunnelAnalyzer, FunnelDefinition, FunnelStep, FunnelStepType
)
from infrastructure.analytics.avancado.cohort_analyzer import (
    CohortAnalyzer, CohortType, RetentionPeriod
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsAdvancedExample:
    """
    Exemplo prático do sistema de analytics avançado.
    
    Demonstra todas as funcionalidades implementadas:
    - Analytics em tempo real
    - Análise de funnels
    - Análise de coortes
    - Dashboards interativos
    - Exportação de dados
    """
    
    def __init__(self):
        """Inicializa o exemplo."""
        self.analytics = RealTimeAnalytics()
        self.funnel_analyzer = FunnelAnalyzer(self.analytics)
        self.cohort_analyzer = CohortAnalyzer()
        
        # Dados simulados para demonstração
        self.simulated_users = []
        self.simulated_events = []
        
        logger.info("[ANALYTICS_EXAMPLE] Sistema inicializado")
    
    def setup_simulated_data(self):
        """Configura dados simulados para demonstração."""
        logger.info("[ANALYTICS_EXAMPLE] Configurando dados simulados...")
        
        # Criar usuários simulados
        for index in range(100):
            user = {
                "user_id": f"user_{index:03d}",
                "signup_date": datetime.now() - timedelta(days=random.randint(1, 365)),
                "plan": random.choice(["free", "premium", "enterprise"]),
                "country": random.choice(["BR", "US", "CA", "UK", "DE"]),
                "source": random.choice(["organic", "paid", "referral", "social"])
            }
            self.simulated_users.append(user)
        
        # Criar eventos simulados
        event_types = [
            EventType.USER_LOGIN,
            EventType.KEYWORD_SEARCH,
            EventType.EXECUTION_START,
            EventType.EXECUTION_COMPLETE,
            EventType.EXPORT_DATA,
            EventType.FEATURE_USAGE
        ]
        
        for _ in range(1000):
            user = random.choice(self.simulated_users)
            event_type = random.choice(event_types)
            
            event_data = self._generate_event_data(event_type, user)
            
            event = AnalyticsEvent(
                event_type=event_type,
                user_id=user["user_id"],
                session_id=f"session_{random.randint(1000, 9999)}",
                timestamp=datetime.now() - timedelta(
                    hours=random.randint(0, 24),
                    minutes=random.randint(0, 60)
                ),
                data=event_data,
                metadata={
                    "user_plan": user["plan"],
                    "user_country": user["country"],
                    "user_source": user["source"]
                }
            )
            self.simulated_events.append(event)
        
        logger.info(f"[ANALYTICS_EXAMPLE] Dados simulados criados: {len(self.simulated_users)} usuários, {len(self.simulated_events)} eventos")
    
    def _generate_event_data(self, event_type: EventType, user: Dict[str, Any]) -> Dict[str, Any]:
        """Gera dados específicos para cada tipo de evento."""
        if event_type == EventType.KEYWORD_SEARCH:
            return {
                "query": random.choice(["seo", "marketing", "digital", "content", "analytics"]),
                "results_count": random.randint(10, 500),
                "search_time": random.randint(1, 30)
            }
        elif event_type == EventType.EXECUTION_START:
            return {
                "execution_type": random.choice(["keyword_analysis", "competitor_analysis", "trend_analysis"]),
                "keywords_count": random.randint(10, 1000)
            }
        elif event_type == EventType.EXECUTION_COMPLETE:
            return {
                "execution_time": random.randint(30, 300),
                "keywords_processed": random.randint(10, 1000),
                "success_rate": random.uniform(0.8, 1.0)
            }
        elif event_type == EventType.EXPORT_DATA:
            return {
                "export_format": random.choice(["csv", "json", "xlsx"]),
                "data_size": random.randint(100, 10000)
            }
        elif event_type == EventType.FEATURE_USAGE:
            return {
                "feature": random.choice(["dashboard", "reports", "alerts", "api", "integrations"]),
                "usage_duration": random.randint(10, 600)
            }
        else:
            return {"timestamp": datetime.now().isoformat()}
    
    def demonstrate_real_time_analytics(self):
        """Demonstra o sistema de analytics em tempo real."""
        logger.info("[ANALYTICS_EXAMPLE] Demonstrando analytics em tempo real...")
        
        # Iniciar o sistema
        self.analytics.start()
        
        # Simular eventos em tempo real
        for event in self.simulated_events[:100]:  # Primeiros 100 eventos
            self.analytics.track_event(event)
            time.sleep(0.01)  # Simular processamento
        
        # Obter métricas em tempo real
        metrics = self.analytics.get_real_time_metrics()
        
        print("\n📊 MÉTRICAS EM TEMPO REAL:")
        print("=" * 50)
        print(f"Total de eventos: {metrics.get('total_events', 0)}")
        print(f"Usuários ativos: {metrics.get('active_users', 0)}")
        print(f"Sessões ativas: {metrics.get('active_sessions', 0)}")
        
        # Métricas por tipo de evento
        events_by_type = metrics.get('events_by_type', {})
        print("\nEventos por tipo:")
        for event_type, count in events_by_type.items():
            print(f"  {event_type}: {count}")
        
        # Análise de usuário específico
        if self.simulated_users:
            user_analytics = self.analytics.get_user_analytics(self.simulated_users[0]["user_id"])
            print(f"\nAnálise do usuário {self.simulated_users[0]['user_id']}:")
            print(f"  Total de eventos: {user_analytics.get('total_events', 0)}")
            print(f"  Última atividade: {user_analytics.get('last_activity', 'N/A')}")
        
        # Dashboard data
        dashboard_data = self.analytics.get_dashboard_data()
        print(f"\nDados do dashboard: {len(dashboard_data.get('widgets', []))} widgets")
        
        logger.info("[ANALYTICS_EXAMPLE] Analytics em tempo real demonstrado")
    
    def demonstrate_funnel_analysis(self):
        """Demonstra a análise de funnels de conversão."""
        logger.info("[ANALYTICS_EXAMPLE] Demonstrando análise de funnels...")
        
        # Criar funnel de onboarding
        onboarding_funnel = FunnelDefinition(
            name="Onboarding de Usuários",
            description="Funnel completo de onboarding de novos usuários",
            steps=[
                FunnelStep(
                    name="Registro",
                    step_type=FunnelStepType.EVENT,
                    event_type=EventType.USER_LOGIN,
                    order=1,
                    description="Usuário faz login pela primeira vez"
                ),
                FunnelStep(
                    name="Primeira Busca",
                    step_type=FunnelStepType.EVENT,
                    event_type=EventType.KEYWORD_SEARCH,
                    order=2,
                    description="Usuário faz sua primeira busca de keywords"
                ),
                FunnelStep(
                    name="Primeira Execução",
                    step_type=FunnelStepType.EVENT,
                    event_type=EventType.EXECUTION_START,
                    order=3,
                    description="Usuário inicia sua primeira execução"
                ),
                FunnelStep(
                    name="Execução Completa",
                    step_type=FunnelStepType.EVENT,
                    event_type=EventType.EXECUTION_COMPLETE,
                    order=4,
                    description="Usuário completa sua primeira execução"
                ),
                FunnelStep(
                    name="Exportação",
                    step_type=FunnelStepType.EVENT,
                    event_type=EventType.EXPORT_DATA,
                    order=5,
                    description="Usuário exporta dados pela primeira vez"
                )
            ],
            time_window_hours=24,
            segment_by="user_plan"
        )
        
        # Criar o funnel
        funnel_id = self.funnel_analyzer.create_funnel(onboarding_funnel)
        print(f"\n🎯 FUNNEL CRIADO: {funnel_id}")
        
        # Simular eventos para o funnel
        for event in self.simulated_events[:200]:
            self.analytics.track_event(event)
        
        # Analisar o funnel
        result = self.funnel_analyzer.analyze_funnel(funnel_id)
        
        if result:
            print("\n📈 RESULTADOS DO FUNNEL:")
            print("=" * 50)
            print(f"Funnel: {result.funnel_name}")
            print(f"Total de usuários: {result.total_users}")
            print(f"Taxa de conversão geral: {result.overall_conversion_rate:.2%}")
            
            print("\nTaxas de conversão por etapa:")
            for index, (step, rate) in enumerate(zip(result.step_results, result.conversion_rates)):
                print(f"  {index+1}. {step['name']}: {rate:.2%}")
            
            print("\nPontos de drop-off:")
            for drop_off in result.drop_off_points:
                print(f"  {drop_off['step_name']}: {drop_off['drop_off_rate']:.2%}")
        
        # Insights de conversão
        insights = self.funnel_analyzer.get_conversion_insights(funnel_id)
        print(f"\n💡 INSIGHTS: {len(insights.get('recommendations', []))} recomendações")
        
        logger.info("[ANALYTICS_EXAMPLE] Análise de funnels demonstrada")
    
    def demonstrate_cohort_analysis(self):
        """Demonstra a análise de coortes."""
        logger.info("[ANALYTICS_EXAMPLE] Demonstrando análise de coortes...")
        
        # Criar dados de analytics para coortes
        analytics_data = {
            "users": self.simulated_users,
            "events": [event.to_dict() for event in self.simulated_events]
        }
        
        # Reconfigurar o analisador com dados
        self.cohort_analyzer = CohortAnalyzer(analytics_data=analytics_data)
        
        # Criar coortes por data de registro
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        
        cohorts = self.cohort_analyzer.create_cohorts(
            cohort_type=CohortType.SIGNUP_DATE,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"\n👥 COORTES CRIADAS: {len(cohorts)} coortes")
        
        # Analisar retenção de uma coorte
        if cohorts:
            cohort = cohorts[0]
            analysis = self.cohort_analyzer.analyze_cohort_retention(
                cohort.cohort_id,
                periods=[RetentionPeriod.DAY_1, RetentionPeriod.DAY_7, RetentionPeriod.DAY_30]
            )
            
            print(f"\n📊 ANÁLISE DA COORTE: {cohort.cohort_id}")
            print("=" * 50)
            print(f"Total de usuários: {analysis.total_users}")
            print(f"Tendência de engajamento: {analysis.engagement_trend}")
            print(f"Score de risco: {analysis.risk_score:.2f}")
            
            if analysis.churn_prediction:
                print(f"Predição de churn: {analysis.churn_prediction:.2%}")
            
            if analysis.ltv_prediction:
                print(f"Predição de LTV: ${analysis.ltv_prediction:.2f}")
            
            print("\nDados de retenção:")
            for retention in analysis.retention_data:
                print(f"  Dia {retention.period.value}: {retention.retention_rate:.2%} retenção")
            
            print(f"\n💡 RECOMENDAÇÕES: {len(analysis.recommendations)} sugestões")
            for index, rec in enumerate(analysis.recommendations[:3], 1):
                print(f"  {index}. {rec}")
        
        # Gerar relatório completo
        if cohorts:
            report = self.cohort_analyzer.generate_cohort_report(cohorts[0].cohort_id)
            print(f"\n📋 RELATÓRIO GERADO: {len(report)} seções")
        
        logger.info("[ANALYTICS_EXAMPLE] Análise de coortes demonstrada")
    
    def demonstrate_data_export(self):
        """Demonstra a exportação de dados."""
        logger.info("[ANALYTICS_EXAMPLE] Demonstrando exportação de dados...")
        
        # Exportar dados de analytics
        analytics_export = self.analytics.export_data(
            format_type="json",
            filters={"event_type": "keyword_search"}
        )
        
        print(f"\n📤 EXPORTAÇÃO DE DADOS:")
        print("=" * 50)
        print(f"Dados de analytics exportados: {len(analytics_export)} caracteres")
        
        # Exportar dados de funnel
        if hasattr(self.funnel_analyzer, 'funnels') and self.funnel_analyzer.funnels:
            funnel_id = list(self.funnel_analyzer.funnels.keys())[0]
            funnel_export = self.funnel_analyzer.export_funnel_data(funnel_id, "json")
            print(f"Dados de funnel exportados: {len(str(funnel_export))} caracteres")
        
        # Exportar dados de coortes
        if hasattr(self.cohort_analyzer, 'cohort_cache') and self.cohort_analyzer.cohort_cache:
            cohort_ids = list(self.cohort_analyzer.cohort_cache.keys())
            cohort_export = self.cohort_analyzer.export_cohort_data(cohort_ids, "json")
            print(f"Dados de coortes exportados: {len(cohort_export)} caracteres")
        
        logger.info("[ANALYTICS_EXAMPLE] Exportação de dados demonstrada")
    
    def demonstrate_dashboard_integration(self):
        """Demonstra a integração com dashboards."""
        logger.info("[ANALYTICS_EXAMPLE] Demonstrando integração com dashboards...")
        
        # Criar dashboard customizado
        dashboard_config = {
            "name": "Dashboard de Demonstração",
            "description": "Dashboard para demonstração do sistema de analytics",
            "widgets": [
                {
                    "type": "metric",
                    "title": "Usuários Ativos",
                    "metric_name": "active_users",
                    "refresh_interval": 30
                },
                {
                    "type": "chart",
                    "title": "Eventos por Tipo",
                    "chart_type": "bar",
                    "data_source": "events_by_type",
                    "refresh_interval": 60
                },
                {
                    "type": "table",
                    "title": "Top Usuários",
                    "data_source": "top_users",
                    "columns": ["user_id", "events_count", "last_activity"],
                    "refresh_interval": 120
                }
            ]
        }
        
        # Simular criação de dashboard
        print(f"\n📊 DASHBOARD CRIADO:")
        print("=" * 50)
        print(f"Nome: {dashboard_config['name']}")
        print(f"Widgets: {len(dashboard_config['widgets'])}")
        
        for widget in dashboard_config['widgets']:
            print(f"  - {widget['title']} ({widget['type']})")
        
        # Obter dados do dashboard
        dashboard_data = self.analytics.get_dashboard_data()
        print(f"\nDados disponíveis: {len(dashboard_data.get('widgets', []))} widgets")
        
        logger.info("[ANALYTICS_EXAMPLE] Integração com dashboards demonstrada")
    
    def run_complete_demonstration(self):
        """Executa demonstração completa do sistema."""
        logger.info("[ANALYTICS_EXAMPLE] Iniciando demonstração completa...")
        
        print("🚀 DEMONSTRAÇÃO COMPLETA - SISTEMA DE ANALYTICS AVANÇADO")
        print("=" * 80)
        
        try:
            # Setup de dados simulados
            self.setup_simulated_data()
            
            # Demonstrações
            self.demonstrate_real_time_analytics()
            self.demonstrate_funnel_analysis()
            self.demonstrate_cohort_analysis()
            self.demonstrate_data_export()
            self.demonstrate_dashboard_integration()
            
            # Parar o sistema
            self.analytics.stop()
            
            print("\n✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 80)
            print("🎯 Sistema de Analytics Avançado implementado e funcionando")
            print("📊 Analytics em tempo real com métricas avançadas")
            print("🎯 Análise de funnels de conversão")
            print("👥 Análise de coortes com predições ML")
            print("📤 Exportação de dados em múltiplos formatos")
            print("📊 Dashboards interativos")
            print("🔍 Integração completa com observabilidade")
            
        except Exception as e:
            logger.error(f"[ANALYTICS_EXAMPLE] Erro na demonstração: {e}")
            print(f"\n❌ ERRO NA DEMONSTRAÇÃO: {e}")
        
        finally:
            # Cleanup
            if hasattr(self.analytics, 'stop'):
                self.analytics.stop()


def main():
    """Função principal para executar o exemplo."""
    print("🎯 EXEMPLO PRÁTICO - SISTEMA DE ANALYTICS AVANÇADO")
    print("=" * 60)
    
    example = AnalyticsAdvancedExample()
    example.run_complete_demonstration()


if __name__ == "__main__":
    main() 