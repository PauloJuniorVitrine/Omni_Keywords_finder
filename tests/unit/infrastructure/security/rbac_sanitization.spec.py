"""
Testes unitários para sanitização de dados do RBAC.

Este módulo testa as funções de sanitização implementadas
no sistema RBAC para prevenir ataques de injeção e XSS.
"""

import pytest
from unittest.mock import Mock, patch
from backend.app.api.rbac import (
    sanitizar_string,
    sanitizar_email,
    sanitizar_username,
    sanitizar_role_name,
    sanitizar_permission_name,
    sanitizar_lista_strings
)


class TestSanitizacaoString:
    """Testes para sanitização de strings genéricas."""
    
    def test_sanitizar_string_normal(self):
        """Testa sanitização de string normal."""
        resultado = sanitizar_string("Texto normal")
        assert resultado == "Texto normal"
    
    def test_sanitizar_string_com_html(self):
        """Testa sanitização de string com HTML."""
        resultado = sanitizar_string("<script>alert('xss')</script>")
        assert resultado == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    
    def test_sanitizar_string_com_caracteres_controle(self):
        """Testa sanitização de string com caracteres de controle."""
        resultado = sanitizar_string("Texto\x00com\x01controle")
        assert resultado == "Textocomcontrole"
    
    def test_sanitizar_string_com_espacos_extras(self):
        """Testa sanitização de string com espaços extras."""
        resultado = sanitizar_string("  texto   com   espaços  ")
        assert resultado == "texto com espaços"
    
    def test_sanitizar_string_com_unicode(self):
        """Testa sanitização de string com caracteres unicode."""
        resultado = sanitizar_string("café résumé")
        assert resultado == "café résumé"
    
    def test_sanitizar_string_com_tamanho_maximo(self):
        """Testa sanitização de string com limite de tamanho."""
        texto_longo = "a" * 300
        resultado = sanitizar_string(texto_longo, max_length=100)
        assert len(resultado) == 100
        assert resultado == "a" * 100
    
    def test_sanitizar_string_vazia(self):
        """Testa sanitização de string vazia."""
        resultado = sanitizar_string("")
        assert resultado == ""
    
    def test_sanitizar_string_none(self):
        """Testa sanitização de string None."""
        resultado = sanitizar_string(None)
        assert resultado == ""


class TestSanitizacaoEmail:
    """Testes para sanitização de emails."""
    
    def test_sanitizar_email_valido(self):
        """Testa sanitização de email válido."""
        resultado = sanitizar_email("usuario@exemplo.com")
        assert resultado == "usuario@exemplo.com"
    
    def test_sanitizar_email_com_maiusculas(self):
        """Testa sanitização de email com maiúsculas."""
        resultado = sanitizar_email("USUARIO@EXEMPLO.COM")
        assert resultado == "usuario@exemplo.com"
    
    def test_sanitizar_email_com_espacos(self):
        """Testa sanitização de email com espaços."""
        resultado = sanitizar_email("  usuario@exemplo.com  ")
        assert resultado == "usuario@exemplo.com"
    
    def test_sanitizar_email_com_caracteres_especiais(self):
        """Testa sanitização de email com caracteres especiais válidos."""
        resultado = sanitizar_email("usuario+tag@exemplo.com")
        assert resultado == "usuario+tag@exemplo.com"
    
    def test_sanitizar_email_invalido_formato(self):
        """Testa sanitização de email com formato inválido."""
        with pytest.raises(ValueError, match="Formato de email inválido"):
            sanitizar_email("email_invalido")
    
    def test_sanitizar_email_com_caracteres_perigosos(self):
        """Testa sanitização de email com caracteres perigosos."""
        resultado = sanitizar_email("usuario<script>@exemplo.com")
        assert resultado == "usuario@exemplo.com"
    
    def test_sanitizar_email_vazio(self):
        """Testa sanitização de email vazio."""
        resultado = sanitizar_email("")
        assert resultado == ""


