"""
Testes Unitários - Serviços de Lote e Agendamento
Testa processamento em lote e agendamento de execuções

Prompt: Implementação de testes para serviços de lote e agendamento
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta

# Importar serviços
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.lote_execucao_service import (
    LoteExecucaoService, LoteConfig, ExecucaoItem, LoteStatus, ExecucaoStatus
)
from app.services.agendamento_service import (
    AgendamentoService, AgendamentoConfig, ExecucaoAgendada, 
    AgendamentoStatus, TipoRecorrencia
)

class TestLoteExecucaoService:
    """Testes para o serviço de execução em lote"""
    
    @pytest.fixture
    def config(self):
        """Configuração de teste"""
        return {
            'max_workers': 5
        }
    
    @pytest.fixture
    def lote_service(self, config):
        """Cria instância do serviço de lote"""
        service = LoteExecucaoService(config)
        yield service
        # Cleanup
        service.stop_processing()
    
    @pytest.fixture
    def execucoes_teste(self):
        """Execuções de teste"""
        return [
            {
                'categoria_id': 1,
                'palavras_chave': ['palavra1', 'palavra2'],
                'cluster': 'test_cluster'
            },
            {
                'categoria_id': 2,
                'palavras_chave': ['palavra3', 'palavra4'],
                'cluster': 'test_cluster2'
            },
            {
                'categoria_id': 3,
                'palavras_chave': ['palavra5'],
                'cluster': None
            }
        ]
    
    def test_lote_service_initialization(self, config):
        """Testa inicialização do serviço de lote"""
        service = LoteExecucaoService(config)
        
        assert service.config == config
        assert service.lotes_ativos == {}
        assert service.running == True
        assert service.stats['lotes_processados'] == 0
        
        service.stop_processing()
    
    def test_criar_lote(self, lote_service, execucoes_teste):
        """Testa criação de lote"""
        config = LoteConfig(
            max_concurrent=2,
            timeout_por_execucao=60,
            retry_delay=30,
            max_retries=3
        )
        
        lote_id = lote_service.criar_lote(execucoes_teste, config, user_id='test_user')
        
        assert lote_id in lote_service.lotes_ativos
        lote_info = lote_service.lotes_ativos[lote_id]
        
        assert lote_info['status'] == LoteStatus.PENDENTE
        assert len(lote_info['execucoes']) == 3
        assert lote_info['user_id'] == 'test_user'
        assert lote_info['config'] == config
    
    def test_obter_status_lote(self, lote_service, execucoes_teste):
        """Testa obtenção de status do lote"""
        lote_id = lote_service.criar_lote(execucoes_teste)
        
        status = lote_service.obter_status_lote(lote_id)
        
        assert status is not None
        assert status['lote_id'] == lote_id
        assert status['status'] == 'pendente'
        assert status['total_execucoes'] == 3
        assert status['execucoes_concluidas'] == 0
        assert status['execucoes_falharam'] == 0
    
    def test_cancelar_lote(self, lote_service, execucoes_teste):
        """Testa cancelamento de lote"""
        lote_id = lote_service.criar_lote(execucoes_teste)
        
        # Cancelar lote
        result = lote_service.cancelar_lote(lote_id)
        assert result == True
        
        # Verificar status
        status = lote_service.obter_status_lote(lote_id)
        assert status['status'] == 'cancelado'
        
        # Tentar cancelar novamente
        result = lote_service.cancelar_lote(lote_id)
        assert result == False
    
    def test_listar_lotes(self, lote_service, execucoes_teste):
        """Testa listagem de lotes"""
        # Criar múltiplos lotes
        lote1 = lote_service.criar_lote(execucoes_teste, user_id='user1')
        lote2 = lote_service.criar_lote(execucoes_teste, user_id='user2')
        lote3 = lote_service.criar_lote(execucoes_teste, user_id='user1')
        
        # Listar todos
        todos = lote_service.listar_lotes()
        assert len(todos) == 3
        
        # Filtrar por usuário
        user1_lotes = lote_service.listar_lotes(user_id='user1')
        assert len(user1_lotes) == 2
        
        # Filtrar por status
        pendentes = lote_service.listar_lotes(status=LoteStatus.PENDENTE)
        assert len(pendentes) == 3
    
    def test_obter_estatisticas(self, lote_service, execucoes_teste):
        """Testa obtenção de estatísticas"""
        # Criar alguns lotes
        lote_service.criar_lote(execucoes_teste)
        lote_service.criar_lote(execucoes_teste)
        
        stats = lote_service.obter_estatisticas()
        
        assert stats['lotes_processados'] == 0  # Ainda não processados
        assert 'lotes_ativos' in stats
        assert 'execucoes_processadas' in stats
        assert 'taxa_sucesso_geral' in stats
    
    def test_limpar_lotes_antigos(self, lote_service, execucoes_teste):
        """Testa limpeza de lotes antigos"""
        # Criar lote
        lote_id = lote_service.criar_lote(execucoes_teste)
        
        # Simular lote antigo
        lote_info = lote_service.lotes_ativos[lote_id]
        lote_info['criado_em'] = datetime.now(timezone.utc) - timedelta(days=10)
        
        # Limpar lotes antigos (mais de 7 dias)
        lote_service.limpar_lotes_antigos(dias=7)
        
        # Verificar se foi removido
        assert lote_id not in lote_service.lotes_ativos
    
    def test_processamento_simulado(self, lote_service, execucoes_teste):
        """Testa processamento simulado de lote"""
        # Configurar callbacks
        resultados = []
        def on_execucao_complete(execucao, resultado):
            resultados.append((execucao.id, resultado))
        
        lote_service.on_execucao_complete = on_execucao_complete
        
        # Criar lote
        lote_id = lote_service.criar_lote(execucoes_teste)
        
        # Aguardar processamento
        time.sleep(5)
        
        # Verificar resultados
        status = lote_service.obter_status_lote(lote_id)
        assert status['status'] in ['concluido', 'falhou']
        assert status['total_execucoes'] == 3

class TestAgendamentoService:
    """Testes para o serviço de agendamento"""
    
    @pytest.fixture
    def config(self):
        """Configuração de teste"""
        return {
            'db_path': ':memory:'  # Banco em memória para testes
        }
    
    @pytest.fixture
    def agendamento_service(self, config):
        """Cria instância do serviço de agendamento"""
        service = AgendamentoService(config)
        yield service
        # Cleanup
        service.stop_scheduler()
    
    @pytest.fixture
    def execucoes_agendadas(self):
        """Execuções agendadas de teste"""
        return [
            {
                'categoria_id': 1,
                'palavras_chave': ['palavra1', 'palavra2'],
                'cluster': 'test_cluster'
            },
            {
                'categoria_id': 2,
                'palavras_chave': ['palavra3', 'palavra4'],
                'cluster': 'test_cluster2'
            }
        ]
    
    def test_agendamento_service_initialization(self, config):
        """Testa inicialização do serviço de agendamento"""
        service = AgendamentoService(config)
        
        assert service.config == config
        assert service.agendamentos == {}
        assert service.running == True
        
        service.stop_scheduler()
    
    def test_criar_agendamento_diario(self, agendamento_service, execucoes_agendadas):
        """Testa criação de agendamento diário"""
        config = AgendamentoConfig(
            nome='Teste Diário',
            descricao='Agendamento de teste diário',
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='10:00'
        )
        
        agendamento_id = agendamento_service.criar_agendamento(
            config, execucoes_agendadas, user_id='test_user'
        )
        
        assert agendamento_id in agendamento_service.agendamentos
        agendamento = agendamento_service.agendamentos[agendamento_id]
        
        assert agendamento.config.nome == 'Teste Diário'
        assert agendamento.config.tipo_recorrencia == TipoRecorrencia.DIARIA
        assert agendamento.status == AgendamentoStatus.ATIVO
        assert agendamento.user_id == 'test_user'
        assert len(agendamento.execucoes) == 2
        assert agendamento.proxima_execucao is not None
    
    def test_criar_agendamento_semanal(self, agendamento_service, execucoes_agendadas):
        """Testa criação de agendamento semanal"""
        config = AgendamentoConfig(
            nome='Teste Semanal',
            descricao='Agendamento de teste semanal',
            tipo_recorrencia=TipoRecorrencia.SEMANAL,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='14:00',
            dias_semana=[0, 3, 6]  # Segunda, Quinta, Domingo
        )
        
        agendamento_id = agendamento_service.criar_agendamento(
            config, execucoes_agendadas, user_id='test_user'
        )
        
        agendamento = agendamento_service.agendamentos[agendamento_id]
        assert agendamento.config.tipo_recorrencia == TipoRecorrencia.SEMANAL
        assert agendamento.config.dias_semana == [0, 3, 6]
    
    def test_criar_agendamento_mensal(self, agendamento_service, execucoes_agendadas):
        """Testa criação de agendamento mensal"""
        config = AgendamentoConfig(
            nome='Teste Mensal',
            descricao='Agendamento de teste mensal',
            tipo_recorrencia=TipoRecorrencia.MENSAL,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='09:00',
            dia_mes=15
        )
        
        agendamento_id = agendamento_service.criar_agendamento(
            config, execucoes_agendadas, user_id='test_user'
        )
        
        agendamento = agendamento_service.agendamentos[agendamento_id]
        assert agendamento.config.tipo_recorrencia == TipoRecorrencia.MENSAL
        assert agendamento.config.dia_mes == 15
    
    def test_criar_agendamento_cron(self, agendamento_service, execucoes_agendadas):
        """Testa criação de agendamento com cron"""
        config = AgendamentoConfig(
            nome='Teste Cron',
            descricao='Agendamento de teste com cron',
            tipo_recorrencia=TipoRecorrencia.CRON,
            data_inicio=datetime.now(timezone.utc),
            cron_expression='0 12 * * 1-5'  # Segunda a sexta às 12:00
        )
        
        agendamento_id = agendamento_service.criar_agendamento(
            config, execucoes_agendadas, user_id='test_user'
        )
        
        agendamento = agendamento_service.agendamentos[agendamento_id]
        assert agendamento.config.tipo_recorrencia == TipoRecorrencia.CRON
        assert agendamento.config.cron_expression == '0 12 * * 1-5'
    
    def test_obter_agendamento(self, agendamento_service, execucoes_agendadas):
        """Testa obtenção de agendamento"""
        config = AgendamentoConfig(
            nome='Teste Obter',
            descricao='Agendamento para teste de obtenção',
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='10:00'
        )
        
        agendamento_id = agendamento_service.criar_agendamento(
            config, execucoes_agendadas, user_id='test_user'
        )
        
        agendamento_data = agendamento_service.obter_agendamento(agendamento_id)
        
        assert agendamento_data is not None
        assert agendamento_data['id'] == agendamento_id
        assert agendamento_data['nome'] == 'Teste Obter'
        assert agendamento_data['tipo_recorrencia'] == 'diaria'
        assert agendamento_data['status'] == 'ativo'
        assert agendamento_data['user_id'] == 'test_user'
        assert len(agendamento_data['execucoes']) == 2
    
    def test_listar_agendamentos(self, agendamento_service, execucoes_agendadas):
        """Testa listagem de agendamentos"""
        # Criar múltiplos agendamentos
        config1 = AgendamentoConfig(
            nome='Teste 1',
            descricao='Primeiro teste',
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='10:00'
        )
        
        config2 = AgendamentoConfig(
            nome='Teste 2',
            descricao='Segundo teste',
            tipo_recorrencia=TipoRecorrencia.SEMANAL,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='14:00',
            dias_semana=[0, 3]
        )
        
        agendamento_service.criar_agendamento(config1, execucoes_agendadas, user_id='user1')
        agendamento_service.criar_agendamento(config2, execucoes_agendadas, user_id='user2')
        agendamento_service.criar_agendamento(config1, execucoes_agendadas, user_id='user1')
        
        # Listar todos
        todos = agendamento_service.listar_agendamentos()
        assert len(todos) == 3
        
        # Filtrar por usuário
        user1_agendamentos = agendamento_service.listar_agendamentos(user_id='user1')
        assert len(user1_agendamentos) == 2
        
        # Filtrar por status
        ativos = agendamento_service.listar_agendamentos(status=AgendamentoStatus.ATIVO)
        assert len(ativos) == 3
    
    def test_cancelar_agendamento(self, agendamento_service, execucoes_agendadas):
        """Testa cancelamento de agendamento"""
        config = AgendamentoConfig(
            nome='Teste Cancelar',
            descricao='Agendamento para cancelamento',
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='10:00'
        )
        
        agendamento_id = agendamento_service.criar_agendamento(
            config, execucoes_agendadas, user_id='test_user'
        )
        
        # Cancelar agendamento
        result = agendamento_service.cancelar_agendamento(agendamento_id)
        assert result == True
        
        # Verificar status
        agendamento_data = agendamento_service.obter_agendamento(agendamento_id)
        assert agendamento_data['status'] == 'cancelado'
        
        # Tentar cancelar novamente
        result = agendamento_service.cancelar_agendamento(agendamento_id)
        assert result == False
    
    def test_pausar_retomar_agendamento(self, agendamento_service, execucoes_agendadas):
        """Testa pausar e retomar agendamento"""
        config = AgendamentoConfig(
            nome='Teste Pausar',
            descricao='Agendamento para pausar/retomar',
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='10:00'
        )
        
        agendamento_id = agendamento_service.criar_agendamento(
            config, execucoes_agendadas, user_id='test_user'
        )
        
        # Pausar agendamento
        result = agendamento_service.pausar_agendamento(agendamento_id)
        assert result == True
        
        agendamento_data = agendamento_service.obter_agendamento(agendamento_id)
        assert agendamento_data['status'] == 'pausado'
        
        # Retomar agendamento
        result = agendamento_service.retomar_agendamento(agendamento_id)
        assert result == True
        
        agendamento_data = agendamento_service.obter_agendamento(agendamento_id)
        assert agendamento_data['status'] == 'ativo'
    
    def test_calcular_proxima_execucao(self, agendamento_service):
        """Testa cálculo de próxima execução"""
        now = datetime.now(timezone.utc)
        
        # Teste diário
        config_diario = AgendamentoConfig(
            nome='Teste',
            descricao='Teste',
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=now,
            hora_execucao='10:00'
        )
        
        proxima = agendamento_service._calcular_proxima_execucao_para_config(config_diario)
        assert proxima is not None
        assert proxima > now
        
        # Teste semanal
        config_semanal = AgendamentoConfig(
            nome='Teste',
            descricao='Teste',
            tipo_recorrencia=TipoRecorrencia.SEMANAL,
            data_inicio=now,
            hora_execucao='14:00',
            dias_semana=[0, 3, 6]
        )
        
        proxima = agendamento_service._calcular_proxima_execucao_para_config(config_semanal)
        assert proxima is not None
        assert proxima > now
    
    def test_obter_estatisticas(self, agendamento_service, execucoes_agendadas):
        """Testa obtenção de estatísticas"""
        # Criar alguns agendamentos
        config = AgendamentoConfig(
            nome='Teste Stats',
            descricao='Agendamento para estatísticas',
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='10:00'
        )
        
        agendamento_service.criar_agendamento(config, execucoes_agendadas, user_id='test_user')
        agendamento_service.criar_agendamento(config, execucoes_agendadas, user_id='test_user')
        
        stats = agendamento_service.obter_estatisticas()
        
        assert stats['total_agendamentos'] == 2
        assert stats['agendamentos_ativos'] == 2
        assert stats['agendamentos_pausados'] == 0
        assert stats['total_execucoes'] == 0  # Ainda não executados
        assert 'taxa_sucesso' in stats

class TestIntegracaoLoteAgendamento:
    """Testes de integração entre lote e agendamento"""
    
    @pytest.fixture
    def lote_service(self):
        """Serviço de lote"""
        service = LoteExecucaoService()
        yield service
        service.stop_processing()
    
    @pytest.fixture
    def agendamento_service(self):
        """Serviço de agendamento"""
        service = AgendamentoService({'db_path': ':memory:'})
        yield service
        service.stop_scheduler()
    
    def test_integracao_lote_agendamento(self, lote_service, agendamento_service):
        """Testa integração entre lote e agendamento"""
        # Configurar callback do agendamento para criar lote
        def on_execucao_agendada(execucao):
            # Criar lote com a execução agendada
            execucoes = [{
                'categoria_id': execucao.categoria_id,
                'palavras_chave': execucao.palavras_chave,
                'cluster': execucao.cluster
            }]
            
            lote_id = lote_service.criar_lote(execucoes)
            return lote_id is not None
        
        agendamento_service.on_execucao_agendada = on_execucao_agendada
        
        # Criar agendamento
        config = AgendamentoConfig(
            nome='Teste Integração',
            descricao='Teste de integração',
            tipo_recorrencia=TipoRecorrencia.UMA_VEZ,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao='10:00'
        )
        
        execucoes = [{
            'categoria_id': 1,
            'palavras_chave': ['teste'],
            'cluster': 'test'
        }]
        
        agendamento_id = agendamento_service.criar_agendamento(
            config, execucoes, user_id='test_user'
        )
        
        # Verificar que agendamento foi criado
        assert agendamento_id in agendamento_service.agendamentos
        
        # Simular execução do agendamento
        agendamento = agendamento_service.agendamentos[agendamento_id]
        agendamento_service._executar_agendamento(agendamento)
        
        # Verificar que lote foi criado
        assert len(lote_service.lotes_ativos) > 0

if __name__ == '__main__':
    pytest.main([__file__]) 