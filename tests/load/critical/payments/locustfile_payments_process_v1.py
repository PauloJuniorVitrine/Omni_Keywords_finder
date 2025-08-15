"""
Teste de Carga - Processamento de Pagamentos
Endpoint: /api/v1/payments/process (POST)
Baseado em: backend/app/api/payments_v1.py linha 40-100
Tracing ID: PAYMENTS_PROCESS_LOAD_TEST_20250127_001
Data: 2025-01-27
"""

from locust import HttpUser, task, between
import json
import logging
import random

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentsProcessLoadTest(HttpUser):
    """
    Teste de carga para endpoint de processamento de pagamentos
    Baseado no código real: backend/app/api/payments_v1.py
    """
    
    wait_time = between(3, 6)  # Intervalo maior para operações críticas de pagamento
    
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

    @task(4)
    def process_payment_credit_card(self):
        """
        Teste de processamento de pagamento com cartão de crédito
        Baseado em: backend/app/api/payments_v1.py linha 40-100
        """
        try:
            # Dados baseados em pagamentos reais do sistema
            payment_data = {
                "payment_id": f"pay_test_{random.randint(10000, 99999)}",
                "amount": random.choice([1000, 2500, 5000, 10000]),  # Em centavos
                "currency": "BRL",
                "payment_method": "credit_card",
                "payment_method_data": {
                    "card_number": "4242424242424242",  # Cartão de teste Stripe
                    "exp_month": "12",
                    "exp_year": "2025",
                    "cvc": "123"
                },
                "customer_data": {
                    "name": "João Silva",
                    "email": "joao.silva@example.com",
                    "document": "12345678901"
                },
                "metadata": {
                    "order_id": f"order_{random.randint(1000, 9999)}",
                    "product": "Premium Plan"
                }
            }
            
            response = self.client.post(
                "/api/v1/payments/process",
                headers=self.headers,
                json=payment_data,
                name="Payments - Processar Pagamento (Cartão)"
            )
            
            # Validações baseadas no código real
            if response.status_code == 200:
                result = response.json()
                assert result["success"] == True, "Pagamento não foi bem-sucedido"
                assert "payment_id" in result, "ID do pagamento não retornado"
                assert "status" in result, "Status do pagamento não retornado"
                assert "timestamp" in result, "Timestamp não retornado"
                
                logger.info(f"Pagamento processado com sucesso: {result['payment_id']}")
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.warning(f"Pagamento rejeitado: {error_data.get('message', 'Erro desconhecido')}")
                
            elif response.status_code == 401:
                logger.warning("Acesso não autorizado - token pode ter expirado")
                self.on_start()
                
            elif response.status_code == 403:
                logger.warning("Acesso negado - usuário sem permissão payments:process")
                
            else:
                logger.error(f"Erro inesperado: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante processamento de pagamento: {str(e)}")

    @task(2)
    def process_payment_pix(self):
        """
        Teste de processamento de pagamento PIX
        Baseado em: backend/app/api/payments_v1.py linha 40-100
        """
        try:
            # Dados baseados em pagamentos PIX reais
            payment_data = {
                "payment_id": f"pay_pix_{random.randint(10000, 99999)}",
                "amount": random.choice([500, 1000, 2000, 5000]),  # Em centavos
                "currency": "BRL",
                "payment_method": "pix",
                "payment_method_data": {
                    "pix_key": "joao.silva@example.com",
                    "pix_key_type": "email"
                },
                "customer_data": {
                    "name": "Maria Santos",
                    "email": "maria.santos@example.com",
                    "document": "98765432100"
                },
                "metadata": {
                    "order_id": f"order_pix_{random.randint(1000, 9999)}",
                    "product": "Basic Plan"
                }
            }
            
            response = self.client.post(
                "/api/v1/payments/process",
                headers=self.headers,
                json=payment_data,
                name="Payments - Processar Pagamento (PIX)"
            )
            
            if response.status_code == 200:
                result = response.json()
                assert result["success"] == True, "Pagamento PIX não foi bem-sucedido"
                assert "payment_id" in result, "ID do pagamento não retornado"
                
                logger.info(f"Pagamento PIX processado com sucesso: {result['payment_id']}")
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.warning(f"Pagamento PIX rejeitado: {error_data.get('message', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"Erro durante processamento de pagamento PIX: {str(e)}")

    @task(1)
    def process_payment_boleto(self):
        """
        Teste de processamento de pagamento Boleto
        Baseado em: backend/app/api/payments_v1.py linha 40-100
        """
        try:
            # Dados baseados em pagamentos Boleto reais
            payment_data = {
                "payment_id": f"pay_boleto_{random.randint(10000, 99999)}",
                "amount": random.choice([1500, 3000, 7500, 15000]),  # Em centavos
                "currency": "BRL",
                "payment_method": "boleto",
                "payment_method_data": {
                    "due_date": "2025-02-15",
                    "instructions": ["Pagável em qualquer banco até o vencimento"]
                },
                "customer_data": {
                    "name": "Pedro Oliveira",
                    "email": "pedro.oliveira@example.com",
                    "document": "11122233344",
                    "address": {
                        "street": "Rua das Flores, 123",
                        "city": "São Paulo",
                        "state": "SP",
                        "zip_code": "01234-567"
                    }
                },
                "metadata": {
                    "order_id": f"order_boleto_{random.randint(1000, 9999)}",
                    "product": "Enterprise Plan"
                }
            }
            
            response = self.client.post(
                "/api/v1/payments/process",
                headers=self.headers,
                json=payment_data,
                name="Payments - Processar Pagamento (Boleto)"
            )
            
            if response.status_code == 200:
                result = response.json()
                assert result["success"] == True, "Pagamento Boleto não foi bem-sucedido"
                assert "payment_id" in result, "ID do pagamento não retornado"
                
                logger.info(f"Pagamento Boleto processado com sucesso: {result['payment_id']}")
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.warning(f"Pagamento Boleto rejeitado: {error_data.get('message', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"Erro durante processamento de pagamento Boleto: {str(e)}")

    @task(1)
    def process_payment_invalid_data(self):
        """
        Teste de processamento com dados inválidos
        Baseado em: backend/app/api/payments_v1.py linha 40-100
        """
        try:
            # Dados inválidos para testar validação
            invalid_payment_data = {
                "payment_id": "",  # ID vazio
                "amount": -100,    # Valor negativo
                "currency": "XXX", # Moeda inválida
                "payment_method": "invalid_method",
                "customer_data": {
                    "name": "",    # Nome vazio
                    "email": "invalid-email"  # Email inválido
                }
            }
            
            response = self.client.post(
                "/api/v1/payments/process",
                headers=self.headers,
                json=invalid_payment_data,
                name="Payments - Processar Pagamento (Dados Inválidos)"
            )
            
            # Deve retornar erro 400 para dados inválidos
            if response.status_code == 400:
                error_data = response.json()
                logger.info(f"Validação funcionando: {error_data.get('detail', 'Erro de validação')}")
                
            elif response.status_code == 422:
                error_data = response.json()
                logger.info(f"Validação Pydantic funcionando: {error_data}")
                
            else:
                logger.warning(f"Resposta inesperada para dados inválidos: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro durante teste de dados inválidos: {str(e)}")

    def on_stop(self):
        """Cleanup ao finalizar"""
        logger.info("Teste de carga Payments Process finalizado") 