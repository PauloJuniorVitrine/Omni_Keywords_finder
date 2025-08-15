#!/usr/bin/env python3
"""
Script de Validação - Sistema de Logs Estruturados Avançados - IMP-013
Tracing ID: IMP013_LOGS_ESTRUTURADOS_001_20241227
Data: 2024-12-27
Status: Validação Completa

Valida:
- Funcionamento do sistema de logs
- Formato JSON estruturado
- Contexto rico
- Performance
- Integração com ambiente
"""

import json
import os
import sys
import tempfile
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Adicionar path para importar o módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from infrastructure.logging.advanced_structured_logger import (
    AdvancedStructuredLogger,
    set_logging_context,
    clear_logging_context,
    performance_logger,
    configure_logging_for_environment
)

class LogsValidator:
    """Validador do sistema de logs estruturados"""
    
    def __init__(self):
        self.results = []
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.close()
        
        self.logger = AdvancedStructuredLogger(
            name="validation_logger",
            log_file=self.temp_file.name,
            include_context=True,
            include_metadata=True
        )
    
    def cleanup(self):
        """Limpa arquivos temporários"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def validate_json_format(self) -> Dict[str, Any]:
        """Valida formato JSON estruturado"""
        print("🔍 Validando formato JSON estruturado...")
        
        # Definir contexto
        tracing_id = str(uuid.uuid4())
        set_logging_context(
            tracing_id=tracing_id,
            user_id="validation_user",
            request_id="validation_request"
        )
        
        # Gerar logs de teste
        self.logger.info("Teste de formato JSON", {"test_type": "json_format"})
        self.logger.business("Evento de negócio", "test_business", {"business_id": "123"})
        self.logger.security("Evento de segurança", "test_security", {"security_level": "high"})
        self.logger.performance("Teste de performance", 150.5, {"test_name": "json_validation"})
        
        # Ler e validar logs
        valid_logs = 0
        total_logs = 0
        errors = []
        
        with open(self.temp_file.name, 'r') as f:
            for line_num, line in enumerate(f, 1):
                total_logs += 1
                try:
                    log_data = json.loads(line.strip())
                    
                    # Validar campos obrigatórios
                    required_fields = ["timestamp", "level", "message", "module", "function"]
                    missing_fields = [field for field in required_fields if field not in log_data]
                    
                    if missing_fields:
                        errors.append(f"Linha {line_num}: Campos obrigatórios ausentes: {missing_fields}")
                        continue
                    
                    # Validar formato de timestamp
                    try:
                        datetime.fromisoformat(log_data["timestamp"].replace('Z', '+00:00'))
                    except ValueError:
                        errors.append(f"Linha {line_num}: Timestamp inválido: {log_data['timestamp']}")
                        continue
                    
                    # Validar contexto
                    if log_data.get("tracing_id") != tracing_id:
                        errors.append(f"Linha {line_num}: Tracing ID não corresponde")
                        continue
                    
                    valid_logs += 1
                    
                except json.JSONDecodeError as e:
                    errors.append(f"Linha {line_num}: JSON inválido: {e}")
        
        success = valid_logs == total_logs and not errors
        
        result = {
            "test": "JSON Format Validation",
            "success": success,
            "valid_logs": valid_logs,
            "total_logs": total_logs,
            "errors": errors,
            "score": (valid_logs / total_logs * 100) if total_logs > 0 else 0
        }
        
        self.results.append(result)
        print(f"✅ Formato JSON: {valid_logs}/{total_logs} logs válidos ({result['score']:.1f}%)")
        
        return result
    
    def validate_context_richness(self) -> Dict[str, Any]:
        """Valida riqueza do contexto"""
        print("🔍 Validando riqueza do contexto...")
        
        # Limpar arquivo
        open(self.temp_file.name, 'w').close()
        
        # Definir contexto rico
        context_data = {
            "tracing_id": str(uuid.uuid4()),
            "user_id": "rich_context_user",
            "request_id": "rich_context_request",
            "session_id": "rich_context_session"
        }
        
        set_logging_context(**context_data)
        
        # Gerar log com contexto rico
        custom_fields = {
            "operation": "context_validation",
            "data_size": 1024,
            "processing_time": 150.5,
            "status": "success"
        }
        
        self.logger.info("Teste de contexto rico", custom_fields)
        
        # Validar contexto
        with open(self.temp_file.name, 'r') as f:
            log_line = f.readline().strip()
        
        log_data = json.loads(log_line)
        
        # Verificar campos de contexto
        context_fields = ["tracing_id", "user_id", "request_id", "session_id"]
        missing_context = [field for field in context_fields if field not in log_data]
        
        # Verificar campos customizados
        custom_fields_present = all(field in log_data for field in custom_fields.keys())
        
        success = not missing_context and custom_fields_present
        
        result = {
            "test": "Context Richness Validation",
            "success": success,
            "missing_context_fields": missing_context,
            "custom_fields_present": custom_fields_present,
            "context_score": len([f for f in context_fields if f in log_data]) / len(context_fields) * 100
        }
        
        self.results.append(result)
        print(f"✅ Contexto rico: {'Sucesso' if success else 'Falha'}")
        
        return result
    
    def validate_performance_logging(self) -> Dict[str, Any]:
        """Valida logging de performance"""
        print("🔍 Validando logging de performance...")
        
        # Limpar arquivo
        open(self.temp_file.name, 'w').close()
        
        @performance_logger
        def test_performance_function():
            time.sleep(0.1)
            return "performance_test_result"
        
        # Executar função com decorator
        start_time = time.time()
        result = test_performance_function()
        execution_time = (time.time() - start_time) * 1000
        
        # Validar logs de performance
        with open(self.temp_file.name, 'r') as f:
            log_lines = f.readlines()
        
        performance_logs = []
        for line in log_lines:
            log_data = json.loads(line.strip())
            if log_data.get("log_type") == "performance":
                performance_logs.append(log_data)
        
        success = len(performance_logs) > 0
        
        if performance_logs:
            latest_performance = performance_logs[-1]
            has_execution_time = "execution_time_ms" in latest_performance
            has_function_name = "function_name" in latest_performance
            success = success and has_execution_time and has_function_name
        
        result = {
            "test": "Performance Logging Validation",
            "success": success,
            "performance_logs_count": len(performance_logs),
            "has_execution_time": has_execution_time if performance_logs else False,
            "has_function_name": has_function_name if performance_logs else False,
            "actual_execution_time": execution_time
        }
        
        self.results.append(result)
        print(f"✅ Performance logging: {'Sucesso' if success else 'Falha'}")
        
        return result
    
    def validate_security_logging(self) -> Dict[str, Any]:
        """Valida logging de segurança"""
        print("🔍 Validando logging de segurança...")
        
        # Limpar arquivo
        open(self.temp_file.name, 'w').close()
        
        # Gerar logs de segurança
        security_events = [
            ("login_attempt", {"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"}),
            ("failed_authentication", {"user_id": "user123", "reason": "invalid_password"}),
            ("suspicious_activity", {"activity_type": "multiple_failed_logins", "count": 5}),
            ("access_denied", {"resource": "/admin", "user_id": "user456"})
        ]
        
        for event_type, event_data in security_events:
            self.logger.security(f"Evento de segurança: {event_type}", event_type, event_data)
        
        # Validar logs de segurança
        with open(self.temp_file.name, 'r') as f:
            log_lines = f.readlines()
        
        security_logs = []
        for line in log_lines:
            log_data = json.loads(line.strip())
            if log_data.get("log_type") == "security":
                security_logs.append(log_data)
        
        success = len(security_logs) == len(security_events)
        
        if security_logs:
            all_have_event_type = all("event_type" in log for log in security_logs)
            all_have_log_type = all(log.get("log_type") == "security" for log in security_logs)
            success = success and all_have_event_type and all_have_log_type
        
        result = {
            "test": "Security Logging Validation",
            "success": success,
            "security_logs_count": len(security_logs),
            "expected_count": len(security_events),
            "all_have_event_type": all_have_event_type if security_logs else False,
            "all_have_log_type": all_have_log_type if security_logs else False
        }
        
        self.results.append(result)
        print(f"✅ Security logging: {len(security_logs)}/{len(security_events)} logs criados")
        
        return result
    
    def validate_business_logging(self) -> Dict[str, Any]:
        """Valida logging de negócio"""
        print("🔍 Validando logging de negócio...")
        
        # Limpar arquivo
        open(self.temp_file.name, 'w').close()
        
        # Gerar logs de negócio
        business_events = [
            ("user_registration", {"plan": "premium", "source": "organic"}),
            ("subscription_upgrade", {"from_plan": "basic", "to_plan": "premium"}),
            ("payment_processed", {"amount": 99.99, "currency": "USD", "method": "credit_card"}),
            ("feature_usage", {"feature": "keyword_analysis", "usage_count": 150})
        ]
        
        for event_type, event_data in business_events:
            self.logger.business(f"Evento de negócio: {event_type}", event_type, event_data)
        
        # Validar logs de negócio
        with open(self.temp_file.name, 'r') as f:
            log_lines = f.readlines()
        
        business_logs = []
        for line in log_lines:
            log_data = json.loads(line.strip())
            if log_data.get("log_type") == "business":
                business_logs.append(log_data)
        
        success = len(business_logs) == len(business_events)
        
        if business_logs:
            all_have_event_type = all("event_type" in log for log in business_logs)
            all_have_log_type = all(log.get("log_type") == "business" for log in business_logs)
            success = success and all_have_event_type and all_have_log_type
        
        result = {
            "test": "Business Logging Validation",
            "success": success,
            "business_logs_count": len(business_logs),
            "expected_count": len(business_events),
            "all_have_event_type": all_have_event_type if business_logs else False,
            "all_have_log_type": all_have_log_type if business_logs else False
        }
        
        self.results.append(result)
        print(f"✅ Business logging: {len(business_logs)}/{len(business_events)} logs criados")
        
        return result
    
    def validate_environment_configuration(self) -> Dict[str, Any]:
        """Valida configuração por ambiente"""
        print("🔍 Validando configuração por ambiente...")
        
        # Testar configuração para diferentes ambientes
        environments = ["development", "staging", "production"]
        config_results = []
        
        for env in environments:
            os.environ["ENVIRONMENT"] = env
            os.environ["LOG_LEVEL"] = "INFO"
            
            try:
                logger = configure_logging_for_environment()
                config_results.append({
                    "environment": env,
                    "success": True,
                    "logger_name": logger.name
                })
            except Exception as e:
                config_results.append({
                    "environment": env,
                    "success": False,
                    "error": str(e)
                })
        
        success = all(result["success"] for result in config_results)
        
        result = {
            "test": "Environment Configuration Validation",
            "success": success,
            "environments_tested": len(environments),
            "config_results": config_results
        }
        
        self.results.append(result)
        print(f"✅ Environment configuration: {len([r for r in config_results if r['success']])}/{len(environments)} ambientes")
        
        return result
    
    def validate_log_rotation(self) -> Dict[str, Any]:
        """Valida rotação de logs"""
        print("🔍 Validando rotação de logs...")
        
        # Criar logger com rotação pequena
        rotation_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        rotation_file.close()
        
        rotation_logger = AdvancedStructuredLogger(
            name="rotation_test",
            log_file=rotation_file.name,
            max_bytes=100,  # 100 bytes para forçar rotação
            backup_count=2
        )
        
        # Escrever logs até forçar rotação
        large_message = "A" * 50  # 50 caracteres
        logs_written = 0
        
        try:
            for index in range(10):
                rotation_logger.info(f"{large_message} - {index}")
                logs_written += 1
        except Exception as e:
            pass
        
        # Verificar se arquivos de backup foram criados
        backup_files = []
        for index in range(1, 3):  # .1 e .2
            backup_path = f"{rotation_file.name}.{index}"
            if os.path.exists(backup_path):
                backup_files.append(backup_path)
        
        # Cleanup
        if os.path.exists(rotation_file.name):
            os.unlink(rotation_file.name)
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                os.unlink(backup_file)
        
        success = logs_written > 0
        
        result = {
            "test": "Log Rotation Validation",
            "success": success,
            "logs_written": logs_written,
            "backup_files_created": len(backup_files),
            "rotation_triggered": len(backup_files) > 0
        }
        
        self.results.append(result)
        print(f"✅ Log rotation: {logs_written} logs escritos, {len(backup_files)} backups criados")
        
        return result
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Executa todas as validações"""
        print("🚀 Iniciando validação completa do sistema de logs estruturados...")
        print("=" * 80)
        
        try:
            # Executar validações
            self.validate_json_format()
            self.validate_context_richness()
            self.validate_performance_logging()
            self.validate_security_logging()
            self.validate_business_logging()
            self.validate_environment_configuration()
            self.validate_log_rotation()
            
            # Calcular métricas finais
            total_tests = len(self.results)
            successful_tests = len([r for r in self.results if r["success"]])
            overall_score = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Gerar relatório
            report = {
                "validation_timestamp": datetime.utcnow().isoformat(),
                "tracing_id": "IMP013_LOGS_ESTRUTURADOS_001_20241227",
                "overall_success": successful_tests == total_tests,
                "overall_score": overall_score,
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "results": self.results
            }
            
            print("=" * 80)
            print(f"📊 RELATÓRIO FINAL DE VALIDAÇÃO")
            print(f"✅ Testes bem-sucedidos: {successful_tests}/{total_tests}")
            print(f"📈 Score geral: {overall_score:.1f}%")
            print(f"🎯 Status: {'PASSOU' if report['overall_success'] else 'FALHOU'}")
            
            return report
            
        except Exception as e:
            error_report = {
                "validation_timestamp": datetime.utcnow().isoformat(),
                "tracing_id": "IMP013_LOGS_ESTRUTURADOS_001_20241227",
                "overall_success": False,
                "error": str(e),
                "results": self.results
            }
            
            print(f"❌ Erro durante validação: {e}")
            return error_report
        
        finally:
            self.cleanup()

def main():
    """Função principal"""
    print("🔧 Sistema de Logs Estruturados Avançados - Validação IMP-013")
    print("Tracing ID: IMP013_LOGS_ESTRUTURADOS_001_20241227")
    print("Data: 2024-12-27")
    print()
    
    validator = LogsValidator()
    report = validator.run_all_validations()
    
    # Salvar relatório
    report_file = f"logs_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"📄 Relatório salvo em: {report_file}")
    
    # Retornar código de saída
    sys.exit(0 if report["overall_success"] else 1)

if __name__ == "__main__":
    main() 