#!/usr/bin/env python3
"""
Script de Execução para Mutation Testing
========================================

Tracing ID: MUTATION_TEST_001
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTAÇÃO

Script para executar mutation testing usando mutmut e gerar relatórios.
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

def setup_environment():
    """Configura o ambiente para mutation testing."""
    print("🔧 Configurando ambiente para mutation testing...")
    
    # Criar diretórios necessários
    directories = [
        "coverage/mutation",
        "logs",
        "reports/mutation"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Diretório criado: {directory}")

def run_mutation_tests(module: Optional[str] = None, strategy: str = "ALL"):
    """Executa mutation testing."""
    print(f"🧬 Executando mutation testing...")
    
    # Comando base
    cmd = ["mutmut", "run"]
    
    # Adicionar módulo específico se fornecido
    if module:
        cmd.extend(["--paths-to-mutate", module])
        print(f"  📁 Módulo específico: {module}")
    
    # Adicionar estratégia
    cmd.extend(["--strategies", strategy])
    print(f"  🎯 Estratégia: {strategy}")
    
    try:
        # Executar mutation testing
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode == 0:
            print("  ✅ Mutation testing executado com sucesso")
            return True
        else:
            print(f"  ❌ Erro na execução: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⏰ Timeout na execução do mutation testing")
        return False
    except Exception as e:
        print(f"  💥 Erro inesperado: {e}")
        return False

def generate_reports():
    """Gera relatórios de mutation testing."""
    print("📊 Gerando relatórios...")
    
    try:
        # Relatório HTML
        subprocess.run(["mutmut", "html"], check=True)
        print("  ✅ Relatório HTML gerado")
        
        # Relatório JSON
        subprocess.run(["mutmut", "json"], check=True)
        print("  ✅ Relatório JSON gerado")
        
        # Relatório de cobertura
        subprocess.run(["mutmut", "coverage"], check=True)
        print("  ✅ Relatório de cobertura gerado")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Erro ao gerar relatórios: {e}")
        return False

def analyze_results() -> Dict[str, Any]:
    """Analisa os resultados do mutation testing."""
    print("🔍 Analisando resultados...")
    
    try:
        # Ler relatório JSON
        report_file = "coverage/mutation/mutation_report.json"
        if os.path.exists(report_file):
            with open(report_file, 'r') as f:
                data = json.load(f)
            
            # Calcular métricas
            total_mutations = len(data.get("mutations", []))
            killed_mutations = sum(1 for m in data.get("mutations", []) if m.get("status") == "killed")
            survived_mutations = sum(1 for m in data.get("mutations", []) if m.get("status") == "survived")
            
            mutation_score = (killed_mutations / total_mutations * 100) if total_mutations > 0 else 0
            
            results = {
                "total_mutations": total_mutations,
                "killed_mutations": killed_mutations,
                "survived_mutations": survived_mutations,
                "mutation_score": mutation_score,
                "timestamp": datetime.now().isoformat(),
                "status": "success" if mutation_score >= 80 else "warning"
            }
            
            print(f"  📈 Total de mutações: {total_mutations}")
            print(f"  💀 Mutações eliminadas: {killed_mutations}")
            print(f"  🧟 Mutações sobreviventes: {survived_mutations}")
            print(f"  🎯 Score de mutação: {mutation_score:.2f}%")
            
            return results
        else:
            print("  ⚠️ Relatório não encontrado")
            return {"status": "error", "message": "Relatório não encontrado"}
            
    except Exception as e:
        print(f"  ❌ Erro ao analisar resultados: {e}")
        return {"status": "error", "message": str(e)}

def save_summary_report(results: Dict[str, Any]):
    """Salva relatório resumido."""
    print("💾 Salvando relatório resumido...")
    
    summary = {
        "tracing_id": "MUTATION_TEST_001",
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "recommendations": []
    }
    
    # Adicionar recomendações baseadas nos resultados
    if results.get("mutation_score", 0) < 80:
        summary["recommendations"].append("Melhorar cobertura de testes para aumentar score de mutação")
    
    if results.get("survived_mutations", 0) > 0:
        summary["recommendations"].append("Revisar testes para eliminar mutações sobreviventes")
    
    # Salvar relatório
    report_file = "reports/mutation/summary_report.json"
    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"  ✅ Relatório salvo: {report_file}")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Executa mutation testing")
    parser.add_argument("--module", help="Módulo específico para testar")
    parser.add_argument("--strategy", default="ALL", help="Estratégia de mutação")
    parser.add_argument("--setup-only", action="store_true", help="Apenas configurar ambiente")
    
    args = parser.parse_args()
    
    print("🧬 Mutation Testing - Omni Keywords Finder")
    print("=" * 50)
    
    # Configurar ambiente
    setup_environment()
    
    if args.setup_only:
        print("✅ Configuração concluída")
        return
    
    # Executar mutation testing
    success = run_mutation_tests(args.module, args.strategy)
    
    if success:
        # Gerar relatórios
        reports_success = generate_reports()
        
        if reports_success:
            # Analisar resultados
            results = analyze_results()
            
            # Salvar relatório resumido
            save_summary_report(results)
            
            print("\n🎉 Mutation testing concluído com sucesso!")
            
            # Exibir resumo
            if results.get("status") == "success":
                print("✅ Score de mutação aceitável")
            else:
                print("⚠️ Score de mutação abaixo do esperado")
        else:
            print("❌ Falha ao gerar relatórios")
    else:
        print("❌ Falha na execução do mutation testing")

if __name__ == "__main__":
    main() 