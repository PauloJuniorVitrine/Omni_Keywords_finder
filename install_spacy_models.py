#!/usr/bin/env python3
"""
Script para instalar modelos SpaCy de forma limpa
Tracing ID: CLEANUP_DEPENDENCIES_20250127_003
Data: 2025-01-27
Versão: 1.0.0
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Executa um comando e trata erros."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} - Sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro:")
        print(f"   Comando: {command}")
        print(f"   Erro: {e.stderr}")
        return False

def check_spacy_installation():
    """Verifica se o SpaCy está instalado."""
    try:
        import spacy
        print(f"✅ SpaCy instalado - Versão: {spacy.__version__}")
        return True
    except ImportError:
        print("❌ SpaCy não está instalado!")
        print("   Execute: pip install spacy>=3.7.0,<4.0.0")
        return False

def install_spacy_models():
    """Instala os modelos SpaCy necessários."""
    models = [
        ("pt_core_news_lg", "Português (Grande)"),
        ("en_core_web_lg", "Inglês (Grande)")
    ]
    
    success_count = 0
    
    for model, description in models:
        print(f"\n📦 Instalando modelo {model} ({description})...")
        
        # Verifica se o modelo já está instalado
        check_command = f"python -c \"import spacy; spacy.load('{model}')\""
        try:
            subprocess.run(check_command, shell=True, check=True, capture_output=True)
            print(f"✅ Modelo {model} já está instalado!")
            success_count += 1
            continue
        except subprocess.CalledProcessError:
            pass
        
        # Instala o modelo
        install_command = f"python -m spacy download {model}"
        if run_command(install_command, f"Instalando {model}"):
            success_count += 1
    
    return success_count == len(models)

def verify_models():
    """Verifica se os modelos estão funcionando."""
    print("\n🔍 Verificando modelos...")
    
    try:
        import spacy
        
        # Testa modelo português
        print("   Testando modelo português...")
        nlp_pt = spacy.load("pt_core_news_lg")
        doc_pt = nlp_pt("Olá mundo! Este é um teste do modelo português.")
        print(f"   ✅ Português: {len(doc_pt)} tokens processados")
        
        # Testa modelo inglês
        print("   Testando modelo inglês...")
        nlp_en = spacy.load("en_core_web_lg")
        doc_en = nlp_en("Hello world! This is a test of the English model.")
        print(f"   ✅ Inglês: {len(doc_en)} tokens processados")
        
        print("✅ Todos os modelos estão funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar modelos: {e}")
        return False

def main():
    """Função principal."""
    print("🚀 INSTALADOR DE MODELOS SPACY")
    print("=" * 50)
    
    # Verifica se o SpaCy está instalado
    if not check_spacy_installation():
        sys.exit(1)
    
    # Instala os modelos
    if not install_spacy_models():
        print("\n❌ Falha na instalação de alguns modelos!")
        sys.exit(1)
    
    # Verifica se os modelos estão funcionando
    if not verify_models():
        print("\n❌ Falha na verificação dos modelos!")
        sys.exit(1)
    
    print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    print("✅ SpaCy instalado e configurado")
    print("✅ Modelos português e inglês instalados")
    print("✅ Todos os modelos testados e funcionando")
    print("\n📝 Próximos passos:")
    print("   1. Execute: pip install -r requirements.txt")
    print("   2. Para desenvolvimento: pip install -r requirements-dev.txt")
    print("   3. Teste o sistema: python -m pytest tests/")

if __name__ == "__main__":
    main() 