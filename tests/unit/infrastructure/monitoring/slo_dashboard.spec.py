from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
🧪 Testes Unitários - SLO Dashboard Manager

Tracing ID: IMP005_SLO_TESTS_2025_001
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Testes unitários para o sistema de SLOs (Service Level Objectives)
Baseado no checklist de revisão definitiva - IMP005

Cobertura:
- Cálculo de métricas SLO
- Detecção de violações
- Geração de relatórios
- Integração com Prometheus
- Validação de dashboards
"""

import unittest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import json

# Adicionar diretório pai ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.monitoring.slo_dashboard import (
    SLODashboardManager,
    SLOMetric,
    SLOViolation,
    SLOSeverity,
    SLOMetricType
)

class TestSLODashboardManager(unittest.TestCase):
    """Testes para SLODashboardManager"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        # Criar arquivo temporário para banco de dados
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Criar arquivo temporário para configuração
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
        self.temp_config.write("""
# Configuração de teste SLO
test_config:
  prometheus_url: "http://localhost:9090"
  grafana_url: "http://localhost:3000"
""")
        self.temp_config.close()
        
        # Mock das variáveis de ambiente
        self.env_patcher = patch.dict(os.environ, {
            'PROMETHEUS_URL': 'http://localhost:9090',
            'GRAFANA_URL': 'http://localhost:3000',
            'GRAFANA_TOKEN': 'test-token'
        })
        self.env_patcher.start()
        
        # Inicializar gerenciador com banco temporário
        with patch('infrastructure.monitoring.slo_dashboard.SLODashboardManager.db_path', self.temp_db.name):
            self.slo_manager = SLODashboardManager(self.temp_config.name)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        # Parar patches
        self.env_patcher.stop()
        
        # Remover arquivos temporários
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_init_database(self):
        """Testa inicialização do banco de dados"""
        # Verificar se as tabelas foram criadas
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            
            # Verificar tabela slo_metrics
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='slo_metrics'")
            self.assertIsNotNone(cursor.fetchone())
            
            # Verificar tabela slo_violations
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='slo_violations'")
            self.assertIsNotNone(cursor.fetchone())
            
            # Verificar tabela error_budgets
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='error_budgets'")
            self.assertIsNotNone(cursor.fetchone())
    
    def test_load_config(self):
        """Testa carregamento de configuração"""
        # Verificar se a configuração foi carregada
        self.assertIsInstance(self.slo_manager.config, dict)
        self.assertIn('test_config', self.slo_manager.config)
    
    @patch('requests.get')
    def test_get_prometheus_metric_success(self, mock_get):
        """Testa busca bem-sucedida de métrica do Prometheus"""
        # Mock da resposta do Prometheus
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "result": [
                    {
                        "value": [1234567890, "0.999"]
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Testar busca de métrica
        result = self.slo_manager.get_prometheus_metric('test_metric')
        
        self.assertEqual(result, 0.999)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_prometheus_metric_failure(self, mock_get):
        """Testa falha na busca de métrica do Prometheus"""
        # Mock de erro
        mock_get.side_effect = Exception("Connection error")
        
        # Testar busca de métrica
        result = self.slo_manager.get_prometheus_metric('test_metric')
        
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_calculate_slo_metrics(self, mock_get):
        """Testa cálculo de métricas SLO"""
        # Mock das respostas do Prometheus
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "result": [
                    {
                        "value": [1234567890, "0.999"]
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Calcular métricas
        metrics = self.slo_manager.calculate_slo_metrics()
        
        # Verificar se métricas foram calculadas
        self.assertIsInstance(metrics, list)
        self.assertGreater(len(metrics), 0)
        
        # Verificar estrutura das métricas
        for metric in metrics:
            self.assertIsInstance(metric, SLOMetric)
            self.assertIsInstance(metric.name, str)
            self.assertIsInstance(metric.service, str)
            self.assertIsInstance(metric.metric_type, SLOMetricType)
            self.assertIsInstance(metric.target, float)
            self.assertIsInstance(metric.current_value, float)
            self.assertIsInstance(metric.error_budget, float)
            self.assertIsInstance(metric.severity, SLOSeverity)
    
    def test_detect_violations_availability(self):
        """Testa detecção de violações de disponibilidade"""
        # Criar métrica com violação
        metric = SLOMetric(
            name="test_availability",
            service="test_service",
            metric_type=SLOMetricType.AVAILABILITY,
            target=0.999,  # 99.9%
            current_value=0.95,  # 95% (violação)
            error_budget=0.05,
            severity=SLOSeverity.CRITICAL,
            description="Test availability",
            timestamp=datetime.utcnow()
        )
        
        # Detectar violações
        violations = self.slo_manager.detect_violations([metric])
        
        # Verificar se violação foi detectada
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].metric_name, "test_availability")
        self.assertEqual(violations[0].service, "test_service")
        self.assertGreater(violations[0].violation_percentage, 0)
    
    def test_detect_violations_latency(self):
        """Testa detecção de violações de latência"""
        # Criar métrica com violação
        metric = SLOMetric(
            name="test_latency",
            service="test_service",
            metric_type=SLOMetricType.LATENCY,
            target=0.2,  # 200ms
            current_value=0.5,  # 500ms (violação)
            error_budget=-0.3,
            severity=SLOSeverity.CRITICAL,
            description="Test latency",
            timestamp=datetime.utcnow()
        )
        
        # Detectar violações
        violations = self.slo_manager.detect_violations([metric])
        
        # Verificar se violação foi detectada
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].metric_name, "test_latency")
        self.assertGreater(violations[0].violation_percentage, 0)
    
    def test_detect_violations_error_rate(self):
        """Testa detecção de violações de taxa de erro"""
        # Criar métrica com violação
        metric = SLOMetric(
            name="test_error_rate",
            service="test_service",
            metric_type=SLOMetricType.ERROR_RATE,
            target=0.001,  # 0.1%
            current_value=0.005,  # 0.5% (violação)
            error_budget=-0.004,
            severity=SLOSeverity.CRITICAL,
            description="Test error rate",
            timestamp=datetime.utcnow()
        )
        
        # Detectar violações
        violations = self.slo_manager.detect_violations([metric])
        
        # Verificar se violação foi detectada
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].metric_name, "test_error_rate")
        self.assertGreater(violations[0].violation_percentage, 0)
    
    def test_detect_violations_no_violation(self):
        """Testa quando não há violações"""
        # Criar métrica sem violação
        metric = SLOMetric(
            name="test_availability",
            service="test_service",
            metric_type=SLOMetricType.AVAILABILITY,
            target=0.999,  # 99.9%
            current_value=0.9995,  # 99.95% (sem violação)
            error_budget=0.0005,
            severity=SLOSeverity.CRITICAL,
            description="Test availability",
            timestamp=datetime.utcnow()
        )
        
        # Detectar violações
        violations = self.slo_manager.detect_violations([metric])
        
        # Verificar que não há violações
        self.assertEqual(len(violations), 0)
    
    def test_save_metrics(self):
        """Testa salvamento de métricas no banco"""
        # Criar métricas de teste
        metrics = [
            SLOMetric(
                name="test_metric_1",
                service="test_service",
                metric_type=SLOMetricType.AVAILABILITY,
                target=0.999,
                current_value=0.995,
                error_budget=0.004,
                severity=SLOSeverity.CRITICAL,
                description="Test metric 1",
                timestamp=datetime.utcnow()
            ),
            SLOMetric(
                name="test_metric_2",
                service="test_service",
                metric_type=SLOMetricType.LATENCY,
                target=0.2,
                current_value=0.15,
                error_budget=0.05,
                severity=SLOSeverity.CRITICAL,
                description="Test metric 2",
                timestamp=datetime.utcnow()
            )
        ]
        
        # Salvar métricas
        self.slo_manager._save_metrics(metrics)
        
        # Verificar se foram salvas
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM slo_metrics")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 2)
    
    def test_save_violation(self):
        """Testa salvamento de violação no banco"""
        # Criar violação de teste
        violation = SLOViolation(
            metric_name="test_violation",
            service="test_service",
            expected_value=0.999,
            actual_value=0.95,
            violation_percentage=4.9,
            severity=SLOSeverity.CRITICAL,
            timestamp=datetime.utcnow(),
            duration_minutes=5
        )
        
        # Salvar violação
        self.slo_manager._save_violation(violation)
        
        # Verificar se foi salva
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM slo_violations")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)
    
    def test_generate_slo_report(self):
        """Testa geração de relatório SLO"""
        # Inserir dados de teste
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            
            # Inserir métricas de teste
            for index in range(5):
                cursor.execute("""
                    INSERT INTO slo_metrics 
                    (name, service, metric_type, target_value, current_value, 
                     error_budget, severity, description, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"test_metric_{index}",
                    "test_service",
                    "availability",
                    0.999,
                    0.995,
                    0.004,
                    "critical",
                    f"Test metric {index}",
                    datetime.utcnow().isoformat()
                ))
            
            # Inserir violações de teste
            for index in range(2):
                cursor.execute("""
                    INSERT INTO slo_violations 
                    (metric_name, service, expected_value, actual_value, 
                     violation_percentage, severity, timestamp, duration_minutes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"test_violation_{index}",
                    "test_service",
                    0.999,
                    0.95,
                    4.9,
                    "critical",
                    datetime.utcnow().isoformat(),
                    5
                ))
            
            conn.commit()
        
        # Gerar relatório
        report = self.slo_manager.generate_slo_report(period_hours=24)
        
        # Verificar estrutura do relatório
        self.assertIsInstance(report, dict)
        self.assertIn('period', report)
        self.assertIn('summary', report)
        self.assertIn('metrics_by_service', report)
        self.assertIn('violations_by_severity', report)
        self.assertIn('error_budgets', report)
        
        # Verificar dados do relatório
        self.assertEqual(report['summary']['total_metrics'], 5)
        self.assertEqual(report['summary']['total_violations'], 2)
        self.assertIn('test_service', report['metrics_by_service'])
        self.assertIn('critical', report['violations_by_severity'])
    
    @patch('requests.post')
    def test_create_grafana_dashboard_success(self, mock_post):
        """Testa criação bem-sucedida de dashboard no Grafana"""
        # Mock da resposta do Grafana
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Testar criação de dashboard
        result = self.slo_manager.create_grafana_dashboard()
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_create_grafana_dashboard_failure(self, mock_post):
        """Testa falha na criação de dashboard no Grafana"""
        # Mock de erro
        mock_post.side_effect = Exception("Grafana error")
        
        # Testar criação de dashboard
        result = self.slo_manager.create_grafana_dashboard()
        
        self.assertFalse(result)
    
    def test_generate_visualization(self):
        """Testa geração de visualização"""
        # Criar relatório de teste
        report = {
            "period": {
                "start": (datetime.utcnow() - timedelta(hours=24)).isoformat(),
                "end": datetime.utcnow().isoformat(),
                "hours": 24
            },
            "summary": {
                "total_metrics": 10,
                "total_violations": 2,
                "violation_rate": 20.0
            },
            "metrics_by_service": {
                "api": {
                    "count": 5,
                    "avg_error_budget": 0.05,
                    "min_error_budget": 0.01,
                    "max_error_budget": 0.1
                },
                "database": {
                    "count": 5,
                    "avg_error_budget": 0.03,
                    "min_error_budget": 0.01,
                    "max_error_budget": 0.05
                }
            },
            "violations_by_severity": {
                "critical": {
                    "count": 1,
                    "avg_violation_percentage": 5.0
                },
                "warning": {
                    "count": 1,
                    "avg_violation_percentage": 2.0
                }
            },
            "error_budgets": {
                "api_availability": {
                    "avg_error_budget": 0.05,
                    "error_budget_trend": [0.05, 0.04, 0.06, 0.05]
                }
            }
        }
        
        # Gerar visualização
        with patch('os.makedirs'):
            with patch('builtins.open', create=True):
                result = self.slo_manager.generate_visualization(report)
        
        # Verificar se retornou caminho
        self.assertIsInstance(result, str)
    
    def test_run_monitoring_cycle(self):
        """Testa execução do ciclo de monitoramento"""
        # Mock das funções internas
        with patch.object(self.slo_manager, 'calculate_slo_metrics') as mock_calc:
            with patch.object(self.slo_manager, 'detect_violations') as mock_detect:
                with patch.object(self.slo_manager, 'generate_slo_report') as mock_report:
                    with patch.object(self.slo_manager, 'generate_visualization') as mock_viz:
                        
                        # Configurar mocks
                        mock_calc.return_value = []
                        mock_detect.return_value = []
                        mock_report.return_value = {}
                        mock_viz.return_value = ""
                        
                        # Executar ciclo
                        self.slo_manager.run_monitoring_cycle()
                        
                        # Verificar se funções foram chamadas
                        mock_calc.assert_called_once()
                        mock_detect.assert_called_once()
                        mock_report.assert_called_once()
                        mock_viz.assert_called_once()

