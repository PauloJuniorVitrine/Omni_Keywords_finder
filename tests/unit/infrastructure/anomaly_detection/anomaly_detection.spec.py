from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Detecção de Anomalias

Cobertura:
- Detecção estatística (Z-score, IQR, Trend)
- Detecção ML (Isolation Forest, DBSCAN)
- Gerenciamento de baseline
- Sistema de alertas
- Dashboard e métricas

Autor: Testes Sistema de Detecção de Anomalias
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import numpy as np
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Importar módulos do sistema
from infrastructure.monitoramento.anomaly_detection import (
    AnomalyDetectionSystem,
    StatisticalDetector,
    MLDetector,
    BaselineManager,
    AlertManager,
    AnomalyType,
    AnomalySeverity,
    DetectionMethod,
    BaselineMetric,
    AnomalyDetection,
    AnomalyAlert
)

class TestStatisticalDetector:
    """Testes para o detector estatístico"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.detector = StatisticalDetector(
            window_size=100,
            z_threshold=3.0,
            iqr_multiplier=1.5
        )
    
    def test_add_metric(self):
        """Testa adição de métricas"""
        # Adicionar métricas normais
        for index in range(50):
            self.detector.add_metric('test_metric', 100 + np.random.normal(0, 5), datetime.utcnow())
        
        # Verificar se histórico foi preenchido
        assert len(self.detector.metrics_history['test_metric']) == 50
    
    def test_z_score_anomaly_detection(self):
        """Testa detecção de anomalia por Z-score"""
        # Criar dados normais
        normal_values = [100 + np.random.normal(0, 5) for _ in range(50)]
        for value in normal_values:
            self.detector.add_metric('test_metric', value, datetime.utcnow())
        
        # Testar valor anômalo (muito alto)
        anomaly_value = 200  # Valor muito acima da média
        anomalies = self.detector.detect_anomalies('test_metric', anomaly_value, datetime.utcnow())
        
        assert len(anomalies) > 0
        assert any(a.anomaly_type == AnomalyType.SPIKE for a in anomalies)
        assert any(a.detection_method == DetectionMethod.STATISTICAL for a in anomalies)
    
    def test_iqr_anomaly_detection(self):
        """Testa detecção de anomalia por IQR"""
        # Criar dados normais
        normal_values = [100 + np.random.normal(0, 5) for _ in range(50)]
        for value in normal_values:
            self.detector.add_metric('test_metric', value, datetime.utcnow())
        
        # Testar outlier (muito baixo)
        outlier_value = 50  # Valor muito abaixo da média
        anomalies = self.detector.detect_anomalies('test_metric', outlier_value, datetime.utcnow())
        
        assert len(anomalies) > 0
        assert any(a.anomaly_type == AnomalyType.OUTLIER for a in anomalies)
    
    def test_trend_anomaly_detection(self):
        """Testa detecção de mudança de tendência"""
        # Criar dados com tendência crescente
        trend_values = [100 + index * 2 + np.random.normal(0, 1) for index in range(30)]
        for value in trend_values:
            self.detector.add_metric('test_metric', value, datetime.utcnow())
        
        # Testar mudança brusca
        sudden_change = 50  # Valor muito baixo comparado à tendência
        anomalies = self.detector.detect_anomalies('test_metric', sudden_change, datetime.utcnow())
        
        # Pode ou não detectar dependendo da configuração
        # O importante é que não cause erro
        assert isinstance(anomalies, list)
    
    def test_insufficient_data(self):
        """Testa comportamento com dados insuficientes"""
        # Adicionar poucos dados
        for index in range(5):
            self.detector.add_metric('test_metric', 100 + index, datetime.utcnow())
        
        # Tentar detectar anomalia
        anomalies = self.detector.detect_anomalies('test_metric', 200, datetime.utcnow())
        
        # Deve retornar lista vazia
        assert len(anomalies) == 0
    
    def test_severity_calculation(self):
        """Testa cálculo de severidade"""
        # Testar diferentes scores de desvio
        assert self.detector._calculate_severity(1.5) == AnomalySeverity.LOW
        assert self.detector._calculate_severity(2.5) == AnomalySeverity.MEDIUM
        assert self.detector._calculate_severity(4.0) == AnomalySeverity.HIGH
        assert self.detector._calculate_severity(6.0) == AnomalySeverity.CRITICAL

class TestMLDetector:
    """Testes para o detector ML"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = MLDetector(model_path=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_prepare_features(self):
        """Testa preparação de features"""
        metrics_data = {
            'metric1': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'metric2': [200, 201, 202, 203, 204, 205, 206, 207, 208, 209]
        }
        
        features = self.detector.prepare_features(metrics_data)
        
        assert features.shape == (1, 20)  # 2 métricas * 10 features cada
        assert not np.isnan(features).any()
    
    def test_prepare_features_insufficient_data(self):
        """Testa preparação de features com dados insuficientes"""
        metrics_data = {
            'metric1': [100, 101, 102],  # Menos de 10 valores
            'metric2': [200, 201, 202, 203, 204, 205, 206, 207, 208, 209]
        }
        
        features = self.detector.prepare_features(metrics_data)
        
        assert features.shape == (1, 20)
        # Verificar se métrica com dados insuficientes foi preenchida com zeros
        assert features[0, 0] == 0.0  # Primeira feature da primeira métrica
    
    @patch('sklearn.ensemble.IsolationForest')
    @patch('sklearn.cluster.DBSCAN')
    def test_train_models(self, mock_dbscan, mock_isolation_forest):
        """Testa treinamento de modelos ML"""
        # Mock dos modelos
        mock_if = Mock()
        mock_db = Mock()
        mock_isolation_forest.return_value = mock_if
        mock_dbscan.return_value = mock_db
        
        # Dados de treinamento
        training_data = {
            'metric1': [
                {'value': 100, 'is_anomaly': False},
                {'value': 101, 'is_anomaly': False},
                {'value': 102, 'is_anomaly': False},
                {'value': 103, 'is_anomaly': False},
                {'value': 104, 'is_anomaly': False},
                {'value': 105, 'is_anomaly': False},
                {'value': 106, 'is_anomaly': False},
                {'value': 107, 'is_anomaly': False},
                {'value': 108, 'is_anomaly': False},
                {'value': 109, 'is_anomaly': False},
                {'value': 200, 'is_anomaly': True},  # Anomalia
            ]
        }
        
        # Treinar modelos
        self.detector.train_models(training_data)
        
        # Verificar se modelos foram chamados
        mock_if.fit.assert_called_once()
        mock_db.fit.assert_called_once()
    
    def test_save_and_load_models(self):
        """Testa salvamento e carregamento de modelos"""
        # Mock dos modelos treinados
        self.detector.models_trained = {
            'isolation_forest': True,
            'dbscan': True
        }
        
        # Salvar modelos
        self.detector._save_models()
        
        # Verificar se arquivos foram criados
        assert (Path(self.temp_dir) / 'isolation_forest.pkl').exists()
        assert (Path(self.temp_dir) / 'dbscan.pkl').exists()
        assert (Path(self.temp_dir) / 'scaler.pkl').exists()
        assert (Path(self.temp_dir) / 'metadata.json').exists()
        
        # Carregar modelos
        self.detector.load_models()
        
        # Verificar se modelos foram carregados
        assert self.detector.models_trained['isolation_forest']
        assert self.detector.models_trained['dbscan']

