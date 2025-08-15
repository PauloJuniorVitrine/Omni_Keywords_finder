"""
Serviço principal de execuções - Refatorado para usar serviços especializados.
Mantém compatibilidade com API existente enquanto delega para serviços específicos.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-002
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 2.0.0
"""

import os
import json
from datetime import datetime
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from backend.app.models import Categoria, Execucao, ExecucaoAgendada, db
from backend.app.utils.log_event import log_event

# 🎯 FASE 4 - INTEGRAÇÃO COM OBSERVABILIDADE
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from infrastructure.observability.trace_decorator import trace_function
from infrastructure.observability.anomaly_detection import AnomalyDetector
from infrastructure.observability.predictive_monitoring import PredictiveMonitor

# Importar serviços especializados
from .lote_execucao_service import LoteExecucaoService
from .agendamento_service import AgendamentoService
from .validacao_execucao_service import ValidacaoExecucaoService
from .prompt_service import PromptService


class ExecucaoService:
    """
    Serviço principal de execuções - Refatorado.
    
    Responsabilidades:
    - Coordenação entre serviços especializados
    - Manutenção de compatibilidade com API existente
    - Orquestração de fluxos complexos
    
    Princípios aplicados:
    - Composição: Usa serviços especializados
    - SRP: Coordenação e orquestração
    - Rastreabilidade: Logging detalhado
    - Compatibilidade: Mantém API existente
    """
    
    def __init__(self):
        """Inicializa o serviço principal de execuções."""
        self.lote_service = LoteExecucaoService()
        self.agendamento_service = AgendamentoService()
        self.validacao_service = ValidacaoExecucaoService()
        self.prompt_service = PromptService()
        
        log_event('info', 'ExecucaoService', 
                 detalhes='Serviço principal de execuções inicializado com serviços especializados')
    
    @trace_function(operation_name="processar_lote_execucoes", service_name="execucao-service")
    def processar_lote_execucoes(self, dados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa um lote de execuções em paralelo.
        Mantém compatibilidade com API existente.
        
        Args:
            dados: Lista de itens a serem processados
            
        Returns:
            Dicionário com resultados do processamento
        """
        try:
            # Validar lote completo
            valido, erros, dados_validados = self.validacao_service.validar_lote_completo(dados)
            
            if not valido:
                log_event('erro', 'ExecucaoService', 
                         detalhes=f'Validação de lote falhou: {erros}')
                
                return {
                    'id_lote': None,
                    'resultados': [{'erro': erro} for erro in erros],
                    'tempo_total': 0.0,
                    'qtd_executada': 0,
                    'log_path': None,
                    'erros_validacao': erros
                }
            
            # Processar lote usando serviço especializado
            resultado = self.lote_service.processar_lote(dados_validados)
            
            log_event('info', 'ExecucaoService', 
                     detalhes=f'Lote processado com sucesso: {len(dados_validados)} itens')
            
            return resultado
            
        except Exception as e:
            log_event('erro', 'ExecucaoService', 
                     detalhes=f'Erro no processamento de lote: {e}')
            
            return {
                'id_lote': None,
                'resultados': [{'erro': str(e)}],
                'tempo_total': 0.0,
                'qtd_executada': 0,
                'log_path': None,
                'erro_interno': str(e)
            }
    
    @trace_function(operation_name="processar_execucoes_agendadas", service_name="execucao-service")
    def processar_execucoes_agendadas(self) -> Optional[Dict[str, Any]]:
        """
        Processa execuções agendadas pendentes.
        Mantém compatibilidade com API existente.
        
        Returns:
            Dicionário com resultados do processamento ou None se não há pendências
        """
        try:
            resultado = self.agendamento_service.processar_agendamentos()
            
            if resultado:
                log_event('info', 'ExecucaoService', 
                         detalhes=f'Execuções agendadas processadas: {resultado["total_processadas"]} itens')
            else:
                log_event('info', 'ExecucaoService', 
                         detalhes='Nenhuma execução agendada pendente')
            
            return resultado
            
        except Exception as e:
            log_event('erro', 'ExecucaoService', 
                     detalhes=f'Erro no processamento de execuções agendadas: {e}')
            return None
    
    def executar_prompt_individual(self, categoria_id: int, palavras_chave: List[str], 
                                 cluster: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa um prompt individual.
        Nova funcionalidade usando serviços especializados.
        
        Args:
            categoria_id: ID da categoria
            palavras_chave: Lista de palavras-chave
            cluster: Cluster opcional
            
        Returns:
            Resultado da execução
        """
        try:
            # Validar dados
            item = {
                'categoria_id': categoria_id,
                'palavras_chave': palavras_chave,
                'cluster': cluster
            }
            
            valido, erro, dados_validados = self.validacao_service.validar_execucao_completa(item)
            if not valido:
                return {'erro': erro, 'categoria_id': categoria_id}
            
            # Processar prompt
            dados_prompt = {
                'palavras_chave': palavras_chave,
                'cluster': cluster or dados_validados['categoria'].cluster,
                'categoria': dados_validados['categoria'].nome
            }
            
            sucesso, erro, prompt_preenchido = self.prompt_service.processar_prompt_completo(
                dados_validados['prompt_path'], dados_prompt
            )
            
            if not sucesso:
                return {'erro': erro, 'categoria_id': categoria_id}
            
            # Criar execução
            t0 = perf_counter()
            execucao = Execucao(
                id_categoria=categoria_id,
                palavras_chave=json.dumps(palavras_chave),
                cluster_usado=cluster or dados_validados['categoria'].cluster,
                prompt_usado=dados_validados['prompt_path'],
                status='executado',
                data_execucao=datetime.utcnow(),
                tempo_estimado=None,
                tempo_real=None,
                log_path=None
            )
            
            db.session.add(execucao)
            db.session.commit()
            
            t1 = perf_counter()
            execucao.tempo_real = t1 - t0
            db.session.commit()
            
            log_event('execução', 'Execucao', 
                     id_referencia=execucao.id, 
                     detalhes=f'Execução individual para categoria {categoria_id}')
            
            return {
                'execucao_id': execucao.id,
                'prompt_preenchido': prompt_preenchido,
                'categoria_id': categoria_id,
                'palavras_chave': palavras_chave,
                'cluster': cluster or dados_validados['categoria'].cluster,
                'tempo_real': execucao.tempo_real
            }
            
        except Exception as e:
            log_event('erro', 'ExecucaoService', 
                     detalhes=f'Erro na execução individual: {e}')
            return {'erro': str(e), 'categoria_id': categoria_id}
    
    def agendar_execucao(self, categoria_id: int, palavras_chave: List[str], 
                        cluster: Optional[str], data_agendada: datetime, 
                        usuario: Optional[str] = None) -> Dict[str, Any]:
        """
        Agenda uma execução.
        Nova funcionalidade usando serviços especializados.
        
        Args:
            categoria_id: ID da categoria
            palavras_chave: Lista de palavras-chave
            cluster: Cluster opcional
            data_agendada: Data/hora agendada
            usuario: Usuário que agendou
            
        Returns:
            Resultado do agendamento
        """
        try:
            # Validar dados
            item = {
                'categoria_id': categoria_id,
                'palavras_chave': palavras_chave,
                'cluster': cluster
            }
            
            valido, erro, dados_validados = self.validacao_service.validar_execucao_completa(item)
            if not valido:
                return {'erro': erro, 'categoria_id': categoria_id}
            
            # Validar data de agendamento
            valido, erro, data_formatada = self.validacao_service.validar_data_agendamento(
                data_agendada.isoformat()
            )
            if not valido:
                return {'erro': erro, 'categoria_id': categoria_id}
            
            # Agendar usando serviço especializado
            resultado = self.agendamento_service.agendar_execucao(
                categoria_id=categoria_id,
                palavras_chave=json.dumps(palavras_chave),
                cluster=cluster,
                data_agendada=data_agendada,
                usuario=usuario
            )
            
            return resultado
            
        except Exception as e:
            log_event('erro', 'ExecucaoService', 
                     detalhes=f'Erro no agendamento: {e}')
            return {'erro': str(e), 'categoria_id': categoria_id}
    
    def obter_estatisticas_servicos(self) -> Dict[str, Any]:
        """
        Obtém estatísticas dos serviços especializados.
        
        Returns:
            Estatísticas consolidadas
        """
        try:
            stats_prompt = self.prompt_service.obter_estatisticas_cache()
            
            return {
                'prompt_service': stats_prompt,
                'timestamp': datetime.utcnow().isoformat(),
                'servicos_ativos': [
                    'LoteExecucaoService',
                    'AgendamentoService', 
                    'ValidacaoExecucaoService',
                    'PromptService'
                ]
            }
            
        except Exception as e:
            log_event('erro', 'ExecucaoService', 
                     detalhes=f'Erro ao obter estatísticas: {e}')
            return {'erro': str(e)}


# Instância global para compatibilidade
_execucao_service = ExecucaoService()

# Funções de compatibilidade com API existente
def processar_lote_execucoes(dados):
    """
    Função de compatibilidade para processamento de lotes.
    Delega para o serviço especializado.
    """
    return _execucao_service.processar_lote_execucoes(dados)

def processar_execucoes_agendadas():
    """
    Função de compatibilidade para processamento de agendamentos.
    Delega para o serviço especializado.
    """
    return _execucao_service.processar_execucoes_agendadas() 