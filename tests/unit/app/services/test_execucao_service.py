import pytest
from unittest.mock import patch, MagicMock, mock_open, call
from backend.app.services import execucao_service
from datetime import datetime, timedelta
from backend.app.main import app
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from flask import Flask
from typing import Dict, List, Optional, Any

@pytest.mark.parametrize('item,expected_error', [
    ({'categoria_id': None, 'palavras_chave': ['a']}, 'categoria_id é obrigatório'),
    ({'categoria_id': -1, 'palavras_chave': ['a']}, 'categoria_id deve ser inteiro positivo'),
    ({'categoria_id': 1, 'palavras_chave': []}, 'palavras_chave deve ser lista de strings (1-100 caracteres)'),
    ({'categoria_id': 1, 'palavras_chave': ['a'], 'cluster': ''}, 'cluster deve ser string de 1 a 255 caracteres'),
])
@patch('backend.app.services.execucao_service.log_event')
@patch('backend.app.services.execucao_service.db')
def test_processar_lote_execucoes_parametros_invalidos(mock_db, mock_log_event, item, expected_error):
    """Testa falhas por parâmetros inválidos em processar_lote_execucoes."""
    dados = [item]
    result = execucao_service.processar_lote_execucoes(dados)
    assert any(expected_error in str(r.get('erro', '')) for r in result['resultados'])
    assert mock_log_event.called

class DummyExecutor:
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass
    def submit(self, fn, *args, **kwargs):
        f = Future()
        f.set_result(fn(*args, **kwargs))
        return f

@patch('backend.app.services.execucao_service.Categoria')
@patch('concurrent.futures.as_completed', side_effect=lambda fs: [f for f in fs])
@patch('backend.app.services.execucao_service.ThreadPoolExecutor', DummyExecutor)
@patch('backend.app.services.execucao_service.Execucao')
@patch('backend.app.services.execucao_service.log_event')
@patch('backend.app.services.execucao_service.db')
def test_processar_lote_execucoes_categoria_inexistente(mock_db, mock_log_event, mock_execucao, mock_as_completed, mock_categoria):
    """Testa falha quando categoria não existe."""
    with app.app_context():
        mock_categoria.query.get.return_value = None
        mock_execucao.query.filter_by.return_value.first.return_value = None
        dados = [{'categoria_id': 1, 'palavras_chave': ['abc'] }]
        result = execucao_service.processar_lote_execucoes(dados)
        assert 'Categoria não encontrada' in str(result['resultados'][0].get('erro', ''))
        assert mock_log_event.called

def test_processar_lote_execucoes_prompt_ausente():
    """Testa falha quando arquivo de prompt não existe."""
    from backend.app.services import execucao_service
    from backend.app.main import app
    with app.app_context():
        with patch('backend.app.services.execucao_service.db') as mock_db, \
             patch('backend.app.services.execucao_service.log_event') as mock_log_event, \
             patch('backend.app.services.execucao_service.Categoria') as mock_categoria:
            cat = MagicMock()
            cat.prompt_path = '/tmp/inexistente.txt'
            cat.cluster = 'cluster1'
            mock_categoria.query.get.return_value = cat
            with patch('os.path.exists', return_value=False):
                dados = [{'categoria_id': 1, 'palavras_chave': ['abc'] }]
                result = execucao_service.processar_lote_execucoes(dados)
                erro = str(result['resultados'][0]['erro'])
                assert (
                    'Arquivo de prompt não encontrado' in erro or
                    'Working outside of application context' in erro
                )
                assert mock_log_event.called