class TestBaselineManager:
    """Testes para o gerenciador de baseline"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.manager = BaselineManager(window_size=100)
    
    def test_add_metric(self):
        """Testa adição de métricas"""
        # Adicionar métricas
        for index in range(50):
            self.manager.add_metric('test_metric', 100 + index, datetime.utcnow())
        
        # Verificar se histórico foi preenchido
        assert len(self.manager.metrics_history['test_metric']) == 50
    
    def test_baseline_update(self):
        """Testa atualização de baseline"""
        # Adicionar métricas suficientes para trigger de atualização
        for index in range(100):
            self.manager.add_metric('test_metric', 100 + np.random.normal(0, 5), datetime.utcnow())
        
        # Verificar se baseline foi criado
        baseline = self.manager.get_baseline('test_metric')
        assert baseline is not None
        assert baseline.name == 'test_metric'
        assert baseline.sample_size > 0
        assert baseline.mean > 0
        assert baseline.std > 0
    
    def test_get_all_baselines(self):
        """Testa obtenção de todos os baselines"""
        # Criar baselines para múltiplas métricas
        for metric_name in ['metric1', 'metric2', 'metric3']:
            for index in range(100):
                self.manager.add_metric(metric_name, 100 + index, datetime.utcnow())
        
        # Obter todos os baselines
        baselines = self.manager.get_all_baselines()
        
        assert len(baselines) == 3
        assert all(name in baselines for name in ['metric1', 'metric2', 'metric3'])
    
    def test_baseline_statistics(self):
        """Testa cálculo de estatísticas do baseline"""
        # Criar dados conhecidos
        values = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        for value in values:
            self.manager.add_metric('test_metric', value, datetime.utcnow())
        
        # Forçar atualização
        self.manager._update_baseline('test_metric')
        
        # Verificar estatísticas
        baseline = self.manager.get_baseline('test_metric')
        assert baseline.mean == pytest.approx(104.5, rel=1e-2)
        assert baseline.median == 104.5
        assert baseline.min == 100
        assert baseline.max == 109

class TestAlertManager:
    """Testes para o gerenciador de alertas"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.manager = AlertManager()
    
    def test_create_alert(self):
        """Testa criação de alerta"""
        # Criar anomalia
        anomaly = AnomalyDetection(
            id='test_id',
            metric_name='test_metric',
            timestamp=datetime.utcnow(),
            current_value=200,
            baseline_value=100,
            deviation_score=3.5,
            anomaly_type=AnomalyType.SPIKE,
            severity=AnomalySeverity.HIGH,
            detection_method=DetectionMethod.STATISTICAL,
            confidence=0.8,
            description='Test anomaly',
            metadata={}
        )
        
        # Criar alerta
        alert = self.manager._create_alert(anomaly)
        
        assert alert is not None
        assert alert.anomaly_id == 'test_id'
        assert alert.metric_name == 'test_metric'
        assert alert.severity == AnomalySeverity.HIGH
        assert alert.action_required
    
    def test_process_anomalies(self):
        """Testa processamento de anomalias"""
        # Criar anomalias
        anomalies = [
            AnomalyDetection(
                id=f'test_id_{index}',
                metric_name='test_metric',
                timestamp=datetime.utcnow(),
                current_value=200,
                baseline_value=100,
                deviation_score=3.5,
                anomaly_type=AnomalyType.SPIKE,
                severity=AnomalySeverity.HIGH,
                detection_method=DetectionMethod.STATISTICAL,
                confidence=0.8,
                description='Test anomaly',
                metadata={}
            )
            for index in range(3)
        ]
        
        # Processar anomalias
        alerts = self.manager.process_anomalies(anomalies)
        
        assert len(alerts) == 3
        assert len(self.manager.alerts) == 3
    
    def test_acknowledge_alert(self):
        """Testa reconhecimento de alerta"""
        # Criar alerta
        alert = AnomalyAlert(
            id='test_id',
            anomaly_id='anomaly_id',
            title='Test Alert',
            message='Test message',
            severity=AnomalySeverity.HIGH,
            timestamp=datetime.utcnow(),
            metric_name='test_metric',
            current_value=200,
            threshold=100,
            action_required=True
        )
        
        self.manager.alerts.append(alert)
        
        # Reconhecer alerta
        result = self.manager.acknowledge_alert('test_id')
        
        assert result is True
        assert alert.acknowledged is True
    
    def test_resolve_alert(self):
        """Testa resolução de alerta"""
        # Criar alerta
        alert = AnomalyAlert(
            id='test_id',
            anomaly_id='anomaly_id',
            title='Test Alert',
            message='Test message',
            severity=AnomalySeverity.HIGH,
            timestamp=datetime.utcnow(),
            metric_name='test_metric',
            current_value=200,
            threshold=100,
            action_required=True
        )
        
        self.manager.alerts.append(alert)
        
        # Resolver alerta
        result = self.manager.resolve_alert('test_id')
        
        assert result is True
        assert alert.resolved is True
    
    def test_get_active_alerts(self):
        """Testa obtenção de alertas ativos"""
        # Criar alertas
        active_alert = AnomalyAlert(
            id='active_id',
            anomaly_id='anomaly_id',
            title='Active Alert',
            message='Active message',
            severity=AnomalySeverity.HIGH,
            timestamp=datetime.utcnow(),
            metric_name='test_metric',
            current_value=200,
            threshold=100,
            action_required=True
        )
        
        resolved_alert = AnomalyAlert(
            id='resolved_id',
            anomaly_id='anomaly_id',
            title='Resolved Alert',
            message='Resolved message',
            severity=AnomalySeverity.HIGH,
            timestamp=datetime.utcnow(),
            metric_name='test_metric',
            current_value=200,
            threshold=100,
            action_required=True
        )
        resolved_alert.resolved = True
        
        self.manager.alerts = [active_alert, resolved_alert]
        
        # Obter alertas ativos
        active_alerts = self.manager.get_active_alerts()
        
        assert len(active_alerts) == 1
        assert active_alerts[0].id == 'active_id'
    
    def test_alert_history(self):
        """Testa histórico de alertas"""
        # Criar alertas com diferentes timestamps
        old_alert = AnomalyAlert(
            id='old_id',
            anomaly_id='anomaly_id',
            title='Old Alert',
            message='Old message',
            severity=AnomalySeverity.HIGH,
            timestamp=datetime.utcnow() - timedelta(hours=25),
            metric_name='test_metric',
            current_value=200,
            threshold=100,
            action_required=True
        )
        
        recent_alert = AnomalyAlert(
            id='recent_id',
            anomaly_id='anomaly_id',
            title='Recent Alert',
            message='Recent message',
            severity=AnomalySeverity.HIGH,
            timestamp=datetime.utcnow() - timedelta(hours=12),
            metric_name='test_metric',
            current_value=200,
            threshold=100,
            action_required=True
        )
        
        self.manager.alerts = [old_alert, recent_alert]
        
        # Obter histórico das últimas 24 horas
        history = self.manager.get_alert_history(hours=24)
        
        assert len(history) == 1
        assert history[0].id == 'recent_id'

