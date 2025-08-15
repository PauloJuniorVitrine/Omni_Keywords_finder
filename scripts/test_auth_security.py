#!/usr/bin/env python3
"""
Script de teste para validar implementações de segurança de autenticação
Testa JWT, rate limiting, validação de entrada e logs de segurança
"""

import requests
import time
import json
import os
import sys
from typing import Dict, List, Any

class AuthSecurityTester:
    """Classe para testar segurança de autenticação"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado do teste"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_jwt_secret_validation(self):
        """Testa validação de JWT_SECRET_KEY"""
        print("\n🔐 Testando validação de JWT_SECRET_KEY...")
        
        # Teste 1: Verificar se JWT_SECRET_KEY está definida
        jwt_secret = os.getenv('JWT_SECRET_KEY')
        if not jwt_secret:
            self.log_test("JWT_SECRET_KEY definida", False, "Variável JWT_SECRET_KEY não está definida")
            return False
        
        # Teste 2: Verificar se não é a chave padrão
        if jwt_secret == 'troque-por-uma-chave-segura':
            self.log_test("JWT_SECRET_KEY não é padrão", False, "Usando chave padrão insegura")
            return False
        
        # Teste 3: Verificar comprimento mínimo
        if len(jwt_secret) < 32:
            self.log_test("JWT_SECRET_KEY comprimento", False, f"Chave muito curta: {len(jwt_secret)} caracteres")
            return False
        
        self.log_test("JWT_SECRET_KEY validação", True, f"Chave segura com {len(jwt_secret)} caracteres")
        return True
    
    def test_rate_limiting(self):
        """Testa rate limiting de autenticação"""
        print("\n🚦 Testando rate limiting...")
        
        # Teste 1: Tentativas normais de login
        for i in range(3):
            response = self.session.post(f"{self.base_url}/api/auth/login", 
                                       json={"username": "test", "senha": "test"})
            
            if response.status_code == 429:
                self.log_test("Rate limiting muito restritivo", False, f"Bloqueado na tentativa {i+1}")
                return False
        
        # Teste 2: Tentativas excessivas
        for i in range(10):
            response = self.session.post(f"{self.base_url}/api/auth/login", 
                                       json={"username": "test", "senha": "test"})
            
            if response.status_code == 429:
                self.log_test("Rate limiting funcionando", True, f"Bloqueado após {i+1} tentativas")
                return True
        
        self.log_test("Rate limiting", False, "Não bloqueou tentativas excessivas")
        return False
    
    def test_input_validation(self):
        """Testa validação de entrada"""
        print("\n🔍 Testando validação de entrada...")
        
        # Teste 1: Username muito curto
        response = self.session.post(f"{self.base_url}/api/auth/login", 
                                   json={"username": "ab", "senha": "test123"})
        
        if response.status_code == 400:
            self.log_test("Validação username curto", True, "Rejeitou username muito curto")
        else:
            self.log_test("Validação username curto", False, "Aceitou username muito curto")
        
        # Teste 2: Username com caracteres inválidos
        response = self.session.post(f"{self.base_url}/api/auth/login", 
                                   json={"username": "test<script>", "senha": "test123"})
        
        if response.status_code == 400:
            self.log_test("Validação caracteres especiais", True, "Rejeitou caracteres especiais")
        else:
            self.log_test("Validação caracteres especiais", False, "Aceitou caracteres especiais")
        
        # Teste 3: Senha muito curta
        response = self.session.post(f"{self.base_url}/api/auth/login", 
                                   json={"username": "testuser", "senha": "123"})
        
        if response.status_code == 400:
            self.log_test("Validação senha curta", True, "Rejeitou senha muito curta")
        else:
            self.log_test("Validação senha curta", False, "Aceitou senha muito curta")
        
        return True
    
    def test_security_headers(self):
        """Testa headers de segurança"""
        print("\n🛡️ Testando headers de segurança...")
        
        response = self.session.get(f"{self.base_url}/api/auth/login")
        
        # Verificar headers de segurança
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]
        
        for header in security_headers:
            if header in response.headers:
                self.log_test(f"Header {header}", True, f"Header {header} presente")
            else:
                self.log_test(f"Header {header}", False, f"Header {header} ausente")
        
        return True
    
    def test_logging(self):
        """Testa logs de segurança"""
        print("\n📝 Testando logs de segurança...")
        
        # Fazer algumas tentativas de login para gerar logs
        for i in range(3):
            self.session.post(f"{self.base_url}/api/auth/login", 
                            json={"username": f"testuser{i}", "senha": "wrongpassword"})
        
        # Verificar se logs foram gerados (simulação)
        log_file = "logs/security.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_content = f.read()
                if "login falhada" in log_content:
                    self.log_test("Logs de segurança", True, "Logs de tentativas falhadas encontrados")
                else:
                    self.log_test("Logs de segurança", False, "Logs de tentativas falhadas não encontrados")
        else:
            self.log_test("Arquivo de logs", False, "Arquivo de logs não encontrado")
        
        return True
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🔒 TESTE DE SEGURANÇA DE AUTENTICAÇÃO - OMNI KEYWORDS FINDER")
        print("=" * 70)
        
        tests = [
            self.test_jwt_secret_validation,
            self.test_rate_limiting,
            self.test_input_validation,
            self.test_security_headers,
            self.test_logging
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Erro: {str(e)}")
        
        # Resumo dos resultados
        self.print_summary()
        
        return self.test_results
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 70)
        print("📊 RESUMO DOS TESTES")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de testes: {total_tests}")
        print(f"✅ Passou: {passed_tests}")
        print(f"❌ Falhou: {failed_tests}")
        print(f"📈 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Salvar resultados em arquivo
        with open("test_results_auth_security.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Resultados salvos em: test_results_auth_security.json")

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    tester = AuthSecurityTester(base_url)
    results = tester.run_all_tests()
    
    # Retornar código de saída baseado nos resultados
    failed_tests = sum(1 for result in results if not result['success'])
    return 1 if failed_tests > 0 else 0

if __name__ == "__main__":
    exit(main()) 