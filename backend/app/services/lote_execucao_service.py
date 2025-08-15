"""
Serviço de Execução em Lote - Omni Keywords Finder
Processamento assíncrono de múltiplas execuções

Prompt: Implementação de serviço de execução em lote
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import asyncio
import json
import uuid
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class LoteStatus(Enum):
    """Status do lote de execução"""
    PENDENTE = "pendente"
    EM_EXECUCAO = "em_execucao"
    CONCLUIDO = "concluido"
    FALHOU = "falhou"
    CANCELADO = "cancelado"
    PAUSADO = "pausado"

class ExecucaoStatus(Enum):
    """Status da execução individual"""
    PENDENTE = "pendente"
    EM_EXECUCAO = "em_execucao"
    CONCLUIDA = "concluida"
    FALHOU = "falhou"
    CANCELADA = "cancelada"

@dataclass
class ExecucaoItem:
    """Item de execução no lote"""
    id: str
    categoria_id: int
    palavras_chave: List[str]
    cluster: Optional[str] = None
    status: ExecucaoStatus = ExecucaoStatus.PENDENTE
    resultado: Optional[Dict[str, Any]] = None
    erro: Optional[str] = None
    tempo_inicio: Optional[datetime] = None
    tempo_fim: Optional[datetime] = None
    tentativas: int = 0
    max_tentativas: int = 3

@dataclass
class LoteConfig:
    """Configuração do lote"""
    max_concurrent: int = 5
    timeout_por_execucao: int = 300  # 5 minutos
    retry_delay: int = 60  # 1 minuto
    max_retries: int = 3
    priority: int = 1  # 1-10, maior = mais prioritário

@dataclass
class LoteResultado:
    """Resultado do processamento do lote"""
    lote_id: str
    total_execucoes: int
    execucoes_concluidas: int
    execucoes_falharam: int
    execucoes_canceladas: int
    tempo_total: float
    tempo_medio_por_execucao: float
    taxa_sucesso: float
    detalhes: Dict[str, Any]

class LoteExecucaoService:
    """Serviço de execução em lote"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.lotes_ativos = {}  # lote_id -> LoteInfo
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_workers', 10)
        )
        self.lote_queue = Queue()
        self.processing_thread = None
        self.running = False
        self.stats = {
            'lotes_processados': 0,
            'execucoes_processadas': 0,
            'tempo_total_processamento': 0.0,
            'taxa_sucesso_geral': 0.0
        }
        
        # Callbacks
        self.on_lote_complete: Optional[Callable] = None
        self.on_execucao_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Iniciar processamento
        self.start_processing()
    
    def start_processing(self):
        """Inicia thread de processamento"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.running = True
            self.processing_thread = threading.Thread(
                target=self._process_lotes_loop,
                daemon=True
            )
            self.processing_thread.start()
            logger.info("Serviço de lote iniciado")
    
    def stop_processing(self):
        """Para o processamento"""
        self.running = False
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5)
        self.executor.shutdown(wait=True)
        logger.info("Serviço de lote parado")
    
    def _process_lotes_loop(self):
        """Loop principal de processamento de lotes"""
        while self.running:
            try:
                # Processar lote da fila
                lote_info = self.lote_queue.get(timeout=1.0)
                self._process_lote(lote_info)
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Erro no processamento de lotes: {str(e)}")
                if self.on_error:
                    self.on_error(e)
    
    def criar_lote(
        self,
        execucoes: List[Dict[str, Any]],
        config: Optional[LoteConfig] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Cria um novo lote de execuções
        
        Args:
            execucoes: Lista de execuções para processar
            config: Configuração do lote
            user_id: ID do usuário que criou o lote
            
        Returns:
            ID do lote criado
        """
        lote_id = str(uuid.uuid4())
        config = config or LoteConfig()
        
        # Criar itens de execução
        execucoes_items = []
        for exec_data in execucoes:
            item = ExecucaoItem(
                id=str(uuid.uuid4()),
                categoria_id=exec_data['categoria_id'],
                palavras_chave=exec_data['palavras_chave'],
                cluster=exec_data.get('cluster'),
                max_tentativas=config.max_retries
            )
            execucoes_items.append(item)
        
        # Criar informações do lote
        lote_info = {
            'id': lote_id,
            'status': LoteStatus.PENDENTE,
            'config': config,
            'execucoes': execucoes_items,
            'user_id': user_id,
            'criado_em': datetime.now(timezone.utc),
            'inicio_processamento': None,
            'fim_processamento': None,
            'progresso': 0,
            'resultado': None
        }
        
        # Adicionar à fila de processamento
        self.lote_queue.put(lote_info)
        self.lotes_ativos[lote_id] = lote_info
        
        logger.info(f"Lote criado: {lote_id} com {len(execucoes_items)} execuções")
        return lote_id
    
    def _process_lote(self, lote_info: Dict[str, Any]):
        """Processa um lote de execuções"""
        lote_id = lote_info['id']
        config = lote_info['config']
        execucoes = lote_info['execucoes']
        
        try:
            logger.info(f"Iniciando processamento do lote: {lote_id}")
            
            # Atualizar status
            lote_info['status'] = LoteStatus.EM_EXECUCAO
            lote_info['inicio_processamento'] = datetime.now(timezone.utc)
            
            # Processar execuções com limite de concorrência
            with ThreadPoolExecutor(max_workers=config.max_concurrent) as executor:
                # Submeter execuções
                future_to_execucao = {}
                for execucao in execucoes:
                    if execucao.status == ExecucaoStatus.PENDENTE:
                        future = executor.submit(
                            self._executar_item,
                            execucao,
                            config
                        )
                        future_to_execucao[future] = execucao
                
                # Processar resultados
                for future in as_completed(future_to_execucao, timeout=config.timeout_por_execucao * len(execucoes)):
                    execucao = future_to_execucao[future]
                    try:
                        resultado = future.result(timeout=config.timeout_por_execucao)
                        self._processar_resultado_execucao(execucao, resultado)
                    except Exception as e:
                        self._processar_erro_execucao(execucao, str(e))
                    
                    # Atualizar progresso
                    self._atualizar_progresso_lote(lote_info)
            
            # Finalizar lote
            self._finalizar_lote(lote_info)
            
        except Exception as e:
            logger.error(f"Erro no processamento do lote {lote_id}: {str(e)}")
            lote_info['status'] = LoteStatus.FALHOU
            lote_info['resultado'] = {'erro': str(e)}
            
            if self.on_error:
                self.on_error(e)
    
    def _executar_item(self, execucao: ExecucaoItem, config: LoteConfig) -> Dict[str, Any]:
        """Executa um item individual"""
        try:
            execucao.status = ExecucaoStatus.EM_EXECUCAO
            execucao.tempo_inicio = datetime.now(timezone.utc)
            
            logger.info(f"Executando item: {execucao.id}")
            
            # Simular execução (em produção, chamar serviço real)
            resultado = self._simular_execucao(execucao)
            
            execucao.status = ExecucaoStatus.CONCLUIDA
            execucao.resultado = resultado
            execucao.tempo_fim = datetime.now(timezone.utc)
            
            logger.info(f"Item concluído: {execucao.id}")
            return resultado
            
        except Exception as e:
            execucao.tentativas += 1
            execucao.erro = str(e)
            
            if execucao.tentativas >= execucao.max_tentativas:
                execucao.status = ExecucaoStatus.FALHOU
                execucao.tempo_fim = datetime.now(timezone.utc)
                logger.error(f"Item falhou após {execucao.tentativas} tentativas: {execucao.id}")
            else:
                execucao.status = ExecucaoStatus.PENDENTE
                logger.warning(f"Tentativa {execucao.tentativas} falhou para item: {execucao.id}")
            
            raise e
    
    def _simular_execucao(self, execucao: ExecucaoItem) -> Dict[str, Any]:
        """Simula execução (substituir por execução real)"""
        # Simular tempo de processamento
        time.sleep(2)
        
        # Simular resultado
        return {
            'palavras_chave_processadas': len(execucao.palavras_chave),
            'resultados_encontrados': len(execucao.palavras_chave) * 10,
            'tempo_processamento': 2.0,
            'cluster_usado': execucao.cluster or 'default',
            'status': 'sucesso'
        }
    
    def _processar_resultado_execucao(self, execucao: ExecucaoItem, resultado: Dict[str, Any]):
        """Processa resultado de execução bem-sucedida"""
        execucao.resultado = resultado
        
        # Atualizar estatísticas
        self.stats['execucoes_processadas'] += 1
        
        # Callback
        if self.on_execucao_complete:
            self.on_execucao_complete(execucao, resultado)
    
    def _processar_erro_execucao(self, execucao: ExecucaoItem, erro: str):
        """Processa erro de execução"""
        execucao.erro = erro
        
        # Callback
        if self.on_error:
            self.on_error(Exception(f"Erro na execução {execucao.id}: {erro}"))
    
    def _atualizar_progresso_lote(self, lote_info: Dict[str, Any]):
        """Atualiza progresso do lote"""
        execucoes = lote_info['execucoes']
        total = len(execucoes)
        concluidas = sum(1 for e in execucoes if e.status == ExecucaoStatus.CONCLUIDA)
        falharam = sum(1 for e in execucoes if e.status == ExecucaoStatus.FALHOU)
        
        progresso = (concluidas + falharam) / total * 100
        lote_info['progresso'] = progresso
    
    def _finalizar_lote(self, lote_info: Dict[str, Any]):
        """Finaliza processamento do lote"""
        lote_id = lote_info['id']
        execucoes = lote_info['execucoes']
        
        # Calcular estatísticas
        total = len(execucoes)
        concluidas = sum(1 for e in execucoes if e.status == ExecucaoStatus.CONCLUIDA)
        falharam = sum(1 for e in execucoes if e.status == ExecucaoStatus.FALHOU)
        canceladas = sum(1 for e in execucoes if e.status == ExecucaoStatus.CANCELADA)
        
        tempo_total = 0
        if lote_info['inicio_processamento'] and lote_info['fim_processamento']:
            tempo_total = (lote_info['fim_processamento'] - lote_info['inicio_processamento']).total_seconds()
        
        tempo_medio = tempo_total / total if total > 0 else 0
        taxa_sucesso = concluidas / total if total > 0 else 0
        
        # Criar resultado
        resultado = LoteResultado(
            lote_id=lote_id,
            total_execucoes=total,
            execucoes_concluidas=concluidas,
            execucoes_falharam=falharam,
            execucoes_canceladas=canceladas,
            tempo_total=tempo_total,
            tempo_medio_por_execucao=tempo_medio,
            taxa_sucesso=taxa_sucesso,
            detalhes={
                'execucoes_detalhadas': [
                    {
                        'id': e.id,
                        'status': e.status.value,
                        'resultado': e.resultado,
                        'erro': e.erro,
                        'tempo_processamento': (e.tempo_fim - e.tempo_inicio).total_seconds() if e.tempo_fim and e.tempo_inicio else None
                    }
                    for e in execucoes
                ]
            }
        )
        
        # Atualizar lote
        lote_info['status'] = LoteStatus.CONCLUIDO if taxa_sucesso > 0.5 else LoteStatus.FALHOU
        lote_info['fim_processamento'] = datetime.now(timezone.utc)
        lote_info['resultado'] = asdict(resultado)
        
        # Atualizar estatísticas globais
        self.stats['lotes_processados'] += 1
        self.stats['tempo_total_processamento'] += tempo_total
        self.stats['taxa_sucesso_geral'] = (
            (self.stats['taxa_sucesso_geral'] * (self.stats['lotes_processados'] - 1) + taxa_sucesso) /
            self.stats['lotes_processados']
        )
        
        logger.info(f"Lote finalizado: {lote_id} - Taxa de sucesso: {taxa_sucesso:.2%}")
        
        # Callback
        if self.on_lote_complete:
            self.on_lote_complete(lote_info, resultado)
    
    def obter_status_lote(self, lote_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status de um lote"""
        if lote_id not in self.lotes_ativos:
            return None
        
        lote_info = self.lotes_ativos[lote_id]
        
        # Calcular estatísticas atuais
        execucoes = lote_info['execucoes']
        total = len(execucoes)
        concluidas = sum(1 for e in execucoes if e.status == ExecucaoStatus.CONCLUIDA)
        falharam = sum(1 for e in execucoes if e.status == ExecucaoStatus.FALHOU)
        em_execucao = sum(1 for e in execucoes if e.status == ExecucaoStatus.EM_EXECUCAO)
        pendentes = sum(1 for e in execucoes if e.status == ExecucaoStatus.PENDENTE)
        
        return {
            'lote_id': lote_id,
            'status': lote_info['status'].value,
            'progresso': lote_info['progresso'],
            'total_execucoes': total,
            'execucoes_concluidas': concluidas,
            'execucoes_falharam': falharam,
            'execucoes_em_execucao': em_execucao,
            'execucoes_pendentes': pendentes,
            'taxa_sucesso': concluidas / total if total > 0 else 0,
            'criado_em': lote_info['criado_em'].isoformat(),
            'inicio_processamento': lote_info['inicio_processamento'].isoformat() if lote_info['inicio_processamento'] else None,
            'fim_processamento': lote_info['fim_processamento'].isoformat() if lote_info['fim_processamento'] else None,
            'resultado': lote_info['resultado']
        }
    
    def cancelar_lote(self, lote_id: str) -> bool:
        """Cancela um lote em execução"""
        if lote_id not in self.lotes_ativos:
            return False
        
        lote_info = self.lotes_ativos[lote_id]
        
        if lote_info['status'] not in [LoteStatus.PENDENTE, LoteStatus.EM_EXECUCAO]:
            return False
        
        # Cancelar execuções pendentes
        for execucao in lote_info['execucoes']:
            if execucao.status in [ExecucaoStatus.PENDENTE, ExecucaoStatus.EM_EXECUCAO]:
                execucao.status = ExecucaoStatus.CANCELADA
        
        lote_info['status'] = LoteStatus.CANCELADO
        lote_info['fim_processamento'] = datetime.now(timezone.utc)
        
        logger.info(f"Lote cancelado: {lote_id}")
        return True
    
    def pausar_lote(self, lote_id: str) -> bool:
        """Pausa um lote em execução"""
        if lote_id not in self.lotes_ativos:
            return False
        
        lote_info = self.lotes_ativos[lote_id]
        
        if lote_info['status'] != LoteStatus.EM_EXECUCAO:
            return False
        
        lote_info['status'] = LoteStatus.PAUSADO
        logger.info(f"Lote pausado: {lote_id}")
        return True
    
    def retomar_lote(self, lote_id: str) -> bool:
        """Retoma um lote pausado"""
        if lote_id not in self.lotes_ativos:
            return False
        
        lote_info = self.lotes_ativos[lote_id]
        
        if lote_info['status'] != LoteStatus.PAUSADO:
            return False
        
        lote_info['status'] = LoteStatus.EM_EXECUCAO
        logger.info(f"Lote retomado: {lote_id}")
        return True
    
    def listar_lotes(self, user_id: Optional[str] = None, status: Optional[LoteStatus] = None) -> List[Dict[str, Any]]:
        """Lista lotes ativos"""
        lotes = []
        
        for lote_info in self.lotes_ativos.values():
            # Filtrar por usuário
            if user_id and lote_info['user_id'] != user_id:
                continue
            
            # Filtrar por status
            if status and lote_info['status'] != status:
                continue
            
            lotes.append(self.obter_status_lote(lote_info['id']))
        
        # Ordenar por data de criação (mais recente primeiro)
        lotes.sort(key=lambda x: x['criado_em'], reverse=True)
        return lotes
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do serviço"""
        return {
            'lotes_ativos': len(self.lotes_ativos),
            'lotes_processados': self.stats['lotes_processados'],
            'execucoes_processadas': self.stats['execucoes_processadas'],
            'tempo_total_processamento': self.stats['tempo_total_processamento'],
            'taxa_sucesso_geral': self.stats['taxa_sucesso_geral'],
            'status_por_lote': {
                status.value: sum(1 for l in self.lotes_ativos.values() if l['status'] == status)
                for status in LoteStatus
            }
        }
    
    def limpar_lotes_antigos(self, dias: int = 7):
        """Remove lotes antigos da memória"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=dias)
        lotes_para_remover = []
        
        for lote_id, lote_info in self.lotes_ativos.items():
            if lote_info['criado_em'] < cutoff_date:
                lotes_para_remover.append(lote_id)
        
        for lote_id in lotes_para_remover:
            del self.lotes_ativos[lote_id]
        
        logger.info(f"Removidos {len(lotes_para_remover)} lotes antigos")

# Instância global
lote_service = None

def init_lote_service(config: Dict[str, Any] = None):
    """Inicializa serviço de lote global"""
    global lote_service
    lote_service = LoteExecucaoService(config)
    return lote_service

def get_lote_service() -> LoteExecucaoService:
    """Obtém instância do serviço de lote"""
    return lote_service 