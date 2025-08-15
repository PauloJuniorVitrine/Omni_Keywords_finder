"""
Testes Unitários para IP Whitelisting
Sistema de Whitelist de IPs - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de whitelist de IPs
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import ipaddress
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.app.security.ip_whitelisting import (
    IPWhitelist,
    ip_whitelist,
    require_whitelisted_ip
)


class TestIPWhitelist:
    """Testes para IPWhitelist"""
    
    @pytest.fixture
    def whitelist(self):
        """Instância do IPWhitelist para testes"""
        return IPWhitelist()
    
    def test_ip_whitelist_initialization(self, whitelist):
        """Testa inicialização do IPWhitelist"""
        assert isinstance(whitelist.whitelisted_ips, set)
        assert isinstance(whitelist.whitelisted_ranges, list)
        assert isinstance(whitelist.temp_whitelist, dict)
        assert isinstance(whitelist.blocked_ips, set)
        assert len(whitelist.whitelisted_ips) == 0
        assert len(whitelist.whitelisted_ranges) == 0
        assert len(whitelist.temp_whitelist) == 0
        assert len(whitelist.blocked_ips) == 0
    
    def test_add_ip_valid(self, whitelist):
        """Testa adição de IP válido"""
        result = whitelist.add_ip("192.168.1.1")
        
        assert result is True
        assert "192.168.1.1" in whitelist.whitelisted_ips
    
    def test_add_ip_invalid(self, whitelist):
        """Testa adição de IP inválido"""
        result = whitelist.add_ip("invalid_ip")
        
        assert result is False
        assert "invalid_ip" not in whitelist.whitelisted_ips
    
    def test_add_ip_ipv6(self, whitelist):
        """Testa adição de IP IPv6"""
        result = whitelist.add_ip("2001:db8::1")
        
        assert result is True
        assert "2001:db8::1" in whitelist.whitelisted_ips
    
    def test_add_ip_duplicate(self, whitelist):
        """Testa adição de IP duplicado"""
        # Adicionar pela primeira vez
        result1 = whitelist.add_ip("192.168.1.1")
        assert result1 is True
        
        # Adicionar novamente
        result2 = whitelist.add_ip("192.168.1.1")
        assert result2 is True  # Deve permitir duplicatas
        
        # Verificar que está na lista
        assert "192.168.1.1" in whitelist.whitelisted_ips
    
    def test_add_range_valid(self, whitelist):
        """Testa adição de range válido"""
        result = whitelist.add_range("192.168.1.0/24")
        
        assert result is True
        assert len(whitelist.whitelisted_ranges) == 1
        assert str(whitelist.whitelisted_ranges[0]) == "192.168.1.0/24"
    
    def test_add_range_invalid(self, whitelist):
        """Testa adição de range inválido"""
        result = whitelist.add_range("invalid_range")
        
        assert result is False
        assert len(whitelist.whitelisted_ranges) == 0
    
    def test_add_range_ipv6(self, whitelist):
        """Testa adição de range IPv6"""
        result = whitelist.add_range("2001:db8::/32")
        
        assert result is True
        assert len(whitelist.whitelisted_ranges) == 1
        assert str(whitelist.whitelisted_ranges[0]) == "2001:db8::/32"
    
    def test_remove_ip_exists(self, whitelist):
        """Testa remoção de IP que existe"""
        # Adicionar IP
        whitelist.add_ip("192.168.1.1")
        assert "192.168.1.1" in whitelist.whitelisted_ips
        
        # Remover IP
        result = whitelist.remove_ip("192.168.1.1")
        
        assert result is True
        assert "192.168.1.1" not in whitelist.whitelisted_ips
    
    def test_remove_ip_not_exists(self, whitelist):
        """Testa remoção de IP que não existe"""
        result = whitelist.remove_ip("192.168.1.1")
        
        assert result is False
        assert "192.168.1.1" not in whitelist.whitelisted_ips
    
    def test_remove_range_exists(self, whitelist):
        """Testa remoção de range que existe"""
        # Adicionar range
        whitelist.add_range("192.168.1.0/24")
        assert len(whitelist.whitelisted_ranges) == 1
        
        # Remover range
        result = whitelist.remove_range("192.168.1.0/24")
        
        assert result is True
        assert len(whitelist.whitelisted_ranges) == 0
    
    def test_remove_range_not_exists(self, whitelist):
        """Testa remoção de range que não existe"""
        result = whitelist.remove_range("192.168.1.0/24")
        
        assert result is False
        assert len(whitelist.whitelisted_ranges) == 0
    
    def test_remove_range_invalid(self, whitelist):
        """Testa remoção de range inválido"""
        result = whitelist.remove_range("invalid_range")
        
        assert result is False
    
    def test_is_whitelisted_individual_ip(self, whitelist):
        """Testa verificação de IP individual na whitelist"""
        # Adicionar IP
        whitelist.add_ip("192.168.1.1")
        
        # Verificar se está na whitelist
        result = whitelist.is_whitelisted("192.168.1.1")
        
        assert result is True
    
    def test_is_whitelisted_range_ip(self, whitelist):
        """Testa verificação de IP dentro de range"""
        # Adicionar range
        whitelist.add_range("192.168.1.0/24")
        
        # Verificar IP dentro do range
        result = whitelist.is_whitelisted("192.168.1.100")
        
        assert result is True
    
    def test_is_whitelisted_outside_range(self, whitelist):
        """Testa verificação de IP fora de range"""
        # Adicionar range
        whitelist.add_range("192.168.1.0/24")
        
        # Verificar IP fora do range
        result = whitelist.is_whitelisted("192.168.2.1")
        
        assert result is False
    
    def test_is_whitelisted_not_whitelisted(self, whitelist):
        """Testa verificação de IP não whitelistado"""
        result = whitelist.is_whitelisted("192.168.1.1")
        
        assert result is False
    
    def test_is_whitelisted_invalid_ip(self, whitelist):
        """Testa verificação de IP inválido"""
        result = whitelist.is_whitelisted("invalid_ip")
        
        assert result is False
    
    def test_add_temp_whitelist_valid(self, whitelist):
        """Testa adição de whitelist temporário válido"""
        result = whitelist.add_temp_whitelist("192.168.1.1", 24)
        
        assert result is True
        assert "192.168.1.1" in whitelist.temp_whitelist
        assert isinstance(whitelist.temp_whitelist["192.168.1.1"], datetime)
    
    def test_add_temp_whitelist_invalid(self, whitelist):
        """Testa adição de whitelist temporário inválido"""
        result = whitelist.add_temp_whitelist("invalid_ip", 24)
        
        assert result is False
        assert "invalid_ip" not in whitelist.temp_whitelist
    
    def test_add_temp_whitelist_custom_duration(self, whitelist):
        """Testa adição de whitelist temporário com duração customizada"""
        result = whitelist.add_temp_whitelist("192.168.1.1", 48)
        
        assert result is True
        assert "192.168.1.1" in whitelist.temp_whitelist
        
        # Verificar que a expiração está no futuro
        expiry = whitelist.temp_whitelist["192.168.1.1"]
        assert expiry > datetime.now()
    
    def test_is_whitelisted_temp_valid(self, whitelist):
        """Testa verificação de whitelist temporário válido"""
        # Adicionar whitelist temporário
        whitelist.add_temp_whitelist("192.168.1.1", 24)
        
        # Verificar se está na whitelist
        result = whitelist.is_whitelisted("192.168.1.1")
        
        assert result is True
    
    def test_is_whitelisted_temp_expired(self, whitelist):
        """Testa verificação de whitelist temporário expirado"""
        # Adicionar whitelist temporário expirado
        whitelist.temp_whitelist["192.168.1.1"] = datetime.now() - timedelta(hours=1)
        
        # Verificar se não está mais na whitelist
        result = whitelist.is_whitelisted("192.168.1.1")
        
        assert result is False
        assert "192.168.1.1" not in whitelist.temp_whitelist  # Deve ser removido automaticamente
    
    def test_block_ip_valid(self, whitelist):
        """Testa bloqueio de IP válido"""
        result = whitelist.block_ip("192.168.1.1")
        
        assert result is True
        assert "192.168.1.1" in whitelist.blocked_ips
    
    def test_block_ip_invalid(self, whitelist):
        """Testa bloqueio de IP inválido"""
        result = whitelist.block_ip("invalid_ip")
        
        assert result is False
        assert "invalid_ip" not in whitelist.blocked_ips
    
    def test_unblock_ip_exists(self, whitelist):
        """Testa desbloqueio de IP que existe"""
        # Bloquear IP
        whitelist.block_ip("192.168.1.1")
        assert "192.168.1.1" in whitelist.blocked_ips
        
        # Desbloquear IP
        result = whitelist.unblock_ip("192.168.1.1")
        
        assert result is True
        assert "192.168.1.1" not in whitelist.blocked_ips
    
    def test_unblock_ip_not_exists(self, whitelist):
        """Testa desbloqueio de IP que não existe"""
        result = whitelist.unblock_ip("192.168.1.1")
        
        assert result is False
        assert "192.168.1.1" not in whitelist.blocked_ips
    
    def test_is_blocked_true(self, whitelist):
        """Testa verificação de IP bloqueado"""
        # Bloquear IP
        whitelist.block_ip("192.168.1.1")
        
        # Verificar se está bloqueado
        result = whitelist.is_blocked("192.168.1.1")
        
        assert result is True
    
    def test_is_blocked_false(self, whitelist):
        """Testa verificação de IP não bloqueado"""
        result = whitelist.is_blocked("192.168.1.1")
        
        assert result is False
    
    def test_get_whitelist_status_empty(self, whitelist):
        """Testa obtenção de status da whitelist vazia"""
        status = whitelist.get_whitelist_status()
        
        assert isinstance(status, dict)
        assert "whitelisted_ips" in status
        assert "whitelisted_ranges" in status
        assert "temp_whitelist" in status
        assert "blocked_ips" in status
        assert len(status["whitelisted_ips"]) == 0
        assert len(status["whitelisted_ranges"]) == 0
        assert len(status["temp_whitelist"]) == 0
        assert len(status["blocked_ips"]) == 0
    
    def test_get_whitelist_status_populated(self, whitelist):
        """Testa obtenção de status da whitelist populada"""
        # Adicionar dados
        whitelist.add_ip("192.168.1.1")
        whitelist.add_range("192.168.2.0/24")
        whitelist.add_temp_whitelist("192.168.3.1", 24)
        whitelist.block_ip("192.168.4.1")
        
        status = whitelist.get_whitelist_status()
        
        assert "192.168.1.1" in status["whitelisted_ips"]
        assert "192.168.2.0/24" in status["whitelisted_ranges"]
        assert "192.168.3.1" in status["temp_whitelist"]
        assert "192.168.4.1" in status["blocked_ips"]
        
        # Verificar formato da data
        temp_expiry = status["temp_whitelist"]["192.168.3.1"]
        assert isinstance(temp_expiry, str)  # Deve ser ISO format


class TestIPWhitelistIntegration:
    """Testes de integração para IPWhitelist"""
    
    @pytest.fixture
    def whitelist(self):
        """Instância do IPWhitelist para testes"""
        return IPWhitelist()
    
    def test_complex_whitelist_scenario(self, whitelist):
        """Testa cenário complexo de whitelist"""
        # Adicionar IPs individuais
        whitelist.add_ip("192.168.1.1")
        whitelist.add_ip("10.0.0.1")
        
        # Adicionar ranges
        whitelist.add_range("172.16.0.0/16")
        whitelist.add_range("2001:db8::/32")
        
        # Adicionar whitelist temporário
        whitelist.add_temp_whitelist("203.0.113.1", 12)
        
        # Bloquear alguns IPs
        whitelist.block_ip("192.168.1.100")
        whitelist.block_ip("10.0.0.100")
        
        # Verificar status
        status = whitelist.get_whitelist_status()
        
        assert len(status["whitelisted_ips"]) == 2
        assert len(status["whitelisted_ranges"]) == 2
        assert len(status["temp_whitelist"]) == 1
        assert len(status["blocked_ips"]) == 2
        
        # Verificar IPs específicos
        assert whitelist.is_whitelisted("192.168.1.1") is True
        assert whitelist.is_whitelisted("172.16.1.1") is True
        assert whitelist.is_whitelisted("2001:db8::1") is True
        assert whitelist.is_whitelisted("203.0.113.1") is True
        
        assert whitelist.is_blocked("192.168.1.100") is True
        assert whitelist.is_blocked("10.0.0.100") is True
        
        # Verificar IPs não whitelistados
        assert whitelist.is_whitelisted("192.168.2.1") is False
        assert whitelist.is_whitelisted("10.0.1.1") is False
    
    def test_whitelist_priority(self, whitelist):
        """Testa prioridade entre whitelist e blacklist"""
        # Adicionar IP à whitelist
        whitelist.add_ip("192.168.1.1")
        
        # Bloquear o mesmo IP
        whitelist.block_ip("192.168.1.1")
        
        # Verificar que está bloqueado (blacklist tem prioridade)
        assert whitelist.is_blocked("192.168.1.1") is True
        
        # Desbloquear
        whitelist.unblock_ip("192.168.1.1")
        
        # Verificar que está na whitelist novamente
        assert whitelist.is_whitelisted("192.168.1.1") is True
        assert whitelist.is_blocked("192.168.1.1") is False


class TestIPWhitelistErrorHandling:
    """Testes de tratamento de erros para IPWhitelist"""
    
    @pytest.fixture
    def whitelist(self):
        """Instância do IPWhitelist para testes"""
        return IPWhitelist()
    
    def test_add_ip_with_special_characters(self, whitelist):
        """Testa adição de IP com caracteres especiais"""
        result = whitelist.add_ip("192.168.1.1")
        
        assert result is True
        assert "192.168.1.1" in whitelist.whitelisted_ips
    
    def test_add_range_with_network_bits(self, whitelist):
        """Testa adição de range com bits de rede"""
        result = whitelist.add_range("192.168.1.0/24")
        
        assert result is True
        assert len(whitelist.whitelisted_ranges) == 1
    
    def test_handle_edge_cases(self, whitelist):
        """Testa casos edge"""
        # IPs de loopback
        assert whitelist.add_ip("127.0.0.1") is True
        assert whitelist.add_ip("::1") is True
        
        # IPs privados
        assert whitelist.add_ip("10.0.0.1") is True
        assert whitelist.add_ip("172.16.0.1") is True
        assert whitelist.add_ip("192.168.0.1") is True
        
        # IPs públicos
        assert whitelist.add_ip("8.8.8.8") is True
        assert whitelist.add_ip("1.1.1.1") is True


class TestIPWhitelistPerformance:
    """Testes de performance para IPWhitelist"""
    
    @pytest.fixture
    def whitelist(self):
        """Instância do IPWhitelist para testes"""
        return IPWhitelist()
    
    def test_multiple_operations_performance(self, whitelist):
        """Testa performance de múltiplas operações"""
        import time
        
        # Preparar dados
        ips = [f"192.168.1.{i}" for i in range(1, 101)]
        ranges = [f"10.{i}.0.0/16" for i in range(1, 11)]
        
        start_time = time.time()
        
        # Adicionar IPs
        for ip in ips:
            whitelist.add_ip(ip)
        
        # Adicionar ranges
        for range_cidr in ranges:
            whitelist.add_range(range_cidr)
        
        # Verificar IPs
        for ip in ips:
            whitelist.is_whitelisted(ip)
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 1.0  # Menos de 1 segundo para 110 operações
        
        # Verificar resultados
        assert len(whitelist.whitelisted_ips) == 100
        assert len(whitelist.whitelisted_ranges) == 10


class TestGlobalIPWhitelist:
    """Testes para instância global do IPWhitelist"""
    
    def test_global_ip_whitelist(self):
        """Testa instância global do IPWhitelist"""
        # Adicionar IP à whitelist global
        result = ip_whitelist.add_ip("192.168.1.1")
        
        assert result is True
        assert "192.168.1.1" in ip_whitelist.whitelisted_ips
        
        # Verificar se está na whitelist
        assert ip_whitelist.is_whitelisted("192.168.1.1") is True
        
        # Limpar para não afetar outros testes
        ip_whitelist.remove_ip("192.168.1.1")


class TestRequireWhitelistedIPDecorator:
    """Testes para decorator require_whitelisted_ip"""
    
    @pytest.fixture
    def mock_request(self):
        """Mock de Request para testes"""
        request = Mock()
        request.client.host = "192.168.1.1"
        return request
    
    def test_require_whitelisted_ip_decorator_whitelisted(self, mock_request):
        """Testa decorator com IP na whitelist"""
        # Adicionar IP à whitelist global
        ip_whitelist.add_ip("192.168.1.1")
        
        # Criar função decorada
        @require_whitelisted_ip()
        async def test_function(request):
            return "success"
        
        # Testar função
        import asyncio
        result = asyncio.run(test_function(mock_request))
        
        assert result == "success"
        
        # Limpar
        ip_whitelist.remove_ip("192.168.1.1")
    
    def test_require_whitelisted_ip_decorator_not_whitelisted(self, mock_request):
        """Testa decorator com IP não na whitelist"""
        # Criar função decorada
        @require_whitelisted_ip()
        async def test_function(request):
            return "success"
        
        # Testar função (deve falhar)
        import asyncio
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(test_function(mock_request))
        
        assert exc_info.value.status_code == 403
        assert "IP address not whitelisted" in str(exc_info.value.detail)
    
    def test_require_whitelisted_ip_decorator_blocked(self, mock_request):
        """Testa decorator com IP bloqueado"""
        # Bloquear IP
        ip_whitelist.block_ip("192.168.1.1")
        
        # Criar função decorada
        @require_whitelisted_ip()
        async def test_function(request):
            return "success"
        
        # Testar função (deve falhar)
        import asyncio
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(test_function(mock_request))
        
        assert exc_info.value.status_code == 403
        assert "IP address is blocked" in str(exc_info.value.detail)
        
        # Limpar
        ip_whitelist.unblock_ip("192.168.1.1")


class TestIPWhitelistEdgeCases:
    """Testes de casos edge para IPWhitelist"""
    
    @pytest.fixture
    def whitelist(self):
        """Instância do IPWhitelist para testes"""
        return IPWhitelist()
    
    def test_empty_string_ip(self, whitelist):
        """Testa IP vazio"""
        assert whitelist.add_ip("") is False
        assert whitelist.is_whitelisted("") is False
    
    def test_none_ip(self, whitelist):
        """Testa IP None"""
        assert whitelist.add_ip(None) is False
        assert whitelist.is_whitelisted(None) is False
    
    def test_very_long_ip(self, whitelist):
        """Testa IP muito longo"""
        long_ip = "192.168.1." + "1" * 100
        assert whitelist.add_ip(long_ip) is False
        assert whitelist.is_whitelisted(long_ip) is False
    
    def test_special_characters_in_ip(self, whitelist):
        """Testa IP com caracteres especiais"""
        special_ip = "192.168.1.1<script>"
        assert whitelist.add_ip(special_ip) is False
        assert whitelist.is_whitelisted(special_ip) is False
    
    def test_whitelist_removal_nonexistent(self, whitelist):
        """Testa remoção de IP que não existe"""
        assert whitelist.remove_ip("192.168.1.999") is False
        assert whitelist.remove_range("192.168.999.0/24") is False


if __name__ == "__main__":
    pytest.main([__file__]) 