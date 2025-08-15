"""
Testes unitários para validação robusta de pagamentos
Prompt: Validação robusta de pagamentos
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from backend.app.schemas.payment_schemas import (
    PaymentCardSchema, PixSchema, BoletoSchema, PaymentMethodSchema,
    PaymentCreateSchema, PaymentUpdateSchema, PaymentFilterSchema
)

class TestPaymentCardSchema:
    """Testes para validação de cartão de crédito"""
    
    def test_valid_card(self):
        """Testa cartão válido"""
        card_data = {
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': 2026,
            'cvc': '123',
            'name': 'João Silva'
        }
        
        card = PaymentCardSchema(**card_data)
        assert card.number == '4242424242424242'
        assert card.exp_month == 12
        assert card.exp_year == 2026
        assert card.cvc == '123'
        assert card.name == 'João Silva'
    
    def test_invalid_card_number(self):
        """Testa número de cartão inválido"""
        card_data = {
            'number': '1234567890123456',  # Número inválido
            'exp_month': 12,
            'exp_year': 2026,
            'cvc': '123',
            'name': 'João Silva'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentCardSchema(**card_data)
        
        assert 'number' in str(exc_info.value)
    
    def test_invalid_cvc(self):
        """Testa CVC inválido"""
        card_data = {
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': 2026,
            'cvc': 'abc',  # CVC com letras
            'name': 'João Silva'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentCardSchema(**card_data)
        
        assert 'CVC deve conter apenas números' in str(exc_info.value)
    
    def test_expired_card(self):
        """Testa cartão expirado"""
        card_data = {
            'number': '4242424242424242',
            'exp_month': 1,
            'exp_year': 2020,  # Ano passado
            'cvc': '123',
            'name': 'João Silva'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentCardSchema(**card_data)
        
        assert 'Cartão expirado' in str(exc_info.value)
    
    def test_sanitized_name(self):
        """Testa sanitização do nome"""
        card_data = {
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': 2026,
            'cvc': '123',
            'name': 'João <script>alert("xss")</script> Silva'  # Nome com XSS
        }
        
        card = PaymentCardSchema(**card_data)
        assert card.name == 'João Silva'  # XSS removido
    
    def test_invalid_exp_month(self):
        """Testa mês de expiração inválido"""
        card_data = {
            'number': '4242424242424242',
            'exp_month': 13,  # Mês inválido
            'exp_year': 2026,
            'cvc': '123',
            'name': 'João Silva'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentCardSchema(**card_data)
        
        assert 'exp_month' in str(exc_info.value)

class TestPixSchema:
    """Testes para validação de PIX"""
    
    def test_valid_cpf_pix(self):
        """Testa PIX com CPF válido"""
        pix_data = {
            'key_type': 'cpf',
            'key_value': '12345678901'
        }
        
        pix = PixSchema(**pix_data)
        assert pix.key_type == 'cpf'
        assert pix.key_value == '12345678901'
    
    def test_valid_email_pix(self):
        """Testa PIX com email válido"""
        pix_data = {
            'key_type': 'email',
            'key_value': 'teste@exemplo.com'
        }
        
        pix = PixSchema(**pix_data)
        assert pix.key_type == 'email'
        assert pix.key_value == 'teste@exemplo.com'
    
    def test_valid_phone_pix(self):
        """Testa PIX com telefone válido"""
        pix_data = {
            'key_type': 'phone',
            'key_value': '+5511999999999'
        }
        
        pix = PixSchema(**pix_data)
        assert pix.key_type == 'phone'
        assert pix.key_value == '+5511999999999'
    
    def test_invalid_key_type(self):
        """Testa tipo de chave PIX inválido"""
        pix_data = {
            'key_type': 'invalid',
            'key_value': '12345678901'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PixSchema(**pix_data)
        
        assert 'Tipo de chave PIX inválido' in str(exc_info.value)
    
    def test_invalid_cpf_format(self):
        """Testa CPF com formato inválido"""
        pix_data = {
            'key_type': 'cpf',
            'key_value': '123.456.789-01'  # Formato com pontos
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PixSchema(**pix_data)
        
        assert 'CPF deve ter 11 dígitos' in str(exc_info.value)
    
    def test_invalid_email_format(self):
        """Testa email com formato inválido"""
        pix_data = {
            'key_type': 'email',
            'key_value': 'email-invalido'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PixSchema(**pix_data)
        
        assert 'Email inválido' in str(exc_info.value)

class TestBoletoSchema:
    """Testes para validação de boleto"""
    
    def test_valid_boleto(self):
        """Testa boleto válido"""
        boleto_data = {
            'customer_name': 'João Silva',
            'customer_document': '12345678901',
            'customer_email': 'joao@exemplo.com',
            'due_date': datetime.now() + timedelta(days=7)
        }
        
        boleto = BoletoSchema(**boleto_data)
        assert boleto.customer_name == 'João Silva'
        assert boleto.customer_document == '12345678901'
        assert boleto.customer_email == 'joao@exemplo.com'
    
    def test_sanitized_customer_name(self):
        """Testa sanitização do nome do cliente"""
        boleto_data = {
            'customer_name': 'João <script>alert("xss")</script> Silva',
            'customer_document': '12345678901',
            'customer_email': 'joao@exemplo.com',
            'due_date': datetime.now() + timedelta(days=7)
        }
        
        boleto = BoletoSchema(**boleto_data)
        assert boleto.customer_name == 'João Silva'  # XSS removido
    
    def test_invalid_document_format(self):
        """Testa documento com formato inválido"""
        boleto_data = {
            'customer_name': 'João Silva',
            'customer_document': '123.456.789-01',  # Formato com pontos
            'customer_email': 'joao@exemplo.com',
            'due_date': datetime.now() + timedelta(days=7)
        }
        
        boleto = BoletoSchema(**boleto_data)
        assert boleto.customer_document == '12345678901'  # Pontos removidos
    
    def test_past_due_date(self):
        """Testa data de vencimento no passado"""
        boleto_data = {
            'customer_name': 'João Silva',
            'customer_document': '12345678901',
            'customer_email': 'joao@exemplo.com',
            'due_date': datetime.now() - timedelta(days=1)  # Data passada
        }
        
        with pytest.raises(ValidationError) as exc_info:
            BoletoSchema(**boleto_data)
        
        assert 'Data de vencimento deve ser futura' in str(exc_info.value)

class TestPaymentMethodSchema:
    """Testes para validação de método de pagamento"""
    
    def test_valid_card_payment(self):
        """Testa pagamento com cartão válido"""
        payment_data = {
            'type': 'card',
            'card': {
                'number': '4242424242424242',
                'exp_month': 12,
                'exp_year': 2026,
                'cvc': '123',
                'name': 'João Silva'
            }
        }
        
        payment = PaymentMethodSchema(**payment_data)
        assert payment.type == 'card'
        assert payment.card is not None
        assert payment.card.number == '4242424242424242'
    
    def test_valid_pix_payment(self):
        """Testa pagamento PIX válido"""
        payment_data = {
            'type': 'pix',
            'pix': {
                'key_type': 'email',
                'key_value': 'teste@exemplo.com'
            }
        }
        
        payment = PaymentMethodSchema(**payment_data)
        assert payment.type == 'pix'
        assert payment.pix is not None
        assert payment.pix.key_type == 'email'
    
    def test_missing_method_data(self):
        """Testa método sem dados específicos"""
        payment_data = {
            'type': 'card'
            # Sem dados do cartão
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentMethodSchema(**payment_data)
        
        assert 'Dados do cartão são obrigatórios' in str(exc_info.value)
    
    def test_invalid_payment_type(self):
        """Testa tipo de pagamento inválido"""
        payment_data = {
            'type': 'invalid',
            'card': {
                'number': '4242424242424242',
                'exp_month': 12,
                'exp_year': 2026,
                'cvc': '123',
                'name': 'João Silva'
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentMethodSchema(**payment_data)
        
        assert 'Tipo de pagamento inválido' in str(exc_info.value)

class TestPaymentCreateSchema:
    """Testes para validação de criação de pagamento"""
    
    def test_valid_payment_creation(self):
        """Testa criação de pagamento válido"""
        payment_data = {
            'amount': 1000,
            'currency': 'brl',
            'payment_method': {
                'type': 'card',
                'card': {
                    'number': '4242424242424242',
                    'exp_month': 12,
                    'exp_year': 2026,
                    'cvc': '123',
                    'name': 'João Silva'
                }
            },
            'description': 'Pagamento teste',
            'metadata': {'user_id': '123'}
        }
        
        payment = PaymentCreateSchema(**payment_data)
        assert payment.amount == 1000
        assert payment.currency == 'brl'
        assert payment.description == 'Pagamento teste'
        assert payment.metadata['user_id'] == '123'
    
    def test_amount_too_small(self):
        """Testa valor muito pequeno"""
        payment_data = {
            'amount': 50,  # Menor que 100
            'currency': 'brl',
            'payment_method': {
                'type': 'card',
                'card': {
                    'number': '4242424242424242',
                    'exp_month': 12,
                    'exp_year': 2026,
                    'cvc': '123',
                    'name': 'João Silva'
                }
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentCreateSchema(**payment_data)
        
        assert 'amount' in str(exc_info.value)
    
    def test_unsupported_currency(self):
        """Testa moeda não suportada"""
        payment_data = {
            'amount': 1000,
            'currency': 'jpy',  # Moeda não suportada
            'payment_method': {
                'type': 'card',
                'card': {
                    'number': '4242424242424242',
                    'exp_month': 12,
                    'exp_year': 2026,
                    'cvc': '123',
                    'name': 'João Silva'
                }
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentCreateSchema(**payment_data)
        
        assert 'Moeda não suportada' in str(exc_info.value)
    
    def test_sanitized_description(self):
        """Testa sanitização da descrição"""
        payment_data = {
            'amount': 1000,
            'currency': 'brl',
            'payment_method': {
                'type': 'card',
                'card': {
                    'number': '4242424242424242',
                    'exp_month': 12,
                    'exp_year': 2026,
                    'cvc': '123',
                    'name': 'João Silva'
                }
            },
            'description': 'Pagamento <script>alert("xss")</script> teste'
        }
        
        payment = PaymentCreateSchema(**payment_data)
        assert payment.description == 'Pagamento teste'  # XSS removido

class TestPaymentFilterSchema:
    """Testes para validação de filtros de pagamento"""
    
    def test_valid_filters(self):
        """Testa filtros válidos"""
        filter_data = {
            'status': 'succeeded',
            'payment_method': 'card',
            'min_amount': 1000,
            'max_amount': 5000,
            'limit': 20,
            'offset': 0
        }
        
        filters = PaymentFilterSchema(**filter_data)
        assert filters.status == 'succeeded'
        assert filters.payment_method == 'card'
        assert filters.min_amount == 1000
        assert filters.max_amount == 5000
    
    def test_invalid_status(self):
        """Testa status inválido"""
        filter_data = {
            'status': 'invalid_status',
            'limit': 20
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentFilterSchema(**filter_data)
        
        assert 'Status inválido' in str(exc_info.value)
    
    def test_invalid_amount_range(self):
        """Testa range de valores inválido"""
        filter_data = {
            'min_amount': 5000,
            'max_amount': 1000,  # Menor que min_amount
            'limit': 20
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentFilterSchema(**filter_data)
        
        assert 'Valor mínimo não pode ser maior que valor máximo' in str(exc_info.value)
    
    def test_limit_too_high(self):
        """Testa limite muito alto"""
        filter_data = {
            'limit': 150  # Maior que 100
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PaymentFilterSchema(**filter_data)
        
        assert 'limit' in str(exc_info.value)

class TestPaymentUpdateSchema:
    """Testes para validação de atualização de pagamento"""
    
    def test_valid_update(self):
        """Testa atualização válida"""
        update_data = {
            'description': 'Nova descrição',
            'metadata': {'updated': True}
        }
        
        update = PaymentUpdateSchema(**update_data)
        assert update.description == 'Nova descrição'
        assert update.metadata['updated'] is True
    
    def test_sanitized_update_description(self):
        """Testa sanitização da descrição na atualização"""
        update_data = {
            'description': 'Nova <script>alert("xss")</script> descrição'
        }
        
        update = PaymentUpdateSchema(**update_data)
        assert update.description == 'Nova descrição'  # XSS removido 