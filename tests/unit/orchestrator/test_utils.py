"""
Testes unitários para utilitários do orquestrador
Tracing ID: TEST_UTILS_001_20241227
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys

# Adicionar path do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from infrastructure.orchestrator.integration import IntegrationSystem
from infrastructure.orchestrator.notifications import NotificationSystem
from infrastructure.orchestrator.metrics import MetricsSystem
from infrastructure.orchestrator.validation import ValidationSystem


class TestIntegrationSystem:
    """Testes para o sistema de integração"""
    
    @pytest.fixture
    def integration_system(self):
        """Instância do sistema de integração"""
        return IntegrationSystem()
    
    def test_integracao_com_modelos_existentes(self, integration_system):
        """Testa integração com modelos de dados existentes"""
        # Arrange
        nicho_data = {
            'nome': 'tecnologia',
            'categorias': ['programacao', 'ia', 'dados']
        }
        
        # Act
        resultado = integration_system.integrar_nicho(nicho_data)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert resultado['nicho_integrado'] == 'tecnologia'
    
    def test_integracao_com_sistema_prompts(self, integration_system):
        """Testa integração com sistema de prompts"""
        # Arrange
        prompt_data = {
            'template': 'Escreva um tutorial sobre {keyword}',
            'parametros': ['keyword', 'volume', 'competition']
        }
        
        # Act
        resultado = integration_system.integrar_prompt(prompt_data)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert 'template' in resultado['prompt_integrado']
    
    def test_integracao_com_logs_auditoria(self, integration_system):
        """Testa integração com sistema de logs e auditoria"""
        # Arrange
        log_data = {
            'acao': 'coleta_keywords',
            'nicho': 'tecnologia',
            'timestamp': '2024-12-27T10:00:00Z',
            'dados': {'keywords_count': 100}
        }
        
        # Act
        resultado = integration_system.registrar_log(log_data)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert resultado['log_id'] is not None


class TestNotificationSystem:
    """Testes para o sistema de notificações"""
    
    @pytest.fixture
    def notification_system(self):
        """Instância do sistema de notificações"""
        return NotificationSystem()
    
    def test_enviar_notificacao_progresso(self, notification_system):
        """Testa envio de notificação de progresso"""
        # Arrange
        dados_progresso = {
            'etapa': 'coleta',
            'progresso': 50,
            'tempo_estimado': 120
        }
        
        # Act
        resultado = notification_system.enviar_notificacao_progresso(dados_progresso)
        
        # Assert
        assert resultado['status'] == 'enviado'
        assert resultado['tipo'] == 'progresso'
    
    def test_enviar_alerta_falha(self, notification_system):
        """Testa envio de alerta de falha"""
        # Arrange
        dados_falha = {
            'etapa': 'validacao',
            'erro': 'API timeout',
            'severidade': 'alta'
        }
        
        # Act
        resultado = notification_system.enviar_alerta_falha(dados_falha)
        
        # Assert
        assert resultado['status'] == 'enviado'
        assert resultado['severidade'] == 'alta'
    
    def test_enviar_notificacao_conclusao(self, notification_system):
        """Testa envio de notificação de conclusão"""
        # Arrange
        dados_conclusao = {
            'nicho': 'tecnologia',
            'keywords_processadas': 150,
            'tempo_total': 300
        }
        
        # Act
        resultado = notification_system.enviar_notificacao_conclusao(dados_conclusao)
        
        # Assert
        assert resultado['status'] == 'enviado'
        assert resultado['tipo'] == 'conclusao'
    
    def test_configurar_canais_notificacao(self, notification_system):
        """Testa configuração de canais de notificação"""
        # Arrange
        canais = ['email', 'slack', 'webhook']
        
        # Act
        resultado = notification_system.configurar_canais(canais)
        
        # Assert
        assert resultado['status'] == 'configurado'
        assert len(resultado['canais_ativos']) == 3


class TestMetricsSystem:
    """Testes para o sistema de métricas"""
    
    @pytest.fixture
    def metrics_system(self):
        """Instância do sistema de métricas"""
        return MetricsSystem()
    
    def test_registrar_metrica_tempo(self, metrics_system):
        """Testa registro de métrica de tempo"""
        # Arrange
        dados_tempo = {
            'etapa': 'coleta',
            'tempo_execucao': 25.5,
            'timestamp': '2024-12-27T10:00:00Z'
        }
        
        # Act
        resultado = metrics_system.registrar_metrica_tempo(dados_tempo)
        
        # Assert
        assert resultado['status'] == 'registrado'
        assert resultado['metrica_id'] is not None
    
    def test_registrar_metrica_sucesso(self, metrics_system):
        """Testa registro de métrica de sucesso"""
        # Arrange
        dados_sucesso = {
            'etapa': 'validacao',
            'total_keywords': 100,
            'keywords_validas': 85,
            'taxa_sucesso': 0.85
        }
        
        # Act
        resultado = metrics_system.registrar_metrica_sucesso(dados_sucesso)
        
        # Assert
        assert resultado['status'] == 'registrado'
        assert resultado['taxa_sucesso'] == 0.85
    
    def test_obter_metricas_etapa(self, metrics_system):
        """Testa obtenção de métricas por etapa"""
        # Arrange
        etapa = 'coleta'
        
        # Act
        metricas = metrics_system.obter_metricas_etapa(etapa)
        
        # Assert
        assert 'tempo_medio' in metricas
        assert 'taxa_sucesso' in metricas
        assert 'total_execucoes' in metricas
    
    def test_obter_metricas_gerais(self, metrics_system):
        """Testa obtenção de métricas gerais"""
        # Act
        metricas = metrics_system.obter_metricas_gerais()
        
        # Assert
        assert 'tempo_total_medio' in metricas
        assert 'taxa_sucesso_geral' in metricas
        assert 'total_keywords_processadas' in metricas
    
    def test_calcular_tendencias(self, metrics_system):
        """Testa cálculo de tendências"""
        # Arrange
        dados_historicos = [
            {'tempo_execucao': 20, 'timestamp': '2024-12-25T10:00:00Z'},
            {'tempo_execucao': 22, 'timestamp': '2024-12-26T10:00:00Z'},
            {'tempo_execucao': 25, 'timestamp': '2024-12-27T10:00:00Z'}
        ]
        
        # Act
        tendencias = metrics_system.calcular_tendencias(dados_historicos)
        
        # Assert
        assert 'tendencia_tempo' in tendencias
        assert 'previsao_proxima_execucao' in tendencias


class TestValidationSystem:
    """Testes para o sistema de validação"""
    
    @pytest.fixture
    def validation_system(self):
        """Instância do sistema de validação"""
        return ValidationSystem()
    
    def test_validar_dados_keywords(self, validation_system):
        """Testa validação de dados de keywords"""
        # Arrange
        dados_validos = [
            {'keyword': 'python tutorial', 'volume': 1000, 'competition': 0.3},
            {'keyword': 'javascript guide', 'volume': 800, 'competition': 0.5}
        ]
        
        dados_invalidos = [
            {'keyword': '', 'volume': 1000, 'competition': 0.3},  # Keyword vazia
            {'keyword': 'teste', 'volume': -1, 'competition': 0.5},  # Volume negativo
            {'keyword': 'teste2', 'volume': 1000, 'competition': 1.5}  # Competition > 1
        ]
        
        # Act & Assert
        assert validation_system.validar_dados_keywords(dados_validos) is True
        assert validation_system.validar_dados_keywords(dados_invalidos) is False
    
    def test_validar_configuracao(self, validation_system):
        """Testa validação de configuração"""
        # Arrange
        config_valida = {
            'nicho': 'tecnologia',
            'max_keywords': 100,
            'timeout_etapa': 300,
            'retry_attempts': 3
        }
        
        config_invalida = {
            'nicho': '',  # Nicho vazio
            'max_keywords': -1,  # Valor negativo
            'timeout_etapa': 0  # Timeout zero
        }
        
        # Act & Assert
        assert validation_system.validar_configuracao(config_valida) is True
        assert validation_system.validar_configuracao(config_invalida) is False
    
    def test_validar_qualidade_conteudo(self, validation_system):
        """Testa validação de qualidade de conteúdo"""
        # Arrange
        conteudo_bom = "Este é um tutorial completo sobre Python com exemplos práticos e explicações detalhadas."
        conteudo_ruim = "Python é uma linguagem."
        
        # Act & Assert
        assert validation_system.validar_qualidade_conteudo(conteudo_bom) is True
        assert validation_system.validar_qualidade_conteudo(conteudo_ruim) is False
    
    def test_validar_formato_arquivo(self, validation_system):
        """Testa validação de formato de arquivo"""
        # Arrange
        dados_zip_validos = {
            'arquivo': 'output.zip',
            'tamanho': 1024,
            'formato': 'zip'
        }
        
        dados_zip_invalidos = {
            'arquivo': 'output.txt',
            'tamanho': 0,
            'formato': 'txt'
        }
        
        # Act & Assert
        assert validation_system.validar_formato_arquivo(dados_zip_validos) is True
        assert validation_system.validar_formato_arquivo(dados_zip_invalidos) is False
    
    def test_validar_integridade_dados(self, validation_system):
        """Testa validação de integridade de dados"""
        # Arrange
        dados_integridade = {
            'keywords_originais': 100,
            'keywords_validas': 85,
            'keywords_processadas': 80,
            'conteudos_gerados': 78
        }
        
        # Act
        resultado = validation_system.validar_integridade_dados(dados_integridade)
        
        # Assert
        assert resultado['status'] == 'valido'
        assert resultado['taxa_perda'] < 0.25  # Máximo 25% de perda
    
    def test_validar_metadados(self, validation_system):
        """Testa validação de metadados"""
        # Arrange
        metadados_validos = {
            'data_exportacao': '2024-12-27T10:00:00Z',
            'total_keywords': 100,
            'total_conteudos': 95,
            'tempo_processamento': 300,
            'versao_sistema': '1.0.0'
        }
        
        metadados_invalidos = {
            'data_exportacao': 'data_invalida',
            'total_keywords': -1,
            'tempo_processamento': 'tempo_invalido'
        }
        
        # Act & Assert
        assert validation_system.validar_metadados(metadados_validos) is True
        assert validation_system.validar_metadados(metadados_invalidos) is False


class TestCacheSystem:
    """Testes para o sistema de cache"""
    
    @pytest.fixture
    def cache_system(self):
        """Instância do sistema de cache"""
        with patch('infrastructure.orchestrator.cache.CacheSystem') as mock_cache:
            return mock_cache.return_value
    
    def test_obter_dados_cache(self, cache_system):
        """Testa obtenção de dados do cache"""
        # Arrange
        chave = 'tecnologia_keywords'
        dados_cache = {
            'keywords': ['python tutorial', 'javascript guide'],
            'timestamp': '2024-12-27T10:00:00Z'
        }
        cache_system.obter.return_value = dados_cache
        
        # Act
        resultado = cache_system.obter(chave)
        
        # Assert
        assert resultado == dados_cache
        cache_system.obter.assert_called_once_with(chave)
    
    def test_salvar_dados_cache(self, cache_system):
        """Testa salvamento de dados no cache"""
        # Arrange
        chave = 'tecnologia_keywords'
        dados = {
            'keywords': ['python tutorial', 'javascript guide'],
            'timestamp': '2024-12-27T10:00:00Z'
        }
        cache_system.salvar.return_value = True
        
        # Act
        resultado = cache_system.salvar(chave, dados, ttl=3600)
        
        # Assert
        assert resultado is True
        cache_system.salvar.assert_called_once_with(chave, dados, ttl=3600)
    
    def test_invalidar_cache(self, cache_system):
        """Testa invalidação de cache"""
        # Arrange
        chave = 'tecnologia_keywords'
        cache_system.invalidar.return_value = True
        
        # Act
        resultado = cache_system.invalidar(chave)
        
        # Assert
        assert resultado is True
        cache_system.invalidar.assert_called_once_with(chave)
    
    def test_limpeza_cache_automatica(self, cache_system):
        """Testa limpeza automática do cache"""
        # Arrange
        cache_system.limpar_expirados.return_value = 5
        
        # Act
        itens_removidos = cache_system.limpar_expirados()
        
        # Assert
        assert itens_removidos == 5
        cache_system.limpar_expirados.assert_called_once()


class TestFileSystemUtils:
    """Testes para utilitários de sistema de arquivos"""
    
    @pytest.fixture
    def temp_dir(self):
        """Diretório temporário para testes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_criar_diretorio_seguro(self, temp_dir):
        """Testa criação segura de diretório"""
        # Arrange
        novo_dir = os.path.join(temp_dir, 'novo_diretorio')
        
        # Act
        from infrastructure.orchestrator.utils import criar_diretorio_seguro
        resultado = criar_diretorio_seguro(novo_dir)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert os.path.exists(novo_dir)
    
    def test_verificar_espaco_disco(self, temp_dir):
        """Testa verificação de espaço em disco"""
        # Act
        from infrastructure.orchestrator.utils import verificar_espaco_disco
        resultado = verificar_espaco_disco(temp_dir)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert 'espaco_livre_mb' in resultado
        assert resultado['espaco_livre_mb'] > 0
    
    def test_backup_arquivo(self, temp_dir):
        """Testa backup de arquivo"""
        # Arrange
        arquivo_original = os.path.join(temp_dir, 'teste.txt')
        with open(arquivo_original, 'w') as f:
            f.write('conteúdo de teste')
        
        # Act
        from infrastructure.orchestrator.utils import backup_arquivo
        resultado = backup_arquivo(arquivo_original)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert os.path.exists(resultado['arquivo_backup'])
    
    def test_limpeza_arquivos_antigos(self, temp_dir):
        """Testa limpeza de arquivos antigos"""
        # Arrange
        arquivo_antigo = os.path.join(temp_dir, 'arquivo_antigo.txt')
        with open(arquivo_antigo, 'w') as f:
            f.write('conteúdo antigo')
        
        # Modificar timestamp para simular arquivo antigo
        os.utime(arquivo_antigo, (0, 0))
        
        # Act
        from infrastructure.orchestrator.utils import limpeza_arquivos_antigos
        resultado = limpeza_arquivos_antigos(temp_dir, dias=1)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert resultado['arquivos_removidos'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-value']) 