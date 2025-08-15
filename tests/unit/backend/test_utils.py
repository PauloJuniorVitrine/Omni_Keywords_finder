"""
Testes unitários para backend/app/utils/
Tracing ID: BACKEND_TESTS_UTILS_001_20250127
"""

import pytest
import json
import hashlib
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from backend.app.utils import (
    validation_utils, security_utils, data_utils, 
    logging_utils, cache_utils, file_utils
)

class TestValidationUtils:
    """Testes para utilitários de validação."""
    
    def test_validate_email_valid(self):
        """Testa validação de email válido."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test-domain.com"
        ]
        
        for email in valid_emails:
            assert validation_utils.validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Testa validação de email inválido."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user name@example.com",
            "user@example..com"
        ]
        
        for email in invalid_emails:
            assert validation_utils.validate_email(email) is False
    
    def test_validate_password_strength(self):
        """Testa validação de força de senha."""
        # Senha forte
        strong_password = "MySecureP@ssw0rd123"
        assert validation_utils.validate_password_strength(strong_password) is True
        
        # Senha fraca (muito curta)
        weak_password = "weak"
        assert validation_utils.validate_password_strength(weak_password) is False
        
        # Senha fraca (sem números)
        weak_password2 = "WeakPassword"
        assert validation_utils.validate_password_strength(weak_password2) is False
        
        # Senha fraca (sem caracteres especiais)
        weak_password3 = "WeakPassword123"
        assert validation_utils.validate_password_strength(weak_password3) is False
    
    def test_validate_phone_number(self):
        """Testa validação de número de telefone."""
        valid_phones = [
            "+55 11 99999-9999",
            "+1 (555) 123-4567",
            "11 99999-9999",
            "(11) 99999-9999"
        ]
        
        for phone in valid_phones:
            assert validation_utils.validate_phone_number(phone) is True
        
        invalid_phones = [
            "invalid",
            "123",
            "+55 11 99999-99999",  # Muito longo
            "11 9999-999"  # Muito curto
        ]
        
        for phone in invalid_phones:
            assert validation_utils.validate_phone_number(phone) is False
    
    def test_validate_cpf(self):
        """Testa validação de CPF."""
        valid_cpfs = [
            "123.456.789-09",
            "98765432100",
            "111.444.777-35"
        ]
        
        for cpf in valid_cpfs:
            assert validation_utils.validate_cpf(cpf) is True
        
        invalid_cpfs = [
            "123.456.789-10",  # Dígito verificador incorreto
            "111.111.111-11",  # CPF com números iguais
            "123.456.789",     # Incompleto
            "invalid"
        ]
        
        for cpf in invalid_cpfs:
            assert validation_utils.validate_cpf(cpf) is False
    
    def test_validate_cnpj(self):
        """Testa validação de CNPJ."""
        valid_cnpjs = [
            "11.222.333/0001-81",
            "11222333000181"
        ]
        
        for cnpj in valid_cnpjs:
            assert validation_utils.validate_cnpj(cnpj) is True
        
        invalid_cnpjs = [
            "11.222.333/0001-82",  # Dígito verificador incorreto
            "11.111.111/1111-11",  # CNPJ com números iguais
            "11.222.333/0001",     # Incompleto
            "invalid"
        ]
        
        for cnpj in invalid_cnpjs:
            assert validation_utils.validate_cnpj(cnpj) is False
    
    def test_validate_url(self):
        """Testa validação de URL."""
        valid_urls = [
            "https://www.example.com",
            "http://example.com",
            "https://subdomain.example.com/path?param=value",
            "ftp://files.example.com"
        ]
        
        for url in valid_urls:
            assert validation_utils.validate_url(url) is True
        
        invalid_urls = [
            "not-a-url",
            "http://",
            "https://.com",
            "ftp://invalid"
        ]
        
        for url in invalid_urls:
            assert validation_utils.validate_url(url) is False
    
    def test_validate_json_schema(self):
        """Testa validação de JSON contra schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "age"]
        }
        
        valid_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        
        assert validation_utils.validate_json_schema(valid_data, schema) is True
        
        invalid_data = {
            "name": "John Doe",
            "age": -5,  # Idade negativa
            "email": "invalid-email"
        }
        
        assert validation_utils.validate_json_schema(invalid_data, schema) is False

