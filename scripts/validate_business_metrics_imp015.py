#!/usr/bin/env python3
"""
Script de Validação - Métricas de Negócio IMP-015
Tracing ID: IMP015_VALIDATION_001_20241227
Data: 2024-12-27
Status: Implementação Completa

Script de validação abrangente para o sistema de métricas de negócio:
- Validação de funcionalidades
- Testes de performance
- Verificação de integridade
- Análise de dados
- Relatório de validação
"""

import os
import sys
import json
import time
import tempfile
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
import traceback
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(levelname)string_data - %(message)string_data'
)
logger = logging.getLogger(__name__)

# Adicionar caminho para importar módulos
sys.path.append('infrastructure/analytics')

try:
    from business_metrics_dashboard_imp015 import (
        BusinessMetricsDashboard,
        BusinessMetric,
        DashboardWidget,
        AlertRule,
        AlertSeverity,
        get_business_dashboard,
        record_business_metric
    )
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

class BusinessMetricsValidator:
    """Validador para sistema de métricas de negócio"""
    
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "performance_metrics": {},
            "recommendations": []
        }
        
        # Criar banco de dados temporário para testes
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Inicializar dashboard para testes
        self.dashboard = BusinessMetricsDashboard(
            db_path=self.temp_db.name,
            enable_web_dashboard=False,
            enable_alerts=True
        )
    
    def __del__(self):
        """Limpeza ao destruir objeto"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def run_validation(self) -> Dict[str, Any]:
        """Executa validação completa"""
        logger.info("🚀 Iniciando validação do sistema de métricas de negócio IMP-015")
        
        try:
            # Executar todos os testes de validação
            self._test_dashboard_initialization()
            self._test_metric_recording()
            self._test_data_retrieval()
            self._test_alert_system()
            self._test_widget_functionality()
            self._test_export_functionality()
            self._test_performance()
            self._test_error_handling()
            self._test_data_integrity()
            self._test_integration()
            
            # Gerar resumo
            self._generate_summary()
            
            logger.info("✅ Validação concluída com sucesso")
            return self.validation_results
            
        except Exception as e:
            logger.error(f"❌ Erro durante validação: {e}")
            self.validation_results["error"] = str(e)
            return self.validation_results
    
    def _test_dashboard_initialization(self):
        """Testa inicialização do dashboard"""
        test_name = "dashboard_initialization"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Verificar se dashboard foi inicializado corretamente
            self.assertIsNotNone(self.dashboard, "Dashboard não foi inicializado")
            self.assertEqual(len(self.dashboard.widgets), 6, "Número incorreto de widgets")
            self.assertEqual(len(self.dashboard.alert_rules), 4, "Número incorreto de regras de alerta")
            
            # Verificar se banco de dados foi criado
            self.assertTrue(os.path.exists(self.temp_db.name), "Banco de dados não foi criado")
            
            # Verificar estrutura do banco
            with sqlite3.connect(self.temp_db.name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['business_metrics', 'dashboard_widgets']
                for table in required_tables:
                    self.assertIn(table, tables, f"Tabela {table} não encontrada")
            
            self._record_test_result(test_name, "PASSED", "Dashboard inicializado corretamente")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_metric_recording(self):
        """Testa registro de métricas"""
        test_name = "metric_recording"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Criar métricas de teste
            test_metrics = [
                BusinessMetric(
                    name="test_revenue",
                    value=15000.0,
                    unit="USD",
                    category="revenue",
                    timestamp=datetime.utcnow(),
                    trend="up",
                    change_percent=5.2
                ),
                BusinessMetric(
                    name="test_users",
                    value=1250,
                    unit="users",
                    category="users",
                    timestamp=datetime.utcnow(),
                    trend="stable",
                    change_percent=0.1
                )
            ]
            
            # Registrar métricas
            for metric in test_metrics:
                self.dashboard.record_metric(metric)
            
            # Verificar se foram salvas no cache
            for metric in test_metrics:
                self.assertIn(metric.name, self.dashboard.metrics_cache)
                self.assertGreater(len(self.dashboard.metrics_cache[metric.name]), 0)
            
            # Verificar se foram salvas no banco
            saved_metrics = self.dashboard.get_metrics()
            for metric in test_metrics:
                self.assertIn(metric.name, saved_metrics)
                self.assertGreater(len(saved_metrics[metric.name]), 0)
            
            self._record_test_result(test_name, "PASSED", f"Registradas {len(test_metrics)} métricas")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_data_retrieval(self):
        """Testa recuperação de dados"""
        test_name = "data_retrieval"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Registrar métrica de teste
            metric = BusinessMetric(
                name="test_retrieval",
                value=100.0,
                unit="test",
                category="test",
                timestamp=datetime.utcnow()
            )
            self.dashboard.record_metric(metric)
            
            # Testar recuperação por nome
            metrics_by_name = self.dashboard.get_metrics(metric_names=["test_retrieval"])
            self.assertIn("test_retrieval", metrics_by_name)
            
            # Testar recuperação por categoria
            metrics_by_category = self.dashboard.get_metrics(category="test")
            self.assertIn("test_retrieval", metrics_by_category)
            
            # Testar recuperação por período
            yesterday = datetime.utcnow() - timedelta(days=1)
            tomorrow = datetime.utcnow() + timedelta(days=1)
            metrics_by_period = self.dashboard.get_metrics(
                start_time=yesterday,
                end_time=tomorrow
            )
            self.assertIn("test_retrieval", metrics_by_period)
            
            self._record_test_result(test_name, "PASSED", "Recuperação de dados funcionando")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_alert_system(self):
        """Testa sistema de alertas"""
        test_name = "alert_system"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Registrar métrica que deve disparar alerta
            metric = BusinessMetric(
                name="daily_revenue",
                value=500.0,  # Abaixo do threshold de 1000
                unit="USD",
                category="revenue",
                timestamp=datetime.utcnow()
            )
            
            initial_alerts = len(self.dashboard.alert_history)
            self.dashboard.record_metric(metric)
            
            # Verificar se alerta foi criado
            self.assertGreater(len(self.dashboard.alert_history), initial_alerts)
            
            # Verificar se alerta tem dados corretos
            latest_alert = self.dashboard.alert_history[-1]
            self.assertEqual(latest_alert["metric_name"], "daily_revenue")
            self.assertEqual(latest_alert["severity"], "CRITICAL")
            
            self._record_test_result(test_name, "PASSED", "Sistema de alertas funcionando")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_widget_functionality(self):
        """Testa funcionalidade dos widgets"""
        test_name = "widget_functionality"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Registrar métricas para widgets
            test_metrics = [
                BusinessMetric(name="daily_revenue", value=15000.0, unit="USD", category="revenue", timestamp=datetime.utcnow()),
                BusinessMetric(name="keywords_processed", value=5000, unit="keywords", category="keywords", timestamp=datetime.utcnow()),
                BusinessMetric(name="active_users", value=1250, unit="users", category="users", timestamp=datetime.utcnow())
            ]
            
            for metric in test_metrics:
                self.dashboard.record_metric(metric)
            
            # Testar dados para diferentes tipos de widget
            widget_tests = [
                ("revenue_overview", "metric_card"),
                ("keyword_performance", "line_chart"),
                ("user_engagement", "bar_chart"),
                ("top_keywords", "table"),
                ("system_health", "gauge_chart")
            ]
            
            for widget_id, widget_type in widget_tests:
                data = self.dashboard.get_dashboard_data(widget_id)
                self.assertIsInstance(data, dict, f"Dados do widget {widget_id} não são dict")
                
                if widget_type == "metric_card":
                    self.assertIn("value", data, f"Widget {widget_id} não tem valor")
                elif widget_type == "table":
                    self.assertIn("headers", data, f"Widget {widget_id} não tem headers")
                    self.assertIn("data", data, f"Widget {widget_id} não tem dados")
            
            self._record_test_result(test_name, "PASSED", f"Testados {len(widget_tests)} widgets")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_export_functionality(self):
        """Testa funcionalidade de exportação"""
        test_name = "export_functionality"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Registrar métrica de teste
            metric = BusinessMetric(
                name="test_export",
                value=100.0,
                unit="test",
                category="test",
                timestamp=datetime.utcnow()
            )
            self.dashboard.record_metric(metric)
            
            # Testar exportação JSON
            json_data = self.dashboard.export_data(format_type="json")
            self.assertIsInstance(json_data, str)
            
            # Verificar se JSON é válido
            parsed_data = json.loads(json_data)
            self.assertIsInstance(parsed_data, dict)
            
            # Verificar se dados estão no JSON
            self.assertIn("test_export", parsed_data)
            
            self._record_test_result(test_name, "PASSED", "Exportação JSON funcionando")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_performance(self):
        """Testa performance do sistema"""
        test_name = "performance"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Teste de performance: registrar muitas métricas
            start_time = time.time()
            
            for index in range(100):
                metric = BusinessMetric(
                    name=f"perf_test_{index}",
                    value=float(index),
                    unit="test",
                    category="performance",
                    timestamp=datetime.utcnow()
                )
                self.dashboard.record_metric(metric)
            
            record_time = time.time() - start_time
            
            # Teste de performance: recuperar métricas
            start_time = time.time()
            metrics = self.dashboard.get_metrics()
            retrieve_time = time.time() - start_time
            
            # Armazenar métricas de performance
            self.validation_results["performance_metrics"] = {
                "record_100_metrics_seconds": record_time,
                "retrieve_all_metrics_seconds": retrieve_time,
                "metrics_per_second": 100 / record_time if record_time > 0 else 0
            }
            
            # Verificar se performance está aceitável
            self.assertLess(record_time, 5.0, f"Registro muito lento: {record_time}string_data")
            self.assertLess(retrieve_time, 2.0, f"Recuperação muito lenta: {retrieve_time}string_data")
            
            self._record_test_result(test_name, "PASSED", 
                                   f"Performance OK - Registro: {record_time:.2f}string_data, Recuperação: {retrieve_time:.2f}string_data")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_error_handling(self):
        """Testa tratamento de erros"""
        test_name = "error_handling"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Testar métrica com nome inválido
            metrics = self.dashboard.get_metrics(metric_names=["invalid_metric"])
            self.assertEqual(len(metrics), 0, "Métrica inválida deveria retornar vazio")
            
            # Testar widget inválido
            data = self.dashboard.get_dashboard_data("invalid_widget")
            self.assertEqual(data, {}, "Widget inválido deveria retornar vazio")
            
            # Testar exportação com formato inválido
            export_result = self.dashboard.export_data(format_type="invalid_format")
            self.assertIn("Formato não suportado", export_result)
            
            self._record_test_result(test_name, "PASSED", "Tratamento de erros funcionando")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_data_integrity(self):
        """Testa integridade dos dados"""
        test_name = "data_integrity"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Registrar métrica com dados específicos
            original_metric = BusinessMetric(
                name="integrity_test",
                value=123.45,
                unit="test",
                category="test",
                timestamp=datetime.utcnow(),
                trend="up",
                change_percent=10.5,
                metadata={"key": "value"}
            )
            
            self.dashboard.record_metric(original_metric)
            
            # Recuperar e verificar integridade
            saved_metrics = self.dashboard.get_metrics(metric_names=["integrity_test"])
            self.assertIn("integrity_test", saved_metrics)
            
            saved_metric = saved_metrics["integrity_test"][0]
            
            # Verificar se todos os campos foram preservados
            self.assertEqual(saved_metric.name, original_metric.name)
            self.assertEqual(saved_metric.value, original_metric.value)
            self.assertEqual(saved_metric.unit, original_metric.unit)
            self.assertEqual(saved_metric.category, original_metric.category)
            self.assertEqual(saved_metric.trend, original_metric.trend)
            self.assertEqual(saved_metric.change_percent, original_metric.change_percent)
            self.assertEqual(saved_metric.metadata, original_metric.metadata)
            
            self._record_test_result(test_name, "PASSED", "Integridade dos dados preservada")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _test_integration(self):
        """Testa integração com outros componentes"""
        test_name = "integration"
        logger.info(f"🔧 Testando: {test_name}")
        
        try:
            # Testar função de conveniência
            record_business_metric(
                name="integration_test",
                value=100.0,
                unit="test",
                category="test"
            )
            
            # Verificar se métrica foi registrada
            metrics = self.dashboard.get_metrics(metric_names=["integration_test"])
            self.assertIn("integration_test", metrics)
            
            # Testar padrão singleton
            dashboard1 = get_business_dashboard()
            dashboard2 = get_business_dashboard()
            self.assertIs(dashboard1, dashboard2, "Padrão singleton não funcionando")
            
            self._record_test_result(test_name, "PASSED", "Integração funcionando")
            
        except Exception as e:
            self._record_test_result(test_name, "FAILED", str(e))
    
    def _record_test_result(self, test_name: str, status: str, message: str):
        """Registra resultado de teste"""
        self.validation_results["tests"][test_name] = {
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if status == "PASSED":
            self.validation_results["summary"]["passed"] += 1
            logger.info(f"✅ {test_name}: {message}")
        elif status == "FAILED":
            self.validation_results["summary"]["failed"] += 1
            logger.error(f"❌ {test_name}: {message}")
        else:
            self.validation_results["summary"]["warnings"] += 1
            logger.warning(f"⚠️ {test_name}: {message}")
        
        self.validation_results["summary"]["total_tests"] += 1
    
    def _generate_summary(self):
        """Gera resumo da validação"""
        summary = self.validation_results["summary"]
        
        # Calcular percentual de sucesso
        success_rate = (summary["passed"] / summary["total_tests"]) * 100 if summary["total_tests"] > 0 else 0
        
        # Adicionar recomendações baseadas nos resultados
        if summary["failed"] > 0:
            self.validation_results["recommendations"].append(
                "Corrigir testes que falharam antes de prosseguir"
            )
        
        if success_rate < 90:
            self.validation_results["recommendations"].append(
                "Investigar e corrigir problemas de qualidade"
            )
        
        # Verificar performance
        perf_metrics = self.validation_results.get("performance_metrics", {})
        if perf_metrics.get("record_100_metrics_seconds", 0) > 3.0:
            self.validation_results["recommendations"].append(
                "Otimizar performance de registro de métricas"
            )
        
        logger.info(f"📊 Resumo da validação:")
        logger.info(f"   Total de testes: {summary['total_tests']}")
        logger.info(f"   Aprovados: {summary['passed']}")
        logger.info(f"   Falharam: {summary['failed']}")
        logger.info(f"   Avisos: {summary['warnings']}")
        logger.info(f"   Taxa de sucesso: {success_rate:.1f}%")
    
    def assertIsNotNone(self, obj, message=""):
        """Assert personalizado"""
        if obj is None:
            raise AssertionError(message or "Objeto é None")
    
    def assertEqual(self, a, b, message=""):
        """Assert personalizado"""
        if a != b:
            raise AssertionError(f"{message} - Esperado: {b}, Obtido: {a}")
    
    def assertIn(self, item, container, message=""):
        """Assert personalizado"""
        if item not in container:
            raise AssertionError(f"{message} - {item} não está em {container}")
    
    def assertGreater(self, a, b, message=""):
        """Assert personalizado"""
        if not a > b:
            raise AssertionError(f"{message} - {a} não é maior que {b}")
    
    def assertLess(self, a, b, message=""):
        """Assert personalizado"""
        if not a < b:
            raise AssertionError(f"{message} - {a} não é menor que {b}")
    
    def assertIsInstance(self, obj, cls, message=""):
        """Assert personalizado"""
        if not isinstance(obj, cls):
            raise AssertionError(f"{message} - {obj} não é instância de {cls}")
    
    def assertTrue(self, condition, message=""):
        """Assert personalizado"""
        if not condition:
            raise AssertionError(message or "Condição é falsa")
    
    def assertIs(self, a, b, message=""):
        """Assert personalizado"""
        if a is not b:
            raise AssertionError(f"{message} - {a} não é {b}")

def main():
    """Função principal"""
    print("🚀 Validador de Métricas de Negócio IMP-015")
    print("=" * 50)
    
    # Executar validação
    validator = BusinessMetricsValidator()
    results = validator.run_validation()
    
    # Salvar resultados
    output_file = f"validation_results_imp015_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Resultados salvos em: {output_file}")
    
    # Exibir resumo
    summary = results["summary"]
    success_rate = (summary["passed"] / summary["total_tests"]) * 100 if summary["total_tests"] > 0 else 0
    
    print(f"\n📊 RESUMO DA VALIDAÇÃO:")
    print(f"   ✅ Aprovados: {summary['passed']}")
    print(f"   ❌ Falharam: {summary['failed']}")
    print(f"   ⚠️ Avisos: {summary['warnings']}")
    print(f"   📈 Taxa de sucesso: {success_rate:.1f}%")
    
    # Exibir recomendações
    if results.get("recommendations"):
        print(f"\n💡 RECOMENDAÇÕES:")
        for index, rec in enumerate(results["recommendations"], 1):
            print(f"   {index}. {rec}")
    
    # Status final
    if summary["failed"] == 0 and success_rate >= 90:
        print(f"\n🎉 VALIDAÇÃO APROVADA! Sistema pronto para produção.")
        return 0
    else:
        print(f"\n⚠️ VALIDAÇÃO COM PROBLEMAS. Verificar recomendações.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 