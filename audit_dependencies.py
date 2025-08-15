#!/usr/bin/env python3
"""
Script para auditar dependências e verificar vulnerabilidades
Tracing ID: CLEANUP_DEPENDENCIES_20250127_004
Data: 2025-01-27
Versão: 1.0.0
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime

def run_command(command, description):
    """Executa um comando e retorna o resultado."""
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
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro:")
        print(f"   Comando: {command}")
        print(f"   Erro: {e.stderr}")
        return None

def check_pip_audit():
    """Executa pip-audit para verificar vulnerabilidades Python."""
    print("\n🔍 AUDITORIA DE DEPENDÊNCIAS PYTHON")
    print("=" * 50)
    
    # Verifica se pip-audit está instalado
    try:
        import pip_audit
    except ImportError:
        print("❌ pip-audit não está instalado!")
        print("   Execute: pip install pip-audit")
        return False
    
    # Executa pip-audit
    result = run_command("pip-audit --format json", "Executando pip-audit")
    
    if result:
        try:
            audit_data = json.loads(result)
            vulnerabilities = audit_data.get('vulnerabilities', [])
            
            if vulnerabilities:
                print(f"\n⚠️  ENCONTRADAS {len(vulnerabilities)} VULNERABILIDADES:")
                for vuln in vulnerabilities:
                    print(f"   📦 {vuln.get('package', {}).get('name', 'N/A')}")
                    print(f"      Versão: {vuln.get('package', {}).get('version', 'N/A')}")
                    print(f"      Severidade: {vuln.get('severity', 'N/A')}")
                    print(f"      Descrição: {vuln.get('description', 'N/A')[:100]}...")
                    print()
                return False
            else:
                print("✅ Nenhuma vulnerabilidade encontrada!")
                return True
        except json.JSONDecodeError:
            print("❌ Erro ao processar resultado do pip-audit")
            return False
    
    return False

def check_npm_audit():
    """Executa npm audit para verificar vulnerabilidades Node.js."""
    print("\n🔍 AUDITORIA DE DEPENDÊNCIAS NODE.JS")
    print("=" * 50)
    
    # Verifica se package.json existe
    if not Path("package.json").exists():
        print("❌ package.json não encontrado!")
        return False
    
    # Executa npm audit
    result = run_command("npm audit --json", "Executando npm audit")
    
    if result:
        try:
            audit_data = json.loads(result)
            vulnerabilities = audit_data.get('vulnerabilities', {})
            
            if vulnerabilities:
                print(f"\n⚠️  ENCONTRADAS {len(vulnerabilities)} VULNERABILIDADES:")
                for pkg_name, vuln_info in vulnerabilities.items():
                    print(f"   📦 {pkg_name}")
                    print(f"      Versão: {vuln_info.get('version', 'N/A')}")
                    print(f"      Severidade: {vuln_info.get('severity', 'N/A')}")
                    print(f"      Título: {vuln_info.get('title', 'N/A')}")
                    print()
                return False
            else:
                print("✅ Nenhuma vulnerabilidade encontrada!")
                return True
        except json.JSONDecodeError:
            print("❌ Erro ao processar resultado do npm audit")
            return False
    
    return False

def check_safety():
    """Executa safety para verificar vulnerabilidades Python."""
    print("\n🔍 AUDITORIA DE SEGURANÇA PYTHON")
    print("=" * 50)
    
    # Verifica se safety está instalado
    try:
        import safety
    except ImportError:
        print("❌ safety não está instalado!")
        print("   Execute: pip install safety")
        return False
    
    # Executa safety
    result = run_command("safety check --json", "Executando safety check")
    
    if result:
        try:
            safety_data = json.loads(result)
            vulnerabilities = safety_data.get('vulnerabilities', [])
            
            if vulnerabilities:
                print(f"\n⚠️  ENCONTRADAS {len(vulnerabilities)} VULNERABILIDADES:")
                for vuln in vulnerabilities:
                    print(f"   📦 {vuln.get('package', 'N/A')}")
                    print(f"      Versão: {vuln.get('installed_version', 'N/A')}")
                    print(f"      Vulnerável: {vuln.get('vulnerable_spec', 'N/A')}")
                    print(f"      Descrição: {vuln.get('description', 'N/A')[:100]}...")
                    print()
                return False
            else:
                print("✅ Nenhuma vulnerabilidade encontrada!")
                return True
        except json.JSONDecodeError:
            print("❌ Erro ao processar resultado do safety")
            return False
    
    return False

def generate_report():
    """Gera relatório de auditoria."""
    print("\n📊 GERANDO RELATÓRIO DE AUDITORIA")
    print("=" * 50)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "python_audit": check_pip_audit(),
        "nodejs_audit": check_npm_audit(),
        "safety_check": check_safety()
    }
    
    # Salva relatório
    report_file = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Relatório salvo em: {report_file}")
    
    return report

def main():
    """Função principal."""
    print("🚀 AUDITORIA DE DEPENDÊNCIAS")
    print("=" * 50)
    
    # Gera relatório
    report = generate_report()
    
    # Resumo
    print("\n📋 RESUMO DA AUDITORIA")
    print("=" * 50)
    
    all_passed = all([
        report["python_audit"],
        report["nodejs_audit"],
        report["safety_check"]
    ])
    
    if all_passed:
        print("✅ TODAS AS AUDITORIAS PASSARAM!")
        print("   Suas dependências estão seguras.")
    else:
        print("⚠️  ALGUMAS AUDITORIAS FALHARAM!")
        print("   Verifique as vulnerabilidades acima.")
        print("\n🔧 RECOMENDAÇÕES:")
        print("   1. Atualize as dependências vulneráveis")
        print("   2. Execute: pip install --upgrade <pacote>")
        print("   3. Execute: npm update <pacote>")
        print("   4. Re-execute a auditoria após as atualizações")
    
    print(f"\n📄 Relatório completo: audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

if __name__ == "__main__":
    main() 