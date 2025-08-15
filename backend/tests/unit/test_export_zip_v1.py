from typing import Dict, List, Optional, Any
"""
Testes unitários para ExportLog e ExportadorZIP (export_zip_v1.py)
"""
import os
import tempfile
import zipfile
import json
from backend.app.services.export_zip_v1 import ExportLog, ExportadorZIP

def test_export_log_salvar():
    with tempfile.TemporaryDirectory() as tmp:
        log_path = os.path.join(tmp, 'log.json')
        metadados_reais = {
            'formato_exportacao': 'csv',
            'total_keywords': 150,
            'nichos_exportados': ['ecommerce', 'saude'],
            'filtros_aplicados': {'volume_minimo': 1000, 'cpc_maximo': 5.0}
        }
        log = ExportLog(
            usuario='usuario_teste_001', 
            arquivos=['keywords_ecommerce.csv', 'keywords_saude.csv'], 
            status='sucesso', 
            metadados=metadados_reais
        )
        log.salvar(log_path)
        with open(log_path) as f:
            data = json.load(f)
            assert data['usuario'] == 'usuario_teste_001'
            assert data['arquivos'] == ['keywords_ecommerce.csv', 'keywords_saude.csv']
            assert data['status'] == 'sucesso'
            assert data['metadados']['formato_exportacao'] == 'csv'
            assert data['metadados']['total_keywords'] == 150
            assert data['metadados']['nichos_exportados'] == ['ecommerce', 'saude']
            assert data['metadados']['filtros_aplicados']['volume_minimo'] == 1000

def test_exportador_zip_estrutura_customizavel():
    with tempfile.TemporaryDirectory() as tmp:
        # Criar arquivos de teste baseados em dados reais do sistema
        keywords_ecommerce = os.path.join(tmp, 'keywords_ecommerce.csv')
        keywords_saude = os.path.join(tmp, 'keywords_saude.csv')
        with open(keywords_ecommerce, 'w') as f: 
            f.write('termo,volume_busca,cpc,concorrencia\n')
            f.write('produto eletronico,5000,2.50,0.8\n')
        with open(keywords_saude, 'w') as f: 
            f.write('termo,volume_busca,cpc,concorrencia\n')
            f.write('consulta medica,3000,4.20,0.6\n')
        
        estrutura = {
            'ecommerce': [keywords_ecommerce], 
            'saude': [keywords_saude]
        }
        zip_path = os.path.join(tmp, 'exportacao_keywords.zip')
        exp = ExportadorZIP(estrutura)
        exp.exportar_zip(zip_path)
        with zipfile.ZipFile(zip_path) as data:
            assert 'ecommerce/keywords_ecommerce.csv' in data.namelist()
            assert 'saude/keywords_saude.csv' in data.namelist()

def test_exportador_zip_com_logs():
    with tempfile.TemporaryDirectory() as tmp:
        # Arquivo de keywords real
        keywords_file = os.path.join(tmp, 'keywords_exportadas.csv')
        with open(keywords_file, 'w') as f: 
            f.write('termo,volume_busca,cpc,concorrencia\n')
            f.write('palavra chave teste,1500,1.80,0.7\n')
        
        # Log de exportação
        log_path = os.path.join(tmp, 'export_log.json')
        log_data = {
            'usuario': 'usuario_teste_002',
            'timestamp': '2024-01-15T10:30:00Z',
            'status': 'concluido'
        }
        with open(log_path, 'w') as f: 
            json.dump(log_data, f)
        
        estrutura = {'': [keywords_file]}
        zip_path = os.path.join(tmp, 'exportacao_completa.zip')
        exp = ExportadorZIP(estrutura)
        exp.exportar_zip(zip_path, arquivos_extra={'export_log.json': log_path})
        with zipfile.ZipFile(zip_path) as data:
            assert 'keywords_exportadas.csv' in data.namelist()
            assert 'export_log.json' in data.namelist() 