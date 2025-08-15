"""
Testes unitários para schemas de validação de execuções
Prompt: Implementação de validação de entrada para execuções
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""
import pytest
from backend.app.schemas.execucao import (
    ExecucaoCreateRequest, ExecucaoLoteRequest, ExecucaoFilterRequest,
    sanitizar_palavra_chave, sanitizar_cluster
)
from pydantic import ValidationError
from datetime import datetime, timedelta

def test_execucao_create_request_valido():
    req = ExecucaoCreateRequest(
        categoria_id=1,
        palavras_chave=["keyword1", "keyword2"],
        cluster="cluster-01"
    )
    assert req.categoria_id == 1
    assert req.palavras_chave == ["keyword1", "keyword2"]
    assert req.cluster == "cluster-01"

def test_execucao_create_request_invalido_categoria():
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=0, palavras_chave=["kw"], cluster="abc")
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=-5, palavras_chave=["kw"], cluster="abc")

def test_execucao_create_request_invalido_palavras():
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=1, palavras_chave=[], cluster="abc")
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=1, palavras_chave=[""], cluster="abc")
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=1, palavras_chave=["a"*101], cluster="abc")
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=1, palavras_chave=["ok", "inv@lid"], cluster="abc")

def test_execucao_create_request_invalido_cluster():
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=1, palavras_chave=["kw"], cluster="")
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=1, palavras_chave=["kw"], cluster="a"*256)
    with pytest.raises(ValidationError):
        ExecucaoCreateRequest(categoria_id=1, palavras_chave=["kw"], cluster="inv@lid")

def test_execucao_lote_request_valido():
    lote = ExecucaoLoteRequest(
        execucoes=[
            ExecucaoCreateRequest(categoria_id=1, palavras_chave=["a"], cluster="c1"),
            ExecucaoCreateRequest(categoria_id=2, palavras_chave=["b"], cluster="c2")
        ],
        max_concurrent=3
    )
    assert len(lote.execucoes) == 2
    assert lote.max_concurrent == 3

def test_execucao_lote_request_invalido():
    with pytest.raises(ValidationError):
        ExecucaoLoteRequest(execucoes=[], max_concurrent=2)
    with pytest.raises(ValidationError):
        ExecucaoLoteRequest(execucoes=[
            ExecucaoCreateRequest(categoria_id=1, palavras_chave=["a"], cluster="c1"),
            ExecucaoCreateRequest(categoria_id=1, palavras_chave=["b"], cluster="c2")
        ], max_concurrent=2)  # categoria_id duplicado
    with pytest.raises(ValidationError):
        ExecucaoLoteRequest(execucoes=[
            ExecucaoCreateRequest(categoria_id=1, palavras_chave=["a"], cluster="c1")
        ], max_concurrent=0)
    with pytest.raises(ValidationError):
        ExecucaoLoteRequest(execucoes=[
            ExecucaoCreateRequest(categoria_id=1, palavras_chave=["a"], cluster="c1")
        ], max_concurrent=21)

def test_execucao_filter_request_valido():
    filtros = ExecucaoFilterRequest(
        categoria_id=1,
        nicho_id=None,
        status=None,
        data_inicio=datetime.utcnow() - timedelta(days=1),
        data_fim=datetime.utcnow(),
        limit=10,
        offset=0
    )
    assert filtros.categoria_id == 1
    assert filtros.limit == 10

def test_execucao_filter_request_invalido():
    with pytest.raises(ValidationError):
        ExecucaoFilterRequest(categoria_id=-1)
    with pytest.raises(ValidationError):
        ExecucaoFilterRequest(limit=0)
    with pytest.raises(ValidationError):
        ExecucaoFilterRequest(offset=-1)
    with pytest.raises(ValidationError):
        ExecucaoFilterRequest(data_inicio=datetime.utcnow(), data_fim=datetime.utcnow() - timedelta(days=1))

def test_sanitizar_palavra_chave():
    assert sanitizar_palavra_chave("<script>alert('x')</script>") == "scriptalert(x)/script"
    assert sanitizar_palavra_chave("   palavra   chave   ") == "palavra chave"
    assert sanitizar_palavra_chave("ok-key_word") == "ok-key_word"
    assert sanitizar_palavra_chave("a\x00b\x1Fc") == "abc"

def test_sanitizar_cluster():
    assert sanitizar_cluster('<script>alert(1)</script>') == 'scriptalert(1)/script'
    assert sanitizar_cluster('   cluster   name   ') == 'cluster name'
    assert sanitizar_cluster('ok-cluster_01') == 'ok-cluster_01'
    assert sanitizar_cluster('a\x00b\x1Fc') == 'abc'
    assert sanitizar_cluster('DROP TABLE cluster;') == 'DROP TABLE cluster;'
    assert sanitizar_cluster('rm -rf /') == 'rm -rf /'
    assert sanitizar_cluster('clu<>ster"\'"') == 'cluster'
    assert sanitizar_cluster(None) == ''
    assert sanitizar_cluster(123) == '' 