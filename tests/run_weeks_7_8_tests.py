#!/usr/bin/env python3
# 🚀 Script de Execução - Testes Semanas 7-8 - Omni Keywords Finder
# 📅 Semana 7-8: Integration & E2E (Meta: 98% cobertura)
# 🎯 Tracing ID: TESTES_98_COBERTURA_001_20250127
# 📝 Prompt: Script para executar testes das semanas 7-8
# 🔧 Ruleset: enterprise_control_layer.yaml

"""
Script de Execução dos Testes das Semanas 7-8
==============================================

Este script executa todos os testes implementados nas semanas 7-8:
- Testes de Integração de APIs
- Testes de Integração com Banco de Dados
- Testes E2E Críticos
- Testes de Qualidade (Load, Security, Performance)

Objetivo: Atingir 98% de cobertura de código
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
import argparse


class TestRunner:
    """Executor de testes para as semanas 7-8."""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {
            "integration": {"passed": 0, "failed": 0, "total": 0},
            "e2e": {"passed": 0, "failed": 0, "total": 0},
            "quality": {"passed": 0, "failed": 0, "total": 0},
            "coverage": {"current": 0.0, "target": 98.0}
        }
        self.test_outputs = []
        
    def log(self, message: str, level: str = "INFO"):
        """Registra mensagem de log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def run_command(self, command: List[str], description: str) -> Tuple[bool, str]:
        """
        Executa comando do sistema.
        
        Args:
            command: Comando a ser executado
            description: Descrição do comando
            
        Returns:
            Tuple (sucesso, output)
        """
        self.log(f"Executando: {description}")
        self.log(f"Comando: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            if result.returncode == 0:
                self.log(f"✅ {description} - SUCESSO", "SUCCESS")
                return True, result.stdout
            else:
                self.log(f"❌ {description} - FALHOU", "ERROR")
                self.log(f"Erro: {result.stderr}", "ERROR")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ {description} - TIMEOUT", "ERROR")
            return False, "Timeout expired"
        except Exception as e:
            self.log(f"💥 {description} - EXCEÇÃO: {str(e)}", "ERROR")
            return False, str(e)
    
    def run_integration_tests(self) -> bool:
        """Executa testes de integração."""
        self.log("🧪 Iniciando testes de integração...")
        
        # Testes de integração de APIs
        api_success, api_output = self.run_command(
            ["python", "-m", "pytest", "tests/integration/api_integration/", "-v", "--tb=short"],
            "Testes de Integração de APIs"
        )
        
        # Testes de integração com banco
        db_success, db_output = self.run_command(
            ["python", "-m", "pytest", "tests/integration/database_integration/", "-v", "--tb=short"],
            "Testes de Integração com Banco de Dados"
        )
        
        # Processar resultados
        if api_success and db_success:
            self.results["integration"]["passed"] += 2
            self.results["integration"]["total"] += 2
            self.log("✅ Todos os testes de integração passaram", "SUCCESS")
            return True
        else:
            self.results["integration"]["failed"] += 1
            self.results["integration"]["total"] += 2
            self.log("❌ Alguns testes de integração falharam", "ERROR")
            return False
    
    def run_e2e_tests(self) -> bool:
        """Executa testes E2E."""
        self.log("🌐 Iniciando testes E2E...")
        
        # Testes E2E críticos
        e2e_success, e2e_output = self.run_command(
            ["python", "-m", "pytest", "tests/e2e/critical_flows/", "-v", "--tb=short"],
            "Testes E2E Críticos"
        )
        
        if e2e_success:
            self.results["e2e"]["passed"] += 1
            self.results["e2e"]["total"] += 1
            self.log("✅ Testes E2E passaram", "SUCCESS")
            return True
        else:
            self.results["e2e"]["failed"] += 1
            self.results["e2e"]["total"] += 1
            self.log("❌ Testes E2E falharam", "ERROR")
            return False
    
    def run_quality_tests(self) -> bool:
        """Executa testes de qualidade."""
        self.log("🔍 Iniciando testes de qualidade...")
        
        # Testes de carga
        load_success, load_output = self.run_command(
            ["python", "-m", "pytest", "tests/quality/load/", "-v", "--tb=short"],
            "Testes de Carga"
        )
        
        # Testes de segurança (se implementados)
        security_success = True
        security_output = ""
        if os.path.exists("tests/quality/security/"):
            security_success, security_output = self.run_command(
                ["python", "-m", "pytest", "tests/quality/security/", "-v", "--tb=short"],
                "Testes de Segurança"
            )
        
        # Processar resultados
        total_tests = 2 if security_success else 1
        passed_tests = (1 if load_success else 0) + (1 if security_success else 0)
        
        self.results["quality"]["passed"] += passed_tests
        self.results["quality"]["total"] += total_tests
        
        if passed_tests == total_tests:
            self.log("✅ Todos os testes de qualidade passaram", "SUCCESS")
            return True
        else:
            self.log("❌ Alguns testes de qualidade falharam", "ERROR")
            return False
    
    def check_coverage(self) -> bool:
        """Verifica cobertura de código."""
        self.log("📊 Verificando cobertura de código...")
        
        # Executar testes com cobertura
        coverage_success, coverage_output = self.run_command(
            [
                "python", "-m", "pytest", 
                "tests/", 
                "--cov=backend", 
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-fail-under=98"
            ],
            "Verificação de Cobertura"
        )
        
        # Extrair porcentagem de cobertura do output
        if coverage_success:
            # Procurar por linha de cobertura no output
            for line in coverage_output.split('\n'):
                if 'TOTAL' in line and '%' in line:
                    try:
                        # Extrair porcentagem (ex: "TOTAL                   1234    45    96%")
                        parts = line.split()
                        for part in parts:
                            if '%' in part:
                                coverage_percent = float(part.replace('%', ''))
                                self.results["coverage"]["current"] = coverage_percent
                                break
                    except (ValueError, IndexError):
                        pass
                    break
            
            self.log(f"📊 Cobertura atual: {self.results['coverage']['current']:.1f}%", "INFO")
            
            if self.results["coverage"]["current"] >= self.results["coverage"]["target"]:
                self.log("🎯 Meta de cobertura ATINGIDA!", "SUCCESS")
                return True
            else:
                self.log(f"⚠️ Meta de cobertura NÃO atingida. Atual: {self.results['coverage']['current']:.1f}%", "WARNING")
                return False
        else:
            self.log("❌ Falha ao verificar cobertura", "ERROR")
            return False
    
    def generate_report(self) -> str:
        """Gera relatório final dos testes."""
        end_time = time.time()
        duration = end_time - self.start_time
        
        report = []
        report.append("=" * 80)
        report.append("📋 RELATÓRIO FINAL - TESTES SEMANAS 7-8")
        report.append("=" * 80)
        report.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duração Total: {duration:.2f} segundos")
        report.append("")
        
        # Resumo por categoria
        report.append("📊 RESUMO POR CATEGORIA")
        report.append("-" * 40)
        
        for category, stats in self.results.items():
            if category != "coverage":
                total = stats["total"]
                passed = stats["passed"]
                failed = stats["failed"]
                success_rate = (passed / total * 100) if total > 0 else 0
                
                status_icon = "✅" if failed == 0 else "⚠️" if passed > 0 else "❌"
                report.append(f"{status_icon} {category.upper()}: {passed}/{total} ({success_rate:.1f}%)")
        
        # Cobertura
        coverage = self.results["coverage"]
        coverage_status = "🎯 ATINGIDA" if coverage["current"] >= coverage["target"] else "⚠️ NÃO ATINGIDA"
        report.append(f"📊 COBERTURA: {coverage['current']:.1f}% / {coverage['target']:.1f}% - {coverage_status}")
        
        # Estatísticas gerais
        total_tests = sum(stats["total"] for key, stats in self.results.items() if key != "coverage")
        total_passed = sum(stats["passed"] for key, stats in self.results.items() if key != "coverage")
        total_failed = sum(stats["failed"] for key, stats in self.results.items() if key != "coverage")
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report.append("")
        report.append("📈 ESTATÍSTICAS GERAIS")
        report.append("-" * 40)
        report.append(f"Total de Testes: {total_tests}")
        report.append(f"Testes Aprovados: {total_passed}")
        report.append(f"Testes Reprovados: {total_failed}")
        report.append(f"Taxa de Sucesso: {overall_success_rate:.1f}%")
        
        # Status final
        report.append("")
        if total_failed == 0 and coverage["current"] >= coverage["target"]:
            report.append("🎉 STATUS FINAL: TODOS OS OBJETIVOS ATINGIDOS!")
            report.append("✅ Sistema pronto para produção com qualidade enterprise")
        elif total_failed == 0:
            report.append("⚠️ STATUS FINAL: TESTES PASSARAM, MAS COBERTURA INSUFICIENTE")
            report.append("🔧 Implementar testes adicionais para atingir 98%")
        else:
            report.append("❌ STATUS FINAL: ALGUNS TESTES FALHARAM")
            report.append("🔧 Corrigir falhas antes de prosseguir")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_results(self, filename: str = "test_results_weeks_7_8.json"):
        """Salva resultados em arquivo JSON."""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": time.time() - self.start_time,
            "results": self.results,
            "test_outputs": self.test_outputs
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            self.log(f"💾 Resultados salvos em: {filename}", "INFO")
        except Exception as e:
            self.log(f"❌ Erro ao salvar resultados: {str(e)}", "ERROR")
    
    def run_all_tests(self) -> bool:
        """Executa todos os testes das semanas 7-8."""
        self.log("🚀 INICIANDO EXECUÇÃO COMPLETA DOS TESTES SEMANAS 7-8")
        self.log("🎯 Objetivo: Atingir 98% de cobertura de código")
        self.log("")
        
        # 1. Testes de Integração
        integration_success = self.run_integration_tests()
        
        # 2. Testes E2E
        e2e_success = self.run_e2e_tests()
        
        # 3. Testes de Qualidade
        quality_success = self.run_quality_tests()
        
        # 4. Verificação de Cobertura
        coverage_success = self.check_coverage()
        
        # Gerar relatório final
        report = self.generate_report()
        print("\n" + report)
        
        # Salvar resultados
        self.save_results()
        
        # Retornar sucesso geral
        overall_success = (
            integration_success and 
            e2e_success and 
            quality_success and 
            coverage_success
        )
        
        if overall_success:
            self.log("🎉 EXECUÇÃO COMPLETA - SUCESSO TOTAL!", "SUCCESS")
        else:
            self.log("⚠️ EXECUÇÃO COMPLETA - ALGUNS OBJETIVOS NÃO ATINGIDOS", "WARNING")
        
        return overall_success


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Executa testes das semanas 7-8 para Omni Keywords Finder"
    )
    
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Executa apenas testes de integração"
    )
    
    parser.add_argument(
        "--e2e-only",
        action="store_true",
        help="Executa apenas testes E2E"
    )
    
    parser.add_argument(
        "--quality-only",
        action="store_true",
        help="Executa apenas testes de qualidade"
    )
    
    parser.add_argument(
        "--coverage-only",
        action="store_true",
        help="Verifica apenas cobertura de código"
    )
    
    parser.add_argument(
        "--save-results",
        type=str,
        default="test_results_weeks_7_8.json",
        help="Arquivo para salvar resultados (padrão: test_results_weeks_7_8.json)"
    )
    
    args = parser.parse_args()
    
    # Criar executor de testes
    runner = TestRunner()
    
    try:
        if args.integration_only:
            runner.log("🧪 Executando apenas testes de integração...")
            success = runner.run_integration_tests()
        elif args.e2e_only:
            runner.log("🌐 Executando apenas testes E2E...")
            success = runner.run_e2e_tests()
        elif args.quality_only:
            runner.log("🔍 Executando apenas testes de qualidade...")
            success = runner.run_quality_tests()
        elif args.coverage_only:
            runner.log("📊 Verificando apenas cobertura...")
            success = runner.check_coverage()
        else:
            # Executar todos os testes
            success = runner.run_all_tests()
        
        # Salvar resultados
        runner.save_results(args.save_results)
        
        # Código de saída
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        runner.log("⏹️ Execução interrompida pelo usuário", "WARNING")
        sys.exit(1)
    except Exception as e:
        runner.log(f"💥 Erro durante execução: {str(e)}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
