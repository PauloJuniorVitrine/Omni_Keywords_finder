#!/usr/bin/env python3
"""
🚀 Script de Execução - Testes de Integração Semântica
📅 Data: 2025-01-27
🔗 Tracing ID: RUN_SEMANTIC_INTEGRATION_001
📋 Ruleset: enterprise_control_layer.yaml

Executa testes de carga para integração semântica
Baseado em código real de análise semântica
"""

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

def setup_environment():
    """Configurar ambiente de teste"""
    # Adicionar diretório de testes ao path
    test_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(test_dir))
    
    # Criar diretório de resultados
    results_dir = Path("test-results")
    results_dir.mkdir(exist_ok=True)
    
    return test_dir, results_dir

def run_semantic_integration_tests(users: int, spawn_rate: int, host: str, duration: int = 300):
    """Executar testes de integração semântica"""
    print(f"🚀 Iniciando testes de integração semântica...")
    print(f"📊 Configuração: {users} usuários, {spawn_rate}/s, {host}")
    print(f"⏱️  Duração: {duration} segundos")
    
    # Caminho para o arquivo de teste
    test_file = Path(__file__).parent.parent / "high" / "integrations" / "locustfile_integration_semantic_v1.py"
    
    if not test_file.exists():
        print(f"❌ Arquivo de teste não encontrado: {test_file}")
        return False
    
    # Comando locust
    cmd = [
        "locust",
        "-f", str(test_file),
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{duration}s",
        "--headless",
        "--html", "test-results/semantic_integration_report.html",
        "--csv", "test-results/semantic_integration_results"
    ]
    
    try:
        print(f"🔧 Executando: {' '.join(cmd)}")
        start_time = time.time()
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 60)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ Teste concluído em {execution_time:.2f} segundos")
        print(f"📊 Código de saída: {result.returncode}")
        
        if result.stdout:
            print("📋 Saída padrão:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Erros:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Teste expirou")
        return False
    except Exception as e:
        print(f"❌ Erro na execução: {str(e)}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes de integração semântica")
    parser.add_argument("-u", "--users", type=int, default=50, help="Número de usuários")
    parser.add_argument("-r", "--spawn-rate", type=int, default=5, help="Taxa de spawn (usuários/segundo)")
    parser.add_argument("--host", default="http://localhost:8000", help="Host do servidor")
    parser.add_argument("-d", "--duration", type=int, default=300, help="Duração do teste em segundos")
    
    args = parser.parse_args()
    
    # Configurar ambiente
    test_dir, results_dir = setup_environment()
    
    print(f"📁 Diretório de testes: {test_dir}")
    print(f"📁 Diretório de resultados: {results_dir}")
    
    # Executar testes
    success = run_semantic_integration_tests(
        users=args.users,
        spawn_rate=args.spawn_rate,
        host=args.host,
        duration=args.duration
    )
    
    if success:
        print("🎉 Testes de integração semântica executados com sucesso!")
        sys.exit(0)
    else:
        print("💥 Falha na execução dos testes de integração semântica")
        sys.exit(1)

if __name__ == "__main__":
    main() 