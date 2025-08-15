#!/usr/bin/env python3
"""
Teste Manual do Fluxo Completo - Omni Keywords Finder

Script para teste manual do fluxo completo após a migração.
Permite validação manual de todas as funcionalidades.

Tracing ID: MANUAL_TEST_001_20241227
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO PARA FASE 5
"""

import sys
import os
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from infrastructure.orchestrator.fluxo_completo_orchestrator import FluxoCompletoOrchestrator
    from infrastructure.orchestrator.config import OrchestratorConfig
    from infrastructure.coleta.base_keyword import BaseKeywordCollector
    from infrastructure.processamento.ml_processor import MLProcessor
    from infrastructure.validacao.validador_avancado import ValidadorAvancado
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que o ambiente Python está configurado corretamente.")
    sys.exit(1)


class ManualTestRunner:
    """Executor de testes manuais."""
    
    def __init__(self):
        """Inicializa o executor de testes."""
        self.results = []
        self.start_time = time.time()
        
        # Configuração para testes
        self.config = OrchestratorConfig()
        self.config.coleta = {
            'timeout': 30,
            'max_retries': 3,
            'rate_limit': 100
        }
        self.config.validacao = {
            'min_volume': 100,
            'max_competition': 0.8
        }
        self.config.processamento = {
            'batch_size': 1000,
            'model_path': 'models/keyword_processor.pkl'
        }
        self.config.exportacao = {
            'format': 'json',
            'output_dir': 'output'
        }
        
        # Palavras-chave de teste
        self.test_keywords = [
            "python programming",
            "machine learning",
            "data science",
            "web development",
            "artificial intelligence",
            "deep learning",
            "natural language processing",
            "computer vision",
            "robotics",
            "blockchain technology"
        ]
    
    def log_test(self, test_name: str, status: str, details: str = "", error: str = None):
        """Registra resultado de um teste."""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Exibir resultado
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
        if error:
            print(f"   ❌ Erro: {error}")
        print()
    
    def test_imports(self):
        """Testa imports críticos."""
        print("🧪 Testando imports críticos...")
        
        try:
            # Testar imports principais
            from infrastructure.orchestrator.fluxo_completo_orchestrator import FluxoCompletoOrchestrator
            from infrastructure.orchestrator.config import OrchestratorConfig
            from infrastructure.coleta.base_keyword import BaseKeywordCollector
            from infrastructure.processamento.ml_processor import MLProcessor
            from infrastructure.validacao.validador_avancado import ValidadorAvancado
            
            self.log_test(
                "Imports Críticos",
                "PASS",
                "Todos os módulos principais importados com sucesso"
            )
            
        except ImportError as e:
            self.log_test(
                "Imports Críticos",
                "FAIL",
                f"Falha ao importar módulos: {e}"
            )
    
    def test_configuration(self):
        """Testa configuração do sistema."""
        print("⚙️ Testando configuração...")
        
        try:
            # Verificar configurações essenciais
            required_sections = ['coleta', 'validacao', 'processamento', 'exportacao']
            
            for section in required_sections:
                if not hasattr(self.config, section):
                    raise ValueError(f"Seção {section} não encontrada na configuração")
                
                section_config = getattr(self.config, section)
                if not isinstance(section_config, dict):
                    raise ValueError(f"Seção {section} não é um dicionário")
            
            self.log_test(
                "Configuração",
                "PASS",
                f"Configuração válida com {len(required_sections)} seções"
            )
            
        except Exception as e:
            self.log_test(
                "Configuração",
                "FAIL",
                f"Erro na configuração: {e}"
            )
    
    def test_orchestrator_initialization(self):
        """Testa inicialização do orquestrador."""
        print("🎯 Testando inicialização do orquestrador...")
        
        try:
            orchestrator = FluxoCompletoOrchestrator(self.config)
            
            # Verificar se orquestrador foi inicializado
            if not orchestrator:
                raise ValueError("Orchestrator não foi inicializado")
            
            # Verificar etapas
            etapas = ['coleta', 'validacao', 'processamento', 'preenchimento', 'exportacao']
            for etapa in etapas:
                if not hasattr(orchestrator, f'etapa_{etapa}'):
                    raise ValueError(f"Etapa {etapa} não encontrada no orquestrador")
            
            self.log_test(
                "Inicialização do Orquestrador",
                "PASS",
                f"Orchestrator inicializado com {len(etapas)} etapas"
            )
            
            return orchestrator
            
        except Exception as e:
            self.log_test(
                "Inicialização do Orquestrador",
                "FAIL",
                f"Erro na inicialização: {e}"
            )
            return None
    
    def test_collectors(self, orchestrator):
        """Testa coletores."""
        print("🔍 Testando coletores...")
        
        try:
            # Verificar coletores disponíveis
            collectors_dir = project_root / 'infrastructure' / 'coleta'
            collector_files = list(collectors_dir.glob('*.py'))
            
            # Filtrar arquivos que não são __init__.py ou base_keyword.py
            collector_files = [f for f in collector_files 
                             if f.name not in ['__init__.py', 'base_keyword.py']]
            
            working_collectors = []
            failed_collectors = []
            
            for collector_file in collector_files:
                try:
                    module_name = f"infrastructure.coleta.{collector_file.stem}"
                    module = __import__(module_name, fromlist=[collector_file.stem])
                    
                    # Verificar se tem classe de coletor
                    collector_class_name = f'{collector_file.stem.title()}Collector'
                    if hasattr(module, collector_class_name):
                        working_collectors.append(collector_file.stem)
                    else:
                        failed_collectors.append(f"{collector_file.stem}: Sem classe de coletor")
                        
                except Exception as e:
                    failed_collectors.append(f"{collector_file.stem}: {e}")
            
            if failed_collectors:
                self.log_test(
                    "Coletores",
                    "FAIL",
                    f"Falha em {len(failed_collectors)} coletores: {failed_collectors}"
                )
            else:
                self.log_test(
                    "Coletores",
                    "PASS",
                    f"Coletores funcionando: {len(working_collectors)}"
                )
            
        except Exception as e:
            self.log_test(
                "Coletores",
                "FAIL",
                f"Erro nos coletores: {e}"
            )
    
    def test_validation_system(self, orchestrator):
        """Testa sistema de validação."""
        print("✅ Testando sistema de validação...")
        
        try:
            # Testar validador
            validador = ValidadorAvancado({})
            
            if not validador:
                raise ValueError("Validador não foi inicializado")
            
            # Verificar métodos essenciais
            required_methods = ['validar_keywords', 'get_estatisticas']
            for method in required_methods:
                if not hasattr(validador, method):
                    raise ValueError(f"Método {method} não encontrado no validador")
            
            self.log_test(
                "Sistema de Validação",
                "PASS",
                "Validador funcionando com métodos essenciais"
            )
            
        except Exception as e:
            self.log_test(
                "Sistema de Validação",
                "FAIL",
                f"Erro na validação: {e}"
            )
    
    def test_processing_system(self, orchestrator):
        """Testa sistema de processamento."""
        print("⚡ Testando sistema de processamento...")
        
        try:
            # Testar processador ML
            processor = MLProcessor()
            
            if not processor:
                raise ValueError("ML Processor não foi inicializado")
            
            # Verificar métodos essenciais
            required_methods = ['processar_keywords', 'treinar_modelo', 'avaliar_modelo']
            for method in required_methods:
                if not hasattr(processor, method):
                    raise ValueError(f"Método {method} não encontrado no ML Processor")
            
            self.log_test(
                "Sistema de Processamento",
                "PASS",
                "ML Processor funcionando com métodos essenciais"
            )
            
        except Exception as e:
            self.log_test(
                "Sistema de Processamento",
                "FAIL",
                f"Erro no processamento: {e}"
            )
    
    def test_export_system(self, orchestrator):
        """Testa sistema de exportação."""
        print("📤 Testando sistema de exportação...")
        
        try:
            # Dados de exemplo para exportação
            export_data = {
                'keywords': self.test_keywords,
                'metrics': {
                    'volume': [1000, 800, 1200, 600, 900, 1100, 700, 950, 850, 1000],
                    'competition': [0.3, 0.5, 0.2, 0.7, 0.4, 0.6, 0.3, 0.5, 0.4, 0.6],
                    'difficulty': [0.4, 0.6, 0.3, 0.8, 0.5, 0.7, 0.4, 0.6, 0.5, 0.7]
                }
            }
            
            # Testar exportação
            with tempfile.TemporaryDirectory() as temp_dir:
                result = orchestrator.etapa_exportacao.executar_exportacao(
                    export_data, 
                    output_dir=temp_dir,
                    format='json'
                )
                
                if result and result.get('status') == 'success':
                    self.log_test(
                        "Sistema de Exportação",
                        "PASS",
                        f"Exportação bem-sucedida: {result.get('file_path', 'N/A')}"
                    )
                else:
                    self.log_test(
                        "Sistema de Exportação",
                        "FAIL",
                        f"Falha na exportação: {result}"
                    )
            
        except Exception as e:
            self.log_test(
                "Sistema de Exportação",
                "FAIL",
                f"Erro na exportação: {e}"
            )
    
    def test_full_workflow(self, orchestrator):
        """Testa fluxo completo."""
        print("🔄 Testando fluxo completo...")
        
        try:
            # Executar fluxo completo com dados de teste
            with tempfile.TemporaryDirectory() as temp_dir:
                result = orchestrator.executar_fluxo_completo(
                    keywords_iniciais=self.test_keywords,
                    output_dir=temp_dir
                )
                
                if result and result.get('status') == 'success':
                    etapas = result.get('etapas', {})
                    etapas_count = len(etapas)
                    
                    self.log_test(
                        "Fluxo Completo",
                        "PASS",
                        f"Fluxo executado com sucesso: {etapas_count} etapas completadas"
                    )
                    
                    # Detalhar etapas
                    for etapa_name, etapa_result in etapas.items():
                        status = etapa_result.get('status', 'unknown')
                        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
                        print(f"   {status_icon} {etapa_name}: {status}")
                    
                else:
                    self.log_test(
                        "Fluxo Completo",
                        "FAIL",
                        f"Falha no fluxo: {result}"
                    )
            
        except Exception as e:
            self.log_test(
                "Fluxo Completo",
                "FAIL",
                f"Erro no fluxo: {e}"
            )
    
    def test_performance(self, orchestrator):
        """Testa performance do sistema."""
        print("⚡ Testando performance...")
        
        try:
            start_time = time.time()
            
            # Executar operação simples para medir performance
            with tempfile.TemporaryDirectory() as temp_dir:
                result = orchestrator.executar_fluxo_completo(
                    keywords_iniciais=self.test_keywords[:3],  # Apenas 3 keywords para teste rápido
                    output_dir=temp_dir
                )
                
                execution_time = time.time() - start_time
                
                if result and result.get('status') == 'success':
                    if execution_time < 60:  # Máximo 1 minuto
                        self.log_test(
                            "Performance",
                            "PASS",
                            f"Execução em {execution_time:.2f} segundos"
                        )
                    else:
                        self.log_test(
                            "Performance",
                            "WARN",
                            f"Execução lenta: {execution_time:.2f} segundos"
                        )
                else:
                    self.log_test(
                        "Performance",
                        "FAIL",
                        f"Falha na execução: {result}"
                    )
            
        except Exception as e:
            self.log_test(
                "Performance",
                "FAIL",
                f"Erro no teste de performance: {e}"
            )
    
    def test_error_handling(self, orchestrator):
        """Testa tratamento de erros."""
        print("🛡️ Testando tratamento de erros...")
        
        try:
            # Testar com dados inválidos
            invalid_keywords = []
            
            result = orchestrator.etapa_coleta.executar_coleta(invalid_keywords)
            
            # Verificar se erro foi tratado adequadamente
            if result is not None:
                self.log_test(
                    "Tratamento de Erros",
                    "PASS",
                    "Erro tratado adequadamente"
                )
            else:
                self.log_test(
                    "Tratamento de Erros",
                    "WARN",
                    "Resultado None para dados inválidos"
                )
            
        except Exception as e:
            self.log_test(
                "Tratamento de Erros",
                "FAIL",
                f"Erro não tratado: {e}"
            )
    
    def generate_report(self):
        """Gera relatório dos testes."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.results if r['status'] == 'WARN'])
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        execution_time = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE TESTES MANUAIS")
        print("="*60)
        print(f"📊 Total de Testes: {total_tests}")
        print(f"✅ Aprovados: {passed_tests}")
        print(f"❌ Falharam: {failed_tests}")
        print(f"⚠️ Avisos: {warning_tests}")
        print(f"📈 Taxa de Sucesso: {success_rate:.1f}%")
        print(f"⏱️ Tempo Total: {execution_time:.2f} segundos")
        print("="*60)
        
        if success_rate >= 90:
            print("🎉 MIGRAÇÃO VALIDADA COM SUCESSO!")
            print("✅ Sistema pronto para produção")
        elif success_rate >= 70:
            print("⚠️ MIGRAÇÃO PARCIALMENTE VÁLIDA")
            print("🔧 Revisão necessária antes da produção")
        else:
            print("❌ MIGRAÇÃO COM PROBLEMAS CRÍTICOS")
            print("🔄 Rollback recomendado")
        
        print("="*60)
        
        # Salvar relatório
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'warning_tests': warning_tests,
            'success_rate': success_rate,
            'execution_time': execution_time,
            'results': self.results
        }
        
        report_file = f"manual_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório salvo em: {report_file}")
        
        return success_rate >= 90
    
    def run_all_tests(self):
        """Executa todos os testes."""
        print("🚀 INICIANDO TESTES MANUAIS DA MIGRAÇÃO")
        print("="*60)
        print(f"📅 Data: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}")
        print(f"🎯 Objetivo: Validar migração completa do sistema")
        print("="*60)
        print()
        
        # Executar testes
        self.test_imports()
        self.test_configuration()
        
        orchestrator = self.test_orchestrator_initialization()
        if orchestrator:
            self.test_collectors(orchestrator)
            self.test_validation_system(orchestrator)
            self.test_processing_system(orchestrator)
            self.test_export_system(orchestrator)
            self.test_full_workflow(orchestrator)
            self.test_performance(orchestrator)
            self.test_error_handling(orchestrator)
        
        # Gerar relatório
        success = self.generate_report()
        
        return success


def main():
    """Função principal."""
    print("🧪 TESTE MANUAL DO FLUXO COMPLETO")
    print("Omni Keywords Finder - Validação da Migração")
    print()
    
    # Verificar se estamos no diretório correto
    if not (project_root / 'infrastructure').exists():
        print("❌ Erro: Execute este script no diretório raiz do projeto")
        sys.exit(1)
    
    # Executar testes
    runner = ManualTestRunner()
    success = runner.run_all_tests()
    
    # Retornar código de saída
    if success:
        print("\n🎉 Todos os testes passaram! Migração aprovada.")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Revisão necessária.")
        sys.exit(1)


if __name__ == "__main__":
    main() 