from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de SLA Compliance Checker - Omni Keywords Finder
Tracing ID: TEST_OBS_003_20241219_001
Data: 2024-12-19
Versão: 1.0

Testa funcionalidades de:
- Registro de métricas de SLA
- Geração de alertas automáticos
- Relatórios de compliance
- Integração com Grafana
- Violações de SLA
- Recomendações automáticas
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sqlite3

from scripts.monitoring.sla_checker import (
    SLAChecker, SLAStatus, SLAViolationType, 
    SLAMetric, SLAViolation, SLAReport
)


class TestSLAChecker:
    """Testes para a classe SLAChecker."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        # Criar arquivo temporário para banco de dados
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.sla_checker = SLAChecker(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Remover arquivo temporário
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_init_database(self):
        """Testa inicialização do banco de dados."""
        # Verificar se as tabelas foram criadas
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            
            # Verificar tabela de métricas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sla_metrics'")
            assert cursor.fetchone() is not None
            
            # Verificar tabela de violações
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sla_violations'")
            assert cursor.fetchone() is not None
            
            # Verificar tabela de alertas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sla_alerts'")
            assert cursor.fetchone() is not None
    
    def test_record_metric_compliant(self):
        """Testa registro de métrica dentro do SLA."""
        # Registrar métrica que está dentro do limite
        self.sla_checker.record_metric("google_trends", "response_time", 1.5, "seconds")
        
        # Verificar se foi salva no banco
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sla_metrics WHERE integration_name = 'google_trends'")
            result = cursor.fetchone()
            
            assert result is not None
            assert result[1] == "google_trends"  # integration_name
            assert result[2] == "response_time"  # metric_type
            assert result[3] == 1.5  # current_value
            assert result[4] == 2.0  # threshold (do config)
            assert result[7] == SLAStatus.COMPLIANT.value  # status
    
    def test_record_metric_violated(self):
        """Testa registro de métrica que viola SLA."""
        # Registrar métrica que viola o limite
        self.sla_checker.record_metric("google_trends", "response_time", 3.0, "seconds")
        
        # Verificar se foi salva como violação
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sla_metrics WHERE integration_name = 'google_trends'")
            result = cursor.fetchone()
            
            assert result is not None
            assert result[7] == SLAStatus.VIOLATED.value  # status
            assert result[8] == SLAViolationType.RESPONSE_TIME.value  # violation_type
    
    def test_record_metric_warning(self):
        """Testa registro de métrica em warning."""
        # Registrar métrica que está em warning (80% do limite)
        self.sla_checker.record_metric("google_trends", "response_time", 1.6, "seconds")
        
        # Verificar se foi salva como warning
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sla_metrics WHERE integration_name = 'google_trends'")
            result = cursor.fetchone()
            
            assert result is not None
            assert result[7] == SLAStatus.WARNING.value  # status
    
    def test_record_metric_availability(self):
        """Testa registro de métrica de disponibilidade."""
        # Para disponibilidade, valor maior é melhor
        self.sla_checker.record_metric("google_trends", "availability", 99.8, "percentage")
        
        # Verificar se foi salva como compliant
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sla_metrics WHERE metric_type = 'availability'")
            result = cursor.fetchone()
            
            assert result is not None
            assert result[7] == SLAStatus.COMPLIANT.value  # status
    
    def test_record_metric_unknown_integration(self):
        """Testa registro de métrica para integração desconhecida."""
        # Registrar métrica para integração não configurada
        self.sla_checker.record_metric("unknown_integration", "response_time", 1.0, "seconds")
        
        # Verificar se não foi salva
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sla_metrics WHERE integration_name = 'unknown_integration'")
            result = cursor.fetchone()
            
            assert result is None
    
    def test_record_metric_unknown_type(self):
        """Testa registro de métrica com tipo desconhecido."""
        # Registrar métrica com tipo não configurado
        self.sla_checker.record_metric("google_trends", "unknown_metric", 1.0, "seconds")
        
        # Verificar se não foi salva
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sla_metrics WHERE metric_type = 'unknown_metric'")
            result = cursor.fetchone()
            
            assert result is None
    
    def test_alert_generation(self):
        """Testa geração de alertas."""
        # Registrar métrica que viola SLA
        self.sla_checker.record_metric("google_trends", "response_time", 3.0, "seconds")
        
        # Verificar se alerta foi gerado
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sla_alerts WHERE integration_name = 'google_trends'")
            result = cursor.fetchone()
            
            assert result is not None
            assert result[1] == "google_trends"  # integration_name
            assert result[2] == "response_time"  # alert_type
            assert "CRITICAL" in result[4]  # severity
            assert "3.0" in result[3]  # message contains value
    
    def test_alert_cooldown(self):
        """Testa cooldown de alertas."""
        # Registrar primeira métrica que viola SLA
        self.sla_checker.record_metric("google_trends", "response_time", 3.0, "seconds")
        
        # Registrar segunda métrica imediatamente
        self.sla_checker.record_metric("google_trends", "response_time", 3.5, "seconds")
        
        # Verificar se apenas um alerta foi gerado (devido ao cooldown)
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sla_alerts WHERE integration_name = 'google_trends'")
            count = cursor.fetchone()[0]
            
            assert count == 1  # Apenas um alerta devido ao cooldown
    
    def test_violation_recording(self):
        """Testa registro de violações."""
        # Registrar métrica que viola SLA
        self.sla_checker.record_metric("google_trends", "response_time", 3.0, "seconds")
        
        # Verificar se violação foi registrada
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sla_violations WHERE integration_name = 'google_trends'")
            result = cursor.fetchone()
            
            assert result is not None
            assert result[1] == "google_trends"  # integration_name
            assert result[2] == SLAViolationType.RESPONSE_TIME.value  # violation_type
            assert result[3] == 3.0  # current_value
            assert result[4] == 2.0  # threshold
            assert result[7] == "MEDIUM"  # severity
    
    def test_get_sla_report_no_data(self):
        """Testa geração de relatório sem dados."""
        # Tentar gerar relatório para integração sem dados
        report = self.sla_checker.get_sla_report("google_trends")
        
        assert report is None
    
    def test_get_sla_report_with_data(self):
        """Testa geração de relatório com dados."""
        # Registrar várias métricas
        self.sla_checker.record_metric("google_trends", "response_time", 1.5, "seconds")
        self.sla_checker.record_metric("google_trends", "response_time", 2.5, "seconds")  # Violação
        self.sla_checker.record_metric("google_trends", "availability", 99.8, "percentage")
        self.sla_checker.record_metric("google_trends", "error_rate", 0.5, "percentage")
        
        # Gerar relatório
        report = self.sla_checker.get_sla_report("google_trends")
        
        assert report is not None
        assert report.integration_name == "google_trends"
        assert report.avg_response_time == 2.0  # (1.5 + 2.5) / 2
        assert report.uptime_percentage == 99.8
        assert report.error_rate == 0.5
        assert report.violations_count == 1
        assert report.status == SLAStatus.WARNING  # 75% compliance (3/4 compliant)
        assert len(report.recommendations) > 0
    
    def test_get_active_violations(self):
        """Testa busca de violações ativas."""
        # Registrar métricas com violações
        self.sla_checker.record_metric("google_trends", "response_time", 3.0, "seconds")
        self.sla_checker.record_metric("amazon_api", "response_time", 4.0, "seconds")
        
        # Buscar violações ativas
        violations = self.sla_checker.get_active_violations()
        
        assert len(violations) == 2
        assert violations[0].integration_name in ["google_trends", "amazon_api"]
        assert violations[1].integration_name in ["google_trends", "amazon_api"]
    
    def test_get_active_violations_by_integration(self):
        """Testa busca de violações ativas por integração."""
        # Registrar métricas com violações
        self.sla_checker.record_metric("google_trends", "response_time", 3.0, "seconds")
        self.sla_checker.record_metric("amazon_api", "response_time", 4.0, "seconds")
        
        # Buscar violações apenas para google_trends
        violations = self.sla_checker.get_active_violations("google_trends")
        
        assert len(violations) == 1
        assert violations[0].integration_name == "google_trends"
    
    def test_get_grafana_metrics(self):
        """Testa geração de métricas para Grafana."""
        # Registrar várias métricas
        self.sla_checker.record_metric("google_trends", "response_time", 1.5, "seconds")
        self.sla_checker.record_metric("google_trends", "response_time", 2.0, "seconds")
        self.sla_checker.record_metric("google_trends", "availability", 99.8, "percentage")
        
        # Gerar métricas Grafana
        grafana_metrics = self.sla_checker.get_grafana_metrics("google_trends")
        
        assert grafana_metrics["integration"] == "google_trends"
        assert "response_time" in grafana_metrics["metrics"]
        assert "availability" in grafana_metrics["metrics"]
        
        # Verificar estatísticas
        response_time_metrics = grafana_metrics["metrics"]["response_time"]
        assert response_time_metrics["average"] == 1.75  # (1.5 + 2.0) / 2
        assert response_time_metrics["minimum"] == 1.5
        assert response_time_metrics["maximum"] == 2.0
        assert response_time_metrics["count"] == 2
    
    def test_export_compliance_report(self):
        """Testa exportação de relatório de compliance."""
        # Registrar métricas para várias integrações
        self.sla_checker.record_metric("google_trends", "response_time", 1.5, "seconds")
        self.sla_checker.record_metric("amazon_api", "response_time", 4.0, "seconds")  # Violação
        
        # Exportar relatório
        temp_report = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_report.close()
        
        try:
            self.sla_checker.export_compliance_report(temp_report.name)
            
            # Verificar se arquivo foi criado
            assert os.path.exists(temp_report.name)
            
            # Verificar conteúdo
            with open(temp_report.name, 'r') as f:
                report_data = json.load(f)
            
            assert "generated_at" in report_data
            assert "integrations" in report_data
            assert "google_trends" in report_data["integrations"]
            assert "amazon_api" in report_data["integrations"]
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_report.name):
                os.unlink(temp_report.name)
    
    def test_recommendations_generation(self):
        """Testa geração de recomendações."""
        # Registrar métricas com diferentes tipos de violações
        self.sla_checker.record_metric("google_trends", "response_time", 3.0, "seconds")
        self.sla_checker.record_metric("google_trends", "availability", 95.0, "percentage")
        self.sla_checker.record_metric("google_trends", "error_rate", 3.0, "percentage")
        
        # Gerar relatório
        report = self.sla_checker.get_sla_report("google_trends")
        
        assert report is not None
        assert len(report.recommendations) > 0
        
        # Verificar se recomendações específicas foram geradas
        recommendations_text = " ".join(report.recommendations).lower()
        assert "performance" in recommendations_text or "otimizar" in recommendations_text
        assert "circuit breaker" in recommendations_text or "fallbacks" in recommendations_text
        assert "erros" in recommendations_text or "retry" in recommendations_text
    
    def test_severity_calculation(self):
        """Testa cálculo de severidade de violações."""
        # Violação leve (1.5x threshold)
        self.sla_checker.record_metric("google_trends", "response_time", 3.0, "seconds")
        
        # Violação crítica (2.5x threshold)
        self.sla_checker.record_metric("amazon_api", "response_time", 7.5, "seconds")
        
        # Verificar severidades
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            
            # Verificar violação leve
            cursor.execute("SELECT severity FROM sla_violations WHERE integration_name = 'google_trends'")
            severity_light = cursor.fetchone()[0]
            assert severity_light == "MEDIUM"
            
            # Verificar violação crítica
            cursor.execute("SELECT severity FROM sla_violations WHERE integration_name = 'amazon_api'")
            severity_critical = cursor.fetchone()[0]
            assert severity_critical == "CRITICAL"


class TestSLACheckerIntegration:
    """Testes de integração para SLAChecker."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.sla_checker = SLAChecker(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_full_sla_monitoring_cycle(self):
        """Testa ciclo completo de monitoramento de SLA."""
        # Simular monitoramento contínuo
        metrics_data = [
            ("google_trends", "response_time", 1.5, "seconds"),
            ("google_trends", "availability", 99.8, "percentage"),
            ("google_trends", "error_rate", 0.5, "percentage"),
            ("amazon_api", "response_time", 4.0, "seconds"),  # Violação
            ("amazon_api", "availability", 98.5, "percentage"),  # Violação
            ("webhook_system", "response_time", 0.8, "seconds"),
            ("webhook_system", "availability", 99.9, "percentage")
        ]
        
        # Registrar todas as métricas
        for integration, metric_type, value, unit in metrics_data:
            self.sla_checker.record_metric(integration, metric_type, value, unit)
        
        # Verificar métricas registradas
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sla_metrics")
            metrics_count = cursor.fetchone()[0]
            assert metrics_count == len(metrics_data)
        
        # Verificar violações
        violations = self.sla_checker.get_active_violations()
        assert len(violations) == 2  # amazon_api tem 2 violações
        
        # Verificar alertas
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sla_alerts")
            alerts_count = cursor.fetchone()[0]
            assert alerts_count == 2  # 2 alertas para amazon_api
        
        # Gerar relatórios
        google_report = self.sla_checker.get_sla_report("google_trends")
        amazon_report = self.sla_checker.get_sla_report("amazon_api")
        webhook_report = self.sla_checker.get_sla_report("webhook_system")
        
        assert google_report is not None
        assert amazon_report is not None
        assert webhook_report is not None
        
        # Verificar status dos relatórios
        assert google_report.status == SLAStatus.COMPLIANT
        assert amazon_report.status == SLAStatus.VIOLATED
        assert webhook_report.status == SLAStatus.COMPLIANT
        
        # Gerar métricas Grafana
        grafana_metrics = self.sla_checker.get_grafana_metrics("amazon_api")
        assert grafana_metrics["integration"] == "amazon_api"
        assert "response_time" in grafana_metrics["metrics"]
        assert "availability" in grafana_metrics["metrics"]
    
    def test_sla_configs_comprehensive(self):
        """Testa configurações de SLA para todas as integrações."""
        # Testar todas as integrações configuradas
        for integration_name, config in self.sla_checker.sla_configs.items():
            # Testar response_time
            threshold = config["response_time_threshold"]
            
            # Testar valor dentro do limite
            self.sla_checker.record_metric(integration_name, "response_time", threshold * 0.5, "seconds")
            
            # Testar valor que viola
            self.sla_checker.record_metric(integration_name, "response_time", threshold * 1.5, "seconds")
            
            # Verificar se métricas foram registradas
            with sqlite3.connect(self.temp_db.name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM sla_metrics 
                    WHERE integration_name = ? AND metric_type = 'response_time'
                """, (integration_name,))
                count = cursor.fetchone()[0]
                assert count == 2  # Duas métricas registradas


if __name__ == '__main__':
    pytest.main([__file__]) 