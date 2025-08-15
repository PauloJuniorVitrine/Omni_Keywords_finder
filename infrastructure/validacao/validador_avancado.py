"""
Validador Avançado - Orquestrador de Validadores Especializados
Coordena múltiplos validadores para validação robusta de keywords

Prompt: Google Keyword Planner como Validador
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-20
Versão: 1.0.0
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_validator import ValidadorEspecializado
from .google_keyword_planner_validator import GoogleKeywordPlannerValidator
from domain.models import Keyword
from shared.logger import logger
from shared.config import get_config

class ValidadorAvancado:
    """
    Orquestrador de validadores especializados.
    
    Funcionalidades:
    - Execução paralela de validadores
    - Priorização inteligente
    - Consolidação de resultados
    - Fallback automático
    - Métricas agregadas
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa validador avançado.
        
        Args:
            config: Configurações dos validadores
        """
        self.config = config
        self.validadores: List[ValidadorEspecializado] = []
        self.execution_stats = {
            "total_executions": 0,
            "total_keywords_processed": 0,
            "total_keywords_approved": 0,
            "total_execution_time": 0.0,
            "validator_stats": {}
        }
        
        # Inicializar validadores
        self._inicializar_validadores()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "validador_avancado_inicializado",
            "status": "success",
            "source": "ValidadorAvancado.__init__",
            "details": {
                "total_validadores": len(self.validadores),
                "validadores_ativos": len([value for value in self.validadores if value.is_enabled()])
            }
        })
    
    def _inicializar_validadores(self):
        """Inicializa todos os validadores configurados."""
        # Google Keyword Planner Validator
        if self.config.get("google_keyword_planner", {}).get("enabled", True):
            google_config = self.config.get("google_keyword_planner", {})
            google_validator = GoogleKeywordPlannerValidator(google_config)
            self.validadores.append(google_validator)
        
        # Ordenar por prioridade (menor número = maior prioridade)
        self.validadores.sort(key=lambda value: value.get_prioridade())
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "validadores_inicializados",
            "status": "info",
            "source": "ValidadorAvancado._inicializar_validadores",
            "details": {
                "validadores": [value.get_nome() for value in self.validadores],
                "prioridades": [value.get_prioridade() for value in self.validadores]
            }
        })
    
    def validar_keywords(self, keywords: List[Keyword], estrategia: str = "cascata") -> List[Keyword]:
        """
        Valida keywords usando estratégia configurada.
        
        Args:
            keywords: Lista de keywords a validar
            estrategia: Estratégia de validação ("cascata", "paralela", "consenso")
            
        Returns:
            Lista de keywords aprovadas
        """
        start_time = time.time()
        keywords_iniciais = len(keywords)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_validacao_avancada",
            "status": "info",
            "source": "ValidadorAvancado.validar_keywords",
            "details": {
                "total_keywords": keywords_iniciais,
                "estrategia": estrategia,
                "validadores_ativos": len([value for value in self.validadores if value.is_enabled()])
            }
        })
        
        # Aplicar estratégia de validação
        if estrategia == "cascata":
            keywords_aprovadas = self._validacao_cascata(keywords)
        elif estrategia == "paralela":
            keywords_aprovadas = self._validacao_paralela(keywords)
        elif estrategia == "consenso":
            keywords_aprovadas = self._validacao_consenso(keywords)
        else:
            raise ValueError(f"Estratégia '{estrategia}' não suportada")
        
        # Atualizar estatísticas
        tempo_execucao = time.time() - start_time
        self._atualizar_estatisticas(keywords_iniciais, len(keywords_aprovadas), tempo_execucao)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "validacao_avancada_concluida",
            "status": "success",
            "source": "ValidadorAvancado.validar_keywords",
            "details": {
                "keywords_iniciais": keywords_iniciais,
                "keywords_aprovadas": len(keywords_aprovadas),
                "taxa_aprovacao": len(keywords_aprovadas) / keywords_iniciais if keywords_iniciais > 0 else 0.0,
                "tempo_execucao": tempo_execucao,
                "estrategia": estrategia
            }
        })
        
        return keywords_aprovadas
    
    def _validacao_cascata(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Validação em cascata: cada validador filtra o resultado do anterior.
        
        Args:
            keywords: Lista de keywords
            
        Returns:
            Keywords aprovadas por todos os validadores
        """
        keywords_atual = keywords.copy()
        
        for validador in self.validadores:
            if not validador.is_enabled():
                continue
                
            try:
                logger.info({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "executando_validador_cascata",
                    "status": "info",
                    "source": "ValidadorAvancado._validacao_cascata",
                    "details": {
                        "validador": validador.get_nome(),
                        "keywords_entrada": len(keywords_atual)
                    }
                })
                
                keywords_atual = validador.validar_keywords(keywords_atual)
                
                logger.info({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "validador_cascata_concluido",
                    "status": "success",
                    "source": "ValidadorAvancado._validacao_cascata",
                    "details": {
                        "validador": validador.get_nome(),
                        "keywords_saida": len(keywords_atual),
                        "rejeitadas": len(keywords) - len(keywords_atual)
                    }
                })
                
            except Exception as e:
                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "erro_validador_cascata",
                    "status": "error",
                    "source": "ValidadorAvancado._validacao_cascata",
                    "details": {
                        "validador": validador.get_nome(),
                        "erro": str(e)
                    }
                })
                # Em cascata, se um validador falha, para a cadeia
                break
        
        return keywords_atual
    
    def _validacao_paralela(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Validação paralela: todos os validadores executam simultaneamente.
        
        Args:
            keywords: Lista de keywords
            
        Returns:
            Keywords aprovadas por pelo menos um validador
        """
        resultados_validadores = {}
        
        # Executar validadores em paralelo
        with ThreadPoolExecutor(max_workers=len(self.validadores)) as executor:
            futures = {}
            
            for validador in self.validadores:
                if not validador.is_enabled():
                    continue
                    
                future = executor.submit(validador.validar_keywords, keywords.copy())
                futures[future] = validador.get_nome()
            
            # Coletar resultados
            for future in as_completed(futures):
                validador_nome = futures[future]
                try:
                    resultado = future.result()
                    resultados_validadores[validador_nome] = resultado
                    
                    logger.info({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "validador_paralelo_concluido",
                        "status": "success",
                        "source": "ValidadorAvancado._validacao_paralela",
                        "details": {
                            "validador": validador_nome,
                            "keywords_aprovadas": len(resultado)
                        }
                    })
                    
                except Exception as e:
                    logger.error({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_validador_paralelo",
                        "status": "error",
                        "source": "ValidadorAvancado._validacao_paralela",
                        "details": {
                            "validador": validador_nome,
                            "erro": str(e)
                        }
                    })
                    resultados_validadores[validador_nome] = []
        
        # Consolidar resultados (união de todos os aprovados)
        keywords_aprovadas = set()
        for resultado in resultados_validadores.values():
            keywords_aprovadas.update([kw.termo for kw in resultado])
        
        # Converter de volta para lista de Keywords
        keywords_finais = []
        for keyword in keywords:
            if keyword.termo in keywords_aprovadas:
                keywords_finais.append(keyword)
        
        return keywords_finais
    
    def _validacao_consenso(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Validação por consenso: keyword deve ser aprovada pela maioria dos validadores.
        
        Args:
            keywords: Lista de keywords
            
        Returns:
            Keywords aprovadas por consenso
        """
        validadores_ativos = [value for value in self.validadores if value.is_enabled()]
        if not validadores_ativos:
            return keywords
        
        # Contar aprovações por keyword
        contagem_aprovacoes = {}
        
        for validador in validadores_ativos:
            try:
                resultado = validador.validar_keywords(keywords.copy())
                
                for keyword in resultado:
                    if keyword.termo not in contagem_aprovacoes:
                        contagem_aprovacoes[keyword.termo] = 0
                    contagem_aprovacoes[keyword.termo] += 1
                    
            except Exception as e:
                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "erro_validador_consenso",
                    "status": "error",
                    "source": "ValidadorAvancado._validacao_consenso",
                    "details": {
                        "validador": validador.get_nome(),
                        "erro": str(e)
                    }
                })
        
        # Determinar consenso (maioria simples)
        threshold_consenso = len(validadores_ativos) / 2
        keywords_consenso = []
        
        for keyword in keywords:
            aprovacoes = contagem_aprovacoes.get(keyword.termo, 0)
            if aprovacoes >= threshold_consenso:
                keywords_consenso.append(keyword)
        
        return keywords_consenso
    
    def _atualizar_estatisticas(self, keywords_iniciais: int, keywords_finais: int, tempo_execucao: float):
        """
        Atualiza estatísticas de execução.
        
        Args:
            keywords_iniciais: Número de keywords antes da validação
            keywords_finais: Número de keywords após validação
            tempo_execucao: Tempo de execução em segundos
        """
        self.execution_stats["total_executions"] += 1
        self.execution_stats["total_keywords_processed"] += keywords_iniciais
        self.execution_stats["total_keywords_approved"] += keywords_finais
        self.execution_stats["total_execution_time"] += tempo_execucao
        
        # Atualizar estatísticas por validador
        for validador in self.validadores:
            validador_stats = validador.get_estatisticas()
            self.execution_stats["validator_stats"][validador.get_nome()] = validador_stats
    
    def get_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas completas do validador avançado.
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            "validador_avancado": {
                "total_executions": self.execution_stats["total_executions"],
                "total_keywords_processed": self.execution_stats["total_keywords_processed"],
                "total_keywords_approved": self.execution_stats["total_keywords_approved"],
                "total_execution_time": self.execution_stats["total_execution_time"],
                "avg_execution_time": (
                    self.execution_stats["total_execution_time"] / self.execution_stats["total_executions"]
                    if self.execution_stats["total_executions"] > 0 else 0.0
                ),
                "overall_approval_rate": (
                    self.execution_stats["total_keywords_approved"] / self.execution_stats["total_keywords_processed"]
                    if self.execution_stats["total_keywords_processed"] > 0 else 0.0
                )
            },
            "validadores": self.execution_stats["validator_stats"]
        }
    
    def reset_estatisticas(self):
        """Reseta todas as estatísticas."""
        self.execution_stats = {
            "total_executions": 0,
            "total_keywords_processed": 0,
            "total_keywords_approved": 0,
            "total_execution_time": 0.0,
            "validator_stats": {}
        }
        
        for validador in self.validadores:
            validador.reset_estatisticas()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "estatisticas_resetadas",
            "status": "info",
            "source": "ValidadorAvancado.reset_estatisticas"
        }) 