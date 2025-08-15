#!/usr/bin/env python3
"""
Script para executar testes do backend
Tracing ID: BACKEND_RUN_TESTS_001_20250127
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def setup_environment():
    """Configura o ambiente para execução dos testes."""
    print("🔧 Configurando ambiente de testes...")
    
    # Adicionar paths necessários
    project_root = Path(__file__).parent.parent.parent
    backend_path = project_root / "backend"
    app_path = project_root / "app"
    
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(backend_path))
    sys.path.insert(0, str(app_path))
    
    # Configurar variáveis de ambiente
    os.environ.setdefault('FLASK_ENV', 'testing')
    os.environ.setdefault('TESTING', 'true')
    os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
    os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key')
    
    print("✅ Ambiente configurado com sucesso!")

def install_dependencies():
    """Instala dependências necessárias para testes."""
    print("📦 Instalando dependências de teste...")
    
    test_dependencies = [
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "pytest-mock",
        "pytest-xdist",
        "pytest-html",
        "pytest-timeout",
        "coverage",
        "flask-testing",
        "factory-boy"
    ]
    
    for dep in test_dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"⚠️  {dep} já instalado ou erro na instalação")
    
    print("✅ Dependências verificadas!")

def run_unit_tests():
    """Executa testes unitários."""
    print("🧪 Executando testes unitários...")
    
    start_time = time.time()
    
    # Comando para executar testes
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/backend/",
        "-v",
        "--tb=short",
        "--cov=backend",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:coverage/backend",
        "--cov-report=xml:coverage/backend/coverage.xml",
        "--cov-fail-under=85",
        "--junitxml=coverage/backend/junit.xml",
        "--html=coverage/backend/report.html",
        "--self-contained-html"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ Testes unitários executados com sucesso em {execution_time:.2f}s")
        print(f"📊 Resultado: {result.stdout}")
        
        return True, execution_time
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na execução dos testes: {e}")
        print(f"📋 Saída de erro: {e.stderr}")
        return False, 0

def run_specific_test_category(category):
    """Executa testes de uma categoria específica."""
    print(f"🎯 Executando testes da categoria: {category}")
    
    category_paths = {
        "main": "tests/unit/backend/test_main.py",
        "models": "tests/unit/backend/test_models.py",
        "api": "tests/unit/backend/test_api.py",
        "services": "tests/unit/backend/test_services.py",
        "utils": "tests/unit/backend/test_utils.py"
    }
    
    if category not in category_paths:
        print(f"❌ Categoria '{category}' não encontrada")
        return False, 0
    
    start_time = time.time()
    
    cmd = [
        sys.executable, "-m", "pytest",
        category_paths[category],
        "-v",
        "--tb=short",
        "--cov=backend",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ Testes da categoria '{category}' executados com sucesso em {execution_time:.2f}s")
        return True, execution_time
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na execução dos testes da categoria '{category}': {e}")
        return False, 0

def generate_coverage_report():
    """Gera relatório de cobertura detalhado."""
    print("📊 Gerando relatório de cobertura...")
    
    try:
        # Gerar relatório HTML
        subprocess.run([
            sys.executable, "-m", "coverage", "html",
            "--directory=coverage/backend/html",
            "--title=Backend Coverage Report"
        ], check=True, capture_output=True)
        
        # Gerar relatório XML
        subprocess.run([
            sys.executable, "-m", "coverage", "xml",
            "--output=coverage/backend/coverage.xml"
        ], check=True, capture_output=True)
        
        print("✅ Relatório de cobertura gerado com sucesso!")
        print("📁 Relatórios disponíveis em:")
        print("   - HTML: coverage/backend/html/index.html")
        print("   - XML: coverage/backend/coverage.xml")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Erro ao gerar relatório de cobertura: {e}")

def run_performance_tests():
    """Executa testes de performance."""
    print("⚡ Executando testes de performance...")
    
    start_time = time.time()
    
    # Comando para testes de performance
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/backend/",
        "-m", "performance",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ Testes de performance executados em {execution_time:.2f}s")
        return True, execution_time
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Nenhum teste de performance encontrado ou erro: {e}")
        return False, 0

def run_security_tests():
    """Executa testes de segurança."""
    print("🔒 Executando testes de segurança...")
    
    start_time = time.time()
    
    # Comando para testes de segurança
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/backend/",
        "-m", "security",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ Testes de segurança executados em {execution_time:.2f}s")
        return True, execution_time
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Nenhum teste de segurança encontrado ou erro: {e}")
        return False, 0

def cleanup():
    """Limpa arquivos temporários de teste."""
    print("🧹 Limpando arquivos temporários...")
    
    temp_files = [
        ".coverage",
        "coverage/.coverage",
        "htmlcov",
        ".pytest_cache"
    ]
    
    for file_path in temp_files:
        if os.path.exists(file_path):
            try:
                if os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                print(f"✅ {file_path} removido")
            except Exception as e:
                print(f"⚠️  Erro ao remover {file_path}: {e}")
    
    print("✅ Limpeza concluída!")

def main():
    """Função principal."""
    print("🚀 INICIANDO EXECUÇÃO DE TESTES DO BACKEND")
    print("=" * 50)
    
    # Configurar ambiente
    setup_environment()
    
    # Instalar dependências
    install_dependencies()
    
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        if category in ["main", "models", "api", "services", "utils"]:
            success, execution_time = run_specific_test_category(category)
        elif category == "performance":
            success, execution_time = run_performance_tests()
        elif category == "security":
            success, execution_time = run_security_tests()
        elif category == "cleanup":
            cleanup()
            return
        else:
            print(f"❌ Categoria '{category}' não reconhecida")
            print("Categorias disponíveis: main, models, api, services, utils, performance, security, cleanup")
            return
    else:
        # Executar todos os testes
        success, execution_time = run_unit_tests()
    
    if success:
        # Gerar relatório de cobertura
        generate_coverage_report()
        
        print("\n" + "=" * 50)
        print("🎉 EXECUÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"⏱️  Tempo total: {execution_time:.2f}s")
        print("📊 Verifique os relatórios em coverage/backend/")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ EXECUÇÃO FALHOU!")
        print("🔍 Verifique os erros acima e corrija os problemas")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()
