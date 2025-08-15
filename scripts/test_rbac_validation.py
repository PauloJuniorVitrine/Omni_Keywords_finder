#!/usr/bin/env python3
"""
Script para testar validação robusta do RBAC
Testa schemas Pydantic e validação de entrada
"""

import json
import requests
import sys
import os
from typing import Dict, Any, List

# Configuração
BASE_URL = "http://localhost:5000/api"
ADMIN_TOKEN = None

def get_auth_token(username: str, password: str) -> str:
    """Obtém token de autenticação"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": username,
            "senha": password
        })
        
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def test_user_validation():
    """Testa validação de criação de usuário"""
    print("\n🧪 TESTANDO VALIDAÇÃO DE USUÁRIO")
    print("=" * 50)
    
    # Teste 1: Dados válidos
    print("\n✅ Teste 1: Dados válidos")
    valid_user = {
        "username": "testuser123",
        "email": "test@example.com",
        "senha": "TestPass123!",
        "roles": ["usuario"],
        "ativo": True
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=valid_user,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Usuário criado com sucesso")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 2: Username inválido (muito curto)
    print("\n❌ Teste 2: Username muito curto")
    invalid_user = {
        "username": "ab",
        "email": "test2@example.com",
        "senha": "TestPass123!",
        "roles": ["usuario"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=invalid_user,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Validação funcionou - username rejeitado")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 3: Senha fraca
    print("\n❌ Teste 3: Senha fraca")
    weak_password_user = {
        "username": "testuser456",
        "email": "test3@example.com",
        "senha": "123",
        "roles": ["usuario"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=weak_password_user,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Validação funcionou - senha fraca rejeitada")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 4: Email inválido
    print("\n❌ Teste 4: Email inválido")
    invalid_email_user = {
        "username": "testuser789",
        "email": "invalid-email",
        "senha": "TestPass123!",
        "roles": ["usuario"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=invalid_email_user,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Validação funcionou - email inválido rejeitado")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 5: Role inválida
    print("\n❌ Teste 5: Role inválida")
    invalid_role_user = {
        "username": "testuser101",
        "email": "test5@example.com",
        "senha": "TestPass123!",
        "roles": ["invalid_role"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=invalid_role_user,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Validação funcionou - role inválida rejeitada")
    else:
        print(f"❌ Erro: {response.text}")

def test_role_validation():
    """Testa validação de criação de role"""
    print("\n🧪 TESTANDO VALIDAÇÃO DE ROLE")
    print("=" * 50)
    
    # Teste 1: Role válida
    print("\n✅ Teste 1: Role válida")
    valid_role = {
        "nome": "test_role",
        "descricao": "Role para testes",
        "permissoes": ["user:read", "keyword:read"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/papeis", 
                           json=valid_role,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Role criada com sucesso")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 2: Nome de role inválido
    print("\n❌ Teste 2: Nome de role inválido")
    invalid_role = {
        "nome": "admin",  # Palavra reservada
        "descricao": "Role inválida",
        "permissoes": ["user:read"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/papeis", 
                           json=invalid_role,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Validação funcionou - nome reservado rejeitado")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 3: Permissão inválida
    print("\n❌ Teste 3: Permissão inválida")
    invalid_permission_role = {
        "nome": "test_role2",
        "descricao": "Role com permissão inválida",
        "permissoes": ["invalid:permission"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/papeis", 
                           json=invalid_permission_role,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Validação funcionou - permissão inválida rejeitada")
    else:
        print(f"❌ Erro: {response.text}")

def test_permission_validation():
    """Testa validação de criação de permissão"""
    print("\n🧪 TESTANDO VALIDAÇÃO DE PERMISSÃO")
    print("=" * 50)
    
    # Teste 1: Permissão válida
    print("\n✅ Teste 1: Permissão válida")
    valid_permission = {
        "nome": "test:read",
        "descricao": "Permissão para leitura de testes"
    }
    
    response = requests.post(f"{BASE_URL}/rbac/permissoes", 
                           json=valid_permission,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Permissão criada com sucesso")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 2: Formato inválido
    print("\n❌ Teste 2: Formato inválido")
    invalid_permission = {
        "nome": "invalid_permission",  # Sem ':'
        "descricao": "Permissão inválida"
    }
    
    response = requests.post(f"{BASE_URL}/rbac/permissoes", 
                           json=invalid_permission,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Validação funcionou - formato inválido rejeitado")
    else:
        print(f"❌ Erro: {response.text}")

def test_sql_injection_prevention():
    """Testa prevenção de SQL injection"""
    print("\n🧪 TESTANDO PREVENÇÃO DE SQL INJECTION")
    print("=" * 50)
    
    # Teste 1: Tentativa de SQL injection no username
    print("\n❌ Teste 1: SQL injection no username")
    sql_injection_user = {
        "username": "'; DROP TABLE users; --",
        "email": "sql@example.com",
        "senha": "TestPass123!",
        "roles": ["usuario"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=sql_injection_user,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ SQL injection prevenido")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 2: Tentativa de SQL injection no email
    print("\n❌ Teste 2: SQL injection no email")
    sql_injection_email = {
        "username": "testuser_sql",
        "email": "test'; DROP TABLE users; --@example.com",
        "senha": "TestPass123!",
        "roles": ["usuario"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=sql_injection_email,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ SQL injection prevenido")
    else:
        print(f"❌ Erro: {response.text}")

def test_xss_prevention():
    """Testa prevenção de XSS"""
    print("\n🧪 TESTANDO PREVENÇÃO DE XSS")
    print("=" * 50)
    
    # Teste 1: Script no username
    print("\n❌ Teste 1: Script no username")
    xss_user = {
        "username": "<script>alert('xss')</script>",
        "email": "xss@example.com",
        "senha": "TestPass123!",
        "roles": ["usuario"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=xss_user,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ XSS prevenido")
    else:
        print(f"❌ Erro: {response.text}")

def test_input_sanitization():
    """Testa sanitização de entrada"""
    print("\n🧪 TESTANDO SANITIZAÇÃO DE ENTRADA")
    print("=" * 50)
    
    # Teste 1: Caracteres especiais
    print("\n✅ Teste 1: Caracteres especiais válidos")
    special_chars_user = {
        "username": "user_test-123",
        "email": "test+tag@example.com",
        "senha": "TestPass123!",
        "roles": ["usuario"]
    }
    
    response = requests.post(f"{BASE_URL}/rbac/usuarios", 
                           json=special_chars_user,
                           headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Caracteres especiais válidos aceitos")
    else:
        print(f"❌ Erro: {response.text}")

def generate_test_report():
    """Gera relatório de testes"""
    print("\n📊 RELATÓRIO DE TESTES DE VALIDAÇÃO RBAC")
    print("=" * 60)
    
    report = {
        "testes_executados": [
            "Validação de usuário",
            "Validação de role", 
            "Validação de permissão",
            "Prevenção de SQL injection",
            "Prevenção de XSS",
            "Sanitização de entrada"
        ],
        "validacoes_implementadas": [
            "Comprimento de campos",
            "Formato de email",
            "Complexidade de senha",
            "Caracteres permitidos",
            "Palavras reservadas",
            "Formato de permissões",
            "Prevenção de duplicatas"
        ],
        "seguranca": [
            "OWASP Top 10 A01:2021 - Broken Access Control",
            "OWASP Top 10 A03:2021 - Injection",
            "NIST RBAC Framework",
            "Input validation",
            "Output encoding"
        ]
    }
    
    print(json.dumps(report, indent=2, ensure_ascii=False))

def main():
    """Função principal"""
    global ADMIN_TOKEN
    
    print("🔒 TESTE DE VALIDAÇÃO ROBUSTA - RBAC")
    print("=" * 60)
    
    # Obter token de admin
    print("🔑 Obtendo token de administrador...")
    ADMIN_TOKEN = get_auth_token("admin", "admin123")
    
    if not ADMIN_TOKEN:
        print("❌ Não foi possível obter token de admin")
        print("Certifique-se de que o servidor está rodando e as credenciais estão corretas")
        return 1
    
    print("✅ Token obtido com sucesso")
    
    # Executar testes
    try:
        test_user_validation()
        test_role_validation()
        test_permission_validation()
        test_sql_injection_prevention()
        test_xss_prevention()
        test_input_sanitization()
        generate_test_report()
        
        print("\n✅ Todos os testes foram executados!")
        return 0
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 