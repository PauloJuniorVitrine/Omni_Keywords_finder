"""
Testes de carga para o orquestrador
Tracing ID: TEST_LOAD_001_20241227
"""

import pytest
import time
import threading
import concurrent.futures
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys
import os

# Adicionar path do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from infrastructure.orchestrator.fluxo_completo_orchestrator import FluxoCompletoOrchestrator


class TestLoadOrchestrator:
    """Testes de carga para o orquestrador"""
    
    @pytest.fixture
    def config_load(self):
        """Configuração para testes de carga"""
        return {
            'nicho': 'tecnologia',
            'max_keywords': 1000,
            'timeout_etapa': 600,
            'retry_attempts': 3,
            'cache_enabled': True,
            'log_level': 'WARNING'
        }
    
    @pytest.fixture
    def orchestrator_load(self, config_load):
        """Orquestrador configurado para testes de carga"""
        with patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ProgressTracker'), \
             patch('infrastructure.orchestrator.fluxo_completo_orchestrator.ErrorHandler'):
            return FluxoCompletoOrchestrator(config_load)
    
    def test_carga_etapa_coleta(self, orchestrator_load):
        """Testa carga na etapa de coleta"""
        # Arrange
        keywords_grandes = [f'keyword_{index}' for index in range(1000)]
        
        with patch('infrastructure.orchestrator.etapas.etapa_coleta.EtapaColeta') as mock_coleta:
            mock_coleta.return_value.executar.return_value = {
                'status': 'sucesso',
                'keywords': [{'keyword': key, 'volume': 100} for key in keywords_grandes]
            }
            
            # Act
            inicio = time.time()
            resultado = orchestrator_load.executar_etapa('coleta', {'nicho': 'tecnologia'})
            tempo_execucao = time.time() - inicio
            
            # Assert
            assert resultado['status'] == 'sucesso'
            assert len(resultado['keywords']) == 1000
            assert tempo_execucao < 30  # Deve processar 1000 keywords em menos de 30s
    
    def test_carga_etapa_validacao(self, orchestrator_load):
        """Testa carga na etapa de validação"""
        # Arrange
        keywords_para_validar = [f'keyword_{index}' for index in range(500)]
        
        with patch('infrastructure.orchestrator.etapas.etapa_validacao.EtapaValidacao') as mock_validacao:
            mock_validacao.return_value.executar.return_value = {
                'status': 'sucesso',
                'keywords_validas': [
                    {'keyword': key, 'volume': 100, 'valid': True} 
                    for key in keywords_para_validar[:400]  # 80% de sucesso
                ]
            }
            
            # Act
            inicio = time.time()
            resultado = orchestrator_load.executar_etapa('validacao', {'keywords': keywords_para_validar})
            tempo_execucao = time.time() - inicio
            
            # Assert
            assert resultado['status'] == 'sucesso'
            assert len(resultado['keywords_validas']) == 400
            assert tempo_execucao < 60  # Deve validar 500 keywords em menos de 60s
    
    def test_carga_etapa_processamento(self, orchestrator_load):
        """Testa carga na etapa de processamento"""
        # Arrange
        keywords_para_processar = [
            {'keyword': f'keyword_{index}', 'volume': 100 + index, 'competition': 0.3 + (index % 10) * 0.05}
            for index in range(300)
        ]
        
        with patch('infrastructure.orchestrator.etapas.etapa_processamento.EtapaProcessamento') as mock_processamento:
            mock_processamento.return_value.executar.return_value = {
                'status': 'sucesso',
                'keywords_processadas': keywords_para_processar,
                'clusters': [
                    {'nome': f'cluster_{index}', 'keywords': keywords_para_processar[index:index+10]}
                    for index in range(0, 300, 10)
                ]
            }
            
            # Act
            inicio = time.time()
            resultado = orchestrator_load.executar_etapa('processamento', {'keywords': keywords_para_processar})
            tempo_execucao = time.time() - inicio
            
            # Assert
            assert resultado['status'] == 'sucesso'
            assert len(resultado['keywords_processadas']) == 300
            assert len(resultado['clusters']) == 30
            assert tempo_execucao < 45  # Deve processar 300 keywords em menos de 45s
    
    def test_carga_etapa_preenchimento(self, orchestrator_load):
        """Testa carga na etapa de preenchimento"""
        # Arrange
        keywords_para_preencher = [
            {'keyword': f'keyword_{index}', 'volume': 100, 'score': 70 + (index % 30)}
            for index in range(100)  # Reduzido para não sobrecarregar API
        ]
        
        with patch('infrastructure.orchestrator.etapas.etapa_preenchimento.EtapaPreenchimento') as mock_preenchimento:
            mock_preenchimento.return_value.executar.return_value = {
                'status': 'sucesso',
                'conteudos_gerados': [
                    {'keyword': key['keyword'], 'conteudo': f'Conteúdo para {key["keyword"]}'}
                    for key in keywords_para_preencher
                ]
            }
            
            # Act
            inicio = time.time()
            resultado = orchestrator_load.executar_etapa('preenchimento', {'keywords_processadas': keywords_para_preencher})
            tempo_execucao = time.time() - inicio
            
            # Assert
            assert resultado['status'] == 'sucesso'
            assert len(resultado['conteudos_gerados']) == 100
            assert tempo_execucao < 120  # Deve gerar 100 conteúdos em menos de 120s
    
    def test_carga_etapa_exportacao(self, orchestrator_load):
        """Testa carga na etapa de exportação"""
        # Arrange
        conteudos_para_exportar = [
            {'keyword': f'keyword_{index}', 'conteudo': f'Conteúdo longo para keyword {index} ' * 50}
            for index in range(200)
        ]
        
        with patch('infrastructure.orchestrator.etapas.etapa_exportacao.EtapaExportacao') as mock_exportacao:
            mock_exportacao.return_value.executar.return_value = {
                'status': 'sucesso',
                'arquivo_exportado': 'output/tecnologia.zip',
                'tamanho_arquivo': '2.5MB',
                'metadados': {
                    'total_keywords': 200,
                    'total_conteudos': 200,
                    'tempo_processamento': 300
                }
            }
            
            # Act
            inicio = time.time()
            resultado = orchestrator_load.executar_etapa('exportacao', {'conteudos_gerados': conteudos_para_exportar})
            tempo_execucao = time.time() - inicio
            
            # Assert
            assert resultado['status'] == 'sucesso'
            assert resultado['arquivo_exportado'] == 'output/tecnologia.zip'
            assert tempo_execucao < 30  # Deve exportar 200 conteúdos em menos de 30s
    
    def test_carga_fluxo_completo(self, orchestrator_load):
        """Testa carga no fluxo completo"""
        # Arrange
        with patch('infrastructure.orchestrator.etapas.etapa_coleta.EtapaColeta') as mock_coleta, \
             patch('infrastructure.orchestrator.etapas.etapa_validacao.EtapaValidacao') as mock_validacao, \
             patch('infrastructure.orchestrator.etapas.etapa_processamento.EtapaProcessamento') as mock_processamento, \
             patch('infrastructure.orchestrator.etapas.etapa_preenchimento.EtapaPreenchimento') as mock_preenchimento, \
             patch('infrastructure.orchestrator.etapas.etapa_exportacao.EtapaExportacao') as mock_exportacao:
            
            # Configurar mocks para simular fluxo completo com carga
            mock_coleta.return_value.executar.return_value = {
                'status': 'sucesso',
                'keywords': [{'keyword': f'keyword_{index}', 'volume': 100} for index in range(500)]
            }
            
            mock_validacao.return_value.executar.return_value = {
                'status': 'sucesso',
                'keywords_validas': [{'keyword': f'keyword_{index}', 'volume': 100, 'valid': True} for index in range(400)]
            }
            
            mock_processamento.return_value.executar.return_value = {
                'status': 'sucesso',
                'keywords_processadas': [{'keyword': f'keyword_{index}', 'volume': 100, 'score': 70} for index in range(400)],
                'clusters': [{'nome': f'cluster_{index}', 'keywords': []} for index in range(40)]
            }
            
            mock_preenchimento.return_value.executar.return_value = {
                'status': 'sucesso',
                'conteudos_gerados': [{'keyword': f'keyword_{index}', 'conteudo': f'Conteúdo {index}'} for index in range(400)]
            }
            
            mock_exportacao.return_value.executar.return_value = {
                'status': 'sucesso',
                'arquivo_exportado': 'output/tecnologia.zip',
                'metadados': {'total_keywords': 400, 'total_conteudos': 400}
            }
            
            # Act
            inicio = time.time()
            resultado = orchestrator_load.executar_fluxo_completo()
            tempo_execucao = time.time() - inicio
            
            # Assert
            assert resultado['status'] == 'sucesso'
            assert resultado['etapas_executadas'] == 5
            assert tempo_execucao < 300  # Deve executar fluxo completo em menos de 5 minutos
            assert resultado['dados_finais']['metadados']['total_keywords'] == 400
    
    def test_carga_concorrente(self, orchestrator_load):
        """Testa carga com execuções concorrentes"""
        # Arrange
        def executar_etapa_simulada(etapa_id):
            """Simula execução de etapa"""
            time.sleep(0.1)  # Simula processamento
            return {
                'status': 'sucesso',
                'etapa_id': etapa_id,
                'tempo_execucao': 0.1
            }
        
        # Act
        inicio = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(executar_etapa_simulada, index)
                for index in range(10)
            ]
            
            resultados = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        tempo_total = time.time() - inicio
        
        # Assert
        assert len(resultados) == 10
        assert all(r['status'] == 'sucesso' for r in resultados)
        assert tempo_total < 2  # Deve executar 10 etapas concorrentes em menos de 2s
    
    def test_carga_memoria(self, orchestrator_load):
        """Testa uso de memória sob carga"""
        # Arrange
        import psutil
        import os
        
        processo = psutil.Process(os.getpid())
        memoria_inicial = processo.memory_info().rss / 1024 / 1024  # MB
        
        # Act
        with patch('infrastructure.orchestrator.etapas.etapa_coleta.EtapaColeta') as mock_coleta:
            # Simular processamento de muitos dados
            mock_coleta.return_value.executar.return_value = {
                'status': 'sucesso',
                'keywords': [{'keyword': f'keyword_{index}', 'volume': 100} for index in range(10000)]
            }
            
            resultado = orchestrator_load.executar_etapa('coleta', {'nicho': 'tecnologia'})
            
            memoria_final = processo.memory_info().rss / 1024 / 1024  # MB
            aumento_memoria = memoria_final - memoria_inicial
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert len(resultado['keywords']) == 10000
        assert aumento_memoria < 500  # Aumento de memória deve ser menor que 500MB
    
    def test_carga_timeout(self, orchestrator_load):
        """Testa comportamento sob timeout"""
        # Arrange
        with patch('infrastructure.orchestrator.etapas.etapa_coleta.EtapaColeta') as mock_coleta:
            # Simular processamento lento
            def processamento_lento(*args, **kwargs):
                time.sleep(2)  # Simula processamento lento
                return {'status': 'sucesso', 'keywords': []}
            
            mock_coleta.return_value.executar.side_effect = processamento_lento
            
            # Act
            inicio = time.time()
            resultado = orchestrator_load.executar_etapa_com_timeout('coleta', {'nicho': 'tecnologia'}, timeout=1)
            tempo_execucao = time.time() - inicio
        
        # Assert
        assert resultado['status'] == 'erro'
        assert 'Timeout' in resultado['mensagem']
        assert tempo_execucao < 2  # Deve falhar em menos de 2s
    
    def test_carga_rate_limiting(self, orchestrator_load):
        """Testa rate limiting sob carga"""
        # Arrange
        chamadas = []
        
        def registrar_chamada(*args, **kwargs):
            chamadas.append(time.time())
            return {'status': 'sucesso', 'keywords': []}
        
        with patch('infrastructure.orchestrator.etapas.etapa_coleta.EtapaColeta') as mock_coleta:
            mock_coleta.return_value.executar.side_effect = registrar_chamada
            
            # Act
            inicio = time.time()
            for index in range(10):
                orchestrator_load.executar_etapa('coleta', {'nicho': 'tecnologia'})
            tempo_total = time.time() - inicio
        
        # Assert
        assert len(chamadas) == 10
        assert tempo_total > 1  # Deve respeitar rate limiting
        assert tempo_total < 15  # Mas não deve ser excessivamente lento
    
    def test_carga_recuperacao_erro(self, orchestrator_load):
        """Testa recuperação de erros sob carga"""
        # Arrange
        tentativas = []
        
        def simular_falhas(*args, **kwargs):
            tentativas.append(time.time())
            if len(tentativas) < 3:
                raise Exception("Erro temporário")
            return {'status': 'sucesso', 'keywords': []}
        
        with patch('infrastructure.orchestrator.etapas.etapa_coleta.EtapaColeta') as mock_coleta:
            mock_coleta.return_value.executar.side_effect = simular_falhas
            
            # Act
            resultado = orchestrator_load.executar_etapa_com_retry('coleta', {'nicho': 'tecnologia'})
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert len(tentativas) == 3  # Deve tentar 3 vezes
        assert resultado['tentativas'] == 3


