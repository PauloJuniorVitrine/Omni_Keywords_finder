#!/usr/bin/env python3
"""
Script de Teste de Integridade - IMP-003
=======================================

Tracing ID: IMP003_INTEGRITY_TEST_20241227
Data/Hora: 2024-12-27 22:40:00 UTC
Versão: 1.0

Este script testa a integridade do sistema após a limpeza de dead code.
"""

import os
import sys
import importlib
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/teste_integridade_imp003.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class IntegrityTester:
    """Classe para teste de integridade do sistema."""
    
    def __init__(self, projeto_root: str = "."):
        self.projeto_root = Path(projeto_root)
        self.testes_executados = []
        self.testes_falharam = []
        self.testes_passaram = []
        self.erros = []
        
        # Adicionar o diretório raiz ao path do Python
        sys.path.insert(0, str(self.projeto_root))
        
    def testar_import_modulo(self, modulo: str) -> Dict:
        """Testa se um módulo pode ser importado corretamente."""
        resultado = {
            'modulo': modulo,
            'status': 'FALHOU',
            'erro': None,
            'tempo_execucao': 0
        }
        
        try:
            import time
            inicio = time.time()
            
            # Tentar importar o módulo
            importlib.import_module(modulo)
            
            fim = time.time()
            resultado['tempo_execucao'] = fim - inicio
            resultado['status'] = 'PASSOU'
            
        except Exception as e:
            resultado['erro'] = str(e)
            resultado['status'] = 'FALHOU'
        
        return resultado
    
    def testar_modulos_principais(self) -> List[Dict]:
        """Testa os módulos principais do sistema."""
        modulos_principais = [
            'infrastructure.processamento.integrador_cauda_longa',
            'infrastructure.processamento.validador_keywords',
            'infrastructure.coleta.google_keyword_planner',
            'infrastructure.coleta.semrush',
            'infrastructure.coleta.ahrefs',
            'backend.app.main',
            'backend.app.api.api_routes',
            'shared.keyword_utils',
            'shared.cache'
        ]
        
        resultados = []
        for modulo in modulos_principais:
            resultado = self.testar_import_modulo(modulo)
            resultados.append(resultado)
            
            if resultado['status'] == 'PASSOU':
                self.testes_passaram.append(resultado)
                logger.info(f"✅ Módulo {modulo} importado com sucesso")
            else:
                self.testes_falharam.append(resultado)
                logger.error(f"❌ Falha ao importar {modulo}: {resultado['erro']}")
        
        return resultados
    
    def testar_funcionalidades_criticas(self) -> List[Dict]:
        """Testa funcionalidades críticas do sistema."""
        funcionalidades = [
            {
                'nome': 'Validador de Keywords',
                'modulo': 'infrastructure.processamento.validador_keywords',
                'classe': 'ValidadorKeywords'
            },
            {
                'nome': 'Integrador Cauda Longa',
                'modulo': 'infrastructure.processamento.integrador_cauda_longa',
                'classe': 'IntegradorCaudaLonga'
            },
            {
                'nome': 'Utilitários de Keywords',
                'modulo': 'shared.keyword_utils',
                'funcao': 'normalizar_keyword'
            }
        ]
        
        resultados = []
        for func in funcionalidades:
            resultado = {
                'funcionalidade': func['nome'],
                'status': 'FALHOU',
                'erro': None
            }
            
            try:
                modulo = importlib.import_module(func['modulo'])
                
                if 'classe' in func:
                    # Testar se a classe existe
                    if hasattr(modulo, func['classe']):
                        resultado['status'] = 'PASSOU'
                    else:
                        resultado['erro'] = f"Classe {func['classe']} não encontrada"
                
                elif 'funcao' in func:
                    # Testar se a função existe
                    if hasattr(modulo, func['funcao']):
                        resultado['status'] = 'PASSOU'
                    else:
                        resultado['erro'] = f"Função {func['funcao']} não encontrada"
                
            except Exception as e:
                resultado['erro'] = str(e)
            
            resultados.append(resultado)
            
            if resultado['status'] == 'PASSOU':
                self.testes_passaram.append(resultado)
                logger.info(f"✅ Funcionalidade {func['nome']} testada com sucesso")
            else:
                self.testes_falharam.append(resultado)
                logger.error(f"❌ Falha na funcionalidade {func['nome']}: {resultado['erro']}")
        
        return resultados
    
    def testar_estrutura_arquivos(self) -> List[Dict]:
        """Testa se a estrutura de arquivos está intacta."""
        arquivos_criticos = [
            'infrastructure/processamento/integrador_cauda_longa.py',
            'infrastructure/processamento/validador_keywords.py',
            'infrastructure/coleta/google_keyword_planner.py',
            'backend/app/main.py',
            'backend/app/api/api_routes.py',
            'shared/keyword_utils.py',
            'shared/cache.py'
        ]
        
        resultados = []
        for arquivo in arquivos_criticos:
            resultado = {
                'arquivo': arquivo,
                'status': 'FALHOU',
                'erro': None
            }
            
            arquivo_path = self.projeto_root / arquivo
            if arquivo_path.exists():
                resultado['status'] = 'PASSOU'
                self.testes_passaram.append(resultado)
                logger.info(f"✅ Arquivo {arquivo} existe")
            else:
                resultado['erro'] = "Arquivo não encontrado"
                self.testes_falharam.append(resultado)
                logger.error(f"❌ Arquivo {arquivo} não encontrado")
            
            resultados.append(resultado)
        
        return resultados
    
    def executar_testes(self) -> Dict:
        """Executa todos os testes de integridade."""
        logger.info("🧪 Iniciando testes de integridade - IMP-003...")
        
        # 1. Testar módulos principais
        logger.info("📦 Testando módulos principais...")
        resultados_modulos = self.testar_modulos_principais()
        
        # 2. Testar funcionalidades críticas
        logger.info("⚙️ Testando funcionalidades críticas...")
        resultados_funcionalidades = self.testar_funcionalidades_criticas()
        
        # 3. Testar estrutura de arquivos
        logger.info("📁 Testando estrutura de arquivos...")
        resultados_arquivos = self.testar_estrutura_arquivos()
        
        # 4. Gerar relatório
        total_testes = len(resultados_modulos) + len(resultados_funcionalidades) + len(resultados_arquivos)
        total_passaram = len(self.testes_passaram)
        total_falharam = len(self.testes_falharam)
        
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'tracing_id': 'IMP003_INTEGRITY_TEST_20241227',
            'total_testes': total_testes,
            'testes_passaram': total_passaram,
            'testes_falharam': total_falharam,
            'taxa_sucesso': (total_passaram / total_testes * 100) if total_testes > 0 else 0,
            'resultados_modulos': resultados_modulos,
            'resultados_funcionalidades': resultados_funcionalidades,
            'resultados_arquivos': resultados_arquivos,
            'status': 'APROVADO' if total_falharam == 0 else 'REPROVADO'
        }
        
        # 5. Salvar relatório
        self.salvar_relatorio(relatorio)
        
        logger.info(f"✅ Testes de integridade concluídos!")
        logger.info(f"📊 Resumo:")
        logger.info(f"   - Total de testes: {total_testes}")
        logger.info(f"   - Testes passaram: {total_passaram}")
        logger.info(f"   - Testes falharam: {total_falharam}")
        logger.info(f"   - Taxa de sucesso: {relatorio['taxa_sucesso']:.1f}%")
        logger.info(f"   - Status: {relatorio['status']}")
        
        return relatorio
    
    def salvar_relatorio(self, relatorio: Dict):
        """Salva o relatório de testes."""
        relatorio_path = self.projeto_root / "logs" / "relatorio_testes_integridade_imp003.json"
        relatorio_path.parent.mkdir(exist_ok=True)
        
        import json
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {relatorio_path}")