class TestSLOMetric(unittest.TestCase):
    """Testes para SLOMetric"""
    
    def test_slo_metric_creation(self):
        """Testa criação de SLOMetric"""
        metric = SLOMetric(
            name="test_metric",
            service="test_service",
            metric_type=SLOMetricType.AVAILABILITY,
            target=0.999,
            current_value=0.995,
            error_budget=0.004,
            severity=SLOSeverity.CRITICAL,
            description="Test metric",
            timestamp=datetime.utcnow()
        )
        
        self.assertEqual(metric.name, "test_metric")
        self.assertEqual(metric.service, "test_service")
        self.assertEqual(metric.metric_type, SLOMetricType.AVAILABILITY)
        self.assertEqual(metric.target, 0.999)
        self.assertEqual(metric.current_value, 0.995)
        self.assertEqual(metric.error_budget, 0.004)
        self.assertEqual(metric.severity, SLOSeverity.CRITICAL)

class TestSLOViolation(unittest.TestCase):
    """Testes para SLOViolation"""
    
    def test_slo_violation_creation(self):
        """Testa criação de SLOViolation"""
        violation = SLOViolation(
            metric_name="test_violation",
            service="test_service",
            expected_value=0.999,
            actual_value=0.95,
            violation_percentage=4.9,
            severity=SLOSeverity.CRITICAL,
            timestamp=datetime.utcnow(),
            duration_minutes=5
        )
        
        self.assertEqual(violation.metric_name, "test_violation")
        self.assertEqual(violation.service, "test_service")
        self.assertEqual(violation.expected_value, 0.999)
        self.assertEqual(violation.actual_value, 0.95)
        self.assertEqual(violation.violation_percentage, 4.9)
        self.assertEqual(violation.severity, SLOSeverity.CRITICAL)
        self.assertEqual(violation.duration_minutes, 5)

class TestSLOSeverity(unittest.TestCase):
    """Testes para SLOSeverity"""
    
    def test_slo_severity_values(self):
        """Testa valores de SLOSeverity"""
        self.assertEqual(SLOSeverity.CRITICAL.value, "critical")
        self.assertEqual(SLOSeverity.WARNING.value, "warning")
        self.assertEqual(SLOSeverity.INFO.value, "info")

class TestSLOMetricType(unittest.TestCase):
    """Testes para SLOMetricType"""
    
    def test_slo_metric_type_values(self):
        """Testa valores de SLOMetricType"""
        self.assertEqual(SLOMetricType.AVAILABILITY.value, "availability")
        self.assertEqual(SLOMetricType.LATENCY.value, "latency")
        self.assertEqual(SLOMetricType.ERROR_RATE.value, "error_rate")
        self.assertEqual(SLOMetricType.THROUGHPUT.value, "throughput")
        self.assertEqual(SLOMetricType.RESILIENCE.value, "resilience")

if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2) 