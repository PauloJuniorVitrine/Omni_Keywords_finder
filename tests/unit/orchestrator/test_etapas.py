"""
Testes unitários para todas as etapas do orquestrador
Tracing ID: TEST_ETAPAS_001_20241227
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys
import os

# Adicionar path do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from infrastructure.orchestrator.etapas.etapa_coleta import EtapaColeta
from infrastructure.orchestrator.etapas.etapa_validacao import EtapaValidacao
from infrastructure.orchestrator.etapas.etapa_processamento import EtapaProcessamento
from infrastructure.orchestrator.etapas.etapa_preenchimento import EtapaPreenchimento
from infrastructure.orchestrator.etapas.etapa_exportacao import EtapaExportacao


class TestEtapaColeta:
    """Testes para a etapa de coleta de keywords"""
    
    @pytest.fixture
    def config_coleta(self):
        """Configuração para testes de coleta"""
        return {
            'nicho': 'tecnologia',
            'max_keywords': 100,
            'timeout': 300,
            'rate_limit': 10
        }
    
    @pytest.fixture
    def etapa_coleta(self, config_coleta):
        """Instância da etapa de coleta"""
        return EtapaColeta(config_coleta)
    
    def test_inicializacao_etapa_coleta(self, config_coleta):
        """Testa inicialização correta da etapa de coleta"""
        # Act
        etapa = EtapaColeta(config_coleta)
        
        # Assert
        assert etapa.config == config_coleta
        assert etapa.nicho == 'tecnologia'
        assert etapa.max_keywords == 100
    
    @patch('infrastructure.orchestrator.etapas.etapa_coleta.ColetorKeywords')
    def test_execucao_coleta_sucesso(self, mock_coletor, etapa_coleta):
        """Testa execução bem-sucedida da coleta"""
        # Arrange
        mock_coletor.return_value.coletar.return_value = [
            {'keyword': 'python tutorial', 'volume': 1000},
            {'keyword': 'javascript guide', 'volume': 800}
        ]
        
        # Act
        resultado = etapa_coleta.executar({'nicho': 'tecnologia'})
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert len(resultado['keywords']) == 2
        assert resultado['keywords'][0]['keyword'] == 'python tutorial'
    
    @patch('infrastructure.orchestrator.etapas.etapa_coleta.ColetorKeywords')
    def test_execucao_coleta_falha(self, mock_coletor, etapa_coleta):
        """Testa execução com falha na coleta"""
        # Arrange
        mock_coletor.return_value.coletar.side_effect = Exception("Erro de API")
        
        # Act
        resultado = etapa_coleta.executar({'nicho': 'tecnologia'})
        
        # Assert
        assert resultado['status'] == 'erro'
        assert 'Erro de API' in resultado['mensagem']
    
    def test_validacao_dados_coleta(self, etapa_coleta):
        """Testa validação dos dados coletados"""
        # Arrange
        dados_validos = [
            {'keyword': 'teste1', 'volume': 100},
            {'keyword': 'teste2', 'volume': 200}
        ]
        
        dados_invalidos = [
            {'keyword': '', 'volume': 100},  # Keyword vazia
            {'keyword': 'teste2', 'volume': -1}  # Volume negativo
        ]
        
        # Act & Assert
        assert etapa_coleta.validar_dados(dados_validos) is True
        assert etapa_coleta.validar_dados(dados_invalidos) is False
    
    def test_filtro_keywords_por_volume(self, etapa_coleta):
        """Testa filtro de keywords por volume mínimo"""
        # Arrange
        keywords = [
            {'keyword': 'baixo', 'volume': 50},
            {'keyword': 'medio', 'volume': 500},
            {'keyword': 'alto', 'volume': 5000}
        ]
        
        # Act
        filtradas = etapa_coleta.filtrar_por_volume(keywords, volume_minimo=100)
        
        # Assert
        assert len(filtradas) == 2
        assert 'baixo' not in [key['keyword'] for key in filtradas]
    
    def test_rate_limiting(self, etapa_coleta):
        """Testa controle de rate limiting"""
        # Arrange
        with patch('time.sleep') as mock_sleep:
            # Act
            etapa_coleta.aplicar_rate_limit()
            
            # Assert
            mock_sleep.assert_called_once()


class TestEtapaValidacao:
    """Testes para a etapa de validação de keywords"""
    
    @pytest.fixture
    def config_validacao(self):
        """Configuração para testes de validação"""
        return {
            'google_api_key': 'test_key',
            'min_volume': 100,
            'max_competition': 0.8,
            'timeout': 300
        }
    
    @pytest.fixture
    def etapa_validacao(self, config_validacao):
        """Instância da etapa de validação"""
        return EtapaValidacao(config_validacao)
    
    def test_inicializacao_etapa_validacao(self, config_validacao):
        """Testa inicialização correta da etapa de validação"""
        # Act
        etapa = EtapaValidacao(config_validacao)
        
        # Assert
        assert etapa.config == config_validacao
        assert etapa.min_volume == 100
        assert etapa.max_competition == 0.8
    
    @patch('infrastructure.orchestrator.etapas.etapa_validacao.GoogleKeywordPlannerValidator')
    def test_validacao_com_google_sucesso(self, mock_validator, etapa_validacao):
        """Testa validação bem-sucedida com Google Keyword Planner"""
        # Arrange
        keywords = ['python tutorial', 'javascript guide']
        mock_validator.return_value.validar.return_value = [
            {'keyword': 'python tutorial', 'volume': 1000, 'competition': 0.3, 'valid': True},
            {'keyword': 'javascript guide', 'volume': 800, 'competition': 0.7, 'valid': True}
        ]
        
        # Act
        resultado = etapa_validacao.executar({'keywords': keywords})
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert len(resultado['keywords_validas']) == 2
        assert all(key['valid'] for key in resultado['keywords_validas'])
    
    @patch('infrastructure.orchestrator.etapas.etapa_validacao.GoogleKeywordPlannerValidator')
    def test_validacao_com_google_falha(self, mock_validator, etapa_validacao):
        """Testa falha na validação com Google Keyword Planner"""
        # Arrange
        mock_validator.return_value.validar.side_effect = Exception("API limit exceeded")
        
        # Act
        resultado = etapa_validacao.executar({'keywords': ['teste']})
        
        # Assert
        assert resultado['status'] == 'erro'
        assert 'API limit exceeded' in resultado['mensagem']
    
    def test_filtro_por_volume_minimo(self, etapa_validacao):
        """Testa filtro por volume mínimo"""
        # Arrange
        keywords = [
            {'keyword': 'baixo', 'volume': 50, 'valid': True},
            {'keyword': 'medio', 'volume': 500, 'valid': True},
            {'keyword': 'alto', 'volume': 5000, 'valid': True}
        ]
        
        # Act
        filtradas = etapa_validacao.filtrar_por_volume(keywords, 100)
        
        # Assert
        assert len(filtradas) == 2
        assert 'baixo' not in [key['keyword'] for key in filtradas]
    
    def test_filtro_por_competicao(self, etapa_validacao):
        """Testa filtro por nível de competição"""
        # Arrange
        keywords = [
            {'keyword': 'baixa_comp', 'competition': 0.2, 'valid': True},
            {'keyword': 'media_comp', 'competition': 0.5, 'valid': True},
            {'keyword': 'alta_comp', 'competition': 0.9, 'valid': True}
        ]
        
        # Act
        filtradas = etapa_validacao.filtrar_por_competicao(keywords, 0.8)
        
        # Assert
        assert len(filtradas) == 2
        assert 'alta_comp' not in [key['keyword'] for key in filtradas]
    
    def test_calculo_score_relevancia(self, etapa_validacao):
        """Testa cálculo de score de relevância"""
        # Arrange
        keyword_data = {
            'volume': 1000,
            'competition': 0.3,
            'cpc': 2.5
        }
        
        # Act
        score = etapa_validacao.calcular_score_relevancia(keyword_data)
        
        # Assert
        assert 0 <= score <= 100
        assert isinstance(score, (int, float))


class TestEtapaProcessamento:
    """Testes para a etapa de processamento de keywords"""
    
    @pytest.fixture
    def config_processamento(self):
        """Configuração para testes de processamento"""
        return {
            'normalizar': True,
            'clusterizar': True,
            'min_score': 50,
            'max_keywords_por_cluster': 10
        }
    
    @pytest.fixture
    def etapa_processamento(self, config_processamento):
        """Instância da etapa de processamento"""
        return EtapaProcessamento(config_processamento)
    
    def test_inicializacao_etapa_processamento(self, config_processamento):
        """Testa inicialização correta da etapa de processamento"""
        # Act
        etapa = EtapaProcessamento(config_processamento)
        
        # Assert
        assert etapa.config == config_processamento
        assert etapa.normalizar is True
        assert etapa.clusterizar is True
    
    def test_normalizacao_keywords(self, etapa_processamento):
        """Testa normalização de keywords"""
        # Arrange
        keywords = [
            {'keyword': 'Python Tutorial', 'volume': 1000},
            {'keyword': 'python tutorial', 'volume': 1000},
            {'keyword': 'PYTHON TUTORIAL', 'volume': 1000}
        ]
        
        # Act
        normalizadas = etapa_processamento.normalizar_keywords(keywords)
        
        # Assert
        assert len(normalizadas) == 1  # Deve agrupar keywords similares
        assert normalizadas[0]['keyword'] == 'python tutorial'
        assert normalizadas[0]['volume'] == 3000  # Soma dos volumes
    
    def test_clusterizacao_semantica(self, etapa_processamento):
        """Testa clusterização semântica de keywords"""
        # Arrange
        keywords = [
            {'keyword': 'python tutorial', 'volume': 1000},
            {'keyword': 'python course', 'volume': 800},
            {'keyword': 'javascript tutorial', 'volume': 900},
            {'keyword': 'javascript course', 'volume': 700}
        ]
        
        # Act
        clusters = etapa_processamento.clusterizar_keywords(keywords)
        
        # Assert
        assert len(clusters) == 2  # Deve criar 2 clusters
        assert any('python' in cluster['keywords'][0]['keyword'] for cluster in clusters)
        assert any('javascript' in cluster['keywords'][0]['keyword'] for cluster in clusters)
    
    def test_calculo_scores(self, etapa_processamento):
        """Testa cálculo de scores para keywords"""
        # Arrange
        keywords = [
            {'keyword': 'teste1', 'volume': 1000, 'competition': 0.3},
            {'keyword': 'teste2', 'volume': 500, 'competition': 0.7}
        ]
        
        # Act
        com_scores = etapa_processamento.calcular_scores(keywords)
        
        # Assert
        assert all('score' in key for key in com_scores)
        assert com_scores[0]['score'] > com_scores[1]['score']  # Maior volume = maior score
    
    def test_filtro_por_score_minimo(self, etapa_processamento):
        """Testa filtro por score mínimo"""
        # Arrange
        keywords = [
            {'keyword': 'baixo', 'score': 30},
            {'keyword': 'medio', 'score': 60},
            {'keyword': 'alto', 'score': 90}
        ]
        
        # Act
        filtradas = etapa_processamento.filtrar_por_score(keywords, 50)
        
        # Assert
        assert len(filtradas) == 2
        assert 'baixo' not in [key['keyword'] for key in filtradas]
    
    def test_execucao_processamento_completo(self, etapa_processamento):
        """Testa execução completa do processamento"""
        # Arrange
        dados_entrada = {
            'keywords': [
                {'keyword': 'Python Tutorial', 'volume': 1000, 'competition': 0.3},
                {'keyword': 'python tutorial', 'volume': 800, 'competition': 0.4},
                {'keyword': 'javascript guide', 'volume': 900, 'competition': 0.5}
            ]
        }
        
        # Act
        resultado = etapa_processamento.executar(dados_entrada)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert 'keywords_processadas' in resultado
        assert 'clusters' in resultado
        assert len(resultado['keywords_processadas']) > 0


class TestEtapaPreenchimento:
    """Testes para a etapa de preenchimento com IA"""
    
    @pytest.fixture
    def config_preenchimento(self):
        """Configuração para testes de preenchimento"""
        return {
            'modelo_ia': 'gpt-3.5-turbo',
            'max_tokens': 1000,
            'temperature': 0.7,
            'prompts_template': 'templates/prompts.json'
        }
    
    @pytest.fixture
    def etapa_preenchimento(self, config_preenchimento):
        """Instância da etapa de preenchimento"""
        return EtapaPreenchimento(config_preenchimento)
    
    def test_inicializacao_etapa_preenchimento(self, config_preenchimento):
        """Testa inicialização correta da etapa de preenchimento"""
        # Act
        etapa = EtapaPreenchimento(config_preenchimento)
        
        # Assert
        assert etapa.config == config_preenchimento
        assert etapa.modelo_ia == 'gpt-3.5-turbo'
        assert etapa.max_tokens == 1000
    
    @patch('infrastructure.orchestrator.etapas.etapa_preenchimento.OpenAI')
    def test_geracao_conteudo_sucesso(self, mock_openai, etapa_preenchimento):
        """Testa geração bem-sucedida de conteúdo"""
        # Arrange
        mock_client = Mock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = "Conteúdo gerado com sucesso"
        mock_openai.return_value = mock_client
        
        keyword = {'keyword': 'python tutorial', 'volume': 1000}
        prompt_template = "Escreva um tutorial sobre {keyword}"
        
        # Act
        resultado = etapa_preenchimento.gerar_conteudo(keyword, prompt_template)
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert 'Conteúdo gerado com sucesso' in resultado['conteudo']
    
    @patch('infrastructure.orchestrator.etapas.etapa_preenchimento.OpenAI')
    def test_geracao_conteudo_falha(self, mock_openai, etapa_preenchimento):
        """Testa falha na geração de conteúdo"""
        # Arrange
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        
        # Act
        resultado = etapa_preenchimento.gerar_conteudo({}, "prompt")
        
        # Assert
        assert resultado['status'] == 'erro'
        assert 'API error' in resultado['mensagem']
    
    def test_validacao_qualidade_conteudo(self, etapa_preenchimento):
        """Testa validação de qualidade do conteúdo gerado"""
        # Arrange
        conteudo_bom = "Este é um tutorial completo sobre Python com exemplos práticos."
        conteudo_ruim = "Python é uma linguagem."
        
        # Act & Assert
        assert etapa_preenchimento.validar_qualidade(conteudo_bom) is True
        assert etapa_preenchimento.validar_qualidade(conteudo_ruim) is False
    
    def test_execucao_preenchimento_completo(self, etapa_preenchimento):
        """Testa execução completa do preenchimento"""
        # Arrange
        dados_entrada = {
            'keywords_processadas': [
                {'keyword': 'python tutorial', 'volume': 1000, 'score': 85},
                {'keyword': 'javascript guide', 'volume': 800, 'score': 75}
            ]
        }
        
        with patch.object(etapa_preenchimento, 'gerar_conteudo') as mock_gerar:
            mock_gerar.return_value = {
                'status': 'sucesso',
                'conteudo': 'Conteúdo gerado'
            }
            
            # Act
            resultado = etapa_preenchimento.executar(dados_entrada)
            
            # Assert
            assert resultado['status'] == 'sucesso'
            assert 'conteudos_gerados' in resultado
            assert len(resultado['conteudos_gerados']) == 2


class TestEtapaExportacao:
    """Testes para a etapa de exportação"""
    
    @pytest.fixture
    def config_exportacao(self):
        """Configuração para testes de exportação"""
        return {
            'formato_saida': 'zip',
            'organizar_por_nicho': True,
            'incluir_metadados': True,
            'diretorio_saida': 'output/'
        }
    
    @pytest.fixture
    def etapa_exportacao(self, config_exportacao):
        """Instância da etapa de exportação"""
        return EtapaExportacao(config_exportacao)
    
    def test_inicializacao_etapa_exportacao(self, config_exportacao):
        """Testa inicialização correta da etapa de exportação"""
        # Act
        etapa = EtapaExportacao(config_exportacao)
        
        # Assert
        assert etapa.config == config_exportacao
        assert etapa.formato_saida == 'zip'
        assert etapa.organizar_por_nicho is True
    
    @patch('zipfile.ZipFile')
    @patch('os.makedirs')
    def test_criacao_arquivo_zip(self, mock_makedirs, mock_zipfile, etapa_exportacao):
        """Testa criação de arquivo ZIP"""
        # Arrange
        mock_zip = Mock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        dados = {
            'conteudos_gerados': [
                {'keyword': 'teste1', 'conteudo': 'conteudo1'},
                {'keyword': 'teste2', 'conteudo': 'conteudo2'}
            ]
        }
        
        # Act
        resultado = etapa_exportacao.criar_arquivo_zip(dados, 'teste_nicho')
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert 'arquivo_zip' in resultado
        mock_zip.writestr.assert_called()
    
    def test_geracao_metadados(self, etapa_exportacao):
        """Testa geração de metadados"""
        # Arrange
        dados = {
            'keywords_processadas': 10,
            'conteudos_gerados': 8,
            'tempo_processamento': 300
        }
        
        # Act
        metadados = etapa_exportacao.gerar_metadados(dados)
        
        # Assert
        assert 'data_exportacao' in metadados
        assert 'total_keywords' in metadados
        assert 'total_conteudos' in metadados
        assert 'tempo_processamento' in metadados
    
    def test_organizacao_por_nicho(self, etapa_exportacao):
        """Testa organização de arquivos por nicho"""
        # Arrange
        dados = {
            'nicho': 'tecnologia',
            'conteudos_gerados': [
                {'keyword': 'python', 'conteudo': 'conteudo1'},
                {'keyword': 'javascript', 'conteudo': 'conteudo2'}
            ]
        }
        
        # Act
        organizados = etapa_exportacao.organizar_por_nicho(dados)
        
        # Assert
        assert organizados['diretorio'] == 'tecnologia'
        assert len(organizados['arquivos']) == 2
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_execucao_exportacao_completa(self, mock_makedirs, mock_exists, etapa_exportacao):
        """Testa execução completa da exportação"""
        # Arrange
        mock_exists.return_value = False
        
        dados_entrada = {
            'nicho': 'tecnologia',
            'conteudos_gerados': [
                {'keyword': 'python tutorial', 'conteudo': 'Tutorial completo'},
                {'keyword': 'javascript guide', 'conteudo': 'Guia completo'}
            ],
            'metadados': {
                'total_keywords': 2,
                'tempo_processamento': 300
            }
        }
        
        with patch.object(etapa_exportacao, 'criar_arquivo_zip') as mock_zip:
            mock_zip.return_value = {
                'status': 'sucesso',
                'arquivo_zip': 'output/tecnologia.zip'
            }
            
            # Act
            resultado = etapa_exportacao.executar(dados_entrada)
            
            # Assert
            assert resultado['status'] == 'sucesso'
            assert 'arquivo_exportado' in resultado
            assert resultado['arquivo_exportado'] == 'output/tecnologia.zip'


if __name__ == '__main__':
    pytest.main([__file__, '-value']) 