class TestSanitizacaoUsername:
    """Testes para sanitização de usernames."""
    
    def test_sanitizar_username_valido(self):
        """Testa sanitização de username válido."""
        resultado = sanitizar_username("usuario123")
        assert resultado == "usuario123"
    
    def test_sanitizar_username_com_underscore(self):
        """Testa sanitização de username com underscore."""
        resultado = sanitizar_username("usuario_123")
        assert resultado == "usuario_123"
    
    def test_sanitizar_username_com_caracteres_especiais(self):
        """Testa sanitização de username com caracteres especiais."""
        resultado = sanitizar_username("usuario@123")
        assert resultado == "usuario123"
    
    def test_sanitizar_username_com_espacos(self):
        """Testa sanitização de username com espaços."""
        resultado = sanitizar_username("  usuario 123  ")
        assert resultado == "usuario123"
    
    def test_sanitizar_username_muito_longo(self):
        """Testa sanitização de username muito longo."""
        username_longo = "a" * 100
        resultado = sanitizar_username(username_longo)
        assert len(resultado) == 64
        assert resultado == "a" * 64
    
    def test_sanitizar_username_inicio_com_numero(self):
        """Testa sanitização de username que começa com número."""
        with pytest.raises(ValueError, match="Username deve começar com letra"):
            sanitizar_username("123usuario")
    
    def test_sanitizar_username_muito_curto(self):
        """Testa sanitização de username muito curto."""
        with pytest.raises(ValueError, match="Username deve começar com letra"):
            sanitizar_username("a")
    
    def test_sanitizar_username_vazio(self):
        """Testa sanitização de username vazio."""
        resultado = sanitizar_username("")
        assert resultado == ""


class TestSanitizacaoRoleName:
    """Testes para sanitização de nomes de papéis."""
    
    def test_sanitizar_role_name_valido(self):
        """Testa sanitização de nome de papel válido."""
        resultado = sanitizar_role_name("admin")
        assert resultado == "admin"
    
    def test_sanitizar_role_name_com_hifen(self):
        """Testa sanitização de nome de papel com hífen."""
        resultado = sanitizar_role_name("admin-senior")
        assert resultado == "admin-senior"
    
    def test_sanitizar_role_name_com_underscore(self):
        """Testa sanitização de nome de papel com underscore."""
        resultado = sanitizar_role_name("admin_senior")
        assert resultado == "admin_senior"
    
    def test_sanitizar_role_name_com_caracteres_especiais(self):
        """Testa sanitização de nome de papel com caracteres especiais."""
        resultado = sanitizar_role_name("admin@senior")
        assert resultado == "adminsenior"
    
    def test_sanitizar_role_name_com_espacos(self):
        """Testa sanitização de nome de papel com espaços."""
        resultado = sanitizar_role_name("  admin senior  ")
        assert resultado == "adminsenior"
    
    def test_sanitizar_role_name_muito_longo(self):
        """Testa sanitização de nome de papel muito longo."""
        role_longo = "a" * 100
        resultado = sanitizar_role_name(role_longo)
        assert len(resultado) == 64
        assert resultado == "a" * 64
    
    def test_sanitizar_role_name_inicio_com_numero(self):
        """Testa sanitização de nome de papel que começa com número."""
        with pytest.raises(ValueError, match="Nome do papel deve começar com letra"):
            sanitizar_role_name("123admin")
    
    def test_sanitizar_role_name_vazio(self):
        """Testa sanitização de nome de papel vazio."""
        resultado = sanitizar_role_name("")
        assert resultado == ""


