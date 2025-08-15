from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
🧪 TESTES UNITÁRIOS - COMPLIANCE MONITORING

Tracing ID: TEST_COMPLIANCE_MONITOR_2025_001
Data/Hora: 2025-01-27 17:15:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Testes unitários para o sistema de monitoramento de compliance.
"""

import unittest
import json
import tempfile
import os
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Adicionar scripts ao path
sys.path.append('scripts/compliance')

# Importar módulos de compliance
from monitor_compliance import (
    ComplianceMonitor, ComplianceMetric, AlertLevel, 
    ComplianceAlert, ComplianceMetrics
)

class TestComplianceMonitor(unittest.TestCase):
    """Testes para o monitor de compliance"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Criar diretórios necessários
        os.makedirs('data/compliance', exist_ok=True)
        os.makedirs('logs/compliance', exist_ok=True)
        os.makedirs('config/compliance', exist_ok=True)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_monitor_initialization(self):
        """Testa inicialização do ComplianceMonitor"""
        monitor = ComplianceMonitor()
        
        self.assertIsNotNone(monitor.tracing_id)
        self.assertIsInstance(monitor.metrics_history, list)
        self.assertIsInstance(monitor.alerts, dict)
        self.assertIsInstance(monitor.thresholds, dict)
        self.assertFalse(monitor.monitoring_active)
    
    def test_thresholds_loading(self):
        """Testa carregamento de thresholds"""
        monitor = ComplianceMonitor()
        
        expected_thresholds = [
            "gdpr_score", "lgpd_score", "soc2_score", 
            "iso27001_score", "pci_dss_score"
        ]
        
        for threshold in expected_thresholds:
            self.assertIn(threshold, monitor.thresholds)
            self.assertIsInstance(monitor.thresholds[threshold], float)
    
    def test_calculate_compliance_scores(self):
        """Testa cálculo de scores de compliance"""
        monitor = ComplianceMonitor()
        
        scores = monitor.calculate_compliance_scores()
        
        expected_keys = [
            "gdpr_score", "lgpd_score", "soc2_score",
            "iso27001_score", "pci_dss_score"
        ]
        
        for key in expected_keys:
            self.assertIn(key, scores)
            self.assertIsInstance(scores[key], float)
            self.assertGreaterEqual(scores[key], 0.0)
            self.assertLessEqual(scores[key], 100.0)
    
    def test_get_current_metrics(self):
        """Testa obtenção de métricas atuais"""
        monitor = ComplianceMonitor()
        
        metrics = monitor.get_current_metrics()
        
        self.assertIsInstance(metrics, ComplianceMetrics)
        self.assertIsInstance(metrics.timestamp, datetime)
        self.assertIsInstance(metrics.overall_compliance_score, float)
        self.assertGreaterEqual(metrics.overall_compliance_score, 0.0)
        self.assertLessEqual(metrics.overall_compliance_score, 100.0)
    
    def test_threshold_checking(self):
        """Testa verificação de thresholds"""
        monitor = ComplianceMonitor()
        
        # Criar métricas com valores baixos para trigger de alertas
        metrics = ComplianceMetrics(
            timestamp=datetime.now(),
            gdpr_score=75.0,  # Abaixo do threshold de 90
            lgpd_score=85.0,  # Abaixo do threshold de 90
            soc2_score=80.0,  # Abaixo do threshold de 85
            iso27001_score=82.0,  # Abaixo do threshold de 85
            pci_dss_score=78.0,  # Abaixo do threshold de 85
            data_subject_requests_pending=10,  # Acima do threshold de 5
            breach_incidents_last_24h=1,  # Acima do threshold de 0
            consent_rate=99.2,
            audit_trail_coverage=100.0,
            data_retention_compliance=100.0,
            overall_compliance_score=80.0
        )
        
        alerts = monitor.check_thresholds(metrics)
        
        # Deve gerar alertas para scores baixos
        self.assertGreater(len(alerts), 0)
        
        # Verificar se alertas têm informações corretas
        for alert in alerts:
            self.assertIsInstance(alert, ComplianceAlert)
            self.assertIsNotNone(alert.id)
            self.assertIsInstance(alert.level, AlertLevel)
            self.assertIsInstance(alert.value, float)
            self.assertIsInstance(alert.threshold, float)
    
    def test_metrics_saving(self):
        """Testa salvamento de métricas"""
        monitor = ComplianceMonitor()
        
        metrics = monitor.get_current_metrics()
        initial_count = len(monitor.metrics_history)
        
        monitor.save_metrics(metrics)
        
        # Verificar se métrica foi adicionada ao histórico
        self.assertEqual(len(monitor.metrics_history), initial_count + 1)
        
        # Verificar se arquivo foi criado
        self.assertTrue(os.path.exists('data/compliance/metrics_history.json'))
    
    def test_alerts_saving(self):
        """Testa salvamento de alertas"""
        monitor = ComplianceMonitor()
        
        alert = ComplianceAlert(
            id="TEST_ALERT_001",
            metric=ComplianceMetric.GDPR_SCORE,
            level=AlertLevel.WARNING,
            message="Test alert",
            timestamp=datetime.now(),
            value=85.0,
            threshold=90.0,
            framework="GDPR"
        )
        
        initial_count = len(monitor.alerts)
        monitor.save_alerts([alert])
        
        # Verificar se alerta foi adicionado
        self.assertEqual(len(monitor.alerts), initial_count + 1)
        self.assertIn(alert.id, monitor.alerts)
        
        # Verificar se arquivo foi criado
        self.assertTrue(os.path.exists('data/compliance/alerts.json'))
    
    def test_dashboard_data_generation(self):
        """Testa geração de dados para dashboard"""
        monitor = ComplianceMonitor()
        
        # Adicionar algumas métricas ao histórico
        for index in range(5):
            metrics = monitor.get_current_metrics()
            monitor.save_metrics(metrics)
            time.sleep(0.1)  # Pequena pausa para timestamps diferentes
        
        dashboard_data = monitor.generate_dashboard_data()
        
        self.assertIsInstance(dashboard_data, dict)
        self.assertIn("timestamp", dashboard_data)
        self.assertIn("overall_score", dashboard_data)
        self.assertIn("framework_scores", dashboard_data)
        self.assertIn("operational_metrics", dashboard_data)
        self.assertIn("active_alerts", dashboard_data)
    
    def test_24h_trend_calculation(self):
        """Testa cálculo de tendência 24h"""
        monitor = ComplianceMonitor()
        
        # Adicionar métricas suficientes
        for index in range(30):
            metrics = monitor.get_current_metrics()
            monitor.save_metrics(metrics)
            time.sleep(0.1)
        
        trend_data = monitor.calculate_24h_trend()
        
        # Deve retornar dados de tendência
        self.assertIsInstance(trend_data, list)
        if trend_data:  # Se há dados suficientes
            self.assertIn("timestamp", trend_data[0])
            self.assertIn("overall_score", trend_data[0])
    
    def test_monitoring_start_stop(self):
        """Testa início e parada do monitoramento"""
        monitor = ComplianceMonitor()
        
        # Iniciar monitoramento
        monitor.start_monitoring(interval_seconds=1)
        self.assertTrue(monitor.monitoring_active)
        self.assertIsNotNone(monitor.monitor_thread)
        
        # Aguardar um pouco
        time.sleep(2)
        
        # Parar monitoramento
        monitor.stop_monitoring()
        self.assertFalse(monitor.monitoring_active)
    
    @patch('time.sleep')  # Mock sleep para acelerar testes
    def test_monitoring_loop(self, mock_sleep):
        """Testa loop de monitoramento"""
        monitor = ComplianceMonitor()
        
        # Configurar mock para não dormir
        mock_sleep.return_value = None
        
        # Iniciar monitoramento com intervalo curto
        monitor.start_monitoring(interval_seconds=0.1)
        
        # Aguardar um pouco para que o loop execute
        time.sleep(0.5)
        
        # Parar monitoramento
        monitor.stop_monitoring()
        
        # Verificar se métricas foram coletadas
        self.assertGreater(len(monitor.metrics_history), 0)
        
        # Verificar se arquivo de dashboard foi criado
        self.assertTrue(os.path.exists('data/compliance/dashboard.json'))