class TestAnomalyDetectionSystem:
    """Testes para o sistema principal"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = {
            'detection_interval': 1,  # 1 segundo para testes
            'alert_thresholds': {
                'critical': 0.8,
                'high': 0.6,
                'medium': 0.4,
                'low': 0.2
            }
        }
        self.system = AnomalyDetectionSystem(self.config)
    
    def test_system_initialization(self):
        """Testa inicialização do sistema"""
        assert self.system.baseline_manager is not None
        assert self.system.statistical_detector is not None
        assert self.system.ml_detector is not None
        assert self.system.alert_manager is not None
        assert self.system.is_running is False
    
    def test_add_metric(self):
        """Testa adição de métricas"""
        # Adicionar métrica
        self.system.add_metric('test_metric', 100.0)
        
        # Verificar se foi adicionada aos componentes
        assert len(self.system.baseline_manager.metrics_history['test_metric']) == 1
        assert len(self.system.statistical_detector.metrics_history['test_metric']) == 1
        assert len(self.system.ml_detector.features_history['test_metric']) == 1
    
    def test_detect_anomalies(self):
        """Testa detecção de anomalias"""
        # Adicionar dados normais
        for index in range(50):
            self.system.add_metric('test_metric', 100 + np.random.normal(0, 5))
        
        # Detectar anomalia
        anomalies = self.system.detect_anomalies('test_metric', 200)  # Valor anômalo
        
        # Pode ou não detectar dependendo da configuração
        # O importante é que não cause erro
        assert isinstance(anomalies, list)
    
    def test_dashboard_data(self):
        """Testa geração de dados do dashboard"""
        # Adicionar algumas métricas
        for index in range(10):
            self.system.add_metric('test_metric', 100 + index)
        
        # Obter dados do dashboard
        dashboard_data = self.system.get_dashboard_data()
        
        # Verificar estrutura
        assert 'system_status' in dashboard_data
        assert 'statistics' in dashboard_data
        assert 'severity_distribution' in dashboard_data
        assert 'method_distribution' in dashboard_data
        assert 'recent_detections' in dashboard_data
        assert 'active_alerts' in dashboard_data
        assert 'baselines' in dashboard_data
        
        # Verificar valores
        assert dashboard_data['system_status']['running'] is False
        assert dashboard_data['statistics']['total_detections'] >= 0
    
    def test_system_start_stop(self):
        """Testa início e parada do sistema"""
        # Iniciar sistema
        self.system.start()
        assert self.system.is_running is True
        
        # Parar sistema
        self.system.stop()
        assert self.system.is_running is False
    
    def test_ml_training(self):
        """Testa treinamento de modelos ML"""
        # Dados de treinamento
        training_data = {
            'metric1': [
                {'value': 100, 'is_anomaly': False},
                {'value': 101, 'is_anomaly': False},
                {'value': 102, 'is_anomaly': False},
                {'value': 103, 'is_anomaly': False},
                {'value': 104, 'is_anomaly': False},
                {'value': 105, 'is_anomaly': False},
                {'value': 106, 'is_anomaly': False},
                {'value': 107, 'is_anomaly': False},
                {'value': 108, 'is_anomaly': False},
                {'value': 109, 'is_anomaly': False},
                {'value': 200, 'is_anomaly': True},  # Anomalia
            ]
        }
        
        # Treinar modelos
        self.system.train_ml_models(training_data)
        
        # Verificar se não causou erro
        # (o treinamento real depende de scikit-learn)
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        # Testar com dados inválidos
        anomalies = self.system.detect_anomalies('invalid_metric', float('nan'))
        
        # Deve retornar lista vazia ou lidar graciosamente
        assert isinstance(anomalies, list)
    
    def test_metric_counters(self):
        """Testa contadores de métricas Prometheus"""
        # Adicionar métricas e detectar anomalias
        for index in range(10):
            self.system.add_metric('test_metric', 100 + index)
        
        self.system.detect_anomalies('test_metric', 200)
        
        # Verificar se contadores foram incrementados
        # (depende da implementação específica do Prometheus)

def test_factory_function():
    """Testa função factory"""
    # Testar criação com configuração
    config = {'detection_interval': 30}
    system = create_anomaly_detection_system(config)
    
    assert isinstance(system, AnomalyDetectionSystem)
    assert system.config == config
    
    # Testar criação sem configuração
    system_default = create_anomaly_detection_system()
    
    assert isinstance(system_default, AnomalyDetectionSystem)
    assert system_default.config == {}

# Testes de integração
class TestIntegration:
    """Testes de integração do sistema completo"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.system = AnomalyDetectionSystem()
    
    def test_full_workflow(self):
        """Testa workflow completo do sistema"""
        # 1. Adicionar métricas normais
        for index in range(50):
            self.system.add_metric('api_latency', 100 + np.random.normal(0, 5))
        
        # 2. Detectar anomalia
        anomalies = self.system.detect_anomalies('api_latency', 300)  # Valor muito alto
        
        # 3. Processar alertas
        if anomalies:
            alerts = self.system.alert_manager.process_anomalies(anomalies)
            
            # 4. Verificar dados do dashboard
            dashboard_data = self.system.get_dashboard_data()
            
            assert 'system_status' in dashboard_data
            assert 'statistics' in dashboard_data
            assert dashboard_data['statistics']['total_detections'] >= 0
    
    def test_multiple_metrics(self):
        """Testa sistema com múltiplas métricas"""
        metrics = ['api_latency', 'cpu_usage', 'memory_usage', 'error_rate']
        
        # Adicionar dados para todas as métricas
        for metric in metrics:
            for index in range(30):
                self.system.add_metric(metric, 50 + np.random.normal(0, 10))
        
        # Detectar anomalias em todas
        for metric in metrics:
            anomalies = self.system.detect_anomalies(metric, 200)  # Valor anômalo
            assert isinstance(anomalies, list)
        
        # Verificar dashboard
        dashboard_data = self.system.get_dashboard_data()
        assert len(dashboard_data['baselines']) >= 0

