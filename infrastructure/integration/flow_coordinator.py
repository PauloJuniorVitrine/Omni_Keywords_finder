"""
Flow Coordinator - Omni Keywords Finder

Coordenador que orquestra o fluxo completo usando o Integration Bridge,
substituindo a simulação por execução real.

Tracing ID: FLOW_COORDINATOR_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTAÇÃO CRÍTICA
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import uuid

from shared.logger import logger
from .integration_bridge import IntegrationBridge, IntegrationResult

@dataclass
class FlowStep:
    """Etapa do fluxo de processamento."""
    name: str
    status: str  # "pending", "running", "completed", "failed"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class FlowResult:
    """Resultado completo do fluxo."""
    flow_id: str
    termo: str
    nicho: str
    success: bool
    steps: Dict[str, FlowStep]
    total_time: float
    keywords_coletadas: int
    keywords_processadas: int
    arquivos_gerados: int
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class FlowCoordinator:
    """
    Coordenador que orquestra o fluxo completo usando Integration Bridge.
    
    Responsabilidades:
    - Executar fluxo completo: coleta → processamento → exportação
    - Gerenciar estado das etapas
    - Implementar retry e fallback
    - Fornecer métricas de execução
    """
    
    def __init__(self):
        """Inicializa o coordenador de fluxo."""
        self.tracing_id = f"FLOW_{uuid.uuid4().hex[:8]}"
        self.bridge = IntegrationBridge()
        self.current_flow: Optional[FlowResult] = None
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "flow_coordinator_initialized",
            "status": "info",
            "source": "FlowCoordinator.__init__",
            "tracing_id": self.tracing_id
        })
    
    def execute_complete_flow(self, termo: str, nicho: str, **kwargs) -> FlowResult:
        """
        Executa fluxo completo usando Integration Bridge.
        
        Args:
            termo: Termo para busca
            nicho: Nicho específico
            **kwargs: Parâmetros adicionais
            
        Returns:
            FlowResult com resultado completo do fluxo
        """
        flow_start = time.time()
        flow_id = f"flow_{uuid.uuid4().hex[:8]}"
        
        # Inicializar resultado do fluxo
        self.current_flow = FlowResult(
            flow_id=flow_id,
            termo=termo,
            nicho=nicho,
            success=False,
            steps={},
            total_time=0.0,
            keywords_coletadas=0,
            keywords_processadas=0,
            arquivos_gerados=0,
            metadata=kwargs
        )
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "complete_flow_started",
            "status": "info",
            "source": "FlowCoordinator.execute_complete_flow",
            "tracing_id": self.tracing_id,
            "details": {
                "flow_id": flow_id,
                "termo": termo,
                "nicho": nicho
            }
        })
        
        try:
            # Verificar se bridge está pronto
            if not self.bridge.is_ready():
                raise RuntimeError("Integration Bridge não está pronto")
            
            # 1. ETAPA: COLETA
            coleta_step = self._execute_coleta_step(termo, nicho, **kwargs)
            self.current_flow.steps["coleta"] = coleta_step
            
            if coleta_step.status == "failed":
                self.current_flow.error = f"Falha na coleta: {coleta_step.error}"
                return self._finalize_flow(flow_start)
            
            # 2. ETAPA: PROCESSAMENTO
            processamento_step = self._execute_processamento_step(
                coleta_step.result, nicho, **kwargs
            )
            self.current_flow.steps["processamento"] = processamento_step
            
            if processamento_step.status == "failed":
                self.current_flow.error = f"Falha no processamento: {processamento_step.error}"
                return self._finalize_flow(flow_start)
            
            # 3. ETAPA: EXPORTAÇÃO
            exportacao_step = self._execute_exportacao_step(
                processamento_step.result["keywords"], nicho, **kwargs
            )
            self.current_flow.steps["exportacao"] = exportacao_step
            
            if exportacao_step.status == "failed":
                self.current_flow.error = f"Falha na exportação: {exportacao_step.error}"
                return self._finalize_flow(flow_start)
            
            # Fluxo concluído com sucesso
            self.current_flow.success = True
            self.current_flow.keywords_coletadas = len(coleta_step.result)
            self.current_flow.keywords_processadas = len(processamento_step.result["keywords"])
            self.current_flow.arquivos_gerados = len(exportacao_step.result.get("arquivos", {}))
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "complete_flow_success",
                "status": "success",
                "source": "FlowCoordinator.execute_complete_flow",
                "tracing_id": self.tracing_id,
                "details": {
                    "flow_id": flow_id,
                    "termo": termo,
                    "nicho": nicho,
                    "keywords_coletadas": self.current_flow.keywords_coletadas,
                    "keywords_processadas": self.current_flow.keywords_processadas,
                    "arquivos_gerados": self.current_flow.arquivos_gerados
                }
            })
            
            return self._finalize_flow(flow_start)
            
        except Exception as e:
            self.current_flow.error = str(e)
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "complete_flow_error",
                "status": "error",
                "source": "FlowCoordinator.execute_complete_flow",
                "tracing_id": self.tracing_id,
                "details": {
                    "flow_id": flow_id,
                    "termo": termo,
                    "nicho": nicho,
                    "error": str(e)
                }
            })
            
            return self._finalize_flow(flow_start)
    
    def _execute_coleta_step(self, termo: str, nicho: str, **kwargs) -> FlowStep:
        """Executa etapa de coleta."""
        step = FlowStep(name="coleta", status="running", start_time=time.time())
        
        try:
            logger.info(f"Executando etapa de coleta para termo: {termo}, nicho: {nicho}")
            
            resultado = self.bridge.execute_coleta(
                termo=termo,
                nicho=nicho,
                limite=kwargs.get("limite", 100)
            )
            
            if resultado.success:
                step.status = "completed"
                step.result = resultado.data
                step.end_time = time.time()
                
                logger.info(f"Coleta concluída: {len(resultado.data)} keywords coletadas")
            else:
                step.status = "failed"
                step.error = resultado.error
                step.end_time = time.time()
                
                logger.error(f"Falha na coleta: {resultado.error}")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.end_time = time.time()
            
            logger.error(f"Erro na etapa de coleta: {str(e)}")
        
        return step
    
    def _execute_processamento_step(self, keywords: List, nicho: str, **kwargs) -> FlowStep:
        """Executa etapa de processamento."""
        step = FlowStep(name="processamento", status="running", start_time=time.time())
        
        try:
            logger.info(f"Executando etapa de processamento para nicho: {nicho}")
            
            resultado = self.bridge.execute_processamento(
                keywords=keywords,
                nicho=nicho,
                idioma=kwargs.get("idioma", "pt")
            )
            
            if resultado.success:
                step.status = "completed"
                step.result = resultado.data
                step.end_time = time.time()
                
                logger.info(f"Processamento concluído: {len(resultado.data['keywords'])} keywords processadas")
            else:
                step.status = "failed"
                step.error = resultado.error
                step.end_time = time.time()
                
                logger.error(f"Falha no processamento: {resultado.error}")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.end_time = time.time()
            
            logger.error(f"Erro na etapa de processamento: {str(e)}")
        
        return step
    
    def _execute_exportacao_step(self, keywords: List, nicho: str, **kwargs) -> FlowStep:
        """Executa etapa de exportação."""
        step = FlowStep(name="exportacao", status="running", start_time=time.time())
        
        try:
            logger.info(f"Executando etapa de exportação para nicho: {nicho}")
            
            resultado = self.bridge.execute_exportacao(
                keywords=keywords,
                nicho=nicho,
                client=kwargs.get("client", "default"),
                category=kwargs.get("category", "main"),
                formatos=kwargs.get("formatos", ["csv", "json"]),
                export_xlsx=kwargs.get("export_xlsx", False)
            )
            
            if resultado.success:
                step.status = "completed"
                step.result = resultado.data
                step.end_time = time.time()
                
                logger.info(f"Exportação concluída: {len(resultado.data.get('arquivos', {}))} arquivos gerados")
            else:
                step.status = "failed"
                step.error = resultado.error
                step.end_time = time.time()
                
                logger.error(f"Falha na exportação: {resultado.error}")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.end_time = time.time()
            
            logger.error(f"Erro na etapa de exportação: {str(e)}")
        
        return step
    
    def _finalize_flow(self, flow_start: float) -> FlowResult:
        """Finaliza o fluxo calculando tempo total."""
        if self.current_flow:
            self.current_flow.total_time = time.time() - flow_start
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "flow_finalized",
                "status": "info",
                "source": "FlowCoordinator._finalize_flow",
                "tracing_id": self.tracing_id,
                "details": {
                    "flow_id": self.current_flow.flow_id,
                    "success": self.current_flow.success,
                    "total_time": self.current_flow.total_time,
                    "error": self.current_flow.error
                }
            })
        
        return self.current_flow
    
    def get_flow_status(self) -> Optional[Dict[str, Any]]:
        """Retorna status do fluxo atual."""
        if not self.current_flow:
            return None
        
        return {
            "flow_id": self.current_flow.flow_id,
            "termo": self.current_flow.termo,
            "nicho": self.current_flow.nicho,
            "success": self.current_flow.success,
            "total_time": self.current_flow.total_time,
            "steps_status": {
                name: {
                    "status": step.status,
                    "duration": step.end_time - step.start_time if step.end_time and step.start_time else 0
                }
                for name, step in self.current_flow.steps.items()
            },
            "error": self.current_flow.error,
            "tracing_id": self.tracing_id
        }
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """Retorna status do Integration Bridge."""
        return self.bridge.get_module_status()
    
    def reset_flow(self):
        """Reseta o fluxo atual."""
        self.current_flow = None
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "flow_reset",
            "status": "info",
            "source": "FlowCoordinator.reset_flow",
            "tracing_id": self.tracing_id
        })