class TestComplianceMetrics(unittest.TestCase):
    """Testes para métricas de compliance"""
    
    def test_metrics_creation(self):
        """Testa criação de métricas"""
        metrics = ComplianceMetrics(
            timestamp=datetime.now(),
            gdpr_score=95.0,
            lgpd_score=92.0,
            soc2_score=88.0,
            iso27001_score=90.0,
            pci_dss_score=87.0,
            data_subject_requests_pending=2,
            breach_incidents_last_24h=0,
            consent_rate=99.5,
            audit_trail_coverage=100.0,
            data_retention_compliance=100.0,
            overall_compliance_score=92.4
        )
        
        self.assertIsInstance(metrics.timestamp, datetime)
        self.assertEqual(metrics.gdpr_score, 95.0)
        self.assertEqual(metrics.overall_compliance_score, 92.4)
        self.assertEqual(metrics.data_subject_requests_pending, 2)

class TestComplianceAlert(unittest.TestCase):
    """Testes para alertas de compliance"""
    
    def test_alert_creation(self):
        """Testa criação de alerta"""
        alert = ComplianceAlert(
            id="TEST_ALERT_001",
            metric=ComplianceMetric.GDPR_SCORE,
            level=AlertLevel.CRITICAL,
            message="GDPR score below threshold",
            timestamp=datetime.now(),
            value=75.0,
            threshold=90.0,
            framework="GDPR",
            action_required=True
        )
        
        self.assertEqual(alert.id, "TEST_ALERT_001")
        self.assertEqual(alert.metric, ComplianceMetric.GDPR_SCORE)
        self.assertEqual(alert.level, AlertLevel.CRITICAL)
        self.assertEqual(alert.value, 75.0)
        self.assertEqual(alert.threshold, 90.0)
        self.assertTrue(alert.action_required)
        self.assertFalse(alert.resolved)

