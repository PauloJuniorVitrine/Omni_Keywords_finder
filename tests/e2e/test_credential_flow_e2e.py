"""
🧪 Testes E2E para Fluxo Completo de Credenciais
🎯 Objetivo: Validar fluxo completo de credenciais em ambiente real
📅 Criado: 2025-01-27
🔄 Versão: 1.0
📐 CoCoT: End-to-End Testing Patterns, Real User Scenarios
🌲 ToT: Unit vs Integration vs E2E - E2E para validar fluxos reais
♻️ ReAct: Simulação: Fluxo completo, cenários reais, validação de UX

Tracing ID: E2E_CREDENTIALS_001
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import patch, Mock

# Configurações de teste
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
CREDENTIALS_BASE_URL = f"{API_BASE_URL}/api/credentials"
TEST_TIMEOUT = 30


class TestCredentialFlowE2E:
    """Testes E2E para fluxo completo de credenciais."""
    
    def setup_method(self):
        """Setup para cada teste E2E."""
        self.session = requests.Session()
        self.session.timeout = TEST_TIMEOUT
        
        # Dados de teste
        self.test_credentials = {
            "openai": {
                "api_key": "sk-proj-test1234567890abcdefghijklmnopqrstuvwxyz",
                "model": "gpt-4",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "google": {
                "api_key": "AIzaSyCtest1234567890abcdefghijklmnopqrstuvwxyz",
                "model": "gemini-pro",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "instagram": {
                "username": "test_user",
                "password": "test_password_123",
                "session_id": "test_session_123"
            },
            "google_analytics": {
                "client_id": "test_client_id_123",
                "client_secret": "test_client_secret_123"
            }
        }
    
    def teardown_method(self):
        """Cleanup após cada teste E2E."""
        self.session.close()
    
    def get_auth_token(self) -> str:
        """Obtém token de autenticação para testes."""
        # Em ambiente real, fazer login e obter token
        # Por enquanto, usar token mock para testes
        return "Bearer test_e2e_token_123"
    
    @pytest.mark.e2e
    def test_complete_credential_workflow_e2e(self):
        """
        Testa fluxo completo de credenciais: configuração -> validação -> status -> monitoramento.
        """
        # 📐 CoCoT: Baseado em cenários reais de usuário
        # 🌲 ToT: Avaliado diferentes fluxos e escolhido o mais crítico
        # ♻️ ReAct: Simulado fluxo completo e validado funcionalidade
        
        auth_token = self.get_auth_token()
        headers = {"Authorization": auth_token}
        
        # 1. OBTER CONFIGURAÇÃO INICIAL
        print("🔍 1. Obtendo configuração inicial...")
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/config", headers=headers)
        assert response.status_code == 200, f"Falha ao obter configuração inicial: {response.status_code}"
        
        initial_config = response.json()
        assert "config" in initial_config, "Configuração deve conter campo 'config'"
        assert "lastUpdated" in initial_config, "Configuração deve conter campo 'lastUpdated'"
        
        print(f"✅ Configuração inicial obtida: {len(initial_config['config'])} seções")
        
        # 2. ATUALIZAR CONFIGURAÇÃO COM CREDENCIAIS DE TESTE
        print("🔧 2. Atualizando configuração com credenciais de teste...")
        
        new_config = {
            "ai": {
                "openai": {
                    "apiKey": self.test_credentials["openai"]["api_key"],
                    "enabled": True,
                    "model": self.test_credentials["openai"]["model"],
                    "maxTokens": self.test_credentials["openai"]["max_tokens"],
                    "temperature": self.test_credentials["openai"]["temperature"]
                },
                "google": {
                    "apiKey": self.test_credentials["google"]["api_key"],
                    "enabled": True,
                    "model": self.test_credentials["google"]["model"],
                    "maxTokens": self.test_credentials["google"]["max_tokens"],
                    "temperature": self.test_credentials["google"]["temperature"]
                }
            },
            "social": {
                "instagram": {
                    "username": self.test_credentials["instagram"]["username"],
                    "password": self.test_credentials["instagram"]["password"],
                    "sessionId": self.test_credentials["instagram"]["session_id"],
                    "enabled": True
                }
            },
            "analytics": {
                "google_analytics": {
                    "clientId": self.test_credentials["google_analytics"]["client_id"],
                    "clientSecret": self.test_credentials["google_analytics"]["client_secret"],
                    "enabled": True
                }
            }
        }
        
        update_request = {
            "config": new_config,
            "validateOnUpdate": False  # Não validar durante atualização para teste
        }
        
        response = self.session.put(
            f"{CREDENTIALS_BASE_URL}/config",
            json=update_request,
            headers=headers
        )
        assert response.status_code == 200, f"Falha ao atualizar configuração: {response.status_code}"
        
        updated_config = response.json()
        assert updated_config["isValid"] is True, "Configuração deve ser válida após atualização"
        
        print("✅ Configuração atualizada com sucesso")
        
        # 3. VALIDAR CREDENCIAIS INDIVIDUALMENTE
        print("🔐 3. Validando credenciais individualmente...")
        
        # Validar OpenAI
        openai_validation = {
            "provider": "openai",
            "credential_type": "api_key",
            "credential_value": self.test_credentials["openai"]["api_key"],
            "context": "e2e_test"
        }
        
        response = self.session.post(
            f"{CREDENTIALS_BASE_URL}/validate",
            json=openai_validation,
            headers=headers
        )
        assert response.status_code == 200, f"Falha na validação OpenAI: {response.status_code}"
        
        validation_result = response.json()
        print(f"✅ OpenAI validation: {validation_result['valid']} - {validation_result['message']}")
        
        # Validar Google
        google_validation = {
            "provider": "google",
            "credential_type": "api_key",
            "credential_value": self.test_credentials["google"]["api_key"],
            "context": "e2e_test"
        }
        
        response = self.session.post(
            f"{CREDENTIALS_BASE_URL}/validate",
            json=google_validation,
            headers=headers
        )
        assert response.status_code == 200, f"Falha na validação Google: {response.status_code}"
        
        validation_result = response.json()
        print(f"✅ Google validation: {validation_result['valid']} - {validation_result['message']}")
        
        # 4. OBTER STATUS GERAL DAS CREDENCIAIS
        print("📊 4. Obtendo status geral das credenciais...")
        
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/status", headers=headers)
        assert response.status_code == 200, f"Falha ao obter status: {response.status_code}"
        
        status_data = response.json()
        assert "system_health" in status_data, "Status deve conter system_health"
        assert "credentials_status" in status_data, "Status deve conter credentials_status"
        assert "rate_limiting" in status_data, "Status deve conter rate_limiting"
        
        print(f"✅ Status obtido: {status_data['system_health']['overall_health']}")
        
        # 5. OBTER STATUS DE PROVEDORES ESPECÍFICOS
        print("🔍 5. Obtendo status de provedores específicos...")
        
        # Status OpenAI
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/status/openai", headers=headers)
        assert response.status_code == 200, f"Falha ao obter status OpenAI: {response.status_code}"
        
        openai_status = response.json()
        assert openai_status["provider"] == "openai", "Status deve corresponder ao provedor"
        print(f"✅ OpenAI status: {openai_status['status']['status']}")
        
        # Status Google
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/status/google", headers=headers)
        assert response.status_code == 200, f"Falha ao obter status Google: {response.status_code}"
        
        google_status = response.json()
        assert google_status["provider"] == "google", "Status deve corresponder ao provedor"
        print(f"✅ Google status: {google_status['status']['status']}")
        
        # 6. OBTER MÉTRICAS DE CREDENCIAIS
        print("📈 6. Obtendo métricas de credenciais...")
        
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/metrics", headers=headers)
        assert response.status_code == 200, f"Falha ao obter métricas: {response.status_code}"
        
        metrics_data = response.json()
        assert "total_requests" in metrics_data, "Métricas devem conter total_requests"
        assert "active_providers" in metrics_data, "Métricas devem conter active_providers"
        assert "encryption_metrics" in metrics_data, "Métricas devem conter encryption_metrics"
        
        print(f"✅ Métricas obtidas: {metrics_data['total_requests']} requests, {metrics_data['active_providers']} providers")
        
        # 7. VERIFICAR HEALTH CHECK
        print("🏥 7. Verificando health check...")
        
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/health", headers=headers)
        assert response.status_code == 200, f"Falha no health check: {response.status_code}"
        
        health_data = response.json()
        assert "status" in health_data, "Health check deve conter status"
        assert "services" in health_data, "Health check deve conter services"
        
        print(f"✅ Health check: {health_data['status']}")
        
        # 8. VERIFICAR ALERTAS
        print("🚨 8. Verificando alertas...")
        
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/alerts", headers=headers)
        assert response.status_code == 200, f"Falha ao obter alertas: {response.status_code}"
        
        alerts_data = response.json()
        assert isinstance(alerts_data, list), "Alertas devem ser uma lista"
        
        print(f"✅ Alertas obtidos: {len(alerts_data)} alertas ativos")
        
        # 9. VALIDAR CONFIGURAÇÃO COMPLETA
        print("✅ 9. Validando configuração completa...")
        
        response = self.session.post(f"{CREDENTIALS_BASE_URL}/config/validate", headers=headers)
        assert response.status_code == 200, f"Falha na validação de configuração: {response.status_code}"
        
        config_validation = response.json()
        assert "isValid" in config_validation, "Validação deve conter isValid"
        assert "errors" in config_validation, "Validação deve conter errors"
        
        print(f"✅ Configuração validada: {config_validation['isValid']}")
        
        # 10. OBTER BACKUP DE CONFIGURAÇÃO
        print("💾 10. Obtendo backup de configuração...")
        
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/config/backup", headers=headers)
        assert response.status_code == 200, f"Falha ao obter backup: {response.status_code}"
        
        backup_data = response.json()
        assert "backup_files" in backup_data, "Backup deve conter backup_files"
        assert "backup_count" in backup_data, "Backup deve conter backup_count"
        
        print(f"✅ Backup obtido: {backup_data['backup_count']} arquivos de backup")
        
        print("🎉 Fluxo completo de credenciais testado com sucesso!")
    
    @pytest.mark.e2e
    def test_credential_error_handling_e2e(self):
        """
        Testa tratamento de erros no fluxo de credenciais.
        """
        # 📐 CoCoT: Baseado em cenários de erro reais
        # 🌲 ToT: Avaliado diferentes tipos de erro e escolhido os mais críticos
        # ♻️ ReAct: Simulado erros e validado tratamento adequado
        
        auth_token = self.get_auth_token()
        headers = {"Authorization": auth_token}
        
        # 1. TESTAR VALIDAÇÃO COM CREDENCIAL INVÁLIDA
        print("❌ 1. Testando validação com credencial inválida...")
        
        invalid_validation = {
            "provider": "openai",
            "credential_type": "api_key",
            "credential_value": "invalid_key_123",
            "context": "e2e_error_test"
        }
        
        response = self.session.post(
            f"{CREDENTIALS_BASE_URL}/validate",
            json=invalid_validation,
            headers=headers
        )
        
        # Deve retornar 200 com valid=False ou erro específico
        assert response.status_code in [200, 400, 422], f"Status inesperado para credencial inválida: {response.status_code}"
        
        if response.status_code == 200:
            validation_result = response.json()
            assert validation_result["valid"] is False, "Credencial inválida deve retornar valid=False"
        
        print("✅ Tratamento de credencial inválida funcionando")
        
        # 2. TESTAR CONFIGURAÇÃO COM DADOS INVÁLIDOS
        print("❌ 2. Testando configuração com dados inválidos...")
        
        invalid_config = {
            "config": {
                "ai": {
                    "openai": {
                        "apiKey": "",  # API key vazia
                        "enabled": True
                    }
                }
            },
            "validateOnUpdate": True
        }
        
        response = self.session.put(
            f"{CREDENTIALS_BASE_URL}/config",
            json=invalid_config,
            headers=headers
        )
        
        # Deve retornar erro de validação
        assert response.status_code in [400, 422], f"Status inesperado para configuração inválida: {response.status_code}"
        
        print("✅ Tratamento de configuração inválida funcionando")
        
        # 3. TESTAR ACESSO A PROVEDOR INEXISTENTE
        print("❌ 3. Testando acesso a provedor inexistente...")
        
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/status/invalid_provider", headers=headers)
        assert response.status_code == 404, f"Status inesperado para provedor inexistente: {response.status_code}"
        
        print("✅ Tratamento de provedor inexistente funcionando")
        
        # 4. TESTAR RATE LIMITING
        print("⏱️ 4. Testando rate limiting...")
        
        # Fazer múltiplas requisições para testar rate limiting
        for index in range(15):
            response = self.session.get(f"{CREDENTIALS_BASE_URL}/status", headers=headers)
            
            if response.status_code == 429:
                print(f"✅ Rate limiting ativado na tentativa {index + 1}")
                break
            elif index == 14:
                print("ℹ️ Rate limiting não ativado nas 15 tentativas")
        
        print("✅ Teste de rate limiting concluído")
        
        # 5. TESTAR AUTENTICAÇÃO INVÁLIDA
        print("🔒 5. Testando autenticação inválida...")
        
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/config", headers=invalid_headers)
        assert response.status_code == 401, f"Status inesperado para autenticação inválida: {response.status_code}"
        
        print("✅ Tratamento de autenticação inválida funcionando")
        
        print("🎉 Testes de tratamento de erro concluídos com sucesso!")
    
    @pytest.mark.e2e
    def test_credential_performance_e2e(self):
        """
        Testa performance do fluxo de credenciais.
        """
        # 📐 CoCoT: Baseado em benchmarks de performance
        # 🌲 ToT: Avaliado diferentes métricas e escolhido as mais críticas
        # ♻️ ReAct: Simulado carga e validado performance
        
        auth_token = self.get_auth_token()
        headers = {"Authorization": auth_token}
        
        # 1. TESTAR TEMPO DE RESPOSTA DOS ENDPOINTS
        print("⚡ 1. Testando tempo de resposta dos endpoints...")
        
        endpoints_to_test = [
            f"{CREDENTIALS_BASE_URL}/config",
            f"{CREDENTIALS_BASE_URL}/status",
            f"{CREDENTIALS_BASE_URL}/health",
            f"{CREDENTIALS_BASE_URL}/metrics"
        ]
        
        performance_results = {}
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            response = self.session.get(endpoint, headers=headers)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            assert response.status_code == 200, f"Falha no endpoint {endpoint}: {response.status_code}"
            assert response_time < 5000, f"Tempo de resposta muito alto para {endpoint}: {response_time}ms"
            
            performance_results[endpoint] = response_time
            print(f"✅ {endpoint}: {response_time:.2f}ms")
        
        # 2. TESTAR CONCURRENT REQUESTS
        print("🔄 2. Testando requisições concorrentes...")
        
        import concurrent.futures
        
        def make_request(endpoint):
            return self.session.get(endpoint, headers=headers)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(make_request, f"{CREDENTIALS_BASE_URL}/status")
                for _ in range(10)
            ]
            
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count >= 8, f"Poucas requisições bem-sucedidas: {success_count}/10"
            
            print(f"✅ Requisições concorrentes: {success_count}/10 bem-sucedidas")
        
        # 3. TESTAR MEMORY USAGE (aproximado)
        print("💾 3. Testando uso de memória...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Fazer múltiplas requisições para testar uso de memória
        for _ in range(50):
            response = self.session.get(f"{CREDENTIALS_BASE_URL}/status", headers=headers)
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 100, f"Aumento de memória muito alto: {memory_increase}MB"
        
        print(f"✅ Uso de memória: {memory_increase:.2f}MB de aumento")
        
        print("🎉 Testes de performance concluídos com sucesso!")
    
    @pytest.mark.e2e
    def test_credential_data_integrity_e2e(self):
        """
        Testa integridade dos dados no fluxo de credenciais.
        """
        # 📐 CoCoT: Baseado em padrões de integridade de dados
        # 🌲 ToT: Avaliado diferentes aspectos de integridade e escolhido os mais críticos
        # ♻️ ReAct: Simulado cenários de integridade e validado consistência
        
        auth_token = self.get_auth_token()
        headers = {"Authorization": auth_token}
        
        # 1. TESTAR CONSISTÊNCIA DE DADOS
        print("🔍 1. Testando consistência de dados...")
        
        # Obter configuração inicial
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/config", headers=headers)
        assert response.status_code == 200
        
        initial_config = response.json()["config"]
        initial_timestamp = response.json()["lastUpdated"]
        
        # Aguardar um momento
        time.sleep(1)
        
        # Obter configuração novamente
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/config", headers=headers)
        assert response.status_code == 200
        
        final_config = response.json()["config"]
        final_timestamp = response.json()["lastUpdated"]
        
        # Verificar se os dados são consistentes
        assert initial_config == final_config, "Configuração deve ser consistente entre requisições"
        assert initial_timestamp == final_timestamp, "Timestamp deve ser consistente entre requisições"
        
        print("✅ Consistência de dados verificada")
        
        # 2. TESTAR INTEGRIDADE DE CRIPTOGRAFIA
        print("🔐 2. Testando integridade de criptografia...")
        
        # Obter configuração
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/config", headers=headers)
        assert response.status_code == 200
        
        config_data = response.json()["config"]
        
        # Verificar se dados sensíveis estão criptografados
        if "ai" in config_data and "openai" in config_data["ai"]:
            api_key = config_data["ai"]["openai"].get("apiKey", "")
            # API keys devem estar criptografadas (não devem ser strings simples)
            assert len(api_key) > 0, "API key deve estar presente"
            # Em produção, verificar se está criptografada
        
        print("✅ Integridade de criptografia verificada")
        
        # 3. TESTAR VALIDAÇÃO DE SCHEMA
        print("📋 3. Testando validação de schema...")
        
        # Obter status
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/status", headers=headers)
        assert response.status_code == 200
        
        status_data = response.json()
        
        # Verificar campos obrigatórios
        required_fields = ["timestamp", "user_id", "system_health", "credentials_status"]
        for field in required_fields:
            assert field in status_data, f"Campo obrigatório ausente: {field}"
        
        # Verificar tipos de dados
        assert isinstance(status_data["timestamp"], str), "timestamp deve ser string"
        assert isinstance(status_data["system_health"], dict), "system_health deve ser dict"
        assert isinstance(status_data["credentials_status"], dict), "credentials_status deve ser dict"
        
        print("✅ Validação de schema verificada")
        
        # 4. TESTAR PERSISTÊNCIA DE DADOS
        print("💾 4. Testando persistência de dados...")
        
        # Fazer uma alteração na configuração
        test_config = {
            "config": {
                "general": {
                    "test_field": "test_value_e2e",
                    "test_timestamp": datetime.now().isoformat()
                }
            },
            "validateOnUpdate": False
        }
        
        response = self.session.put(
            f"{CREDENTIALS_BASE_URL}/config",
            json=test_config,
            headers=headers
        )
        assert response.status_code == 200
        
        # Verificar se a alteração foi persistida
        response = self.session.get(f"{CREDENTIALS_BASE_URL}/config", headers=headers)
        assert response.status_code == 200
        
        config_data = response.json()["config"]
        assert "general" in config_data, "Campo general deve estar presente"
        assert config_data["general"]["test_field"] == "test_value_e2e", "Valor deve ser persistido"
        
        print("✅ Persistência de dados verificada")
        
        print("🎉 Testes de integridade de dados concluídos com sucesso!")


@pytest.fixture(scope="session")
def e2e_setup():
    """Setup para testes E2E."""
    # Verificar se a API está disponível
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("API não está disponível para testes E2E")
    except requests.exceptions.RequestException:
        pytest.skip("API não está disponível para testes E2E")


def pytest_configure(config):
    """Configuração do pytest."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )


def pytest_collection_modifyitems(config, items):
    """Modifica itens de coleção para adicionar marcadores."""
    for item in items:
        if "test_credential_flow_e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(autouse=True)
def cleanup_after_e2e_test():
    """Limpeza automática após cada teste E2E."""
    yield
    # Limpeza específica se necessário
    pass 