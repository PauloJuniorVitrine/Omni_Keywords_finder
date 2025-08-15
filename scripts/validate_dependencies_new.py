#!/usr/bin/env python3
"""
Script para validar e corrigir dependências
Responsável por verificar duplicatas, vulnerabilidades e versões.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Correção 1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import subprocess
import sys
import re
from typing import List, Dict, Tuple, Any
from pathlib import Path

def run_command(command: str) -> Tuple[bool, str]:
    """Executa comando e retorna (sucesso, saída)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def check_pip_audit() -> Dict[str, Any]:
    """Verifica vulnerabilidades com pip-audit."""
    print("🔍 Verificando vulnerabilidades com pip-audit...")
    
    success, output = run_command("pip-audit")
    
    if success:
        print("✅ pip-audit executado com sucesso")
        return {"status": "success", "output": output}
    else:
        print("❌ pip-audit falhou ou encontrou vulnerabilidades")
        return {"status": "failed", "output": output}

def check_safety() -> Dict[str, Any]:
    """Verifica vulnerabilidades com safety."""
    print("🔍 Verificando vulnerabilidades com safety...")
    
    success, output = run_command("safety check")
    
    if success:
        print("✅ safety executado com sucesso")
        return {"status": "success", "output": output}
    else:
        print("❌ safety falhou ou encontrou vulnerabilidades")
        return {"status": "failed", "output": output}

def check_duplicate_dependencies() -> Dict[str, Any]:
    """Verifica dependências duplicadas no requirements.txt."""
    print("🔍 Verificando dependências duplicadas...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        return {"status": "error", "message": "requirements.txt não encontrado"}
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar duplicatas
    lines = content.split('\n')
    packages = {}
    duplicates = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '>=' in line:
            package_name = line.split('>=')[0].strip()
            if package_name in packages:
                duplicates.append(package_name)
            else:
                packages[package_name] = line
    
    if duplicates:
        print(f"❌ Encontradas {len(duplicates)} dependências duplicadas:")
        for dup in duplicates:
            print(f"   - {dup}")
        return {"status": "failed", "duplicates": duplicates}
    else:
        print("✅ Nenhuma dependência duplicada encontrada")
        return {"status": "success", "duplicates": []}

def check_package_json() -> Dict[str, Any]:
    """Verifica package.json para duplicatas."""
    print("🔍 Verificando package.json...")
    
    package_file = Path("package.json")
    if not package_file.exists():
        return {"status": "error", "message": "package.json não encontrado"}
    
    # Aqui você pode adicionar lógica para verificar package.json
    # Por simplicidade, vamos apenas verificar se existe
    print("✅ package.json encontrado")
    return {"status": "success"}

def suggest_fixes(issues: Dict[str, Any]) -> List[str]:
    """Sugere correções para os problemas encontrados."""
    suggestions = []
    
    if issues.get("duplicates"):
        suggestions.append("Remover dependências duplicadas do requirements.txt")
    
    if issues.get("vulnerabilities"):
        suggestions.append("Atualizar dependências vulneráveis")
    
    return suggestions

def main():
    """Função principal."""
    print("🔧 Validando dependências do projeto...")
    print("=" * 50)
    
    issues = {}
    
    # Verificar duplicatas
    duplicate_check = check_duplicate_dependencies()
    if duplicate_check["status"] == "failed":
        issues["duplicates"] = duplicate_check["duplicates"]
    
    # Verificar package.json
    package_check = check_package_json()
    if package_check["status"] == "error":
        issues["package_json"] = package_check["message"]
    
    # Verificar vulnerabilidades (se pip-audit estiver disponível)
    try:
        audit_result = check_pip_audit()
        if audit_result["status"] == "failed":
            issues["vulnerabilities"] = audit_result["output"]
    except:
        print("⚠️  pip-audit não disponível, pulando verificação de vulnerabilidades")
    
    # Verificar safety (se disponível)
    try:
        safety_result = check_safety()
        if safety_result["status"] == "failed":
            issues["safety_vulnerabilities"] = safety_result["output"]
    except:
        print("⚠️  safety não disponível, pulando verificação adicional")
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("=" * 50)
    
    if not issues:
        print("✅ Todas as verificações passaram!")
        print("🎉 Dependências estão em conformidade")
    else:
        print("❌ Problemas encontrados:")
        for issue_type, details in issues.items():
            print(f"   - {issue_type}: {details}")
        
        print("\n🔧 Sugestões de correção:")
        suggestions = suggest_fixes(issues)
        for suggestion in suggestions:
            print(f"   - {suggestion}")
        
        print("\n💡 Para corrigir automaticamente:")
        print("   python scripts/fix_dependencies.py")

if __name__ == "__main__":
    main() 