class TestComplianceIntegration(unittest.TestCase):
    """Testes de integração do sistema de compliance"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/compliance', exist_ok=True)
        os.makedirs('logs/compliance', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_monitoring_workflow(self):
        """Testa workflow completo de monitoramento"""
        monitor = ComplianceMonitor()
        
        # 1. Coletar métricas
        metrics = monitor.get_current_metrics()
        monitor.save_metrics(metrics)
        
        # 2. Verificar alertas
        alerts = monitor.check_thresholds(metrics)
        if alerts:
            monitor.save_alerts(alerts)
        
        # 3. Gerar dashboard
        dashboard_data = monitor.generate_dashboard_data()
        
        # 4. Verificar se dados foram salvos
        self.assertTrue(os.path.exists('data/compliance/metrics_history.json'))
        if alerts:
            self.assertTrue(os.path.exists('data/compliance/alerts.json'))
        
        # 5. Verificar estrutura do dashboard
        self.assertIsInstance(dashboard_data, dict)
        self.assertIn("overall_score", dashboard_data)
    
    def test_alert_escalation(self):
        """Testa escalação de alertas"""
        monitor = ComplianceMonitor()
        
        # Criar alertas de diferentes níveis
        critical_alert = ComplianceAlert(
            id="CRITICAL_001",
            metric=ComplianceMetric.GDPR_SCORE,
            level=AlertLevel.CRITICAL,
            message="Critical GDPR issue",
            timestamp=datetime.now(),
            value=70.0,
            threshold=90.0,
            framework="GDPR"
        )
        
        warning_alert = ComplianceAlert(
            id="WARNING_001",
            metric=ComplianceMetric.LGPD_SCORE,
            level=AlertLevel.WARNING,
            message="LGPD warning",
            timestamp=datetime.now(),
            value=85.0,
            threshold=90.0,
            framework="LGPD"
        )
        
        monitor.save_alerts([critical_alert, warning_alert])
        
        # Verificar se alertas foram salvos
        self.assertEqual(len(monitor.alerts), 2)
        self.assertIn("CRITICAL_001", monitor.alerts)
        self.assertIn("WARNING_001", monitor.alerts)
        
        # Verificar níveis
        self.assertEqual(monitor.alerts["CRITICAL_001"].level, AlertLevel.CRITICAL)
        self.assertEqual(monitor.alerts["WARNING_001"].level, AlertLevel.WARNING)

if __name__ == "__main__":
    unittest.main() 