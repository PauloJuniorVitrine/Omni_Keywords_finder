"""
Exemplo Prático de A/B Testing
==============================

Este exemplo demonstra como usar o sistema completo de A/B Testing:
- Criação de experimentos
- Atribuição de usuários
- Tracking de conversões
- Análise estatística
- Geração de relatórios

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: AB_TESTING_EXAMPLE_001
"""

import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

from infrastructure.ab_testing.framework import ABTestingFramework
from infrastructure.ab_testing.experiment_manager import ExperimentManager
from infrastructure.ab_testing.analytics import ABTestingAnalytics


class ABTestingExample:
    """
    Exemplo completo de uso do sistema de A/B Testing
    
    Demonstra:
    - Criação e configuração de experimentos
    - Simulação de tráfego de usuários
    - Tracking de conversões
    - Análise estatística em tempo real
    - Geração de relatórios
    """
    
    def __init__(self):
        """Inicializa o exemplo"""
        # Framework principal
        self.framework = ABTestingFramework(
            redis_config=None,  # Sem Redis para simplicidade
            enable_observability=False
        )
        
        # Gerenciador de experimentos
        self.manager = ExperimentManager(
            framework=self.framework,
            enable_monitoring=True,
            enable_alerts=True
        )
        
        # Analytics
        self.analytics = ABTestingAnalytics(
            framework=self.framework,
            enable_visualization=False,
            enable_observability=False
        )
        
        # Dados simulados
        self.simulated_users = []
        self.conversion_events = []
        
        print("🚀 Sistema de A/B Testing inicializado")
    
    def create_button_color_experiment(self) -> str:
        """Cria experimento de teste de cor de botão"""
        print("\n📊 Criando experimento: Teste de Cor de Botão")
        
        experiment_id = self.manager.create_experiment_with_template(
            template_name="button_color",
            name="Teste de Cor de Botão - Landing Page",
            description="Testa diferentes cores de botão CTA para maximizar conversões",
            custom_config={
                "traffic_allocation": 0.15,  # 15% do tráfego
                "min_sample_size": 200,
                "tags": ["landing_page", "conversion", "ui"]
            }
        )
        
        print(f"✅ Experimento criado: {experiment_id}")
        return experiment_id
    
    def create_headline_experiment(self) -> str:
        """Cria experimento de teste de headline"""
        print("\n📊 Criando experimento: Teste de Headline")
        
        experiment_id = self.manager.create_experiment_with_template(
            template_name="headline_test",
            name="Teste de Headline - Página Principal",
            description="Testa diferentes headlines para aumentar engajamento",
            custom_config={
                "traffic_allocation": 0.10,  # 10% do tráfego
                "min_sample_size": 300,
                "tags": ["content", "engagement", "seo"]
            }
        )
        
        print(f"✅ Experimento criado: {experiment_id}")
        return experiment_id
    
    def create_pricing_experiment(self) -> str:
        """Cria experimento de teste de preços"""
        print("\n📊 Criando experimento: Teste de Preços")
        
        experiment_id = self.manager.create_experiment_with_template(
            template_name="pricing_test",
            name="Teste de Estratégia de Preços",
            description="Testa diferentes estratégias de preços para maximizar receita",
            custom_config={
                "traffic_allocation": 0.05,  # 5% do tráfego (preços são sensíveis)
                "min_sample_size": 500,
                "tags": ["pricing", "revenue", "business"]
            }
        )
        
        print(f"✅ Experimento criado: {experiment_id}")
        return experiment_id
    
    def activate_experiments(self, experiment_ids: List[str]):
        """Ativa todos os experimentos"""
        print("\n🎯 Ativando experimentos...")
        
        for experiment_id in experiment_ids:
            try:
                self.framework.activate_experiment(experiment_id)
                print(f"✅ Experimento {experiment_id} ativado")
            except Exception as e:
                print(f"❌ Erro ao ativar {experiment_id}: {e}")
    
    def simulate_user_traffic(self, 
                            experiment_ids: List[str], 
                            num_users: int = 1000,
                            duration_minutes: int = 30):
        """Simula tráfego de usuários"""
        print(f"\n👥 Simulando {num_users} usuários por {duration_minutes} minutos...")
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        user_count = 0
        conversion_count = 0
        
        while datetime.utcnow() < end_time and user_count < num_users:
            # Simular chegada de usuário
            user_id = f"user_{user_count:06d}"
            session_id = f"session_{user_count:06d}"
            
            # Atribuir usuário a experimentos
            for experiment_id in experiment_ids:
                variant = self.framework.assign_user_to_variant(
                    user_id=user_id,
                    experiment_id=experiment_id,
                    session_id=session_id,
                    user_attributes={
                        "country": random.choice(["BR", "US", "CA", "UK"]),
                        "device": random.choice(["desktop", "mobile", "tablet"]),
                        "user_type": random.choice(["new", "returning"])
                    }
                )
                
                if variant:
                    # Simular conversão baseada na variante
                    conversion_probability = self._get_conversion_probability(variant, experiment_id)
                    
                    if random.random() < conversion_probability:
                        # Registrar conversão
                        self.framework.track_conversion(
                            user_id=user_id,
                            experiment_id=experiment_id,
                            metric_name="conversion_rate",
                            value=1.0,
                            metadata={
                                "session_id": session_id,
                                "timestamp": datetime.utcnow().isoformat(),
                                "user_attributes": {
                                    "country": random.choice(["BR", "US", "CA", "UK"]),
                                    "device": random.choice(["desktop", "mobile", "tablet"])
                                }
                            }
                        )
                        conversion_count += 1
                        
                        # Simular métricas adicionais
                        self._simulate_additional_metrics(user_id, experiment_id, variant)
            
            user_count += 1
            
            # Pausa para simular tempo real
            time.sleep(0.1)
            
            # Progresso a cada 100 usuários
            if user_count % 100 == 0:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                rate = user_count / elapsed if elapsed > 0 else 0
                print(f"📈 Progresso: {user_count}/{num_users} usuários ({rate:.1f} usuários/seg)")
        
        print(f"✅ Simulação concluída: {user_count} usuários, {conversion_count} conversões")
        return user_count, conversion_count
    
    def _get_conversion_probability(self, variant: str, experiment_id: str) -> float:
        """Retorna probabilidade de conversão baseada na variante"""
        experiment = self.framework.experiments[experiment_id]
        
        # Probabilidades baseadas no tipo de experimento
        if "button_color" in experiment.tags:
            if variant == "control":
                return 0.05  # 5% baseline
            elif variant == "green":
                return 0.06  # 6% - 20% melhor
            elif variant == "red":
                return 0.04  # 4% - 20% pior
        
        elif "headline_test" in experiment.tags:
            if variant == "control":
                return 0.08  # 8% baseline
            elif variant == "benefit":
                return 0.10  # 10% - 25% melhor
            elif variant == "urgency":
                return 0.09  # 9% - 12.5% melhor
        
        elif "pricing_test" in experiment.tags:
            if variant == "control":
                return 0.03  # 3% baseline
            elif variant == "higher":
                return 0.02  # 2% - 33% pior
            elif variant == "lower":
                return 0.04  # 4% - 33% melhor
        
        return 0.05  # Probabilidade padrão
    
    def _simulate_additional_metrics(self, user_id: str, experiment_id: str, variant: str):
        """Simula métricas adicionais"""
        # Simular tempo na página
        time_on_page = random.uniform(30, 300)  # 30s a 5min
        self.framework.track_conversion(
            user_id=user_id,
            experiment_id=experiment_id,
            metric_name="time_on_page",
            value=time_on_page
        )
        
        # Simular receita (apenas para alguns usuários)
        if random.random() < 0.1:  # 10% dos usuários geram receita
            revenue = random.uniform(10, 100)
            self.framework.track_conversion(
                user_id=user_id,
                experiment_id=experiment_id,
                metric_name="revenue",
                value=revenue
            )
        
        # Simular taxa de rejeição
        if random.random() < 0.3:  # 30% dos usuários rejeitam
            self.framework.track_conversion(
                user_id=user_id,
                experiment_id=experiment_id,
                metric_name="bounce_rate",
                value=1.0
            )
    
    def analyze_experiments(self, experiment_ids: List[str]):
        """Analisa todos os experimentos"""
        print("\n📊 Analisando experimentos...")
        
        for experiment_id in experiment_ids:
            try:
                print(f"\n🔍 Analisando experimento: {experiment_id}")
                
                # Obter resumo do experimento
                summary = self.framework.get_experiment_summary(experiment_id)
                print(f"   Nome: {summary['name']}")
                print(f"   Status: {summary['status']}")
                print(f"   Usuários: {summary['variant_counts']}")
                
                # Análise estatística
                analysis = self.analytics.analyze_experiment_statistical(experiment_id)
                
                if "error" in analysis:
                    print(f"   ❌ Erro na análise: {analysis['error']}")
                    continue
                
                # Mostrar resultados por variante
                print("   📈 Resultados por variante:")
                for variant, data in analysis["variant_analyses"].items():
                    print(f"     {variant}:")
                    print(f"       Amostra: {data['sample_size']} usuários")
                    print(f"       Taxa de conversão: {data['conversion_rate']:.3f}")
                    print(f"       Média: {data['mean_value']:.3f}")
                    print(f"       Intervalo de confiança: [{data['confidence_interval'][0]:.3f}, {data['confidence_interval'][1]:.3f}]")
                
                # Mostrar resultados estatísticos
                print("   🧮 Análise estatística:")
                for variant, stats in analysis["statistical_results"].items():
                    print(f"     {variant} vs control:")
                    print(f"       P-value: {stats['p_value']:.4f}")
                    print(f"       Significativo: {'✅' if stats['is_significant'] else '❌'}")
                    print(f"       Lift: {stats['lift']:.1f}%")
                    print(f"       Poder estatístico: {stats['power']:.2f}")
                
                # Análise geral
                overall = analysis["overall_analysis"]
                print(f"   📊 Análise geral:")
                print(f"     Total de usuários: {overall['total_users']}")
                print(f"     Melhor variante: {overall['best_variant']}")
                print(f"     Melhor lift: {overall['best_lift']:.1f}%")
                print(f"     Variantes significativas: {overall['significant_variants']}")
                print(f"     Recomendação: {overall['recommendation']}")
                
            except Exception as e:
                print(f"   ❌ Erro ao analisar {experiment_id}: {e}")
    
    def generate_reports(self, experiment_ids: List[str]):
        """Gera relatórios completos"""
        print("\n📋 Gerando relatórios...")
        
        for experiment_id in experiment_ids:
            try:
                print(f"\n📄 Gerando relatório para: {experiment_id}")
                
                # Relatório do gerenciador
                manager_report = self.manager.generate_experiment_report(experiment_id)
                
                # Relatório do analytics
                analytics_report = self.analytics.generate_report(experiment_id)
                
                # Salvar relatórios
                self._save_report(experiment_id, manager_report, "manager")
                self._save_report(experiment_id, analytics_report, "analytics")
                
                print(f"   ✅ Relatórios salvos para {experiment_id}")
                
            except Exception as e:
                print(f"   ❌ Erro ao gerar relatório para {experiment_id}: {e}")
    
    def _save_report(self, experiment_id: str, report: Dict[str, Any], report_type: str):
        """Salva relatório em arquivo"""
        filename = f"reports/{experiment_id}_{report_type}_report.json"
        
        # Criar diretório se não existir
        import os
        os.makedirs("reports", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    def show_experiment_health(self, experiment_ids: List[str]):
        """Mostra saúde dos experimentos"""
        print("\n🏥 Verificando saúde dos experimentos...")
        
        for experiment_id in experiment_ids:
            try:
                health = self.manager.get_experiment_health(experiment_id)
                
                print(f"\n🔍 Saúde do experimento: {experiment_id}")
                print(f"   Score: {health['health_score']}/100")
                print(f"   Status: {health['status']}")
                print(f"   Usuários: {health['total_users']}/{health['min_sample_size']}")
                print(f"   Distribuição: {health['variant_distribution']}")
                
                if health['recommendations']:
                    print("   💡 Recomendações:")
                    for rec in health['recommendations']:
                        print(f"     - {rec}")
                
            except Exception as e:
                print(f"   ❌ Erro ao verificar saúde de {experiment_id}: {e}")
    
    def run_complete_example(self):
        """Executa exemplo completo"""
        print("🎯 EXEMPLO COMPLETO DE A/B TESTING")
        print("=" * 50)
        
        # 1. Criar experimentos
        experiment_ids = []
        experiment_ids.append(self.create_button_color_experiment())
        experiment_ids.append(self.create_headline_experiment())
        experiment_ids.append(self.create_pricing_experiment())
        
        # 2. Ativar experimentos
        self.activate_experiments(experiment_ids)
        
        # 3. Simular tráfego
        print("\n" + "=" * 50)
        print("🚦 SIMULAÇÃO DE TRÁFEGO")
        print("=" * 50)
        
        users, conversions = self.simulate_user_traffic(
            experiment_ids=experiment_ids,
            num_users=500,  # 500 usuários
            duration_minutes=5  # 5 minutos
        )
        
        # 4. Verificar saúde
        print("\n" + "=" * 50)
        print("🏥 VERIFICAÇÃO DE SAÚDE")
        print("=" * 50)
        
        self.show_experiment_health(experiment_ids)
        
        # 5. Analisar experimentos
        print("\n" + "=" * 50)
        print("📊 ANÁLISE ESTATÍSTICA")
        print("=" * 50)
        
        self.analyze_experiments(experiment_ids)
        
        # 6. Gerar relatórios
        print("\n" + "=" * 50)
        print("📋 GERAÇÃO DE RELATÓRIOS")
        print("=" * 50)
        
        self.generate_reports(experiment_ids)
        
        # 7. Resumo final
        print("\n" + "=" * 50)
        print("🎉 RESUMO FINAL")
        print("=" * 50)
        
        print(f"✅ Experimentos criados: {len(experiment_ids)}")
        print(f"👥 Usuários simulados: {users}")
        print(f"💰 Conversões registradas: {conversions}")
        print(f"📈 Taxa de conversão geral: {conversions/users*100:.2f}%")
        
        print("\n📁 Relatórios salvos em: reports/")
        print("🔍 Verifique os arquivos JSON para análise detalhada")
        
        return {
            "experiments": experiment_ids,
            "users": users,
            "conversions": conversions,
            "conversion_rate": conversions/users if users > 0 else 0
        }


def main():
    """Função principal"""
    print("🚀 Iniciando exemplo de A/B Testing...")
    
    # Criar e executar exemplo
    example = ABTestingExample()
    results = example.run_complete_example()
    
    print(f"\n🎯 Exemplo concluído com sucesso!")
    print(f"📊 Resultados: {results}")


if __name__ == "__main__":
    main() 