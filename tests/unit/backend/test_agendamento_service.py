"""
Testes unitários para AgendamentoService
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 1.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import tempfile
import os
import json
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from backend.app.services.agendamento_service import (
    AgendamentoService,
    AgendamentoConfig,
    ExecucaoAgendada,
    Agendamento,
    AgendamentoStatus,
    TipoRecorrencia,
    init_agendamento_service,
    get_agendamento_service
)

class TestAgendamentoService:
    """Testes para AgendamentoService baseados no código real."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Fixture para banco de dados temporário."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        
        yield temp_path
        
        # Limpeza
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def service(self, temp_db_path):
        """Fixture para serviço com banco temporário."""
        config = {'db_path': temp_db_path}
        return AgendamentoService(config)
    
    @pytest.fixture
    def sample_config(self):
        """Fixture para configuração de agendamento real."""
        return AgendamentoConfig(
            nome="Agendamento Marketing Digital",
            descricao="Execução diária de keywords de marketing digital",
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=datetime.now(timezone.utc) + timedelta(hours=1),
            hora_execucao="09:00",
            timeout_minutos=30,
            retry_on_failure=True,
            max_retries=3,
            notificar_erro=True
        )
    
    @pytest.fixture
    def sample_execucoes(self):
        """Fixture para execuções agendadas reais."""
        return [
            {
                'categoria_id': 1,
                'palavras_chave': ["seo", "ads", "social media"],
                'cluster': "marketing_digital",
                'parametros_extras': {
                    'regiao': 'brasil',
                    'idioma': 'pt-BR'
                }
            },
            {
                'categoria_id': 2,
                'palavras_chave': ["email marketing", "automacao"],
                'cluster': "email_marketing",
                'parametros_extras': {
                    'regiao': 'brasil',
                    'idioma': 'pt-BR'
                }
            }
        ]
    
    def test_init_service(self, temp_db_path):
        """Testa inicialização do serviço."""
        service = AgendamentoService({'db_path': temp_db_path})
        
        assert service.db_path == temp_db_path
        assert isinstance(service.agendamentos, dict)
        assert service.running is True
        assert service.on_execucao_agendada is None
        assert service.on_agendamento_complete is None
        assert service.on_error is None
        
        # Verificar se banco foi criado
        assert os.path.exists(temp_db_path)
    
    def test_init_database_creates_tables(self, temp_db_path):
        """Testa criação das tabelas no banco de dados."""
        service = AgendamentoService({'db_path': temp_db_path})
        
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Verificar se tabelas existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'agendamentos' in tables
        assert 'execucoes_agendadas' in tables
        assert 'historico_execucoes' in tables
        
        # Verificar se índices existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        assert 'idx_proxima_execucao' in indexes
        assert 'idx_status' in indexes
        assert 'idx_user_id' in indexes
        
        conn.close()
    
    def test_criar_agendamento_sucesso(self, service, sample_config, sample_execucoes):
        """Testa criação de agendamento com sucesso."""
        user_id = "user_123"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        assert agendamento_id is not None
        assert agendamento_id in service.agendamentos
        
        agendamento = service.agendamentos[agendamento_id]
        assert agendamento.config.nome == "Agendamento Marketing Digital"
        assert agendamento.config.descricao == "Execução diária de keywords de marketing digital"
        assert agendamento.config.tipo_recorrencia == TipoRecorrencia.DIARIA
        assert agendamento.status == AgendamentoStatus.ATIVO
        assert agendamento.user_id == user_id
        assert len(agendamento.execucoes) == 2
        assert agendamento.proxima_execucao is not None
    
    def test_criar_agendamento_com_execucoes(self, service, sample_config, sample_execucoes):
        """Testa criação de agendamento com execuções específicas."""
        user_id = "user_456"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        agendamento = service.agendamentos[agendamento_id]
        
        # Verificar primeira execução
        execucao1 = agendamento.execucoes[0]
        assert execucao1.categoria_id == 1
        assert execucao1.palavras_chave == ["seo", "ads", "social media"]
        assert execucao1.cluster == "marketing_digital"
        assert execucao1.parametros_extras == {
            'regiao': 'brasil',
            'idioma': 'pt-BR'
        }
        
        # Verificar segunda execução
        execucao2 = agendamento.execucoes[1]
        assert execucao2.categoria_id == 2
        assert execucao2.palavras_chave == ["email marketing", "automacao"]
        assert execucao2.cluster == "email_marketing"
    
    def test_calcular_proxima_execucao_diaria(self, service, sample_config):
        """Testa cálculo de próxima execução para recorrência diária."""
        # Configurar para execução diária às 09:00
        config = AgendamentoConfig(
            nome="Teste Diário",
            descricao="Teste",
            tipo_recorrencia=TipoRecorrencia.DIARIA,
            data_inicio=datetime.now(timezone.utc),
            hora_execucao="09:00"
        )
        
        proxima = service._calcular_proxima_execucao_para_config(config)
        
        assert proxima is not None
        assert proxima.hour == 9
        assert proxima.minute == 0
        assert proxima.second == 0
        assert proxima.microsecond == 0
    
    def test_calcular_proxima_execucao_uma_vez(self, service):
        """Testa cálculo de próxima execução para execução única."""
        data_futura = datetime.now(timezone.utc) + timedelta(days=1)
        
        config = AgendamentoConfig(
            nome="Teste Único",
            descricao="Teste",
            tipo_recorrencia=TipoRecorrencia.UMA_VEZ,
            data_inicio=data_futura,
            hora_execucao="14:30"
        )
        
        proxima = service._calcular_proxima_execucao_para_config(config)
        
        assert proxima is not None
        assert proxima.date() == data_futura.date()
        assert proxima.hour == 14
        assert proxima.minute == 30
    
    def test_obter_agendamento_existente(self, service, sample_config, sample_execucoes):
        """Testa obtenção de agendamento existente."""
        user_id = "user_789"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        resultado = service.obter_agendamento(agendamento_id)
        
        assert resultado is not None
        assert resultado['id'] == agendamento_id
        assert resultado['nome'] == "Agendamento Marketing Digital"
        assert resultado['descricao'] == "Execução diária de keywords de marketing digital"
        assert resultado['tipo_recorrencia'] == "diaria"
        assert resultado['status'] == "ativo"
        assert resultado['user_id'] == user_id
        assert len(resultado['execucoes']) == 2
        assert resultado['total_execucoes'] == 0
        assert resultado['execucoes_sucesso'] == 0
        assert resultado['execucoes_falha'] == 0
    
    def test_obter_agendamento_inexistente(self, service):
        """Testa obtenção de agendamento inexistente."""
        resultado = service.obter_agendamento("agendamento_inexistente")
        assert resultado is None
    
    def test_listar_agendamentos_vazio(self, service):
        """Testa listagem de agendamentos quando não há nenhum."""
        agendamentos = service.listar_agendamentos()
        assert agendamentos == []
    
    def test_listar_agendamentos_com_filtros(self, service, sample_config, sample_execucoes):
        """Testa listagem de agendamentos com filtros."""
        user_id_1 = "user_111"
        user_id_2 = "user_222"
        
        # Criar agendamentos para diferentes usuários
        agendamento_id_1 = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id_1
        )
        
        agendamento_id_2 = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id_2
        )
        
        # Listar todos
        todos = service.listar_agendamentos()
        assert len(todos) == 2
        
        # Filtrar por usuário
        do_usuario_1 = service.listar_agendamentos(user_id=user_id_1)
        assert len(do_usuario_1) == 1
        assert do_usuario_1[0]['user_id'] == user_id_1
        
        # Filtrar por status
        ativos = service.listar_agendamentos(status=AgendamentoStatus.ATIVO)
        assert len(ativos) == 2
        assert all(a['status'] == 'ativo' for a in ativos)
    
    def test_cancelar_agendamento_sucesso(self, service, sample_config, sample_execucoes):
        """Testa cancelamento de agendamento com sucesso."""
        user_id = "user_cancel"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        # Verificar que está ativo
        agendamento = service.agendamentos[agendamento_id]
        assert agendamento.status == AgendamentoStatus.ATIVO
        
        # Cancelar
        sucesso = service.cancelar_agendamento(agendamento_id)
        assert sucesso is True
        
        # Verificar que foi cancelado
        agendamento = service.agendamentos[agendamento_id]
        assert agendamento.status == AgendamentoStatus.CANCELADO
        assert agendamento.proxima_execucao is None
    
    def test_cancelar_agendamento_inexistente(self, service):
        """Testa cancelamento de agendamento inexistente."""
        sucesso = service.cancelar_agendamento("agendamento_inexistente")
        assert sucesso is False
    
    def test_pausar_agendamento_sucesso(self, service, sample_config, sample_execucoes):
        """Testa pausa de agendamento com sucesso."""
        user_id = "user_pause"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        # Verificar que está ativo
        agendamento = service.agendamentos[agendamento_id]
        assert agendamento.status == AgendamentoStatus.ATIVO
        
        # Pausar
        sucesso = service.pausar_agendamento(agendamento_id)
        assert sucesso is True
        
        # Verificar que foi pausado
        agendamento = service.agendamentos[agendamento_id]
        assert agendamento.status == AgendamentoStatus.PAUSADO
    
    def test_pausar_agendamento_ja_pausado(self, service, sample_config, sample_execucoes):
        """Testa pausa de agendamento já pausado."""
        user_id = "user_pause_duplo"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        # Pausar primeira vez
        sucesso1 = service.pausar_agendamento(agendamento_id)
        assert sucesso1 is True
        
        # Tentar pausar novamente
        sucesso2 = service.pausar_agendamento(agendamento_id)
        assert sucesso2 is False
    
    def test_retomar_agendamento_sucesso(self, service, sample_config, sample_execucoes):
        """Testa retomada de agendamento pausado."""
        user_id = "user_resume"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        # Pausar primeiro
        service.pausar_agendamento(agendamento_id)
        
        # Retomar
        sucesso = service.retomar_agendamento(agendamento_id)
        assert sucesso is True
        
        # Verificar que foi retomado
        agendamento = service.agendamentos[agendamento_id]
        assert agendamento.status == AgendamentoStatus.ATIVO
        assert agendamento.proxima_execucao is not None
    
    def test_retomar_agendamento_nao_pausado(self, service, sample_config, sample_execucoes):
        """Testa retomada de agendamento não pausado."""
        user_id = "user_resume_erro"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        # Tentar retomar sem pausar
        sucesso = service.retomar_agendamento(agendamento_id)
        assert sucesso is False
    
    def test_obter_estatisticas_vazio(self, service):
        """Testa obtenção de estatísticas quando não há agendamentos."""
        stats = service.obter_estatisticas()
        
        assert stats['total_agendamentos'] == 0
        assert stats['agendamentos_ativos'] == 0
        assert stats['agendamentos_pausados'] == 0
        assert stats['total_execucoes'] == 0
        assert stats['execucoes_sucesso'] == 0
        assert stats['execucoes_falha'] == 0
        assert stats['taxa_sucesso'] == 0
    
    def test_obter_estatisticas_com_agendamentos(self, service, sample_config, sample_execucoes):
        """Testa obtenção de estatísticas com agendamentos."""
        user_id = "user_stats"
        
        # Criar agendamento ativo
        agendamento_id_1 = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        # Criar agendamento pausado
        agendamento_id_2 = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        service.pausar_agendamento(agendamento_id_2)
        
        # Simular algumas execuções
        agendamento1 = service.agendamentos[agendamento_id_1]
        agendamento1.total_execucoes = 10
        agendamento1.execucoes_sucesso = 8
        agendamento1.execucoes_falha = 2
        
        agendamento2 = service.agendamentos[agendamento_id_2]
        agendamento2.total_execucoes = 5
        agendamento2.execucoes_sucesso = 4
        agendamento2.execucoes_falha = 1
        
        stats = service.obter_estatisticas()
        
        assert stats['total_agendamentos'] == 2
        assert stats['agendamentos_ativos'] == 1
        assert stats['agendamentos_pausados'] == 1
        assert stats['total_execucoes'] == 15
        assert stats['execucoes_sucesso'] == 12
        assert stats['execucoes_falha'] == 3
        assert stats['taxa_sucesso'] == 0.8
    
    def test_registrar_execucao_historico(self, service, temp_db_path):
        """Testa registro de execução no histórico."""
        agendamento_id = "test_hist_123"
        
        # Registrar execução de sucesso
        service._registrar_execucao_historico(
            agendamento_id=agendamento_id,
            sucesso=True,
            resultado="Execução concluída com sucesso",
            erro=None
        )
        
        # Verificar no banco
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT agendamento_id, status, resultado, erro 
            FROM historico_execucoes 
            WHERE agendamento_id = ?
        ''', (agendamento_id,))
        
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == agendamento_id
        assert row[1] == 'sucesso'
        assert row[2] == "Execução concluída com sucesso"
        assert row[3] is None
        
        conn.close()
    
    def test_save_agendamento_persistence(self, service, sample_config, sample_execucoes, temp_db_path):
        """Testa persistência de agendamento no banco de dados."""
        user_id = "user_persist"
        
        agendamento_id = service.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        # Verificar se foi salvo no banco
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, nome, status, user_id FROM agendamentos WHERE id = ?', (agendamento_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == agendamento_id
        assert row[1] == "Agendamento Marketing Digital"
        assert row[2] == "ativo"
        assert row[3] == user_id
        
        # Verificar execuções agendadas
        cursor.execute('SELECT COUNT(*) FROM execucoes_agendadas WHERE agendamento_id = ?', (agendamento_id,))
        count = cursor.fetchone()[0]
        assert count == 2
        
        conn.close()
    
    def test_load_agendamentos_from_database(self, temp_db_path, sample_config, sample_execucoes):
        """Testa carregamento de agendamentos do banco de dados."""
        # Criar primeiro serviço e agendamento
        service1 = AgendamentoService({'db_path': temp_db_path})
        user_id = "user_load"
        
        agendamento_id = service1.criar_agendamento(
            config=sample_config,
            execucoes=sample_execucoes,
            user_id=user_id
        )
        
        # Criar segundo serviço (deve carregar do banco)
        service2 = AgendamentoService({'db_path': temp_db_path})
        
        # Verificar se agendamento foi carregado
        assert agendamento_id in service2.agendamentos
        
        agendamento = service2.agendamentos[agendamento_id]
        assert agendamento.config.nome == "Agendamento Marketing Digital"
        assert agendamento.status == AgendamentoStatus.ATIVO
        assert agendamento.user_id == user_id
        assert len(agendamento.execucoes) == 2
    
    def test_start_stop_scheduler(self, service):
        """Testa início e parada do scheduler."""
        # Verificar que scheduler está rodando
        assert service.running is True
        assert service.scheduler_thread is not None
        
        # Parar scheduler
        service.stop_scheduler()
        assert service.running is False
    
    def test_init_agendamento_service_global(self, temp_db_path):
        """Testa inicialização do serviço global."""
        config = {'db_path': temp_db_path}
        
        service = init_agendamento_service(config)
        
        assert service is not None
        assert isinstance(service, AgendamentoService)
        assert service.db_path == temp_db_path
    
    def test_get_agendamento_service_global(self, temp_db_path):
        """Testa obtenção do serviço global."""
        config = {'db_path': temp_db_path}
        init_agendamento_service(config)
        
        service = get_agendamento_service()
        
        assert service is not None
        assert isinstance(service, AgendamentoService)
        assert service.db_path == temp_db_path 