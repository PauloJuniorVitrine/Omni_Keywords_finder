from typing import Dict, List, Optional, Any
def test_criar_listar_editar_remover_nicho(client):
    # Criar
    resp = client.post('/api/nichos/', json={'nome': 'Finanças'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['nome'] == 'Finanças'
    nicho_id = data['id']

    # Listar
    resp = client.get('/api/nichos/')
    assert resp.status_code == 200
    lista = resp.get_json()
    assert any(n['nome'] == 'Finanças' for n in lista)

    # Editar
    resp = client.put(f'/api/nichos/{nicho_id}', json={'nome': 'Finanças 2'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['nome'] == 'Finanças 2'

    # Remover
    resp = client.delete(f'/api/nichos/{nicho_id}')
    assert resp.status_code == 204
    # Verificar remoção
    resp = client.get('/api/nichos/')
    lista = resp.get_json()
    assert not any(n['id'] == nicho_id for n in lista)


def test_criar_nicho_duplicado(client):
    client.post('/api/nichos/', json={'nome': 'Saúde'})
    resp = client.post('/api/nichos/', json={'nome': 'Saúde'})
    assert resp.status_code == 409 