class TestSecurityUtils:
    """Testes para utilitários de segurança."""
    
    def test_hash_password(self):
        """Testa hash de senha."""
        password = "MySecurePassword123"
        hashed = security_utils.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > len(password)
        assert hashed.startswith("$2b$")  # bcrypt hash
    
    def test_verify_password(self):
        """Testa verificação de senha."""
        password = "MySecurePassword123"
        hashed = security_utils.hash_password(password)
        
        # Senha correta
        assert security_utils.verify_password(password, hashed) is True
        
        # Senha incorreta
        assert security_utils.verify_password("WrongPassword", hashed) is False
    
    def test_generate_jwt_token(self):
        """Testa geração de token JWT."""
        payload = {
            "user_id": 123,
            "email": "test@example.com",
            "role": "admin"
        }
        
        secret_key = "test-secret-key"
        token = security_utils.generate_jwt_token(payload, secret_key)
        
        assert token is not None
        assert len(token.split('.')) == 3  # JWT tem 3 partes
        
        # Decodificar token
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        assert decoded["user_id"] == 123
        assert decoded["email"] == "test@example.com"
        assert decoded["role"] == "admin"
    
    def test_verify_jwt_token(self):
        """Testa verificação de token JWT."""
        payload = {
            "user_id": 123,
            "email": "test@example.com"
        }
        
        secret_key = "test-secret-key"
        token = security_utils.generate_jwt_token(payload, secret_key)
        
        # Token válido
        decoded = security_utils.verify_jwt_token(token, secret_key)
        assert decoded is not None
        assert decoded["user_id"] == 123
        
        # Token inválido
        invalid_token = "invalid.token.here"
        decoded = security_utils.verify_jwt_token(invalid_token, secret_key)
        assert decoded is None
    
    def test_generate_random_string(self):
        """Testa geração de string aleatória."""
        # String de 10 caracteres
        random_str = security_utils.generate_random_string(10)
        assert len(random_str) == 10
        assert random_str.isalnum()
        
        # String de 20 caracteres
        random_str2 = security_utils.generate_random_string(20)
        assert len(random_str2) == 20
        assert random_str2.isalnum()
        
        # Strings diferentes
        assert random_str != random_str2
    
    def test_encrypt_data(self):
        """Testa criptografia de dados."""
        data = "Dados sensíveis para criptografar"
        key = "minha-chave-secreta-32-chars"
        
        encrypted = security_utils.encrypt_data(data, key)
        
        assert encrypted != data
        assert isinstance(encrypted, bytes)
        
        # Descriptografar
        decrypted = security_utils.decrypt_data(encrypted, key)
        assert decrypted == data
    
    def test_decrypt_data(self):
        """Testa descriptografia de dados."""
        data = "Dados para teste de criptografia"
        key = "minha-chave-secreta-32-chars"
        
        encrypted = security_utils.encrypt_data(data, key)
        decrypted = security_utils.decrypt_data(encrypted, key)
        
        assert decrypted == data
    
    def test_generate_api_key(self):
        """Testa geração de chave de API."""
        api_key = security_utils.generate_api_key()
        
        assert len(api_key) == 64  # 64 caracteres hex
        assert all(c in '0123456789abcdef' for c in api_key)
    
    def test_validate_api_key(self):
        """Testa validação de chave de API."""
        # Chave válida
        valid_key = "a" * 64
        assert security_utils.validate_api_key(valid_key) is True
        
        # Chave inválida (muito curta)
        invalid_key = "short"
        assert security_utils.validate_api_key(invalid_key) is False
        
        # Chave inválida (caracteres não hex)
        invalid_key2 = "g" * 64
        assert security_utils.validate_api_key(invalid_key2) is False

