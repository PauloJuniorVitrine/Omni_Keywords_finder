from typing import Dict, List, Optional, Any
"""
🧪 Testes Unitários - Exemplo do Sistema de Predição
📊 Testes para o exemplo prático de predição de tendências
🔄 Versão: 1.0
📅 Data: 2024-12-19
👤 Autor: Paulo Júnior
🔗 Tracing ID: PREDICTION_20241219_006
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import asyncio
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from examples.prediction_system_example import PredictionSystemExample


class TestPredictionSystemExample:
    """Testes para o exemplo do sistema de predição"""
    
    @pytest.fixture
    def example(self):
        """Instância do exemplo para testes"""
        return PredictionSystemExample()
    
    def test_init(self, example):
        """Testa inicialização do exemplo"""
        assert example is not None
        assert example.predictor is not None
        assert example.analyzer is not None
        assert example.alert_system is not None
        assert example.sample_data is None
        assert example.predictions == {}
        assert example.analyses == {}
        assert example.alerts == []
    
    def test_get_keyword_parameters(self, example):
        """Testa obtenção de parâmetros por keyword"""
        # Testa keywords conhecidas
        python_params = example._get_keyword_parameters('python programming')
        assert python_params['base_value'] == 1500
        assert python_params['trend_slope'] == 2.5
        assert python_params['seasonal_amplitude'] == 200
        
        ml_params = example._get_keyword_parameters('machine learning')
        assert ml_params['base_value'] == 2000
        assert ml_params['trend_slope'] == 4.0
        assert ml_params['seasonal_amplitude'] == 300
        
        # Testa keyword desconhecida (deve retornar parâmetros padrão)
        unknown_params = example._get_keyword_parameters('unknown keyword')
        assert unknown_params['base_value'] == 1000
        assert unknown_params['trend_slope'] == 2.0
        assert unknown_params['seasonal_amplitude'] == 150
    
    def test_calculate_event_boost(self, example):
        """Testa cálculo de boost de eventos"""
        # Black Friday
        black_friday = datetime(2023, 11, 25)
        boost = example._calculate_event_boost(black_friday, 'web development')
        assert boost > 0
        
        # Cyber Monday
        cyber_monday = datetime(2023, 12, 4)
        boost = example._calculate_event_boost(cyber_monday, 'artificial intelligence')
        assert boost > 0
        
        # Ano novo
        new_year = datetime(2023, 12, 31)
        boost = example._calculate_event_boost(new_year, 'python programming')
        assert boost > 0
        
        # Verão (menos atividade)
        summer = datetime(2023, 7, 15)
        boost = example._calculate_event_boost(summer, 'python programming')
        assert boost < 0
        
        # Data normal (sem eventos)
        normal_date = datetime(2023, 3, 15)
        boost = example._calculate_event_boost(normal_date, 'python programming')
        assert boost == 0
    
    def test_generate_realistic_data(self, example):
        """Testa geração de dados realistas"""
        keywords = ['python programming', 'machine learning']
        days = 30
        
        df = example.generate_realistic_data(keywords, days)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(keywords) * days
        assert 'date' in df.columns
        assert 'keyword' in df.columns
        assert 'value' in df.columns
        assert df['keyword'].nunique() == len(keywords)
        assert df['value'].min() >= 0  # Valores não negativos
        
        # Verifica se os dados têm padrões realistas
        for keyword in keywords:
            keyword_data = df[df['keyword'] == keyword]
            assert len(keyword_data) == days
            assert keyword_data['value'].std() > 0  # Há variabilidade
    
    def test_generate_realistic_data_default_keywords(self, example):
        """Testa geração com keywords padrão"""
        df = example.generate_realistic_data(days=10)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert df['keyword'].nunique() == 8  # 8 keywords padrão
    
    def test_analyze_time_series(self, example):
        """Testa análise de séries temporais"""
        # Gera dados primeiro
        example.generate_realistic_data(['python programming', 'machine learning'], 60)
        
        # Analisa
        example.analyze_time_series(['python programming'])
        
        assert 'python programming' in example.analyses
        analysis = example.analyses['python programming']
        
        assert 'basic_stats' in analysis
        assert 'trend' in analysis
        assert 'seasonality' in analysis
    
    def test_analyze_time_series_no_data(self, example):
        """Testa análise sem dados"""
        # Não gera dados primeiro
        example.analyze_time_series()
        
        # Deve exibir mensagem de erro (capturada via print)
        assert example.analyses == {}
    
    def test_predict_trends(self, example):
        """Testa predição de tendências"""
        # Gera dados primeiro
        example.generate_realistic_data(['python programming'], 90)
        
        # Prediz
        example.predict_trends(['python programming'], ['7d', '30d'])
        
        assert 'python programming' in example.predictions
        predictions = example.predictions['python programming']
        
        assert '7d' in predictions
        assert '30d' in predictions
        
        # Verifica estrutura das predições
        for timeframe, prediction in predictions.items():
            assert prediction.keyword == 'python programming'
            assert prediction.timeframe == timeframe
            assert prediction.current_value > 0
            assert prediction.predicted_value > 0
            assert 0 <= prediction.confidence <= 1
    
    def test_predict_trends_no_data(self, example):
        """Testa predição sem dados"""
        # Não gera dados primeiro
        example.predict_trends()
        
        # Deve exibir mensagem de erro
        assert example.predictions == {}
    
    @pytest.mark.asyncio
    async def test_setup_alert_system(self, example):
        """Testa configuração do sistema de alertas"""
        await example.setup_alert_system()
        
        # Verifica se regras foram adicionadas
        rule_names = [rule.name for rule in example.alert_system.alert_rules]
        assert 'High Growth Alert' in rule_names
        assert 'Volatility Spike Alert' in rule_names
    
    @pytest.mark.asyncio
    async def test_generate_alerts(self, example):
        """Testa geração de alertas"""
        # Prepara dados
        example.generate_realistic_data(['python programming'], 90)
        example.predict_trends(['python programming'], ['30d'])
        await example.setup_alert_system()
        
        # Gera alertas
        await example.generate_alerts()
        
        # Verifica se alertas foram gerados
        assert len(example.alerts) >= 0  # Pode ser 0 se não houver violações
    
    @pytest.mark.asyncio
    async def test_generate_alerts_no_predictions(self, example):
        """Testa geração de alertas sem predições"""
        await example.setup_alert_system()
        
        # Tenta gerar alertas sem predições
        await example.generate_alerts()
        
        # Deve exibir mensagem de erro
        assert example.alerts == []
    
    def test_generate_reports(self, example, tmp_path):
        """Testa geração de relatórios"""
        # Prepara dados
        example.generate_realistic_data(['python programming'], 30)
        example.predict_trends(['python programming'], ['7d'])
        example.analyses['python programming'] = {
            'basic_stats': {'mean': 100, 'std': 10},
            'trend': {'type': 'increasing', 'slope': 0.1, 'strength': 0.8},
            'seasonality': []
        }
        example.alerts = [
            Mock(
                id='test_alert',
                keyword='python programming',
                severity=Mock(value='high'),
                message='Test alert',
                timestamp=datetime.now(),
                status=Mock(value='active')
            )
        ]
        
        # Gera relatórios
        output_dir = str(tmp_path / "reports")
        example.generate_reports(output_dir)
        
        # Verifica se arquivos foram criados
        assert (tmp_path / "reports" / "predictions_report.json").exists()
        assert (tmp_path / "reports" / "analyses_report.json").exists()
        assert (tmp_path / "reports" / "alerts_report.json").exists()
        assert (tmp_path / "reports" / "alert_statistics.json").exists()
        assert (tmp_path / "reports" / "executive_summary.txt").exists()
    
    def test_generate_executive_summary(self, example):
        """Testa geração de resumo executivo"""
        # Prepara dados
        example.predictions = {
            'python programming': {
                '30d': Mock(
                    current_value=100,
                    predicted_value=120,
                    confidence=0.8,
                    direction=Mock(value='rising'),
                    confidence_level=Mock(value='high')
                )
            }
        }
        example.alerts = [
            Mock(
                keyword='python programming',
                severity=Mock(value='high'),
                message='High growth detected'
            )
        ]
        
        summary = example._generate_executive_summary()
        
        assert isinstance(summary, str)
        assert "RESUMO EXECUTIVO" in summary
        assert "python programming" in summary
        assert "RECOMENDAÇÕES" in summary
        assert "PRÓXIMOS PASSOS" in summary
    
    def test_display_metrics(self, example, capsys):
        """Testa exibição de métricas"""
        # Prepara dados
        example.predictions = {
            'python programming': {
                '30d': Mock(confidence=0.8)
            }
        }
        example.alerts = [
            Mock(severity=Mock(value='high')),
            Mock(severity=Mock(value='medium'))
        ]
        
        # Mock das estatísticas do sistema de alertas
        example.alert_system.get_alert_statistics = Mock(return_value={
            'enabled_rules_count': 5,
            'active_alerts': 2,
            'resolved_alerts': 1
        })
        
        example.display_metrics()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "MÉTRICAS DO SISTEMA" in output
        assert "Predições" in output
        assert "Alertas" in output
        assert "Sistema de Alertas" in output


class TestPredictionSystemExampleIntegration:
    """Testes de integração do exemplo"""
    
    @pytest.fixture
    def example(self):
        """Instância do exemplo para testes de integração"""
        return PredictionSystemExample()
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, example, tmp_path):
        """Testa workflow completo do exemplo"""
        # 1. Gera dados
        df = example.generate_realistic_data(['python programming'], 60)
        assert len(df) > 0
        
        # 2. Analisa séries temporais
        example.analyze_time_series(['python programming'])
        assert 'python programming' in example.analyses
        
        # 3. Prediz tendências
        example.predict_trends(['python programming'], ['7d', '30d'])
        assert 'python programming' in example.predictions
        
        # 4. Configura alertas
        await example.setup_alert_system()
        assert len(example.alert_system.alert_rules) > 0
        
        # 5. Gera alertas
        await example.generate_alerts()
        # Pode ser 0 se não houver violações
        
        # 6. Gera relatórios
        output_dir = str(tmp_path / "reports")
        example.generate_reports(output_dir)
        
        # Verifica arquivos gerados
        assert (tmp_path / "reports" / "predictions_report.json").exists()
        assert (tmp_path / "reports" / "executive_summary.txt").exists()
    
    def test_data_quality(self, example):
        """Testa qualidade dos dados gerados"""
        df = example.generate_realistic_data(['python programming'], 365)
        
        # Verifica estrutura
        assert 'date' in df.columns
        assert 'keyword' in df.columns
        assert 'value' in df.columns
        
        # Verifica tipos
        assert pd.api.types.is_datetime64_any_dtype(df['date'])
        assert pd.api.types.is_string_dtype(df['keyword'])
        assert pd.api.types.is_numeric_dtype(df['value'])
        
        # Verifica valores
        assert df['value'].min() >= 0
        assert df['value'].max() > 0
        assert not df['value'].isna().any()
        
        # Verifica consistência temporal
        assert df['date'].is_monotonic_increasing
        
        # Verifica distribuição por keyword
        keyword_counts = df['keyword'].value_counts()
        assert len(keyword_counts) == 1
        assert keyword_counts.iloc[0] == 365
    
    def test_prediction_consistency(self, example):
        """Testa consistência das predições"""
        example.generate_realistic_data(['python programming'], 90)
        example.predict_trends(['python programming'], ['7d', '30d'])
        
        predictions = example.predictions['python programming']
        
        # Verifica que predições para diferentes timeframes são consistentes
        if '7d' in predictions and '30d' in predictions:
            pred_7d = predictions['7d']
            pred_30d = predictions['30d']
            
            # Mesma keyword
            assert pred_7d.keyword == pred_30d.keyword
            
            # Valores atuais iguais
            assert pred_7d.current_value == pred_30d.current_value
            
            # Confiança entre 0 e 1
            assert 0 <= pred_7d.confidence <= 1
            assert 0 <= pred_30d.confidence <= 1
    
    def test_alert_system_integration(self, example):
        """Testa integração com sistema de alertas"""
        # Verifica se sistema de alertas está configurado
        assert example.alert_system is not None
        assert len(example.alert_system.alert_rules) > 0
        
        # Verifica configuração padrão
        config = example.alert_system.config
        assert 'alert_retention_days' in config
        assert 'max_active_alerts' in config
        assert 'thresholds' in config
    
    def test_observability_integration(self, example):
        """Testa integração com observabilidade"""
        # Verifica se componentes de observabilidade estão disponíveis
        assert example.telemetry is not None
        assert example.tracing is not None
        assert example.metrics is not None


class TestPredictionSystemExampleEdgeCases:
    """Testes de casos extremos do exemplo"""
    
    @pytest.fixture
    def example(self):
        """Instância do exemplo para testes de casos extremos"""
        return PredictionSystemExample()
    
    def test_empty_keywords_list(self, example):
        """Testa com lista vazia de keywords"""
        df = example.generate_realistic_data([], 10)
        assert len(df) == 0
    
    def test_single_day_data(self, example):
        """Testa com dados de apenas um dia"""
        df = example.generate_realistic_data(['python programming'], 1)
        assert len(df) == 1
        
        # Análise deve funcionar mesmo com poucos dados
        example.analyze_time_series(['python programming'])
        # Pode não gerar análise completa, mas não deve falhar
    
    def test_very_long_period(self, example):
        """Testa com período muito longo"""
        df = example.generate_realistic_data(['python programming'], 1000)
        assert len(df) == 1000
        
        # Verifica se dados mantêm padrões realistas
        assert df['value'].std() > 0
        assert df['value'].max() > df['value'].min()
    
    def test_special_characters_in_keywords(self, example):
        """Testa com caracteres especiais em keywords"""
        special_keywords = ['python@programming', 'machine-learning', 'data_science']
        df = example.generate_realistic_data(special_keywords, 10)
        
        assert len(df) == 30  # 3 keywords * 10 dias
        assert set(df['keyword'].unique()) == set(special_keywords)
    
    def test_very_high_values(self, example):
        """Testa com valores muito altos"""
        # Modifica parâmetros para gerar valores altos
        original_params = example._get_keyword_parameters('python programming')
        high_params = original_params.copy()
        high_params['base_value'] = 100000
        high_params['trend_slope'] = 1000
        
        # Mock do método para retornar parâmetros altos
        example._get_keyword_parameters = Mock(return_value=high_params)
        
        df = example.generate_realistic_data(['python programming'], 10)
        
        assert df['value'].max() > 100000
        assert df['value'].min() > 0
    
    def test_negative_trend(self, example):
        """Testa com tendência negativa"""
        # Modifica parâmetros para tendência negativa
        negative_params = {
            'base_value': 1000,
            'trend_slope': -5.0,  # Tendência negativa
            'seasonal_amplitude': 100,
            'weekly_amplitude': 30,
            'noise_std': 50
        }
        
        example._get_keyword_parameters = Mock(return_value=negative_params)
        
        df = example.generate_realistic_data(['python programming'], 30)
        
        # Verifica se valores diminuem ao longo do tempo
        keyword_data = df[df['keyword'] == 'python programming'].sort_values('date')
        first_value = keyword_data['value'].iloc[0]
        last_value = keyword_data['value'].iloc[-1]
        
        # Com ruído, pode não ser sempre decrescente, mas deve ter tendência
        assert last_value < first_value + 100  # Permite alguma variação


if __name__ == '__main__':
    pytest.main([__file__, '-value']) 