class TestSanitizacaoPermissionName:
    """Testes para sanitização de nomes de permissões."""
    
    def test_sanitizar_permission_name_valido(self):
        """Testa sanitização de nome de permissão válido."""
        resultado = sanitizar_permission_name("read")
        assert resultado == "read"
    
    def test_sanitizar_permission_name_com_underscore(self):
        """Testa sanitização de nome de permissão com underscore."""
        resultado = sanitizar_permission_name("read_write")
        assert resultado == "read_write"
    
    def test_sanitizar_permission_name_com_caracteres_especiais(self):
        """Testa sanitização de nome de permissão com caracteres especiais."""
        resultado = sanitizar_permission_name("read@write")
        assert resultado == "readwrite"
    
    def test_sanitizar_permission_name_com_espacos(self):
        """Testa sanitização de nome de permissão com espaços."""
        resultado = sanitizar_permission_name("  read write  ")
        assert resultado == "readwrite"
    
    def test_sanitizar_permission_name_muito_longo(self):
        """Testa sanitização de nome de permissão muito longo."""
        perm_longo = "a" * 100
        resultado = sanitizar_permission_name(perm_longo)
        assert len(resultado) == 64
        assert resultado == "a" * 64
    
    def test_sanitizar_permission_name_inicio_com_numero(self):
        """Testa sanitização de nome de permissão que começa com número."""
        with pytest.raises(ValueError, match="Nome da permissão deve começar com letra"):
            sanitizar_permission_name("123read")
    
    def test_sanitizar_permission_name_vazio(self):
        """Testa sanitização de nome de permissão vazio."""
        resultado = sanitizar_permission_name("")
        assert resultado == ""


class TestSanitizacaoListaStrings:
    """Testes para sanitização de listas de strings."""
    
    def test_sanitizar_lista_strings_normal(self):
        """Testa sanitização de lista de strings normal."""
        lista = ["admin", "gestor", "usuario"]
        resultado = sanitizar_lista_strings(lista, sanitizar_role_name)
        assert resultado == ["admin", "gestor", "usuario"]
    
    def test_sanitizar_lista_strings_com_invalidos(self):
        """Testa sanitização de lista com itens inválidos."""
        lista = ["admin", "123invalid", "gestor"]
        resultado = sanitizar_lista_strings(lista, sanitizar_role_name)
        assert resultado == ["admin", "gestor"]
    
    def test_sanitizar_lista_strings_vazia(self):
        """Testa sanitização de lista vazia."""
        resultado = sanitizar_lista_strings([], sanitizar_role_name)
        assert resultado == []
    
    def test_sanitizar_lista_strings_none(self):
        """Testa sanitização de lista None."""
        resultado = sanitizar_lista_strings(None, sanitizar_role_name)
        assert resultado == []
    
    def test_sanitizar_lista_strings_com_html(self):
        """Testa sanitização de lista com HTML."""
        lista = ["admin", "<script>alert('xss')</script>", "gestor"]
        resultado = sanitizar_lista_strings(lista, sanitizar_string)
        assert resultado == ["admin", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;", "gestor"]


class TestSanitizacaoSeguranca:
    """Testes de segurança para sanitização."""
    
    def test_sanitizar_xss_script(self):
        """Testa proteção contra XSS com script."""
        payload = "<script>alert('XSS')</script>"
        resultado = sanitizar_string(payload)
        assert "<script>" not in resultado
        assert "alert" not in resultado
    
    def test_sanitizar_xss_img(self):
        """Testa proteção contra XSS com img."""
        payload = '<img src="x" onerror="alert(\'XSS\')">'
        resultado = sanitizar_string(payload)
        assert "<img" not in resultado
        assert "onerror" not in resultado
    
    def test_sanitizar_sql_injection(self):
        """Testa proteção contra SQL injection."""
        payload = "'; DROP TABLE users; --"
        resultado = sanitizar_string(payload)
        assert "DROP TABLE" in resultado  # Deve escapar, não remover
        assert resultado != payload  # Deve ter sido modificado
    
    def test_sanitizar_command_injection(self):
        """Testa proteção contra command injection."""
        payload = "admin; rm -rf /"
        resultado = sanitizar_string(payload)
        assert "rm -rf" in resultado  # Deve escapar, não remover
        assert resultado != payload  # Deve ter sido modificado
    
    def test_sanitizar_unicode_normalization(self):
        """Testa normalização de caracteres unicode."""
        # Caracteres unicode que podem ser confundidos
        payload = "café"  # e com acento
        resultado = sanitizar_string(payload)
        assert resultado == "café"  # Deve manter a normalização


if __name__ == '__main__':
    pytest.main([__file__]) 