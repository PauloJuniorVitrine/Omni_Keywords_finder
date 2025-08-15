from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Testes Unitários - CDN Cache Invalidation
Tracing ID: IMP003_CDN_TESTS_001
Data: 2025-01-27
Versão: 1.0
Status: Em Implementação

Testes abrangentes para o sistema de invalidação de cache CDN
"""

import pytest
import unittest.mock as mock
from unittest.mock import Mock, patch, MagicMock
import json
import yaml
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path

# Importa o módulo a ser testado
import sys
sys.path.append('scripts')
from cdn_invalidation import CDNInvalidationManager, InvalidationConfig, CacheWarmingConfig

class TestCDNInvalidationManager:
    """Testes para CDNInvalidationManager"""
    
    @pytest.fixture
    def mock_config(self):
        """Configuração mock para testes"""
        return {
            'cdn': {
                'distribution_id': 'E1234567890ABCD',
                'invalidation': {
                    'automatic': {
                        'enabled': True
                    },
                    'manual': {
                        'enabled': True,
                        'patterns': ['/api/*', '/static/*'],
                        'max_invalidations_per_month': 1000
                    }
                },
                'cache_warming': {
                    'urls': [
                        'https://omni-keywords-finder.com/',
                        'https://omni-keywords-finder.com/api/health'
                    ],
                    'concurrent_requests': 5,
                    'timeout': 30,
                    'retry_attempts': 3
                }
            }
        }
    
    @pytest.fixture
    def mock_cloudfront_client(self):
        """Mock do cliente CloudFront"""
        client = Mock()
        
        # Mock para list_invalidations
        client.list_invalidations.return_value = {
            'InvalidationList': {
                'Items': [
                    {
                        'Id': 'I1234567890ABCD',
                        'Status': 'Completed',
                        'CreateTime': datetime.now() - timedelta(days=1)
                    },
                    {
                        'Id': 'I0987654321DCBA',
                        'Status': 'Completed',
                        'CreateTime': datetime.now() - timedelta(days=15)
                    }
                ]
            }
        }
        
        # Mock para create_invalidation
        client.create_invalidation.return_value = {
            'Invalidation': {
                'Id': 'I1234567890ABCD',
                'Status': 'InProgress'
            }
        }
        
        # Mock para get_invalidation
        client.get_invalidation.return_value = {
            'Invalidation': {
                'Id': 'I1234567890ABCD',
                'Status': 'Completed'
            }
        }
        
        return client
    
    @pytest.fixture
    def mock_cloudwatch_client(self):
        """Mock do cliente CloudWatch"""
        client = Mock()
        client.put_metric_data.return_value = {}
        client.get_metric_statistics.return_value = {
            'Datapoints': [
                {
                    'Timestamp': datetime.now(),
                    'Average': 95.5,
                    'Sum': 1000,
                    'Maximum': 100
                }
            ]
        }
        return client
    
    @pytest.fixture
    def temp_config_file(self, mock_config):
        """Arquivo de configuração temporário"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(mock_config, f)
            temp_file = f.name
        
        yield temp_file
        
        # Limpa o arquivo temporário
        os.unlink(temp_file)
    
    @patch('boto3.client')
    def test_init_success(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa inicialização bem-sucedida"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        manager = CDNInvalidationManager(temp_config_file)
        
        assert manager.invalidation_config.distribution_id == 'E1234567890ABCD'
        assert manager.invalidation_config.automatic_enabled is True
        assert manager.invalidation_config.manual_enabled is True
        assert len(manager.cache_warming_config.urls) == 2
    
    @patch('boto3.client')
    def test_init_config_file_not_found(self, mock_boto3_client):
        """Testa erro quando arquivo de configuração não existe"""
        with pytest.raises(FileNotFoundError):
            CDNInvalidationManager('nonexistent_config.yaml')
    
    @patch('boto3.client')
    def test_init_invalid_yaml(self, mock_boto3_client):
        """Testa erro com YAML inválido"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            temp_file = f.name
        
        try:
            with pytest.raises(Exception):
                CDNInvalidationManager(temp_file)
        finally:
            os.unlink(temp_file)
    
    @patch('boto3.client')
    def test_get_invalidation_count(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa contagem de invalidações"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        manager = CDNInvalidationManager(temp_config_file)
        count = manager.get_invalidation_count()
        
        assert count == 2
        mock_cloudfront_client.list_invalidations.assert_called_once()
    
    @patch('boto3.client')
    def test_get_invalidation_count_error(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa erro na contagem de invalidações"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        mock_cloudfront_client.list_invalidations.side_effect = Exception("AWS Error")
        
        manager = CDNInvalidationManager(temp_config_file)
        count = manager.get_invalidation_count()
        
        assert count == 0
    
    @patch('boto3.client')
    def test_create_invalidation_success(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa criação bem-sucedida de invalidação"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        manager = CDNInvalidationManager(temp_config_file)
        invalidation_id = manager.create_invalidation(['/api/test', '/static/css/main.css'])
        
        assert invalidation_id == 'I1234567890ABCD'
        mock_cloudfront_client.create_invalidation.assert_called_once()
        mock_cloudwatch_client.put_metric_data.assert_called_once()
    
    @patch('boto3.client')
    def test_create_invalidation_limit_exceeded(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa erro quando limite de invalidações é excedido"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        # Mock para simular limite excedido
        mock_cloudfront_client.list_invalidations.return_value = {
            'InvalidationList': {
                'Items': [{'Status': 'Completed', 'CreateTime': datetime.now()}] * 1001
            }
        }
        
        manager = CDNInvalidationManager(temp_config_file)
        
        with pytest.raises(ValueError, match="Limite de invalidações atingido"):
            manager.create_invalidation(['/api/test'])
    
    @patch('boto3.client')
    def test_wait_for_invalidation_success(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa aguardar invalidação com sucesso"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        manager = CDNInvalidationManager(temp_config_file)
        success = manager.wait_for_invalidation('I1234567890ABCD')
        
        assert success is True
        mock_cloudfront_client.get_invalidation.assert_called_once()
    
    @patch('boto3.client')
    def test_wait_for_invalidation_timeout(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa timeout ao aguardar invalidação"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        # Mock para simular invalidação sempre em progresso
        mock_cloudfront_client.get_invalidation.return_value = {
            'Invalidation': {
                'Id': 'I1234567890ABCD',
                'Status': 'InProgress'
            }
        }
        
        manager = CDNInvalidationManager(temp_config_file)
        success = manager.wait_for_invalidation('I1234567890ABCD', timeout=1)
        
        assert success is False
    
    @patch('boto3.client')
    def test_automatic_invalidation_deploy(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa invalidação automática para deploy"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        manager = CDNInvalidationManager(temp_config_file)
        success = manager.automatic_invalidation('deploy')
        
        assert success is True
        mock_cloudfront_client.create_invalidation.assert_called_once()
    
    @patch('boto3.client')
    def test_automatic_invalidation_disabled(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa invalidação automática desabilitada"""
        # Modifica configuração para desabilitar invalidação automática
        config = {
            'cdn': {
                'distribution_id': 'E1234567890ABCD',
                'invalidation': {
                    'automatic': {
                        'enabled': False
                    },
                    'manual': {
                        'enabled': True,
                        'patterns': ['/api/*', '/static/*'],
                        'max_invalidations_per_month': 1000
                    }
                },
                'cache_warming': {
                    'urls': [],
                    'concurrent_requests': 5,
                    'timeout': 30,
                    'retry_attempts': 3
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_file = f.name
        
        try:
            mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
            
            manager = CDNInvalidationManager(temp_file)
            success = manager.automatic_invalidation('deploy')
            
            assert success is False
            mock_cloudfront_client.create_invalidation.assert_not_called()
        finally:
            os.unlink(temp_file)
    
    @patch('boto3.client')
    def test_automatic_invalidation_invalid_type(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa invalidação automática com tipo inválido"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        manager = CDNInvalidationManager(temp_config_file)
        success = manager.automatic_invalidation('invalid_type')
        
        assert success is False
    
    @patch('requests.get')
    @patch('boto3.client')
    def test_cache_warming_success(self, mock_boto3_client, mock_requests_get, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa cache warming bem-sucedido"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        # Mock para requests bem-sucedidos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response
        
        manager = CDNInvalidationManager(temp_config_file)
        results = manager.cache_warming()
        
        assert len(results) == 2
        assert all(results.values())  # Todas as URLs foram bem-sucedidas
        mock_cloudwatch_client.put_metric_data.assert_called_once()
    
    @patch('requests.get')
    @patch('boto3.client')
    def test_cache_warming_partial_failure(self, mock_boto3_client, mock_requests_get, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa cache warming com falhas parciais"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        # Mock para requests com falhas
        def mock_get(url):
            response = Mock()
            if 'health' in url:
                response.status_code = 200
            else:
                response.status_code = 500
            return response
        
        mock_requests_get.side_effect = mock_get
        
        manager = CDNInvalidationManager(temp_config_file)
        results = manager.cache_warming()
        
        assert len(results) == 2
        assert results['https://omni-keywords-finder.com/api/health'] is True
        assert results['https://omni-keywords-finder.com/'] is False
    
    @patch('requests.get')
    @patch('boto3.client')
    def test_cache_warming_exception(self, mock_boto3_client, mock_requests_get, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa cache warming com exceção"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        mock_requests_get.side_effect = Exception("Network error")
        
        manager = CDNInvalidationManager(temp_config_file)
        results = manager.cache_warming()
        
        assert results == {}
    
    @patch('boto3.client')
    def test_get_cdn_metrics(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa obtenção de métricas do CDN"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        manager = CDNInvalidationManager(temp_config_file)
        metrics = manager.get_cdn_metrics()
        
        assert 'Requests' in metrics
        assert 'CacheHitRate' in metrics
        assert metrics['Requests']['average'] == 95.5
        mock_cloudwatch_client.get_metric_statistics.assert_called()
    
    @patch('boto3.client')
    def test_get_cdn_metrics_error(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa erro ao obter métricas do CDN"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        mock_cloudwatch_client.get_metric_statistics.side_effect = Exception("CloudWatch error")
        
        manager = CDNInvalidationManager(temp_config_file)
        metrics = manager.get_cdn_metrics()
        
        assert metrics == {}

class TestInvalidationConfig:
    """Testes para InvalidationConfig"""
    
    def test_invalidation_config_creation(self):
        """Testa criação de InvalidationConfig"""
        config = InvalidationConfig(
            distribution_id='E1234567890ABCD',
            patterns=['/api/*', '/static/*'],
            max_invalidations_per_month=1000,
            automatic_enabled=True,
            manual_enabled=True
        )
        
        assert config.distribution_id == 'E1234567890ABCD'
        assert len(config.patterns) == 2
        assert config.max_invalidations_per_month == 1000
        assert config.automatic_enabled is True
        assert config.manual_enabled is True

class TestCacheWarmingConfig:
    """Testes para CacheWarmingConfig"""
    
    def test_cache_warming_config_creation(self):
        """Testa criação de CacheWarmingConfig"""
        config = CacheWarmingConfig(
            urls=['https://example.com'],
            concurrent_requests=5,
            timeout=30,
            retry_attempts=3
        )
        
        assert len(config.urls) == 1
        assert config.concurrent_requests == 5
        assert config.timeout == 30
        assert config.retry_attempts == 3

class TestIntegration:
    """Testes de integração"""
    
    @patch('boto3.client')
    def test_full_invalidation_workflow(self, mock_boto3_client, temp_config_file, mock_cloudfront_client, mock_cloudwatch_client):
        """Testa workflow completo de invalidação"""
        mock_boto3_client.side_effect = [mock_cloudfront_client, mock_cloudwatch_client]
        
        manager = CDNInvalidationManager(temp_config_file)
        
        # Testa criação de invalidação
        invalidation_id = manager.create_invalidation(['/api/test'])
        assert invalidation_id == 'I1234567890ABCD'
        
        # Testa aguardar conclusão
        success = manager.wait_for_invalidation(invalidation_id)
        assert success is True
        
        # Testa métricas
        metrics = manager.get_cdn_metrics()
        assert isinstance(metrics, dict)

if __name__ == '__main__':
    pytest.main([__file__, '-value']) 