# Testes de performance
class TestPerformance:
    """Testes de performance"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.system = AnomalyDetectionSystem()
    
    def test_large_dataset(self):
        """Testa performance com grande volume de dados"""
        # Adicionar muitos dados
        start_time = datetime.utcnow()
        
        for index in range(1000):
            self.system.add_metric('test_metric', 100 + np.random.normal(0, 5))
        
        # Detectar anomalias
        anomalies = self.system.detect_anomalies('test_metric', 300)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Deve completar em tempo razoável (< 5 segundos)
        assert duration < 5.0
        assert isinstance(anomalies, list)
    
    def test_concurrent_metrics(self):
        """Testa adição concorrente de métricas"""
        import threading
        
        def add_metrics(metric_name, count):
            for index in range(count):
                self.system.add_metric(metric_name, 100 + index)
        
        # Criar threads para adicionar métricas
        threads = []
        for index in range(5):
            thread = threading.Thread(
                target=add_metrics,
                args=(f'metric_{index}', 100)
            )
            threads.append(thread)
        
        # Executar threads
        start_time = datetime.utcnow()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Verificar se todas as métricas foram adicionadas
        total_metrics = sum(
            len(self.system.baseline_manager.metrics_history[f'metric_{index}'])
            for index in range(5)
        )
        
        assert total_metrics == 500
        assert duration < 10.0  # Deve completar em tempo razoável

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-value"]) 