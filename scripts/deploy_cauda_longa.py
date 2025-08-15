from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Script de Deploy - Sistema de Cauda Longa

Tracing ID: DEPLOY_LONG_TAIL_20241220_001
Data/Hora: 2024-12-20 18:55:00 UTC
Versão: 1.0
Status: ✅ IMPLEMENTADO

Este script automatiza o processo de deploy do sistema de cauda longa.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def verificar_pre_requisitos():
    """Verifica pré-requisitos do sistema."""
    print("🔍 Verificando pré-requisitos...")
    
    requisitos = [
        ("Python 3.11+", "python --version"),
        ("pip", "pip --version"),
        ("git", "git --version")
    ]
    
    for nome, comando in requisitos:
        try:
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
            if resultado.returncode == 0:
                print(f"✅ {nome}: OK")
            else:
                print(f"❌ {nome}: FALHOU")
                return False
        except Exception as e:
            print(f"❌ {nome}: ERRO - {e}")
            return False
    
    return True

def instalar_dependencias():
    """Instala dependências do projeto."""
    print("📦 Instalando dependências...")
    
    try:
        resultado = subprocess.run("pip install -r requirements_cauda_longa.txt", shell=True)
        if resultado.returncode == 0:
            print("✅ Dependências instaladas")
            return True
        else:
            print("❌ Falha na instalação")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def configurar_ambiente(ambiente="development"):
    """Configura ambiente de deploy."""
    print(f"⚙️ Configurando ambiente: {ambiente}")
    
    # Copiar arquivo de ambiente
    env_source = f".env.{ambiente}"
    env_target = ".env"
    
    if Path(env_source).exists():
        import shutil
        shutil.copy2(env_source, env_target)
        print(f"✅ Ambiente configurado: {env_source}")
        return True
    else:
        print(f"❌ Arquivo não encontrado: {env_source}")
        return False

def executar_testes():
    """Executa testes básicos."""
    print("🧪 Executando testes...")
    
    try:
        resultado = subprocess.run("python -m pytest tests/unit/ -value", shell=True)
        if resultado.returncode == 0:
            print("✅ Testes passaram")
            return True
        else:
            print("❌ Testes falharam")
            return False
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        return False

def iniciar_aplicacao():
    """Inicia a aplicação."""
    print("🚀 Iniciando aplicação...")
    
    try:
        # Configurar variáveis de ambiente
        os.environ["FLASK_ENV"] = "development"
        os.environ["FLASK_DEBUG"] = "True"
        
        # Iniciar aplicação
        comando = "python -m flask run --host=0.0.0.0 --port=5000"
        print(f"Executando: {comando}")
        
        processo = subprocess.Popen(comando, shell=True)
        
        print("✅ Aplicação iniciada")
        print("🌐 Acesse: http://localhost:5000")
        print("🔗 API Cauda Longa: http://localhost:5000/api/cauda-longa/health")
        
        return processo
        
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
        return None

def main():
    """Função principal."""
    print("🚀 DEPLOY DO SISTEMA DE CAUDA LONGA")
    print("=" * 50)
    
    # Verificar pré-requisitos
    if not verificar_pre_requisitos():
        print("❌ Pré-requisitos não atendidos")
        return 1
    
    # Instalar dependências
    if not instalar_dependencias():
        print("❌ Falha na instalação")
        return 1
    
    # Configurar ambiente
    if not configurar_ambiente():
        print("❌ Falha na configuração")
        return 1
    
    # Executar testes
    if not executar_testes():
        print("❌ Falha nos testes")
        return 1
    
    # Iniciar aplicação
    processo = iniciar_aplicacao()
    if not processo:
        print("❌ Falha ao iniciar")
        return 1
    
    print("\n🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
    print("\n📋 Próximos passos:")
    print("1. Testar endpoints manualmente")
    print("2. Configurar monitoramento")
    print("3. Configurar backup")
    print("4. Deploy em produção")
    
    try:
        processo.wait()
    except KeyboardInterrupt:
        print("\n🛑 Aplicação parada pelo usuário")
        processo.terminate()
    
    return 0

if __name__ == "__main__":
    exit(main()) 