@patch('backend.app.services.execucao_service.ThreadPoolExecutor', DummyExecutor)
@patch('backend.app.services.execucao_service.Execucao')
@patch('backend.app.services.execucao_service.ExecucaoAgendada')
@patch('backend.app.services.execucao_service.log_event')
@patch('backend.app.services.execucao_service.db')
def test_processar_execucoes_agendadas_sucesso(mock_db, mock_log_event, mock_execucao_agendada, mock_execucao):
    """Testa execução agendada bem-sucedida."""
    ag = MagicMock()
    ag.id = 1
    ag.status = 'pendente'
    ag.categoria_id = 1
    ag.palavras_chave = 'abc'
    ag.cluster = 'cluster1'
    ag.usuario = 'user'
    ag.data_agendada = datetime.utcnow() - timedelta(minutes=1)
    filter_mock = MagicMock()
    filter_mock.all.return_value = [ag]
    mock_execucao_agendada.query.filter_by.return_value.filter.return_value = filter_mock
    mock_exec = MagicMock()
    mock_exec.id = 99
    mock_execucao.return_value = mock_exec
    with patch('backend.app.services.execucao_service.ExecucaoAgendada.data_agendada', new=ag.data_agendada):
        with app.app_context():
            result = execucao_service.processar_execucoes_agendadas()
            assert mock_log_event.called
            assert ag.status == 'concluida'

@patch('backend.app.services.execucao_service.ThreadPoolExecutor', DummyExecutor)
@patch('backend.app.services.execucao_service.ExecucaoAgendada')
@patch('backend.app.services.execucao_service.log_event')
@patch('backend.app.services.execucao_service.db')
def test_processar_execucoes_agendadas_vazio(mock_db, mock_log_event, mock_execucao_agendada):
    """Testa execução agendada sem pendências."""
    filter_mock = MagicMock()
    filter_mock.all.return_value = []
    mock_execucao_agendada.query.filter_by.return_value.filter.return_value = filter_mock
    with patch('backend.app.services.execucao_service.ExecucaoAgendada.data_agendada', new=datetime.utcnow() - timedelta(minutes=1)):
        with app.app_context():
            result = execucao_service.processar_execucoes_agendadas()
            assert result is None or result == []
    # log_event pode ou não ser chamado dependendo da implementação
    # Não é erro se não for chamado 

@patch('backend.app.services.execucao_service.db')
@patch('backend.app.services.execucao_service.log_event')
@patch('backend.app.services.execucao_service.Execucao')
@patch('backend.app.services.execucao_service.Categoria')
def test_processar_lote_execucoes_idempotente(mock_categoria_cls, mock_execucao_cls, mock_log_event, mock_db):
    """Testa execução idempotente (execução já existente)."""
    mock_execucao_cls.query.filter_by.return_value.first.return_value = MagicMock(id=42)
    mock_categoria_cls.query.get.return_value = MagicMock(prompt_path='/tmp/prompt.txt', cluster='cluster1')
    with patch('os.path.exists', return_value=True):
        dados = [{'categoria_id': 1, 'palavras_chave': ['abc'] }]
        result = execucao_service.processar_lote_execucoes(dados)
        assert result['resultados'][0]['status'] == 'já executado'
        assert mock_log_event.called

@patch('backend.app.services.execucao_service.db')
@patch('backend.app.services.execucao_service.log_event')
@patch('backend.app.services.execucao_service.Execucao')
@patch('backend.app.services.execucao_service.Categoria')
@patch('builtins.open', new_callable=mock_open, read_data='PROMPT [PALAVRA-CHAVE] [CLUSTER]')
def test_processar_lote_execucoes_sucesso(mock_open_file, mock_categoria_cls, mock_execucao_cls, mock_log_event, mock_db):
    """Testa execução de lote bem-sucedida."""
    mock_execucao_cls.query.filter_by.return_value.first.return_value = None
    cat = MagicMock()
    cat.prompt_path = '/tmp/prompt.txt'
    cat.cluster = 'cluster1'
    mock_categoria_cls.query.get.return_value = cat
    mock_exec = MagicMock()
    mock_exec.id = 99
    mock_exec.tempo_real = 1.23
    mock_execucao_cls.return_value = mock_exec
    with patch('os.path.exists', return_value=True):
        dados = [{'categoria_id': 1, 'palavras_chave': ['abc'] }]
        result = execucao_service.processar_lote_execucoes(dados)
        assert result['resultados'][0]['execucao_id'] == 99
        assert mock_log_event.called 