class TestDataUtils:
    """Testes para utilitários de dados."""
    
    def test_clean_text(self):
        """Testa limpeza de texto."""
        dirty_text = "  Texto   com   espaços   extras  \n\t"
        clean_text = data_utils.clean_text(dirty_text)
        
        assert clean_text == "Texto com espaços extras"
        
        # Texto com caracteres especiais
        special_text = "Texto com @#$%^&*() caracteres especiais"
        clean_text = data_utils.clean_text(special_text, remove_special=True)
        
        assert clean_text == "Texto com caracteres especiais"
    
    def test_normalize_string(self):
        """Testa normalização de string."""
        # Remover acentos
        accented_text = "São Paulo - Cidade Maravilhosa"
        normalized = data_utils.normalize_string(accented_text, remove_accents=True)
        
        assert normalized == "Sao Paulo - Cidade Maravilhosa"
        
        # Converter para minúsculas
        upper_text = "TEXTO EM MAIÚSCULAS"
        normalized = data_utils.normalize_string(upper_text, to_lower=True)
        
        assert normalized == "texto em maiúsculas"
    
    def test_format_currency(self):
        """Testa formatação de moeda."""
        # Formato brasileiro
        value = 1234.56
        formatted = data_utils.format_currency(value, locale="pt_BR")
        
        assert "R$" in formatted
        assert "1.234,56" in formatted
        
        # Formato americano
        formatted = data_utils.format_currency(value, locale="en_US")
        
        assert "$" in formatted
        assert "1,234.56" in formatted
    
    def test_parse_date(self):
        """Testa parsing de datas."""
        # Data em formato brasileiro
        date_str = "25/12/2024"
        parsed = data_utils.parse_date(date_str, format="%d/%m/%Y")
        
        assert parsed.year == 2024
        assert parsed.month == 12
        assert parsed.day == 25
        
        # Data em formato ISO
        iso_date = "2024-12-25T10:30:00"
        parsed = data_utils.parse_date(iso_date, format="%Y-%m-%dT%H:%M:%S")
        
        assert parsed.year == 2024
        assert parsed.month == 12
        assert parsed.day == 25
        assert parsed.hour == 10
        assert parsed.minute == 30
    
    def test_format_date(self):
        """Testa formatação de datas."""
        date = datetime(2024, 12, 25, 10, 30, 0)
        
        # Formato brasileiro
        formatted = data_utils.format_date(date, format="%d/%m/%Y")
        assert formatted == "25/12/2024"
        
        # Formato ISO
        formatted = data_utils.format_date(date, format="%Y-%m-%d")
        assert formatted == "2024-12-25"
        
        # Formato relativo
        formatted = data_utils.format_date(date, format="relative")
        assert "dias" in formatted or "horas" in formatted
    
    def test_convert_units(self):
        """Testa conversão de unidades."""
        # Conversão de peso
        kg_to_lbs = data_utils.convert_units(1, "kg", "lbs")
        assert abs(kg_to_lbs - 2.20462) < 0.01
        
        # Conversão de distância
        km_to_miles = data_utils.convert_units(1, "km", "miles")
        assert abs(km_to_miles - 0.621371) < 0.01
        
        # Conversão de temperatura
        celsius_to_fahrenheit = data_utils.convert_units(0, "celsius", "fahrenheit")
        assert celsius_to_fahrenheit == 32
    
    def test_validate_data_types(self):
        """Testa validação de tipos de dados."""
        # Dados válidos
        valid_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "active": True
        }
        
        schema = {
            "name": str,
            "age": int,
            "email": str,
            "active": bool
        }
        
        assert data_utils.validate_data_types(valid_data, schema) is True
        
        # Dados inválidos
        invalid_data = {
            "name": "John Doe",
            "age": "30",  # Deveria ser int
            "email": "john@example.com",
            "active": True
        }
        
        assert data_utils.validate_data_types(invalid_data, schema) is False

class TestLoggingUtils:
    """Testes para utilitários de logging."""
    
    def test_setup_logging(self):
        """Testa configuração de logging."""
        config = {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "test.log"
        }
        
        logger = logging_utils.setup_logging("test_logger", config)
        
        assert logger is not None
        assert logger.name == "test_logger"
        assert logger.level == 20  # INFO level
    
    def test_log_function_call(self):
        """Testa logging de chamadas de função."""
        with patch('backend.app.utils.logging_utils.logger') as mock_logger:
            @logging_utils.log_function_call
            def test_function(param1, param2):
                return param1 + param2
            
            result = test_function(5, 3)
            
            assert result == 8
            mock_logger.info.assert_called()
    
    def test_log_execution_time(self):
        """Testa logging de tempo de execução."""
        with patch('backend.app.utils.logging_utils.logger') as mock_logger:
            @logging_utils.log_execution_time
            def slow_function():
                import time
                time.sleep(0.1)
                return "done"
            
            result = slow_function()
            
            assert result == "done"
            mock_logger.info.assert_called()
            # Verificar se o log contém informação sobre tempo
            log_call = mock_logger.info.call_args[0][0]
            assert "execution_time" in log_call
    
    def test_log_error_with_context(self):
        """Testa logging de erro com contexto."""
        with patch('backend.app.utils.logging_utils.logger') as mock_logger:
            try:
                raise ValueError("Test error")
            except Exception as e:
                logging_utils.log_error_with_context(e, "test_function", {"param": "value"})
            
            mock_logger.error.assert_called()
            # Verificar se o contexto foi incluído
            log_call = mock_logger.error.call_args[0][0]
            assert "test_function" in log_call
            assert "param" in log_call

