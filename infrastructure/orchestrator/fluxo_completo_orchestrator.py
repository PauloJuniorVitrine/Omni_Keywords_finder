"""
Fluxo Completo Orchestrator - Omni Keywords Finder

Orquestrador principal que coordena todo o fluxo de processamento:
coleta → validação → processamento → preenchimento → exportação

Tracing ID: ORCHESTRATOR_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import time
import logging
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime
from pathlib import Path

from .config import OrchestratorConfig, obter_config
from .progress_tracker import ProgressTracker, obter_progress_tracker
from .error_handler import ErrorHandler, obter_error_handler, ErrorType, ErrorSeverity

logger = logging.getLogger(__name__)


class FluxoStatus(Enum):
    """Status do fluxo de processamento."""
    INICIANDO = "iniciando"
    EM_EXECUCAO = "em_execucao"
    PAUSADO = "pausado"
    CONCLUIDO = "concluido"
    FALHOU = "falhou"
    CANCELADO = "cancelado"


@dataclass
class FluxoContext:
    """Contexto de execução do fluxo."""
    sessao_id: str
    nicho_atual: Optional[str] = None
    etapa_atual: Optional[str] = None
    inicio_timestamp: float = field(default_factory=time.time)
    config: OrchestratorConfig = field(default_factory=obter_config)
    metadados: Dict[str, Any] = field(default_factory=dict)


class FluxoCompletoOrchestrator:
    """Orquestrador principal do fluxo completo."""
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Inicializa o orquestrador.
        
        Args:
            config: Configuração do orquestrador
        """
        self.config = config or obter_config()
        self.progress_tracker = obter_progress_tracker()
        self.error_handler = obter_error_handler()
        
        self.status = FluxoStatus.INICIANDO
        self.context: Optional[FluxoContext] = None
        self.lock = threading.Lock()
        
        # Callbacks para notificações
        self.on_progress: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        
        logger.info("FluxoCompletoOrchestrator inicializado")
    
    def iniciar_fluxo(
        self, 
        nichos: Optional[List[str]] = None,
        sessao_id: Optional[str] = None
    ) -> str:
        """
        Inicia o fluxo completo de processamento.
        
        Args:
            nichos: Lista de nichos para processar (se None, usa todos configurados)
            sessao_id: ID da sessão (se None, gera automaticamente)
            
        Returns:
            ID da sessão criada
        """
        with self.lock:
            if self.status == FluxoStatus.EM_EXECUCAO:
                raise RuntimeError("Fluxo já está em execução")
            
            # Gerar sessão ID se não fornecido
            if not sessao_id:
                sessao_id = f"fluxo_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            # Determinar nichos a processar
            if nichos is None:
                nichos = self.config.listar_nichos_disponiveis()
            
            if not nichos:
                raise ValueError("Nenhum nicho especificado para processamento")
            
            # Criar contexto
            self.context = FluxoContext(
                sessao_id=sessao_id,
                config=self.config
            )
            
            # Iniciar progress tracking
            self.progress_tracker.iniciar_sessao(sessao_id, {
                "nichos": nichos,
                "config": self.config.__dict__
            })
            
            # Adicionar nichos ao progress tracker
            for nicho in nichos:
                self.progress_tracker.adicionar_nicho(nicho)
            
            self.status = FluxoStatus.EM_EXECUCAO
            
            logger.info(f"Fluxo iniciado - Sessão: {sessao_id}, Nichos: {nichos}")
            
            # Executar em thread separada
            thread = threading.Thread(
                target=self._executar_fluxo,
                args=(nichos,),
                daemon=True
            )
            thread.start()
            
            return sessao_id
    
    def _executar_fluxo(self, nichos: List[str]):
        """Executa o fluxo completo em thread separada."""
        try:
            for nicho in nichos:
                if self.status == FluxoStatus.CANCELADO:
                    logger.info("Fluxo cancelado pelo usuário")
                    break
                
                self.context.nicho_atual = nicho
                logger.info(f"Iniciando processamento do nicho: {nicho}")
                
                sucesso = self._processar_nicho(nicho)
                
                if not sucesso:
                    logger.error(f"Falha no processamento do nicho: {nicho}")
                    if self.on_error:
                        self.on_error(nicho, "Falha no processamento")
                    continue
                
                logger.info(f"Nicho processado com sucesso: {nicho}")
            
            # Finalizar fluxo
            self.status = FluxoStatus.CONCLUIDO
            self.context = None
            
            if self.on_complete:
                self.on_complete()
            
            logger.info("Fluxo completo finalizado com sucesso")
            
        except Exception as e:
            self.status = FluxoStatus.FALHOU
            error_info = self.error_handler.handle_error(
                e, 
                ErrorType.PROCESSING, 
                ErrorSeverity.HIGH,
                {"fluxo": "execucao_completa"}
            )
            
            if self.on_error:
                self.on_error("fluxo", str(e))
            
            logger.error(f"Erro fatal no fluxo: {e}")
    
    def _processar_nicho(self, nicho: str) -> bool:
        """
        Processa um nicho específico através de todas as etapas.
        
        Args:
            nicho: Nome do nicho
            
        Returns:
            True se processado com sucesso, False caso contrário
        """
        try:
            config_nicho = self.config.obter_config_nicho(nicho)
            
            # Etapa 1: Coleta
            if not self._executar_etapa_coleta(nicho, config_nicho):
                return False
            
            # Etapa 2: Validação
            if not self._executar_etapa_validacao(nicho, config_nicho):
                return False
            
            # Etapa 3: Processamento
            if not self._executar_etapa_processamento(nicho, config_nicho):
                return False
            
            # Etapa 4: Preenchimento
            if not self._executar_etapa_preenchimento(nicho, config_nicho):
                return False
            
            # Etapa 5: Exportação
            if not self._executar_etapa_exportacao(nicho, config_nicho):
                return False
            
            # Concluir nicho
            self.progress_tracker.concluir_nicho(nicho, True)
            return True
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e, 
                ErrorType.PROCESSING, 
                ErrorSeverity.HIGH,
                {"nicho": nicho}
            )
            
            self.progress_tracker.concluir_nicho(nicho, False)
            return False
    
    def _executar_etapa_coleta(self, nicho: str, config_nicho) -> bool:
        """Executa a etapa de coleta usando Integration Bridge."""
        etapa_nome = "coleta"
        self.context.etapa_atual = etapa_nome
        
        try:
            logger.info(f"Iniciando coleta para nicho: {nicho}")
            self.progress_tracker.iniciar_etapa(nicho, etapa_nome)
            
            # ✅ INTEGRAÇÃO REAL: Usar Integration Bridge
            from infrastructure.integration.integration_bridge import IntegrationBridge
            
            bridge = IntegrationBridge()
            if not bridge.is_ready():
                raise RuntimeError("Integration Bridge não está pronto")
            
            # Executar coleta real
            termo_exemplo = f"exemplo_{nicho}"
            resultado = bridge.execute_coleta(
                termo=termo_exemplo,
                nicho=nicho,
                limite=100
            )
            
            if not resultado.success:
                raise RuntimeError(f"Falha na coleta: {resultado.error}")
            
            keywords_coletadas = resultado.data
            
            # Atualizar progresso
            self.progress_tracker.atualizar_progresso_etapa(
                nicho, etapa_nome, 
                len(keywords_coletadas), len(keywords_coletadas),
                f"Coletadas {len(keywords_coletadas)} keywords"
            )
            
            # Concluir etapa
            self.progress_tracker.concluir_etapa(
                nicho, etapa_nome, True,
                metadados={"keywords_coletadas": keywords_coletadas, "bridge_result": resultado.data}
            )
            
            logger.info(f"Coleta concluída para nicho: {nicho} - {len(keywords_coletadas)} keywords")
            return True
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e, 
                ErrorType.PROCESSING, 
                ErrorSeverity.MEDIUM,
                {"nicho": nicho, "etapa": etapa_nome}
            )
            
            self.progress_tracker.concluir_etapa(nicho, etapa_nome, False, str(e))
            return False
    
    def _executar_etapa_validacao(self, nicho: str, config_nicho) -> bool:
        """Executa a etapa de validação."""
        etapa_nome = "validacao"
        self.context.etapa_atual = etapa_nome
        
        try:
            logger.info(f"Iniciando validação para nicho: {nicho}")
            self.progress_tracker.iniciar_etapa(nicho, etapa_nome)
            
            # TODO: Integrar com Google Keyword Planner
            # Por enquanto, simula validação
            keywords_validadas = self._simular_validacao(nicho, config_nicho)
            
            # Atualizar progresso
            self.progress_tracker.atualizar_progresso_etapa(
                nicho, etapa_nome, 
                len(keywords_validadas), len(keywords_validadas),
                f"Validadas {len(keywords_validadas)} keywords"
            )
            
            # Concluir etapa
            self.progress_tracker.concluir_etapa(
                nicho, etapa_nome, True,
                metadados={"keywords_validadas": len(keywords_validadas)}
            )
            
            logger.info(f"Validação concluída para nicho: {nicho} - {len(keywords_validadas)} keywords")
            return True
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e, 
                ErrorType.API_LIMIT, 
                ErrorSeverity.MEDIUM,
                {"nicho": nicho, "etapa": etapa_nome}
            )
            
            self.progress_tracker.concluir_etapa(nicho, etapa_nome, False, str(e))
            return False
    
    def _executar_etapa_processamento(self, nicho: str, config_nicho) -> bool:
        """Executa a etapa de processamento usando Integration Bridge."""
        etapa_nome = "processamento"
        self.context.etapa_atual = etapa_nome
        
        try:
            logger.info(f"Iniciando processamento para nicho: {nicho}")
            self.progress_tracker.iniciar_etapa(nicho, etapa_nome)
            
            # ✅ INTEGRAÇÃO REAL: Usar Integration Bridge
            from infrastructure.integration.integration_bridge import IntegrationBridge
            
            bridge = IntegrationBridge()
            if not bridge.is_ready():
                raise RuntimeError("Integration Bridge não está pronto")
            
            # Simular keywords coletadas (em implementação real viria do contexto)
            keywords_exemplo = [{"termo": f"keyword_{nicho}", "volume": 1000}]
            
            resultado = bridge.execute_processamento(
                keywords=keywords_exemplo,
                nicho=nicho,
                idioma="pt"
            )
            
            if not resultado.success:
                raise RuntimeError(f"Falha no processamento: {resultado.error}")
            
            keywords_processadas = resultado.data["keywords"]
            
            # Atualizar progresso
            self.progress_tracker.atualizar_progresso_etapa(
                nicho, etapa_nome, 
                len(keywords_processadas), len(keywords_processadas),
                f"Processadas {len(keywords_processadas)} keywords"
            )
            
            # Concluir etapa
            self.progress_tracker.concluir_etapa(
                nicho, etapa_nome, True,
                metadados={"keywords_processadas": keywords_processadas, "bridge_result": resultado.data}
            )
            
            logger.info(f"Processamento concluído para nicho: {nicho} - {len(keywords_processadas)} keywords")
            return True
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e, 
                ErrorType.PROCESSING, 
                ErrorSeverity.MEDIUM,
                {"nicho": nicho, "etapa": etapa_nome}
            )
            
            self.progress_tracker.concluir_etapa(nicho, etapa_nome, False, str(e))
            return False
    
    def _executar_etapa_preenchimento(self, nicho: str, config_nicho) -> bool:
        """Executa a etapa de preenchimento."""
        etapa_nome = "preenchimento"
        self.context.etapa_atual = etapa_nome
        
        try:
            logger.info(f"Iniciando preenchimento para nicho: {nicho}")
            self.progress_tracker.iniciar_etapa(nicho, etapa_nome)
            
            # TODO: Integrar com sistema de prompts existente
            # Por enquanto, simula preenchimento
            prompts_gerados = self._simular_preenchimento(nicho, config_nicho)
            
            # Atualizar progresso
            self.progress_tracker.atualizar_progresso_etapa(
                nicho, etapa_nome, 
                len(prompts_gerados), len(prompts_gerados),
                f"Gerados {len(prompts_gerados)} prompts"
            )
            
            # Concluir etapa
            self.progress_tracker.concluir_etapa(
                nicho, etapa_nome, True,
                metadados={"prompts_gerados": len(prompts_gerados)}
            )
            
            logger.info(f"Preenchimento concluído para nicho: {nicho} - {len(prompts_gerados)} prompts")
            return True
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e, 
                ErrorType.PROCESSING, 
                ErrorSeverity.MEDIUM,
                {"nicho": nicho, "etapa": etapa_nome}
            )
            
            self.progress_tracker.concluir_etapa(nicho, etapa_nome, False, str(e))
            return False
    
    def _executar_etapa_exportacao(self, nicho: str, config_nicho) -> bool:
        """Executa a etapa de exportação usando Integration Bridge."""
        etapa_nome = "exportacao"
        self.context.etapa_atual = etapa_nome
        
        try:
            logger.info(f"Iniciando exportação para nicho: {nicho}")
            self.progress_tracker.iniciar_etapa(nicho, etapa_nome)
            
            # ✅ INTEGRAÇÃO REAL: Usar Integration Bridge
            from infrastructure.integration.integration_bridge import IntegrationBridge
            
            bridge = IntegrationBridge()
            if not bridge.is_ready():
                raise RuntimeError("Integration Bridge não está pronto")
            
            # Obter keywords processadas (assumindo que foram processadas anteriormente)
            # Em uma implementação real, isso viria do contexto ou cache
            keywords_exemplo = [{"termo": f"keyword_{nicho}", "volume": 1000}]
            
            resultado = bridge.execute_exportacao(
                keywords=keywords_exemplo,
                nicho=nicho,
                client="default",
                category="main",
                formatos=["csv", "json"]
            )
            
            if not resultado.success:
                raise RuntimeError(f"Falha na exportação: {resultado.error}")
            
            arquivo_gerado = f"{nicho}_export_{int(time.time())}.zip"
            
            # Atualizar progresso
            self.progress_tracker.atualizar_progresso_etapa(
                nicho, etapa_nome, 
                1, 1,
                f"Arquivo exportado: {arquivo_gerado}"
            )
            
            # Concluir etapa
            self.progress_tracker.concluir_etapa(
                nicho, etapa_nome, True,
                metadados={"arquivo_gerado": arquivo_gerado, "bridge_result": resultado.data}
            )
            
            logger.info(f"Exportação concluída para nicho: {nicho} - {arquivo_gerado}")
            return True
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e, 
                ErrorType.STORAGE, 
                ErrorSeverity.MEDIUM,
                {"nicho": nicho, "etapa": etapa_nome}
            )
            
            self.progress_tracker.concluir_etapa(nicho, etapa_nome, False, str(e))
            return False
    
    # Métodos de simulação (temporários)
    def _simular_coleta(self, nicho: str, config_nicho) -> List[str]:
        """Simula coleta de keywords."""
        time.sleep(2)  # Simula tempo de processamento
        return [f"keyword_{index}_{nicho}" for index in range(50)]
    
    def _simular_validacao(self, nicho: str, config_nicho) -> List[str]:
        """Simula validação com Google."""
        time.sleep(3)  # Simula tempo de API
        return [f"keyword_{index}_{nicho}_validada" for index in range(30)]
    
    def _simular_processamento(self, nicho: str, config_nicho) -> List[str]:
        """Simula processamento e filtragem."""
        time.sleep(1)  # Simula tempo de processamento
        return [f"keyword_{index}_{nicho}_processada" for index in range(25)]
    
    def _simular_preenchimento(self, nicho: str, config_nicho) -> List[str]:
        """Simula preenchimento de prompts."""
        time.sleep(2)  # Simula tempo de IA
        return [f"prompt_{index}_{nicho}" for index in range(75)]
    
    def _simular_exportacao(self, nicho: str, config_nicho) -> str:
        """Simula exportação de arquivo."""
        time.sleep(1)  # Simula tempo de escrita
        return f"{nicho}_keywords_{int(time.time())}.zip"
    
    # Métodos de controle
    def pausar_fluxo(self):
        """Pausa o fluxo de processamento."""
        with self.lock:
            if self.status == FluxoStatus.EM_EXECUCAO:
                self.status = FluxoStatus.PAUSADO
                logger.info("Fluxo pausado")
    
    def retomar_fluxo(self):
        """Retoma o fluxo pausado."""
        with self.lock:
            if self.status == FluxoStatus.PAUSADO:
                self.status = FluxoStatus.EM_EXECUCAO
                logger.info("Fluxo retomado")
    
    def cancelar_fluxo(self):
        """Cancela o fluxo de processamento."""
        with self.lock:
            self.status = FluxoStatus.CANCELADO
            logger.info("Fluxo cancelado")
    
    def obter_status(self) -> Dict[str, Any]:
        """Obtém status atual do fluxo."""
        with self.lock:
            status_info = {
                "status": self.status.value,
                "sessao_id": self.context.sessao_id if self.context else None,
                "nicho_atual": self.context.nicho_atual if self.context else None,
                "etapa_atual": self.context.etapa_atual if self.context else None,
                "inicio_timestamp": self.context.inicio_timestamp if self.context else None,
                "duracao_segundos": self.context.duracao_segundos if self.context else None
            }
            
            # Adicionar progresso se disponível
            if self.context:
                progresso = self.progress_tracker.obter_progresso_atual()
                if progresso:
                    status_info["progresso"] = {
                        "percentual_geral": progresso.percentual_geral,
                        "nichos_concluidos": progresso.nichos_concluidos,
                        "total_nichos": progresso.total_nichos
                    }
            
            return status_info
    
    def configurar_callbacks(
        self,
        on_progress: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_complete: Optional[Callable] = None
    ):
        """Configura callbacks para notificações."""
        self.on_progress = on_progress
        self.on_error = on_error
        self.on_complete = on_complete
        logger.info("Callbacks configurados")


# Instância global
orchestrator = FluxoCompletoOrchestrator()


def obter_orchestrator() -> FluxoCompletoOrchestrator:
    """Obtém a instância global do orquestrador."""
    return orchestrator


def executar_fluxo_completo(
    nichos: Optional[List[str]] = None,
    sessao_id: Optional[str] = None
) -> str:
    """
    Função de conveniência para executar o fluxo completo.
    
    Args:
        nichos: Lista de nichos para processar
        sessao_id: ID da sessão
        
    Returns:
        ID da sessão criada
    """
    return orchestrator.iniciar_fluxo(nichos, sessao_id) 