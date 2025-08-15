#!/usr/bin/env python3
"""
Script Principal de Validação - Item 13 Completo
Tracing ID: ITEM_13_MAIN_20250127_001

Executa todos os testes de validação do item 13:
- 13.1: Validação completa
- 13.2: Métricas de performance
- 13.3: Compliance
"""

import os
import sys
import time
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ValidationSummary:
    """Resumo de uma validação"""
    item_name: str
    status: bool
    success_rate: float
    execution_time: float
    details: str

class Item13Validator:
    """Validador principal do item 13"""
    
    def __init__(self):
        self.tracing_id = "ITEM_13_MAIN_20250127_001"
        self.results: List[ValidationSummary] = []
        self.start_time = time.time()
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)string_data] [%(levelname)string_data] [%(name)string_data] %(message)string_data',
            handlers=[
                logging.FileHandler(f'logs/item_13_validation_{time.strftime("%Y%m%data")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"[{self.tracing_id}] Iniciando validação completa do item 13")
    
    def run_validation_13_1(self) -> ValidationSummary:
        """Executa validação 13.1 - Validação completa"""
        self.logger.info("Executando validação 13.1 - Validação completa...")
        
        try:
            start_time = time.time()
            
            # Executar script de validação final
            result = subprocess.run([
                sys.executable, "scripts/run_final_validation.py"
            ], capture_output=True, text=True, timeout=300)
            
            execution_time = time.time() - start_time
            
            # Analisar resultado
            success = result.returncode == 0
            success_rate = 100.0 if success else 0.0
            
            details = f"Exit code: {result.returncode}, Output: {result.stdout[:200]}..."
            
            return ValidationSummary(
                item_name="13.1 - Validação Completa",
                status=success,
                success_rate=success_rate,
                execution_time=execution_time,
                details=details
            )
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout na validação 13.1")
            return ValidationSummary(
                item_name="13.1 - Validação Completa",
                status=False,
                success_rate=0.0,
                execution_time=300.0,
                details="Timeout após 5 minutos"
            )
        except Exception as e:
            self.logger.error(f"Erro na validação 13.1: {e}")
            return ValidationSummary(
                item_name="13.1 - Validação Completa",
                status=False,
                success_rate=0.0,
                execution_time=0.0,
                details=f"Erro: {str(e)}"
            )
    
    def run_validation_13_2(self) -> ValidationSummary:
        """Executa validação 13.2 - Métricas de performance"""
        self.logger.info("Executando validação 13.2 - Métricas de performance...")
        
        try:
            start_time = time.time()
            
            # Executar script de validação de performance
            result = subprocess.run([
                sys.executable, "scripts/validate_performance_metrics.py"
            ], capture_output=True, text=True, timeout=300)
            
            execution_time = time.time() - start_time
            
            # Analisar resultado
            success = result.returncode == 0
            success_rate = 100.0 if success else 0.0
            
            details = f"Exit code: {result.returncode}, Output: {result.stdout[:200]}..."
            
            return ValidationSummary(
                item_name="13.2 - Métricas de Performance",
                status=success,
                success_rate=success_rate,
                execution_time=execution_time,
                details=details
            )
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout na validação 13.2")
            return ValidationSummary(
                item_name="13.2 - Métricas de Performance",
                status=False,
                success_rate=0.0,
                execution_time=300.0,
                details="Timeout após 5 minutos"
            )
        except Exception as e:
            self.logger.error(f"Erro na validação 13.2: {e}")
            return ValidationSummary(
                item_name="13.2 - Métricas de Performance",
                status=False,
                success_rate=0.0,
                execution_time=0.0,
                details=f"Erro: {str(e)}"
            )
    
    def run_validation_13_3(self) -> ValidationSummary:
        """Executa validação 13.3 - Compliance"""
        self.logger.info("Executando validação 13.3 - Compliance...")
        
        try:
            start_time = time.time()
            
            # Executar script de validação de compliance
            result = subprocess.run([
                sys.executable, "scripts/validate_compliance.py"
            ], capture_output=True, text=True, timeout=300)
            
            execution_time = time.time() - start_time
            
            # Analisar resultado
            success = result.returncode == 0
            success_rate = 100.0 if success else 0.0
            
            details = f"Exit code: {result.returncode}, Output: {result.stdout[:200]}..."
            
            return ValidationSummary(
                item_name="13.3 - Compliance",
                status=success,
                success_rate=success_rate,
                execution_time=execution_time,
                details=details
            )
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout na validação 13.3")
            return ValidationSummary(
                item_name="13.3 - Compliance",
                status=False,
                success_rate=0.0,
                execution_time=300.0,
                details="Timeout após 5 minutos"
            )
        except Exception as e:
            self.logger.error(f"Erro na validação 13.3: {e}")
            return ValidationSummary(
                item_name="13.3 - Compliance",
                status=False,
                success_rate=0.0,
                execution_time=0.0,
                details=f"Erro: {str(e)}"
            )
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Executa todas as validações do item 13"""
        self.logger.info(f"[{self.tracing_id}] Iniciando execução de todas as validações do item 13")
        
        # Executar validações
        self.results.append(self.run_validation_13_1())
        self.results.append(self.run_validation_13_2())
        self.results.append(self.run_validation_13_3())
        
        # Calcular métricas finais
        total_validations = len(self.results)
        successful_validations = sum(1 for result in self.results if result.status)
        avg_success_rate = sum(result.success_rate for result in self.results) / total_validations if total_validations > 0 else 0
        total_execution_time = sum(result.execution_time for result in self.results)
        
        overall_execution_time = time.time() - self.start_time
        
        # Gerar relatório
        report = {
            "tracing_id": self.tracing_id,
            "timestamp": time.strftime("%Y-%m-%data %H:%M:%S"),
            "overall_execution_time_seconds": overall_execution_time,
            "total_validations": total_validations,
            "successful_validations": successful_validations,
            "failed_validations": total_validations - successful_validations,
            "overall_success_rate": (successful_validations / total_validations * 100) if total_validations > 0 else 0,
            "average_success_rate": avg_success_rate,
            "total_validation_time": total_execution_time,
            "results": [
                {
                    "item_name": result.item_name,
                    "status": result.status,
                    "success_rate": result.success_rate,
                    "execution_time": result.execution_time,
                    "details": result.details
                }
                for result in self.results
            ]
        }
        
        # Salvar relatório
        self._save_report(report)
        
        self.logger.info(f"[{self.tracing_id}] Validação do item 13 concluída")
        self.logger.info(f"Tempo total de execução: {overall_execution_time:.2f}string_data")
        self.logger.info(f"Taxa de sucesso geral: {report['overall_success_rate']:.1f}%")
        self.logger.info(f"Validações bem-sucedidas: {successful_validations}/{total_validations}")
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Salva relatório de validação do item 13"""
        report_file = f"logs/item_13_validation_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("logs", exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Relatório salvo em: {report_file}")

def main():
    """Função principal"""
    validator = Item13Validator()
    report = validator.run_all_validations()
    
    # Exibir resumo
    print("\n" + "="*60)
    print("📊 RESUMO DA VALIDAÇÃO DO ITEM 13")
    print("="*60)
    
    for result in report["results"]:
        status_icon = "✅" if result["status"] else "❌"
        print(f"{status_icon} {result['item_name']}")
        print(f"   Taxa de sucesso: {result['success_rate']:.1f}%")
        print(f"   Tempo de execução: {result['execution_time']:.2f}string_data")
        print()
    
    print(f"📈 Taxa de sucesso geral: {report['overall_success_rate']:.1f}%")
    print(f"⏱️ Tempo total: {report['overall_execution_time_seconds']:.2f}string_data")
    print("="*60)
    
    # Retornar código de saída baseado no sucesso
    if report["overall_success_rate"] == 100:
        print("🎉 TODAS AS VALIDAÇÕES DO ITEM 13 PASSARAM!")
        sys.exit(0)
    else:
        print(f"⚠️ {report['failed_validations']} VALIDAÇÕES FALHARAM")
        sys.exit(1)

if __name__ == "__main__":
    main() 