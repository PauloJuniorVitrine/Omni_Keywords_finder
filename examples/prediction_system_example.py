from typing import Dict, List, Optional, Any
"""
🎯 Exemplo Prático - Sistema de Predição de Tendências
📊 Demonstração completa do uso do sistema de predição
🔄 Versão: 1.0
📅 Data: 2024-12-19
👤 Autor: Paulo Júnior
🔗 Tracing ID: PREDICTION_20241219_005
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import json
from pathlib import Path

# Sistema de predição
from infrastructure.prediction.trend_predictor import TrendPredictor, predict_keyword_trends
from infrastructure.prediction.time_series_analyzer import TimeSeriesAnalyzer, analyze_keyword_timeseries
from infrastructure.prediction.alert_system import AlertSystem, create_alert_system

# Observability
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager


class PredictionSystemExample:
    """
    🎯 Exemplo Completo do Sistema de Predição
    
    Demonstra:
    - Geração de dados sintéticos realistas
    - Análise de séries temporais
    - Predição de tendências
    - Sistema de alertas
    - Integração com observabilidade
    - Relatórios e métricas
    """
    
    def __init__(self):
        """Inicializa o exemplo"""
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
        
        # Componentes do sistema
        self.predictor = TrendPredictor()
        self.analyzer = TimeSeriesAnalyzer()
        self.alert_system = create_alert_system()
        
        # Dados
        self.sample_data = None
        self.predictions = {}
        self.analyses = {}
        self.alerts = []
        
        print("🎯 Sistema de Predição de Tendências - Exemplo Prático")
        print("=" * 60)
    
    def generate_realistic_data(self, keywords: list = None, days: int = 365) -> pd.DataFrame:
        """
        Gera dados sintéticos realistas para demonstração
        
        Args:
            keywords: Lista de keywords
            days: Número de dias de dados
            
        Returns:
            DataFrame com dados sintéticos
        """
        if keywords is None:
            keywords = [
                'python programming',
                'machine learning',
                'data science',
                'web development',
                'artificial intelligence',
                'blockchain',
                'cybersecurity',
                'cloud computing'
            ]
        
        print(f"📊 Gerando dados para {len(keywords)} keywords ({days} dias)...")
        
        dates = pd.date_range(start='2023-01-01', end=f'2023-01-01 + {days} days', freq='D')
        data = []
        
        for keyword in keywords:
            # Parâmetros específicos por keyword
            keyword_params = self._get_keyword_parameters(keyword)
            
            for date in dates:
                # Tendência base
                days_from_start = (date - dates[0]).days
                trend = keyword_params['trend_slope'] * days_from_start
                
                # Sazonalidade
                seasonal = keyword_params['seasonal_amplitude'] * np.sin(
                    2 * np.pi * date.dayofyear / 365
                )
                
                # Sazonalidade semanal
                weekly = keyword_params['weekly_amplitude'] * np.sin(
                    2 * np.pi * date.dayofweek / 7
                )
                
                # Eventos sazonais (ex: Black Friday, Cyber Monday)
                event_boost = self._calculate_event_boost(date, keyword)
                
                # Ruído aleatório
                noise = np.random.normal(0, keyword_params['noise_std'])
                
                # Valor final
                base_value = keyword_params['base_value']
                value = base_value + trend + seasonal + weekly + event_boost + noise
                value = max(0, value)  # Não pode ser negativo
                
                data.append({
                    'date': date,
                    'keyword': keyword,
                    'value': value
                })
        
        df = pd.DataFrame(data)
        self.sample_data = df
        
        print(f"✅ Dados gerados: {len(df)} registros")
        print(f"   Período: {df['date'].min()} a {df['date'].max()}")
        print(f"   Keywords: {df['keyword'].nunique()}")
        print(f"   Valores: {df['value'].min():.1f} - {df['value'].max():.1f}")
        
        return df
    
    def _get_keyword_parameters(self, keyword: str) -> dict:
        """Retorna parâmetros específicos para cada keyword"""
        params = {
            'python programming': {
                'base_value': 1500,
                'trend_slope': 2.5,
                'seasonal_amplitude': 200,
                'weekly_amplitude': 50,
                'noise_std': 100
            },
            'machine learning': {
                'base_value': 2000,
                'trend_slope': 4.0,
                'seasonal_amplitude': 300,
                'weekly_amplitude': 80,
                'noise_std': 150
            },
            'data science': {
                'base_value': 1800,
                'trend_slope': 3.2,
                'seasonal_amplitude': 250,
                'weekly_amplitude': 60,
                'noise_std': 120
            },
            'web development': {
                'base_value': 1200,
                'trend_slope': 1.8,
                'seasonal_amplitude': 150,
                'weekly_amplitude': 40,
                'noise_std': 80
            },
            'artificial intelligence': {
                'base_value': 2500,
                'trend_slope': 5.0,
                'seasonal_amplitude': 400,
                'weekly_amplitude': 100,
                'noise_std': 200
            },
            'blockchain': {
                'base_value': 800,
                'trend_slope': 1.2,
                'seasonal_amplitude': 100,
                'weekly_amplitude': 30,
                'noise_std': 60
            },
            'cybersecurity': {
                'base_value': 1600,
                'trend_slope': 2.8,
                'seasonal_amplitude': 220,
                'weekly_amplitude': 55,
                'noise_std': 110
            },
            'cloud computing': {
                'base_value': 1400,
                'trend_slope': 2.2,
                'seasonal_amplitude': 180,
                'weekly_amplitude': 45,
                'noise_std': 90
            }
        }
        
        return params.get(keyword, {
            'base_value': 1000,
            'trend_slope': 2.0,
            'seasonal_amplitude': 150,
            'weekly_amplitude': 40,
            'noise_std': 80
        })
    
    def _calculate_event_boost(self, date: datetime, keyword: str) -> float:
        """Calcula boost de eventos sazonais"""
        boost = 0
        
        # Black Friday (última sexta de novembro)
        if date.month == 11 and date.day >= 20:
            if keyword in ['web development', 'cybersecurity']:
                boost += 300
        
        # Cyber Monday (primeira segunda de dezembro)
        if date.month == 12 and date.day <= 7:
            if keyword in ['artificial intelligence', 'machine learning']:
                boost += 400
        
        # Ano novo (dezembro/janeiro)
        if (date.month == 12 and date.day >= 25) or (date.month == 1 and date.day <= 10):
            if keyword in ['python programming', 'data science']:
                boost += 200
        
        # Verão (julho/agosto) - menos atividade
        if date.month in [7, 8]:
            boost -= 150
        
        return boost
    
    def analyze_time_series(self, keywords: list = None):
        """
        Analisa séries temporais das keywords
        
        Args:
            keywords: Lista de keywords para análise
        """
        if self.sample_data is None:
            print("❌ Gere dados primeiro usando generate_realistic_data()")
            return
        
        if keywords is None:
            keywords = self.sample_data['keyword'].unique()[:4]  # Primeiras 4 keywords
        
        print(f"\n📈 Analisando séries temporais para {len(keywords)} keywords...")
        
        for keyword in keywords:
            print(f"\n🔍 Analisando: {keyword}")
            
            # Filtra dados da keyword
            keyword_data = self.sample_data[self.sample_data['keyword'] == keyword]
            series = keyword_data.set_index('date')['value']
            
            # Análise completa
            analysis = self.analyzer.analyze_series(series, keyword)
            self.analyses[keyword] = analysis
            
            # Exibe resultados principais
            if analysis:
                stats = analysis.get('basic_stats', {})
                trend = analysis.get('trend', {})
                seasonality = analysis.get('seasonality', [])
                
                print(f"   📊 Estatísticas:")
                print(f"      Média: {stats.get('mean', 0):.1f}")
                print(f"      Desvio: {stats.get('std', 0):.1f}")
                print(f"      CV: {stats.get('cv', 0):.2f}")
                
                print(f"   📈 Tendência:")
                print(f"      Tipo: {trend.get('type', 'unknown')}")
                print(f"      Inclinação: {trend.get('slope', 0):.4f}")
                print(f"      Força: {trend.get('strength', 0):.2f}")
                
                print(f"   🌊 Sazonalidade:")
                if seasonality:
                    for pattern in seasonality[:2]:  # Top 2
                        print(f"      {pattern.type.value}: força={pattern.strength:.2f}, período={pattern.period}")
                else:
                    print("      Nenhuma sazonalidade significativa detectada")
        
        print(f"\n✅ Análise concluída para {len(keywords)} keywords")
    
    def predict_trends(self, keywords: list = None, timeframes: list = None):
        """
        Prediz tendências para as keywords
        
        Args:
            keywords: Lista de keywords
            timeframes: Lista de timeframes para predição
        """
        if self.sample_data is None:
            print("❌ Gere dados primeiro usando generate_realistic_data()")
            return
        
        if keywords is None:
            keywords = self.sample_data['keyword'].unique()[:4]
        
        if timeframes is None:
            timeframes = ['7d', '30d', '90d']
        
        print(f"\n🔮 Predizendo tendências para {len(keywords)} keywords...")
        
        for keyword in keywords:
            print(f"\n🎯 Predições para: {keyword}")
            
            keyword_predictions = {}
            
            for timeframe in timeframes:
                # Filtra dados da keyword
                keyword_data = self.sample_data[self.sample_data['keyword'] == keyword]
                
                # Predição
                prediction = self.predictor.predict_trend(keyword_data, keyword, timeframe)
                
                if prediction:
                    keyword_predictions[timeframe] = prediction
                    
                    print(f"   📅 {timeframe}:")
                    print(f"      Atual: {prediction.current_value:.1f}")
                    print(f"      Predito: {prediction.predicted_value:.1f}")
                    print(f"      Mudança: {((prediction.predicted_value - prediction.current_value) / prediction.current_value * 100):.1f}%")
                    print(f"      Direção: {prediction.direction.value}")
                    print(f"      Confiança: {prediction.confidence:.2f} ({prediction.confidence_level.value})")
                else:
                    print(f"   📅 {timeframe}: Sem predição disponível")
            
            self.predictions[keyword] = keyword_predictions
        
        print(f"\n✅ Predições concluídas para {len(keywords)} keywords")
    
    async def setup_alert_system(self):
        """Configura sistema de alertas"""
        print(f"\n🚨 Configurando sistema de alertas...")
        
        # Adiciona regras customizadas
        custom_rules = [
            {
                'name': 'High Growth Alert',
                'alert_type': 'trend_change',
                'severity': 'high',
                'conditions': {'change_percentage': 0.25, 'confidence_min': 0.7},
                'actions': ['email', 'slack']
            },
            {
                'name': 'Volatility Spike Alert',
                'alert_type': 'volatility_spike',
                'severity': 'medium',
                'conditions': {'volatility_threshold': 1.8},
                'actions': ['slack']
            }
        ]
        
        for rule_config in custom_rules:
            from infrastructure.prediction.alert_system import AlertRule, AlertType, AlertSeverity
            
            rule = AlertRule(
                name=rule_config['name'],
                alert_type=AlertType(rule_config['alert_type']),
                severity=AlertSeverity(rule_config['severity']),
                conditions=rule_config['conditions'],
                actions=rule_config['actions']
            )
            
            self.alert_system.add_alert_rule(rule)
        
        print(f"✅ {len(custom_rules)} regras customizadas adicionadas")
    
    async def generate_alerts(self):
        """Gera alertas baseados nas predições"""
        if not self.predictions:
            print("❌ Execute predições primeiro usando predict_trends()")
            return
        
        print(f"\n🚨 Gerando alertas...")
        
        # Converte predições para formato esperado pelo sistema de alertas
        alert_predictions = []
        
        for keyword, timeframes in self.predictions.items():
            for timeframe, prediction in timeframes.items():
                alert_predictions.append({
                    'keyword': keyword,
                    'current_value': prediction.current_value,
                    'predicted_value': prediction.predicted_value,
                    'confidence': prediction.confidence,
                    'timeframe': timeframe,
                    'metadata': {
                        'direction': prediction.direction.value,
                        'confidence_level': prediction.confidence_level.value,
                        'factors': prediction.factors
                    }
                })
        
        # Gera alertas
        alerts = await self.alert_system.evaluate_predictions(alert_predictions)
        self.alerts = alerts
        
        print(f"✅ {len(alerts)} alertas gerados")
        
        # Exibe alertas críticos
        critical_alerts = [a for a in alerts if a.severity.value in ['critical', 'high']]
        if critical_alerts:
            print(f"\n🚨 Alertas Críticos ({len(critical_alerts)}):")
            for alert in critical_alerts[:3]:  # Top 3
                print(f"   {alert.severity.value.upper()}: {alert.keyword} - {alert.message}")
    
    def generate_reports(self, output_dir: str = "reports"):
        """
        Gera relatórios completos
        
        Args:
            output_dir: Diretório para salvar relatórios
        """
        print(f"\n📊 Gerando relatórios em {output_dir}...")
        
        # Cria diretório
        Path(output_dir).mkdir(exist_ok=True)
        
        # Relatório de predições
        predictions_report = {
            'timestamp': datetime.now().isoformat(),
            'total_keywords': len(self.predictions),
            'predictions': {}
        }
        
        for keyword, timeframes in self.predictions.items():
            predictions_report['predictions'][keyword] = {}
            for timeframe, prediction in timeframes.items():
                predictions_report['predictions'][keyword][timeframe] = {
                    'current_value': prediction.current_value,
                    'predicted_value': prediction.predicted_value,
                    'change_percentage': ((prediction.predicted_value - prediction.current_value) / prediction.current_value * 100),
                    'direction': prediction.direction.value,
                    'confidence': prediction.confidence,
                    'confidence_level': prediction.confidence_level.value,
                    'timeframe': prediction.timeframe
                }
        
        # Salva relatório de predições
        with open(f"{output_dir}/predictions_report.json", 'w') as f:
            json.dump(predictions_report, f, indent=2)
        
        # Relatório de análises
        analyses_report = {
            'timestamp': datetime.now().isoformat(),
            'total_keywords': len(self.analyses),
            'analyses': {}
        }
        
        for keyword, analysis in self.analyses.items():
            if analysis:
                analyses_report['analyses'][keyword] = {
                    'basic_stats': analysis.get('basic_stats', {}),
                    'trend': {
                        'type': analysis.get('trend', {}).get('type', 'unknown'),
                        'slope': analysis.get('trend', {}).get('slope', 0),
                        'strength': analysis.get('trend', {}).get('strength', 0)
                    },
                    'seasonality_count': len(analysis.get('seasonality', [])),
                    'anomalies_count': len(analysis.get('anomalies', {}).get('anomalies', []))
                }
        
        # Salva relatório de análises
        with open(f"{output_dir}/analyses_report.json", 'w') as f:
            json.dump(analyses_report, f, indent=2)
        
        # Relatório de alertas
        alerts_report = {
            'timestamp': datetime.now().isoformat(),
            'total_alerts': len(self.alerts),
            'alerts': []
        }
        
        for alert in self.alerts:
            alerts_report['alerts'].append({
                'id': alert.id,
                'keyword': alert.keyword,
                'severity': alert.severity.value,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'status': alert.status.value
            })
        
        # Salva relatório de alertas
        with open(f"{output_dir}/alerts_report.json", 'w') as f:
            json.dump(alerts_report, f, indent=2)
        
        # Estatísticas do sistema de alertas
        alert_stats = self.alert_system.get_alert_statistics()
        with open(f"{output_dir}/alert_statistics.json", 'w') as f:
            json.dump(alert_stats, f, indent=2)
        
        # Relatório executivo
        executive_summary = self._generate_executive_summary()
        with open(f"{output_dir}/executive_summary.txt", 'w') as f:
            f.write(executive_summary)
        
        print(f"✅ Relatórios gerados:")
        print(f"   📄 predictions_report.json")
        print(f"   📄 analyses_report.json")
        print(f"   📄 alerts_report.json")
        print(f"   📄 alert_statistics.json")
        print(f"   📄 executive_summary.txt")
    
    def _generate_executive_summary(self) -> str:
        """Gera resumo executivo"""
        summary = []
        summary.append("🎯 RESUMO EXECUTIVO - SISTEMA DE PREDIÇÃO DE TENDÊNCIAS")
        summary.append("=" * 60)
        summary.append(f"📅 Data: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}")
        summary.append("")
        
        # Estatísticas gerais
        summary.append("📊 ESTATÍSTICAS GERAIS:")
        summary.append(f"   Keywords analisadas: {len(self.predictions)}")
        summary.append(f"   Predições realizadas: {sum(len(t) for t in self.predictions.values())}")
        summary.append(f"   Alertas gerados: {len(self.alerts)}")
        summary.append("")
        
        # Top keywords por crescimento
        if self.predictions:
            growth_data = []
            for keyword, timeframes in self.predictions.items():
                for timeframe, prediction in timeframes.items():
                    growth_pct = ((prediction.predicted_value - prediction.current_value) / prediction.current_value * 100)
                    growth_data.append({
                        'keyword': keyword,
                        'timeframe': timeframe,
                        'growth': growth_pct,
                        'confidence': prediction.confidence
                    })
            
            # Ordena por crescimento
            growth_data.sort(key=lambda value: value['growth'], reverse=True)
            
            summary.append("🚀 TOP 5 KEYWORDS POR CRESCIMENTO:")
            for index, item in enumerate(growth_data[:5], 1):
                summary.append(f"   {index}. {item['keyword']} ({item['timeframe']}): {item['growth']:+.1f}% (conf: {item['confidence']:.2f})")
            summary.append("")
        
        # Alertas críticos
        critical_alerts = [a for a in self.alerts if a.severity.value in ['critical', 'high']]
        if critical_alerts:
            summary.append("🚨 ALERTAS CRÍTICOS:")
            for alert in critical_alerts[:5]:
                summary.append(f"   • {alert.keyword}: {alert.message}")
            summary.append("")
        
        # Recomendações
        summary.append("💡 RECOMENDAÇÕES:")
        if growth_data:
            top_growth = growth_data[0]
            summary.append(f"   • Focar em '{top_growth['keyword']}' - maior potencial de crescimento")
        
        if critical_alerts:
            summary.append(f"   • Monitorar {len(critical_alerts)} alertas críticos")
        
        summary.append("   • Revisar predições semanalmente")
        summary.append("   • Ajustar thresholds de alerta conforme necessário")
        summary.append("")
        
        summary.append("📈 PRÓXIMOS PASSOS:")
        summary.append("   1. Implementar ações baseadas nos alertas")
        summary.append("   2. Acompanhar acurácia das predições")
        summary.append("   3. Refinar modelos com novos dados")
        summary.append("   4. Expandir para mais keywords")
        
        return "\n".join(summary)
    
    def display_metrics(self):
        """Exibe métricas do sistema"""
        print(f"\n📈 MÉTRICAS DO SISTEMA:")
        print("=" * 40)
        
        # Métricas de predição
        if self.predictions:
            total_predictions = sum(len(t) for t in self.predictions.values())
            avg_confidence = np.mean([
                pred.confidence 
                for timeframes in self.predictions.values() 
                for pred in timeframes.values()
            ])
            
            print(f"🎯 Predições:")
            print(f"   Total: {total_predictions}")
            print(f"   Keywords: {len(self.predictions)}")
            print(f"   Confiança média: {avg_confidence:.2f}")
        
        # Métricas de alertas
        if self.alerts:
            severity_counts = {}
            for alert in self.alerts:
                severity = alert.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            print(f"\n🚨 Alertas:")
            print(f"   Total: {len(self.alerts)}")
            for severity, count in severity_counts.items():
                print(f"   {severity}: {count}")
        
        # Métricas do sistema de alertas
        alert_stats = self.alert_system.get_alert_statistics()
        print(f"\n⚙️ Sistema de Alertas:")
        print(f"   Regras ativas: {alert_stats.get('enabled_rules_count', 0)}")
        print(f"   Alertas ativos: {alert_stats.get('active_alerts', 0)}")
        print(f"   Alertas resolvidos: {alert_stats.get('resolved_alerts', 0)}")


async def main():
    """Função principal do exemplo"""
    print("🎯 EXEMPLO PRÁTICO - SISTEMA DE PREDIÇÃO DE TENDÊNCIAS")
    print("=" * 60)
    
    # Inicializa exemplo
    example = PredictionSystemExample()
    
    try:
        # 1. Gera dados realistas
        example.generate_realistic_data(days=365)
        
        # 2. Analisa séries temporais
        example.analyze_time_series()
        
        # 3. Prediz tendências
        example.predict_trends()
        
        # 4. Configura sistema de alertas
        await example.setup_alert_system()
        
        # 5. Gera alertas
        await example.generate_alerts()
        
        # 6. Gera relatórios
        example.generate_reports()
        
        # 7. Exibe métricas
        example.display_metrics()
        
        print(f"\n✅ Exemplo concluído com sucesso!")
        print(f"📁 Relatórios salvos em: reports/")
        
    except Exception as e:
        print(f"❌ Erro no exemplo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Executa exemplo
    asyncio.run(main()) 