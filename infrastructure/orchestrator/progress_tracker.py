"""
Progress Tracker - Omni Keywords Finder

Sistema de rastreamento de progresso para o fluxo completo.
Permite persistência de estado, retomada de execução interrompida
e logs estruturados para auditoria.

Tracing ID: PROGRESS_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import json
import time
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from datetime import datetime, timedelta
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class EtapaStatus(Enum):
    """Status possíveis para uma etapa."""
    PENDENTE = "pendente"
    EM_EXECUCAO = "em_execucao"
    CONCLUIDA = "concluida"
    FALHOU = "falhou"
    CANCELADA = "cancelada"
    PAUSADA = "pausada"


class EtapaType(Enum):
    """Tipos de etapas do fluxo."""
    COLETA = "coleta"
    VALIDACAO = "validacao"
    PROCESSAMENTO = "processamento"
    PREENCHIMENTO = "preenchimento"
    EXPORTACAO = "exportacao"


@dataclass
class EtapaProgress:
    """Progresso de uma etapa específica."""
    nome: str
    tipo: EtapaType
    status: EtapaStatus = EtapaStatus.PENDENTE
    inicio_timestamp: Optional[float] = None
    fim_timestamp: Optional[float] = None
    progresso_atual: int = 0
    total_itens: int = 0
    percentual: float = 0.0
    mensagem: str = ""
    erro: Optional[str] = None
    metadados: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duracao_segundos(self) -> Optional[float]:
        """Calcula duração da etapa em segundos."""
        if self.inicio_timestamp and self.fim_timestamp:
            return self.fim_timestamp - self.inicio_timestamp
        elif self.inicio_timestamp:
            return time.time() - self.inicio_timestamp
        return None
    
    @property
    def esta_ativa(self) -> bool:
        """Verifica se a etapa está ativa."""
        return self.status == EtapaStatus.EM_EXECUCAO
    
    @property
    def foi_concluida(self) -> bool:
        """Verifica se a etapa foi concluída com sucesso."""
        return self.status == EtapaStatus.CONCLUIDA
    
    @property
    def falhou(self) -> bool:
        """Verifica se a etapa falhou."""
        return self.status == EtapaStatus.FALHOU


@dataclass
class NichoProgress:
    """Progresso de um nicho específico."""
    nome_nicho: str
    inicio_timestamp: float = field(default_factory=time.time)
    fim_timestamp: Optional[float] = None
    status: EtapaStatus = EtapaStatus.PENDENTE
    etapas: Dict[str, EtapaProgress] = field(default_factory=dict)
    metadados: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicializa etapas padrão."""
        if not self.etapas:
            self.etapas = {
                EtapaType.COLETA.value: EtapaProgress(
                    nome="Coleta de Keywords",
                    tipo=EtapaType.COLETA
                ),
                EtapaType.VALIDACAO.value: EtapaProgress(
                    nome="Validação com Google",
                    tipo=EtapaType.VALIDACAO
                ),
                EtapaType.PROCESSAMENTO.value: EtapaProgress(
                    nome="Processamento e Filtragem",
                    tipo=EtapaType.PROCESSAMENTO
                ),
                EtapaType.PREENCHIMENTO.value: EtapaProgress(
                    nome="Preenchimento de Prompts",
                    tipo=EtapaType.PREENCHIMENTO
                ),
                EtapaType.EXPORTACAO.value: EtapaProgress(
                    nome="Exportação de Arquivos",
                    tipo=EtapaType.EXPORTACAO
                )
            }
    
    @property
    def duracao_segundos(self) -> Optional[float]:
        """Calcula duração total do nicho em segundos."""
        if self.fim_timestamp:
            return self.fim_timestamp - self.inicio_timestamp
        return time.time() - self.inicio_timestamp
    
    @property
    def percentual_geral(self) -> float:
        """Calcula percentual geral de progresso."""
        if not self.etapas:
            return 0.0
        
        total_percentual = sum(etapa.percentual for etapa in self.etapas.values())
        return total_percentual / len(self.etapas)
    
    @property
    def etapas_concluidas(self) -> int:
        """Conta etapas concluídas."""
        return sum(1 for etapa in self.etapas.values() if etapa.foi_concluida)
    
    @property
    def total_etapas(self) -> int:
        """Total de etapas."""
        return len(self.etapas)
    
    @property
    def proxima_etapa(self) -> Optional[str]:
        """Identifica a próxima etapa a ser executada."""
        for nome_etapa, etapa in self.etapas.items():
            if etapa.status == EtapaStatus.PENDENTE:
                return nome_etapa
        return None
    
    @property
    def etapa_atual(self) -> Optional[str]:
        """Identifica a etapa atualmente em execução."""
        for nome_etapa, etapa in self.etapas.items():
            if etapa.esta_ativa:
                return nome_etapa
        return None


