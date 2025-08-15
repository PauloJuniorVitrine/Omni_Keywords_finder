"""
Integration Bridge - Omni Keywords Finder

Bridge Pattern que conecta módulos funcionais existentes ao orquestrador,
resolvendo problemas de integração identificados.

Tracing ID: INTEGRATION_BRIDGE_001_20250127
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTAÇÃO CRÍTICA
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid

from shared.logger import logger

@dataclass
class IntegrationResult:
    """Resultado da integração entre módulos."""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None

class IntegrationBridge:
    """
    Bridge que conecta módulos funcionais ao orquestrador.
    
    Responsabilidades:
    - Conectar módulos de coleta, processamento e exportação
    - Gerenciar dependências entre módulos
    - Tratar erros de integração
    - Fornecer interface unificada
    """
    
    def __init__(self):
        """Inicializa o bridge de integração."""
        self.tracing_id = f"BRIDGE_{uuid.uuid4().hex[:8]}"
        self.modules_initialized = False
        self.coletor = None
        self.processador = None
        self.exportador = None
        
        # Métricas de integração
        self.metrics = {
            "total_integrations": 0,
            "successful_integrations": 0,
            "failed_integrations": 0,
            "last_error": None,
            "last_success": None
        }
        
        self._initialize_modules()
        self._log_initialization()
    
    def _initialize_modules(self):
        """Inicializa módulos funcionais existentes."""
        try:
            # Importar módulos de coleta
            from infrastructure.coleta.base import ColetorBase
            from infrastructure.coleta.google_keyword_planner import GoogleKeywordPlannerColetor
            from infrastructure.coleta.google_suggest import GoogleSuggestColetor
            from infrastructure.coleta.google_trends import GoogleTrendsColetor
            
            # Importar módulos de processamento
            from infrastructure.processamento.processador_orquestrador import ProcessadorOrquestrador
            from infrastructure.processamento.analisador_semantico import AnalisadorSemantico
            from infrastructure.processamento.calculador_scores_processor import CalculadorScoresProcessor
            
            # Importar módulos de exportação
            from infrastructure.processamento.exportador_keywords import ExportadorKeywords
            
            # Inicializar módulos
            self.coletor = {
                "base": ColetorBase,
                "google_planner": GoogleKeywordPlannerColetor,
                "google_suggest": GoogleSuggestColetor,
                "google_trends": GoogleTrendsColetor
            }
            
            self.processador = ProcessadorOrquestrador()
            self.exportador = ExportadorKeywords()
            
            self.modules_initialized = True
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "modules_initialized_successfully",
                "status": "success",
                "source": "IntegrationBridge._initialize_modules",
                "tracing_id": self.tracing_id,
                "details": {
                    "coletor_modules": len(self.coletor),
                    "processador_initialized": self.processador is not None,
                    "exportador_initialized": self.exportador is not None
                }
            })
            
        except ImportError as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "module_import_error",
                "status": "error",
                "source": "IntegrationBridge._initialize_modules",
                "tracing_id": self.tracing_id,
                "details": {"error": str(e)}
            })
            self.modules_initialized = False
    
    def _log_initialization(self):
        """Registra log de inicialização."""
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "integration_bridge_initialized",
            "status": "info",
            "source": "IntegrationBridge.__init__",
            "tracing_id": self.tracing_id,
            "details": {
                "modules_initialized": self.modules_initialized,
                "total_modules": len(self.coletor) if self.coletor else 0
            }
        })
    
    def is_ready(self) -> bool:
        """Verifica se o bridge está pronto para uso."""
        return self.modules_initialized and all([
            self.coletor is not None,
            self.processador is not None,
            self.exportador is not None
        ])
    
    def get_module_status(self) -> Dict[str, Any]:
        """Retorna status dos módulos integrados."""
        return {
            "bridge_ready": self.is_ready(),
            "modules_initialized": self.modules_initialized,
            "coletor_available": self.coletor is not None,
            "processador_available": self.processador is not None,
            "exportador_available": self.exportador is not None,
            "metrics": self.metrics.copy()
        }
    
    def execute_coleta(self, termo: str, nicho: str, **kwargs) -> IntegrationResult:
        """
        Executa coleta de keywords usando módulos funcionais.
        
        Args:
            termo: Termo para busca
            nicho: Nicho específico
            **kwargs: Parâmetros adicionais
            
        Returns:
            IntegrationResult com dados coletados
        """
        if not self.is_ready():
            return IntegrationResult(
                success=False,
                data=None,
                error="Bridge não está pronto",
                metadata={"tracing_id": self.tracing_id}
            )
        
        start_time = time.time()
        
        try:
            # Usar módulo de coleta funcional
            coletor_instance = self.coletor["google_suggest"](termo, nicho)
            keywords = coletor_instance.coletar_keywords(termo, limite=kwargs.get("limite", 100))
            
            execution_time = time.time() - start_time
            
            # Atualizar métricas
            self.metrics["total_integrations"] += 1
            self.metrics["successful_integrations"] += 1
            self.metrics["last_success"] = datetime.utcnow().isoformat()
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "coleta_executed_successfully",
                "status": "success",
                "source": "IntegrationBridge.execute_coleta",
                "tracing_id": self.tracing_id,
                "details": {
                    "termo": termo,
                    "nicho": nicho,
                    "keywords_coletadas": len(keywords),
                    "execution_time": execution_time
                }
            })
            
            return IntegrationResult(
                success=True,
                data=keywords,
                execution_time=execution_time,
                metadata={
                    "tracing_id": self.tracing_id,
                    "termo": termo,
                    "nicho": nicho,
                    "total_keywords": len(keywords)
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Atualizar métricas
            self.metrics["total_integrations"] += 1
            self.metrics["failed_integrations"] += 1
            self.metrics["last_error"] = str(e)
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "coleta_execution_error",
                "status": "error",
                "source": "IntegrationBridge.execute_coleta",
                "tracing_id": self.tracing_id,
                "details": {
                    "termo": termo,
                    "nicho": nicho,
                    "error": str(e),
                    "execution_time": execution_time
                }
            })
            
            return IntegrationResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                metadata={
                    "tracing_id": self.tracing_id,
                    "termo": termo,
                    "nicho": nicho
                }
            )
    
    def execute_processamento(self, keywords: List, nicho: str, **kwargs) -> IntegrationResult:
        """
        Executa processamento usando módulos funcionais.
        
        Args:
            keywords: Lista de keywords para processar
            nicho: Nicho específico
            **kwargs: Parâmetros adicionais
            
        Returns:
            IntegrationResult com dados processados
        """
        if not self.is_ready():
            return IntegrationResult(
                success=False,
                data=None,
                error="Bridge não está pronto",
                metadata={"tracing_id": self.tracing_id}
            )
        
        start_time = time.time()
        
        try:
            # Usar módulo de processamento funcional
            keywords_processadas, relatorio = self.processador.processar_keywords(
                keywords=keywords,
                nicho=nicho,
                idioma=kwargs.get("idioma", "pt")
            )
            
            execution_time = time.time() - start_time
            
            # Atualizar métricas
            self.metrics["total_integrations"] += 1
            self.metrics["successful_integrations"] += 1
            self.metrics["last_success"] = datetime.utcnow().isoformat()
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "processamento_executed_successfully",
                "status": "success",
                "source": "IntegrationBridge.execute_processamento",
                "tracing_id": self.tracing_id,
                "details": {
                    "nicho": nicho,
                    "keywords_inicial": len(keywords),
                    "keywords_final": len(keywords_processadas),
                    "execution_time": execution_time
                }
            })
            
            return IntegrationResult(
                success=True,
                data={"keywords": keywords_processadas, "relatorio": relatorio},
                execution_time=execution_time,
                metadata={
                    "tracing_id": self.tracing_id,
                    "nicho": nicho,
                    "keywords_inicial": len(keywords),
                    "keywords_final": len(keywords_processadas)
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Atualizar métricas
            self.metrics["total_integrations"] += 1
            self.metrics["failed_integrations"] += 1
            self.metrics["last_error"] = str(e)
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "processamento_execution_error",
                "status": "error",
                "source": "IntegrationBridge.execute_processamento",
                "tracing_id": self.tracing_id,
                "details": {
                    "nicho": nicho,
                    "error": str(e),
                    "execution_time": execution_time
                }
            })
            
            return IntegrationResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                metadata={
                    "tracing_id": self.tracing_id,
                    "nicho": nicho
                }
            )
    
    def execute_exportacao(self, keywords: List, nicho: str, **kwargs) -> IntegrationResult:
        """
        Executa exportação usando módulos funcionais.
        
        Args:
            keywords: Lista de keywords para exportar
            nicho: Nicho específico
            **kwargs: Parâmetros adicionais
            
        Returns:
            IntegrationResult com dados de exportação
        """
        if not self.is_ready():
            return IntegrationResult(
                success=False,
                data=None,
                error="Bridge não está pronto",
                metadata={"tracing_id": self.tracing_id}
            )
        
        start_time = time.time()
        
        try:
            # Usar módulo de exportação funcional
            resultado = self.exportador.exportar_keywords(
                keywords=keywords,
                client=kwargs.get("client", "default"),
                niche=nicho,
                category=kwargs.get("category", "main"),
                formatos=kwargs.get("formatos", ["csv", "json"]),
                export_xlsx=kwargs.get("export_xlsx", False)
            )
            
            execution_time = time.time() - start_time
            
            # Atualizar métricas
            self.metrics["total_integrations"] += 1
            self.metrics["successful_integrations"] += 1
            self.metrics["last_success"] = datetime.utcnow().isoformat()
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "exportacao_executed_successfully",
                "status": "success",
                "source": "IntegrationBridge.execute_exportacao",
                "tracing_id": self.tracing_id,
                "details": {
                    "nicho": nicho,
                    "keywords_exportadas": len(keywords),
                    "arquivos_gerados": len(resultado.get("arquivos", {})),
                    "execution_time": execution_time
                }
            })
            
            return IntegrationResult(
                success=True,
                data=resultado,
                execution_time=execution_time,
                metadata={
                    "tracing_id": self.tracing_id,
                    "nicho": nicho,
                    "keywords_exportadas": len(keywords),
                    "arquivos_gerados": len(resultado.get("arquivos", {}))
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Atualizar métricas
            self.metrics["total_integrations"] += 1
            self.metrics["failed_integrations"] += 1
            self.metrics["last_error"] = str(e)
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "exportacao_execution_error",
                "status": "error",
                "source": "IntegrationBridge.execute_exportacao",
                "tracing_id": self.tracing_id,
                "details": {
                    "nicho": nicho,
                    "error": str(e),
                    "execution_time": execution_time
                }
            })
            
            return IntegrationResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                metadata={
                    "tracing_id": self.tracing_id,
                    "nicho": nicho
                }
            )
    
    def execute_fluxo_completo(self, termo: str, nicho: str, **kwargs) -> Dict[str, Any]:
        """
        Executa fluxo completo: coleta → processamento → exportação.
        
        Args:
            termo: Termo para busca
            nicho: Nicho específico
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com resultados de todas as etapas
        """
        if not self.is_ready():
            return {
                "success": False,
                "error": "Bridge não está pronto",
                "tracing_id": self.tracing_id
            }
        
        fluxo_start = time.time()
        resultados = {
            "tracing_id": self.tracing_id,
            "termo": termo,
            "nicho": nicho,
            "etapas": {},
            "success": True,
            "error": None,
            "tempo_total": 0.0
        }
        
        try:
            # 1. Coleta
            logger.info(f"Iniciando fluxo completo para termo: {termo}, nicho: {nicho}")
            
            resultado_coleta = self.execute_coleta(termo, nicho, **kwargs)
            resultados["etapas"]["coleta"] = resultado_coleta.__dict__
            
            if not resultado_coleta.success:
                resultados["success"] = False
                resultados["error"] = f"Falha na coleta: {resultado_coleta.error}"
                return resultados
            
            # 2. Processamento
            keywords_coletadas = resultado_coleta.data
            resultado_processamento = self.execute_processamento(keywords_coletadas, nicho, **kwargs)
            resultados["etapas"]["processamento"] = resultado_processamento.__dict__
            
            if not resultado_processamento.success:
                resultados["success"] = False
                resultados["error"] = f"Falha no processamento: {resultado_processamento.error}"
                return resultados
            
            # 3. Exportação
            keywords_processadas = resultado_processamento.data["keywords"]
            resultado_exportacao = self.execute_exportacao(keywords_processadas, nicho, **kwargs)
            resultados["etapas"]["exportacao"] = resultado_exportacao.__dict__
            
            if not resultado_exportacao.success:
                resultados["success"] = False
                resultados["error"] = f"Falha na exportação: {resultado_exportacao.error}"
                return resultados
            
            # Calcular tempo total
            resultados["tempo_total"] = time.time() - fluxo_start
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "fluxo_completo_executed_successfully",
                "status": "success",
                "source": "IntegrationBridge.execute_fluxo_completo",
                "tracing_id": self.tracing_id,
                "details": {
                    "termo": termo,
                    "nicho": nicho,
                    "tempo_total": resultados["tempo_total"],
                    "keywords_coletadas": len(keywords_coletadas),
                    "keywords_processadas": len(keywords_processadas),
                    "arquivos_gerados": len(resultado_exportacao.data.get("arquivos", {}))
                }
            })
            
            return resultados
            
        except Exception as e:
            resultados["success"] = False
            resultados["error"] = str(e)
            resultados["tempo_total"] = time.time() - fluxo_start
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "fluxo_completo_execution_error",
                "status": "error",
                "source": "IntegrationBridge.execute_fluxo_completo",
                "tracing_id": self.tracing_id,
                "details": {
                    "termo": termo,
                    "nicho": nicho,
                    "error": str(e),
                    "tempo_total": resultados["tempo_total"]
                }
            })
            
            return resultados
