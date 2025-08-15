#!/usr/bin/env python3
"""
Script de execução para testes de carga de banco de dados

Prompt: CHECKLIST_TESTES_CARGA_CRITICIDADE.md - Nível Médio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: LOAD_DATABASE_20250127_001

Funcionalidades:
- Execução de testes de carga para banco de dados
- Configuração de parâmetros de teste
- Monitoramento de métricas
- Geração de relatórios
- Validação de resultados
"""

import os
import sys
import argparse
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

def run_database_load_test(
    users: int = 50,
    spawn_rate: int = 10,
    host: str = "http://localhost:8000",
    duration: int = 300,
    output_dir: str = "reports/database_load"
):
    """
    Executa teste de carga de banco de dados
    
    Args:
        users: Número de usuários concorrentes
        spawn_rate: Taxa de spawn de usuários por segundo
        host: Host do servidor
        duration: Duração do teste em segundos
        output_dir: Diretório de saída dos relatórios
    """
    
    print(f"🚀 Iniciando teste de carga de banco de dados")
    print(f"📊 Parâmetros:")
    print(f"   - Usuários: {users}")
    print(f"   - Taxa de spawn: {spawn_rate}/s")
    print(f"   - Host: {host}")
    print(f"   - Duração: {duration}s")
    print(f"   - Saída: {output_dir}")
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # Nome do arquivo de teste
    locustfile = "tests/load/medium/infrastructure/locustfile_database_load_v1.py"
    
    # Verificar se arquivo existe
    if not os.path.exists(locustfile):
        print(f"❌ Arquivo de teste não encontrado: {locustfile}")
        return False
    
    # Comando Locust
    cmd = [
        "locust",
        "-f", locustfile,
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{duration}s",
        "--headless",
        "--html", f"{output_dir}/database_load_report.html",
        "--csv", f"{output_dir}/database_load_metrics",
        "--json", f"{output_dir}/database_load_results.json"
    ]
    
    print(f"🔧 Comando: {' '.join(cmd)}")
    
    try:
        # Executar teste
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 60)
        end_time = time.time()
        
        # Verificar resultado
        if result.returncode == 0:
            print(f"✅ Teste concluído com sucesso em {end_time - start_time:.2f}s")
            
            # Gerar relatório resumido
            generate_summary_report(output_dir, users, spawn_rate, duration)
            
            return True
        else:
            print(f"❌ Teste falhou com código {result.returncode}")
            print(f"📝 Erro: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Teste expirou após {duration + 60}s")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False

def generate_summary_report(output_dir: str, users: int, spawn_rate: int, duration: int):
    """Gera relatório resumido do teste"""
    
    report_file = f"{output_dir}/database_load_summary.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"""# 📊 Relatório de Teste de Carga - Banco de Dados

**Data/Hora**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Tracing ID**: LOAD_DATABASE_20250127_001

## 📈 Parâmetros do Teste

- **Usuários**: {users}
- **Taxa de Spawn**: {spawn_rate}/s
- **Duração**: {duration}s
- **Host**: http://localhost:8000

## 🎯 Endpoints Testados

### Operações de Leitura
- `GET /api/nichos` - Listagem de nichos com paginação
- `GET /api/categorias` - Listagem de categorias com filtros
- `GET /api/execucoes` - Listagem de execuções com joins
- `GET /api/logs/execucoes` - Consulta de logs com filtros complexos
- `GET /api/notificacoes` - Listagem de notificações
- `GET /api/prompt-system/nichos` - Listagem de nichos do prompt system
- `GET /api/prompt-system/categorias` - Listagem de categorias do prompt system

### Operações de Escrita (Transações)
- `POST /api/execucoes` - Criação de execuções
- `POST /api/prompt-system/nichos` - Criação de nichos
- `POST /api/prompt-system/categorias` - Criação de categorias

## 🔍 Cenários de Teste

### 1. Carga em Pool de Conexões
- Testa o comportamento do pool de conexões sob carga
- Valida limites de conexões simultâneas
- Monitora tempo de espera por conexão

### 2. Queries Complexas com Joins
- Testa queries que envolvem múltiplas tabelas
- Valida performance de joins complexos
- Monitora uso de índices

### 3. Transações Concorrentes
- Testa operações de escrita simultâneas
- Valida isolamento de transações
- Monitora deadlocks e timeouts

### 4. Paginação e Filtros
- Testa queries com paginação
- Valida performance com diferentes tamanhos de página
- Monitora uso de memória

### 5. Consultas de Logs
- Testa queries em tabelas de logs
- Valida performance com filtros complexos
- Monitora uso de índices em logs

## 📊 Métricas Coletadas

- **Response Time**: Tempo de resposta por endpoint
- **Throughput**: Requisições por segundo
- **Error Rate**: Taxa de erros
- **Database Connections**: Uso do pool de conexões
- **Query Performance**: Performance de queries específicas

## 📁 Arquivos Gerados

- `database_load_report.html` - Relatório HTML detalhado
- `database_load_metrics.csv` - Métricas em CSV
- `database_load_results.json` - Resultados em JSON
- `database_load_summary.md` - Este relatório resumido

## 🎯 Próximos Passos

1. Analisar métricas de performance
2. Identificar gargalos no banco de dados
3. Otimizar queries problemáticas
4. Ajustar configurações do pool de conexões
5. Implementar índices necessários

---
**Gerado automaticamente pelo sistema de testes de carga**
""")
    
    print(f"📄 Relatório resumido gerado: {report_file}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes de carga de banco de dados")
    
    parser.add_argument(
        "-u", "--users",
        type=int,
        default=50,
        help="Número de usuários concorrentes (default: 50)"
    )
    
    parser.add_argument(
        "-r", "--spawn-rate",
        type=int,
        default=10,
        help="Taxa de spawn de usuários por segundo (default: 10)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="http://localhost:8000",
        help="Host do servidor (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=300,
        help="Duração do teste em segundos (default: 300)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="reports/database_load",
        help="Diretório de saída (default: reports/database_load)"
    )
    
    args = parser.parse_args()
    
    # Executar teste
    success = run_database_load_test(
        users=args.users,
        spawn_rate=args.spawn_rate,
        host=args.host,
        duration=args.duration,
        output_dir=args.output
    )
    
    if success:
        print(f"🎉 Teste de carga de banco de dados executado com sucesso!")
        print(f"📊 Relatórios disponíveis em: {args.output}")
        sys.exit(0)
    else:
        print(f"❌ Teste de carga de banco de dados falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main() 