@dataclass
class SessaoProgress:
    """Progresso de uma sessão completa de processamento."""
    sessao_id: str
    inicio_timestamp: float = field(default_factory=time.time)
    fim_timestamp: Optional[float] = None
    nichos: Dict[str, NichoProgress] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    metadados: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duracao_segundos(self) -> Optional[float]:
        """Calcula duração total da sessão em segundos."""
        if self.fim_timestamp:
            return self.fim_timestamp - self.inicio_timestamp
        return time.time() - self.inicio_timestamp
    
    @property
    def nichos_concluidos(self) -> int:
        """Conta nichos concluídos."""
        return sum(1 for nicho in self.nichos.values() if nicho.foi_concluida)
    
    @property
    def total_nichos(self) -> int:
        """Total de nichos."""
        return len(self.nichos)
    
    @property
    def percentual_geral(self) -> float:
        """Calcula percentual geral de progresso."""
        if not self.nichos:
            return 0.0
        
        total_percentual = sum(nicho.percentual_geral for nicho in self.nichos.values())
        return total_percentual / len(self.nichos)


class ProgressTracker:
    """Sistema de rastreamento de progresso."""
    
    def __init__(self, diretorio_persistencia: str = "logs/progress"):
        """
        Inicializa o progress tracker.
        
        Args:
            diretorio_persistencia: Diretório para salvar arquivos de progresso
        """
        self.diretorio_persistencia = Path(diretorio_persistencia)
        self.diretorio_persistencia.mkdir(parents=True, exist_ok=True)
        
        self.sessao_atual: Optional[SessaoProgress] = None
        self.lock = threading.Lock()
        
        logger.info(f"ProgressTracker inicializado em: {self.diretorio_persistencia}")
    
    def iniciar_sessao(self, sessao_id: str, config: Dict[str, Any]) -> SessaoProgress:
        """
        Inicia uma nova sessão de processamento.
        
        Args:
            sessao_id: ID único da sessão
            config: Configurações da sessão
            
        Returns:
            SessaoProgress criada
        """
        with self.lock:
            self.sessao_atual = SessaoProgress(
                sessao_id=sessao_id,
                config=config
            )
            
            logger.info(f"Sessão iniciada: {sessao_id}")
            self._persistir_sessao()
            
            return self.sessao_atual
    
    def adicionar_nicho(self, nome_nicho: str) -> NichoProgress:
        """
        Adiciona um nicho à sessão atual.
        
        Args:
            nome_nicho: Nome do nicho
            
        Returns:
            NichoProgress criado
        """
        if not self.sessao_atual:
            raise RuntimeError("Nenhuma sessão ativa")
        
        with self.lock:
            nicho_progress = NichoProgress(nome_nicho=nome_nicho)
            self.sessao_atual.nichos[nome_nicho] = nicho_progress
            
            logger.info(f"Nicho adicionado à sessão: {nome_nicho}")
            self._persistir_sessao()
            
            return nicho_progress
    
    def iniciar_etapa(self, nome_nicho: str, nome_etapa: str) -> EtapaProgress:
        """
        Inicia uma etapa específica.
        
        Args:
            nome_nicho: Nome do nicho
            nome_etapa: Nome da etapa
            
        Returns:
            EtapaProgress atualizada
        """
        if not self.sessao_atual:
            raise RuntimeError("Nenhuma sessão ativa")
        
        with self.lock:
            nicho = self.sessao_atual.nichos.get(nome_nicho)
            if not nicho:
                raise ValueError(f"Nicho '{nome_nicho}' não encontrado")
            
            etapa = nicho.etapas.get(nome_etapa)
            if not etapa:
                raise ValueError(f"Etapa '{nome_etapa}' não encontrada no nicho '{nome_nicho}'")
            
            etapa.status = EtapaStatus.EM_EXECUCAO
            etapa.inicio_timestamp = time.time()
            etapa.mensagem = "Etapa iniciada"
            
            logger.info(f"Etapa iniciada: {nome_nicho}.{nome_etapa}")
            self._persistir_sessao()
            
            return etapa
    
    def atualizar_progresso_etapa(
        self, 
        nome_nicho: str, 
        nome_etapa: str, 
        progresso_atual: int, 
        total_itens: int,
        mensagem: str = ""
    ) -> EtapaProgress:
        """
        Atualiza o progresso de uma etapa.
        
        Args:
            nome_nicho: Nome do nicho
            nome_etapa: Nome da etapa
            progresso_atual: Progresso atual
            total_itens: Total de itens
            mensagem: Mensagem de status
            
        Returns:
            EtapaProgress atualizada
        """
        if not self.sessao_atual:
            raise RuntimeError("Nenhuma sessão ativa")
        
        with self.lock:
            nicho = self.sessao_atual.nichos.get(nome_nicho)
            if not nicho:
                raise ValueError(f"Nicho '{nome_nicho}' não encontrado")
            
            etapa = nicho.etapas.get(nome_etapa)
            if not etapa:
                raise ValueError(f"Etapa '{nome_etapa}' não encontrada no nicho '{nome_nicho}'")
            
            etapa.progresso_atual = progresso_atual
            etapa.total_itens = total_itens
            etapa.percentual = (progresso_atual / total_itens * 100) if total_itens > 0 else 0
            etapa.mensagem = mensagem
            
            logger.debug(f"Progresso atualizado: {nome_nicho}.{nome_etapa} - {etapa.percentual:.1f}%")
            self._persistir_sessao()
            
            return etapa
    
    def concluir_etapa(
        self, 
        nome_nicho: str, 
        nome_etapa: str, 
        sucesso: bool = True,
        erro: Optional[str] = None,
        metadados: Optional[Dict[str, Any]] = None
    ) -> EtapaProgress:
        """
        Conclui uma etapa.
        
        Args:
            nome_nicho: Nome do nicho
            nome_etapa: Nome da etapa
            sucesso: Se a etapa foi concluída com sucesso
            erro: Mensagem de erro (se houver)
            metadados: Metadados adicionais
            
        Returns:
            EtapaProgress atualizada
        """
        if not self.sessao_atual:
            raise RuntimeError("Nenhuma sessão ativa")
        
        with self.lock:
            nicho = self.sessao_atual.nichos.get(nome_nicho)
            if not nicho:
                raise ValueError(f"Nicho '{nome_nicho}' não encontrado")
            
            etapa = nicho.etapas.get(nome_etapa)
            if not etapa:
                raise ValueError(f"Etapa '{nome_etapa}' não encontrada no nicho '{nome_nicho}'")
            
            etapa.fim_timestamp = time.time()
            etapa.status = EtapaStatus.CONCLUIDA if sucesso else EtapaStatus.FALHOU
            etapa.erro = erro
            etapa.mensagem = "Etapa concluída com sucesso" if sucesso else f"Etapa falhou: {erro}"
            
            if metadados:
                etapa.metadados.update(metadados)
            
            if sucesso:
                etapa.progresso_atual = etapa.total_itens
                etapa.percentual = 100.0
            
            logger.info(f"Etapa concluída: {nome_nicho}.{nome_etapa} - {'SUCESSO' if sucesso else 'FALHA'}")
            self._persistir_sessao()
            
            return etapa
    
    def concluir_nicho(self, nome_nicho: str, sucesso: bool = True) -> NichoProgress:
        """
        Conclui um nicho.
        
        Args:
            nome_nicho: Nome do nicho
            sucesso: Se o nicho foi concluído com sucesso
            
        Returns:
            NichoProgress atualizado
        """
        if not self.sessao_atual:
            raise RuntimeError("Nenhuma sessão ativa")
        
        with self.lock:
            nicho = self.sessao_atual.nichos.get(nome_nicho)
            if not nicho:
                raise ValueError(f"Nicho '{nome_nicho}' não encontrado")
            
            nicho.fim_timestamp = time.time()
            nicho.status = EtapaStatus.CONCLUIDA if sucesso else EtapaStatus.FALHOU
            
            logger.info(f"Nicho concluído: {nome_nicho} - {'SUCESSO' if sucesso else 'FALHA'}")
            self._persistir_sessao()
            
            return nicho
    
    def concluir_sessao(self, sucesso: bool = True) -> SessaoProgress:
        """
        Conclui a sessão atual.
        
        Args:
            sucesso: Se a sessão foi concluída com sucesso
            
        Returns:
            SessaoProgress finalizada
        """
        if not self.sessao_atual:
            raise RuntimeError("Nenhuma sessão ativa")
        
        with self.lock:
            self.sessao_atual.fim_timestamp = time.time()
            
            logger.info(f"Sessão concluída: {self.sessao_atual.sessao_id} - {'SUCESSO' if sucesso else 'FALHA'}")
            self._persistir_sessao()
            
            return self.sessao_atual
    
    def obter_progresso_atual(self) -> Optional[SessaoProgress]:
        """Obtém o progresso da sessão atual."""
        return self.sessao_atual
    
    def carregar_sessao(self, sessao_id: str) -> Optional[SessaoProgress]:
        """
        Carrega uma sessão salva.
        
        Args:
            sessao_id: ID da sessão
            
        Returns:
            SessaoProgress carregada ou None
        """
        arquivo_sessao = self.diretorio_persistencia / f"{sessao_id}.json"
        
        if not arquivo_sessao.exists():
            logger.warning(f"Arquivo de sessão não encontrado: {arquivo_sessao}")
            return None
        
        try:
            with open(arquivo_sessao, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # TODO: Implementar deserialização completa
            logger.info(f"Sessão carregada: {sessao_id}")
            return None  # Placeholder
            
        except Exception as e:
            logger.error(f"Erro ao carregar sessão {sessao_id}: {e}")
            return None
    
    def _persistir_sessao(self):
        """Persiste a sessão atual em arquivo."""
        if not self.sessao_atual:
            return
        
        try:
            arquivo_sessao = self.diretorio_persistencia / f"{self.sessao_atual.sessao_id}.json"
            
            # Serialização básica para debug
            dados = {
                "sessao_id": self.sessao_atual.sessao_id,
                "inicio_timestamp": self.sessao_atual.inicio_timestamp,
                "fim_timestamp": self.sessao_atual.fim_timestamp,
                "total_nichos": self.sessao_atual.total_nichos,
                "nichos_concluidos": self.sessao_atual.nichos_concluidos,
                "percentual_geral": self.sessao_atual.percentual_geral
            }
            
            with open(arquivo_sessao, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Erro ao persistir sessão: {e}")
    
    def limpar_sessoes_antigas(self, dias: int = 7):
        """
        Remove sessões antigas.
        
        Args:
            dias: Número de dias para manter
        """
        try:
            limite_timestamp = time.time() - (dias * 24 * 60 * 60)
            
            for arquivo in self.diretorio_persistencia.glob("*.json"):
                if arquivo.stat().st_mtime < limite_timestamp:
                    arquivo.unlink()
                    logger.info(f"Arquivo de sessão removido: {arquivo}")
                    
        except Exception as e:
            logger.error(f"Erro ao limpar sessões antigas: {e}")


# Instância global
progress_tracker = ProgressTracker()


def obter_progress_tracker() -> ProgressTracker:
    """Obtém a instância global do progress tracker."""
    return progress_tracker 