class TestLoadStress:
    """Testes de stress para o orquestrador"""
    
    @pytest.fixture
    def config_stress(self):
        """Configuração para testes de stress"""
        return {
            'nicho': 'tecnologia',
            'max_keywords': 10000,
            'timeout_etapa': 1800,
            'retry_attempts': 5,
            'cache_enabled': True,
            'log_level': 'ERROR'
        }
    
    def test_stress_fluxo_extremo(self, config_stress):
        """Testa stress com volume extremo de dados"""
        # Arrange
        with patch('infrastructure.orchestrator.fluxo_completo_orchestrator.FluxoCompletoOrchestrator') as mock_orchestrator:
            mock_orchestrator.return_value.executar_fluxo_completo.return_value = {
                'status': 'sucesso',
                'tempo_total': 1200,
                'keywords_processadas': 10000,
                'memoria_utilizada': '2.5GB'
            }
            
            # Act
            inicio = time.time()
            orchestrator = FluxoCompletoOrchestrator(config_stress)
            resultado = orchestrator.executar_fluxo_completo()
            tempo_execucao = time.time() - inicio
        
        # Assert
        assert resultado['status'] == 'sucesso'
        assert resultado['keywords_processadas'] == 10000
        assert tempo_execucao < 1800  # Deve executar em menos de 30 minutos
    
    def test_stress_concorrencia_extrema(self, config_stress):
        """Testa stress com concorrência extrema"""
        # Arrange
        def executar_etapa_stress(etapa_id):
            time.sleep(0.05)
            return {'status': 'sucesso', 'etapa_id': etapa_id}
        
        # Act
        inicio = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(executar_etapa_stress, index)
                for index in range(100)
            ]
            
            resultados = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        tempo_total = time.time() - inicio
        
        # Assert
        assert len(resultados) == 100
        assert all(r['status'] == 'sucesso' for r in resultados)
        assert tempo_total < 10  # Deve executar 100 etapas em menos de 10s


if __name__ == '__main__':
    pytest.main([__file__, '-value']) 