def main():
    """Função principal."""
    print("🧪 TESTES DE INTEGRIDADE - IMP-003")
    print("=" * 50)
    
    # Executar testes
    tester = IntegrityTester()
    relatorio = tester.executar_testes()
    
    # Exibir resultados
    print(f"\n📊 RESULTADOS TESTES IMP-003:")
    print(f"   🧪 Total de testes: {relatorio['total_testes']}")
    print(f"   ✅ Testes passaram: {relatorio['testes_passaram']}")
    print(f"   ❌ Testes falharam: {relatorio['testes_falharam']}")
    print(f"   📈 Taxa de sucesso: {relatorio['taxa_sucesso']:.1f}%")
    print(f"   🎯 Status: {relatorio['status']}")
    
    if relatorio['testes_falharam'] > 0:
        print("\n❌ Testes que falharam:")
        for resultado in relatorio['resultados_modulos']:
            if resultado['status'] == 'FALHOU':
                print(f"   - Módulo {resultado['modulo']}: {resultado['erro']}")
        
        for resultado in relatorio['resultados_funcionalidades']:
            if resultado['status'] == 'FALHOU':
                print(f"   - Funcionalidade {resultado['funcionalidade']}: {resultado['erro']}")
        
        for resultado in relatorio['resultados_arquivos']:
            if resultado['status'] == 'FALHOU':
                print(f"   - Arquivo {resultado['arquivo']}: {resultado['erro']}")
    
    print(f"\n📄 Relatório completo salvo em: logs/relatorio_testes_integridade_imp003.json")
    
    if relatorio['status'] == 'APROVADO':
        print("\n🎯 IMP-003: Testes de Integridade - APROVADO!")
    else:
        print("\n⚠️ IMP-003: Testes de Integridade - REPROVADO!")

if __name__ == "__main__":
    main() 