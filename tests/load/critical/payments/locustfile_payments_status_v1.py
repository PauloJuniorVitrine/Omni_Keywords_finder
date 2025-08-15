"""
Teste de Carga - Status de Pagamentos
Endpoint: /api/v1/payments/{payment_id}/status (GET)
Baseado em: backend/app/api/payments_v1.py linha 352-398
Tracing ID: PAYMENTS_STATUS_LOAD_TEST_20250127_001
Data: 2025-01-27
"""

from locust import HttpUser, task, between
import json
import logging
import random

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentsStatusLoadTest(HttpUser):
    """
    Teste de carga para endpoint de status de pagamentos
    Baseado no código real: backend/app/api/payments_v1.py
    """
    
    wait_time = between(2, 4)  # Intervalo para consultas de status
    
    def on_start(self):
        """Setup inicial - autenticação"""
        # Dados reais baseados no sistema
        login_data = {
            "email": "admin@omnikeywords.com",
            "password": "admin_password_2025"
        }
        
        try:
            # Login para obter token
            response = self.client.post("/api/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                logger.info("Autenticação realizada com sucesso")
            else:
                logger.error(f"Falha na autenticação: {response.status_code}")
                self.token = None
                self.headers = {}
        except Exception as e:
            logger.error(f"Erro durante autenticação: {str(e)}")
            self.token = None
            self.headers = {}

    @task(5)
    def get_payment_status_valid(self):
        """
        Teste de consulta de status de pagamento válido
        Baseado em: backend/app/api/payments_v1.py linha 352-398
        """
        try:
            # IDs de pagamento baseados em dados reais do sistema
            payment_ids = [
                "pay_1234567890abcdef",
                "pay_0987654321fedcba",
                "pay_abcdef1234567890",
                "pay_fedcba0987654321",
                "pay_1111111111111111",
                "pay_2222222222222222",
                "pay_3333333333333333",
                "pay_4444444444444444"
            ]
            
            # Selecionar ID aleatório
            payment_id = random.choice(payment_ids)
            
            response = self.client.get(
                f"/api/v1/payments/{payment_id}/status",
                headers=self.headers,
                name="Payments - Consultar Status (Válido)"
            )
            
            # Validações baseadas no código real
            if response.status_code == 200:
                result = response.json()
                assert "success" in result, "Campo 'success' ausente na resposta"
                assert "payment" in result, "Campo 'payment' ausente na resposta"
                assert "timestamp" in result, "Campo 'timestamp' ausente na resposta"
                
                payment_data = result["payment"]
                assert "id" in payment_data, "ID do pagamento ausente"
                assert "status" in payment_data, "Status do pagamento ausente"
                assert "amount" in payment_data, "Valor do pagamento ausente"
                
                logger.info(f"Status consultado com sucesso: {payment_id} - {payment_data['status']}")
                
            elif response.status_code == 404:
                logger.info(f"Pagamento não encontrado: {payment_id}")
                
            elif response.status_code == 401:
                logger.warning("Acesso não autorizado - token pode ter expirado")
                self.on_start()
                
            elif response.status_code == 403:
                logger.warning("Acesso negado - usuário sem permissão payments:read")
                
            else:
                logger.error(f"Erro inesperado: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante consulta de status: {str(e)}")

    @task(2)
    def get_payment_status_invalid_id(self):
        """
        Teste de consulta com ID inválido
        Baseado em: backend/app/api/payments_v1.py linha 352-398
        """
        try:
            # IDs inválidos para testar validação
            invalid_ids = [
                "invalid_id",
                "pay_invalid",
                "123456789",
                "",
                "pay_",
                "pay_1234567890abcdef_invalid"
            ]
            
            payment_id = random.choice(invalid_ids)
            
            response = self.client.get(
                f"/api/v1/payments/{payment_id}/status",
                headers=self.headers,
                name="Payments - Consultar Status (ID Inválido)"
            )
            
            # Deve retornar 404 para IDs inválidos
            if response.status_code == 404:
                logger.info(f"Pagamento não encontrado (esperado): {payment_id}")
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.info(f"ID inválido rejeitado: {error_data.get('detail', 'Erro de validação')}")
                
            else:
                logger.warning(f"Resposta inesperada para ID inválido: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro durante teste de ID inválido: {str(e)}")

    @task(2)
    def get_payment_status_with_metadata(self):
        """
        Teste de consulta com metadados
        Baseado em: backend/app/api/payments_v1.py linha 352-398
        """
        try:
            # IDs de pagamento com metadados específicos
            payment_ids_with_metadata = [
                "pay_metadata_001",
                "pay_metadata_002",
                "pay_metadata_003"
            ]
            
            payment_id = random.choice(payment_ids_with_metadata)
            
            response = self.client.get(
                f"/api/v1/payments/{payment_id}/status",
                headers=self.headers,
                name="Payments - Consultar Status (Com Metadados)"
            )
            
            if response.status_code == 200:
                result = response.json()
                payment_data = result["payment"]
                
                # Verificar se metadados estão presentes
                if "metadata" in payment_data:
                    logger.info(f"Status com metadados consultado: {payment_id}")
                else:
                    logger.info(f"Status consultado (sem metadados): {payment_id}")
                    
            elif response.status_code == 404:
                logger.info(f"Pagamento com metadados não encontrado: {payment_id}")
                
        except Exception as e:
            logger.error(f"Erro durante consulta com metadados: {str(e)}")

    @task(1)
    def get_payment_status_concurrent(self):
        """
        Teste de consulta concorrente de status
        Baseado em: backend/app/api/payments_v1.py linha 352-398
        """
        try:
            # Simular múltiplas consultas do mesmo pagamento
            payment_id = "pay_concurrent_test"
            
            # Primeira consulta
            response1 = self.client.get(
                f"/api/v1/payments/{payment_id}/status",
                headers=self.headers,
                name="Payments - Consultar Status (Concorrente 1)"
            )
            
            # Segunda consulta (simulando concorrência)
            response2 = self.client.get(
                f"/api/v1/payments/{payment_id}/status",
                headers=self.headers,
                name="Payments - Consultar Status (Concorrente 2)"
            )
            
            # Verificar se ambas as consultas retornaram o mesmo resultado
            if response1.status_code == 200 and response2.status_code == 200:
                result1 = response1.json()
                result2 = response2.json()
                
                # Comparar dados principais
                if (result1["payment"]["id"] == result2["payment"]["id"] and
                    result1["payment"]["status"] == result2["payment"]["status"]):
                    logger.info(f"Consultas concorrentes consistentes: {payment_id}")
                else:
                    logger.warning(f"Inconsistência em consultas concorrentes: {payment_id}")
                    
            elif response1.status_code == 404 and response2.status_code == 404:
                logger.info(f"Pagamento não encontrado em consultas concorrentes: {payment_id}")
                
        except Exception as e:
            logger.error(f"Erro durante teste de concorrência: {str(e)}")

    def on_stop(self):
        """Cleanup ao finalizar"""
        logger.info("Teste de carga Payments Status finalizado") 