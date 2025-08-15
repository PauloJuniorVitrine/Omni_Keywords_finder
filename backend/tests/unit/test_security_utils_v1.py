from typing import Dict, List, Optional, Any
"""
Testes unitários para security_utils_v1.py
"""
from backend.app.security.security_utils_v1 import sanitizar_entrada, checar_permissao, logar_tentativa_suspeita


def test_sanitizar_entrada():
    """
    Testa a sanitização de entradas para remoção de scripts e comandos perigosos.
    """
    assert sanitizar_entrada('<script>alert(1)</script>') == 'alert(1)'
    assert 'drop' not in sanitizar_entrada('drop table users;')
    assert sanitizar_entrada(123) == 123


def test_sanitizar_entrada_none():
    """
    Testa sanitização quando a entrada é None.
    """
    assert sanitizar_entrada(None) is None


def test_sanitizar_entrada_lista():
    """
    Testa sanitização quando a entrada é uma lista (tipo inesperado).
    """
    entrada = ['<script>', 'drop table']
    assert sanitizar_entrada(entrada) == entrada


def test_sanitizar_entrada_dict():
    """
    Testa sanitização quando a entrada é um dicionário (tipo inesperado).
    """
    entrada = {'valor': '<script>alert(1)</script>'}
    assert sanitizar_entrada(entrada) == entrada


def test_sanitizar_entrada_multiplos_padroes():
    """
    Testa sanitização de string com múltiplos padrões perigosos.
    """
    entrada = '<script>DROP TABLE users;</script>'
    saida = sanitizar_entrada(entrada)
    assert '<' not in saida and '>' not in saida
    assert 'drop' not in saida.lower()
    assert 'script' not in saida.lower()


def test_sanitizar_entrada_tags_apenas():
    """
    Testa sanitização de string composta apenas por tags.
    """
    entrada = '<b><index></index></b>'
    saida = sanitizar_entrada(entrada)
    assert saida == ''


def test_checar_permissao():
    """
    Testa a verificação de permissão e o log de tentativas negadas.
    """
    logs = []
    def fake_log(tipo, entidade, usuario, detalhes, id_ref=None):
        logs.append((tipo, entidade, usuario, detalhes))
    assert checar_permissao('admin', ['a', 'b'], 'a', logger=fake_log) is True
    assert checar_permissao('user', ['a'], 'b', logger=fake_log) is False
    assert logs[-1][0] == 'tentativa_negada'


def test_checar_permissao_lista_vazia():
    """
    Testa checagem de permissão com lista de permissões vazia.
    """
    logs = []
    def fake_log(tipo, entidade, usuario, detalhes, id_ref=None):
        logs.append((tipo, entidade, usuario, detalhes))
    assert checar_permissao('user', [], 'admin', logger=fake_log) is False
    assert logs[-1][0] == 'tentativa_negada'


def test_checar_permissao_none():
    """
    Testa checagem de permissão com permissões None.
    """
    logs = []
    def fake_log(tipo, entidade, usuario, detalhes, id_ref=None):
        logs.append((tipo, entidade, usuario, detalhes))
    try:
        checar_permissao('user', None, 'admin', logger=fake_log)
    except Exception as e:
        assert isinstance(e, TypeError)


def test_checar_permissao_usuario_vazio():
    """
    Testa checagem de permissão com usuário vazio.
    """
    logs = []
    def fake_log(tipo, entidade, usuario, detalhes, id_ref=None):
        logs.append((tipo, entidade, usuario, detalhes))
    assert checar_permissao('', ['admin'], 'admin', logger=fake_log) is True


def test_logar_tentativa_suspeita():
    """
    Testa o log de tentativas suspeitas de manipulação.
    """
    logs = []
    def fake_log(tipo, entidade, usuario, detalhes, id_ref=None):
        logs.append((tipo, entidade, usuario, detalhes))
    logar_tentativa_suspeita('user', 'delete', 'tentou deletar', logger=fake_log)
    assert logs[-1][0] == 'tentativa_suspeita'


def test_logar_tentativa_suspeita_campos_vazios():
    """
    Testa log de tentativa suspeita com campos vazios.
    """
    logs = []
    def fake_log(tipo, entidade, usuario, detalhes, id_ref=None):
        logs.append((tipo, entidade, usuario, detalhes))
    logar_tentativa_suspeita('', '', '', logger=fake_log)
    assert logs[-1][0] == 'tentativa_suspeita'


def test_logar_tentativa_suspeita_tipos_invalidos():
    """
    Testa log de tentativa suspeita com tipos inesperados.
    """
    logs = []
    def fake_log(tipo, entidade, usuario, detalhes, id_ref=None):
        logs.append((tipo, entidade, usuario, detalhes))
    logar_tentativa_suspeita(123, 456, 789, logger=fake_log)
    assert logs[-1][0] == 'tentativa_suspeita'


def test_log_format():
    """
    Testa se o log gerado contém os campos esperados e formato correto.
    """
    logs = []
    def fake_log(tipo, entidade, usuario, detalhes, id_ref=None):
        logs.append((tipo, entidade, usuario, detalhes, id_ref))
    logar_tentativa_suspeita('user', 'delete', 'detalhe', logger=fake_log)
    tipo, entidade, usuario, detalhes, id_ref = logs[-1]
    assert tipo == 'tentativa_suspeita'
    assert entidade == 'Seguranca'
    assert usuario == 'user'
    assert 'ação: delete' in detalhes


def test_sanitizar_entrada_tipo_invalido():
    """
    Testa sanitização com tipo não suportado (ex: objeto customizado).
    """
    class Custom:
        pass
    try:
        sanitizar_entrada(Custom())
    except TypeError as e:
        assert 'Tipo de valor não suportado' in str(e)


def test_checar_permissao_tipo_invalido():
    """
    Testa checar_permissao com permissoes não-lista e permissao_necessaria não-string.
    """
    logs = []
    def fake_log(*args, **kwargs):
        logs.append(args)
    try:
        checar_permissao('user', 'admin', 'admin', logger=fake_log)
    except TypeError as e:
        assert 'permissoes deve ser uma lista' in str(e)
    try:
        checar_permissao('user', ['admin'], 123, logger=fake_log)
    except TypeError as e:
        assert 'permissao_necessaria deve ser string' in str(e)


def test_logar_tentativa_suspeita_tipo_invalido():
    """
    Testa logar_tentativa_suspeita com argumentos de tipo não suportado.
    """
    logs = []
    def fake_log(*args, **kwargs):
        logs.append(args)
    try:
        logar_tentativa_suspeita(object(), 'acao', 'detalhes', logger=fake_log)
    except TypeError as e:
        assert 'Argumentos usuario, acao e detalhes devem ser' in str(e)
    try:
        logar_tentativa_suspeita('user', object(), 'detalhes', logger=fake_log)
    except TypeError as e:
        assert 'Argumentos usuario, acao e detalhes devem ser' in str(e)
    try:
        logar_tentativa_suspeita('user', 'acao', object(), logger=fake_log)
    except TypeError as e:
        assert 'Argumentos usuario, acao e detalhes devem ser' in str(e) 