class TestCacheUtils:
    """Testes para utilitários de cache."""
    
    def test_cache_decorator(self):
        """Testa decorator de cache."""
        call_count = 0
        
        @cache_utils.cache(ttl=60)
        def expensive_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}_{call_count}"
        
        # Primeira chamada
        result1 = expensive_function("test")
        assert result1 == "result_test_1"
        assert call_count == 1
        
        # Segunda chamada (deve usar cache)
        result2 = expensive_function("test")
        assert result2 == "result_test_1"
        assert call_count == 1  # Não deve incrementar
        
        # Chamada com parâmetro diferente
        result3 = expensive_function("other")
        assert result3 == "result_other_2"
        assert call_count == 2
    
    def test_cache_invalidate(self):
        """Testa invalidação de cache."""
        call_count = 0
        
        @cache_utils.cache(ttl=60)
        def cached_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}_{call_count}"
        
        # Primeira chamada
        result1 = cached_function("test")
        assert call_count == 1
        
        # Segunda chamada (cache)
        result2 = cached_function("test")
        assert call_count == 1
        
        # Invalidar cache
        cache_utils.invalidate_cache("cached_function", "test")
        
        # Terceira chamada (deve executar novamente)
        result3 = cached_function("test")
        assert call_count == 2
    
    def test_cache_get_set(self):
        """Testa operações get/set do cache."""
        # Definir valor
        cache_utils.set_cache("test_key", "test_value", ttl=60)
        
        # Buscar valor
        value = cache_utils.get_cache("test_key")
        assert value == "test_value"
        
        # Buscar chave inexistente
        value = cache_utils.get_cache("nonexistent_key")
        assert value is None
    
    def test_cache_clear(self):
        """Testa limpeza do cache."""
        # Definir múltiplos valores
        cache_utils.set_cache("key1", "value1", ttl=60)
        cache_utils.set_cache("key2", "value2", ttl=60)
        
        # Verificar se estão no cache
        assert cache_utils.get_cache("key1") == "value1"
        assert cache_utils.get_cache("key2") == "value2"
        
        # Limpar cache
        cache_utils.clear_cache()
        
        # Verificar se foram removidos
        assert cache_utils.get_cache("key1") is None
        assert cache_utils.get_cache("key2") is None

class TestFileUtils:
    """Testes para utilitários de arquivo."""
    
    def test_read_file_safe(self):
        """Testa leitura segura de arquivo."""
        # Criar arquivo temporário
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Conteúdo do arquivo de teste")
            temp_file = f.name
        
        try:
            content = file_utils.read_file_safe(temp_file)
            assert content == "Conteúdo do arquivo de teste"
        finally:
            os.unlink(temp_file)
    
    def test_write_file_safe(self):
        """Testa escrita segura de arquivo."""
        import tempfile
        import os
        
        temp_file = tempfile.mktemp()
        
        try:
            content = "Conteúdo para escrever"
            file_utils.write_file_safe(temp_file, content)
            
            # Verificar se foi escrito
            with open(temp_file, 'r') as f:
                written_content = f.read()
            
            assert written_content == content
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_file_exists_safe(self):
        """Testa verificação segura de existência de arquivo."""
        import tempfile
        import os
        
        # Arquivo existente
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            assert file_utils.file_exists_safe(temp_file) is True
        finally:
            os.unlink(temp_file)
        
        # Arquivo inexistente
        assert file_utils.file_exists_safe("/caminho/inexistente/arquivo.txt") is False
    
    def test_get_file_info(self):
        """Testa obtenção de informações do arquivo."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Conteúdo de teste")
            temp_file = f.name
        
        try:
            info = file_utils.get_file_info(temp_file)
            
            assert 'size' in info
            assert 'modified' in info
            assert 'created' in info
            assert info['size'] > 0
        finally:
            os.unlink(temp_file)
    
    def test_validate_file_type(self):
        """Testa validação de tipo de arquivo."""
        # Arquivo de imagem válido
        valid_image = "image.jpg"
        assert file_utils.validate_file_type(valid_image, ["jpg", "png", "gif"]) is True
        
        # Arquivo de imagem inválido
        invalid_image = "document.pdf"
        assert file_utils.validate_file_type(invalid_image, ["jpg", "png", "gif"]) is False
    
    def test_sanitize_filename(self):
        """Testa sanitização de nome de arquivo."""
        # Nome com caracteres especiais
        dirty_name = "Arquivo com @#$%^&*() caracteres especiais.txt"
        clean_name = file_utils.sanitize_filename(dirty_name)
        
        assert clean_name == "Arquivo_com_caracteres_especiais.txt"
        
        # Nome com espaços
        spaced_name = "Arquivo com espaços.pdf"
        clean_name = file_utils.sanitize_filename(spaced_name)
        
        assert clean_name == "Arquivo_com_espacos.pdf"
    
    def test_create_backup(self):
        """Testa criação de backup de arquivo."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Conteúdo original")
            original_file = f.name
        
        try:
            # Criar backup
            backup_file = file_utils.create_backup(original_file)
            
            # Verificar se backup foi criado
            assert os.path.exists(backup_file)
            
            # Verificar conteúdo do backup
            with open(backup_file, 'r') as f:
                backup_content = f.read()
            
            assert backup_content == "Conteúdo original"
            
            # Limpar backup
            os.unlink(backup_file)
        finally:
            os.unlink(original_file)
