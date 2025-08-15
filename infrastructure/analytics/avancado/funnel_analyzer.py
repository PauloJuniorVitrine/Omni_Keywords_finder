"""
Sistema de Análise de Funnels de Conversão - Omni Keywords Finder
================================================================

Este módulo implementa análise de funnels de conversão com:
- Definição de funnels customizáveis
- Cálculo de taxas de conversão
- Análise de drop-off points
- Segmentação por usuários
- Relatórios automáticos

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: FUNNEL_001
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import logging
from enum import Enum

# Integração com analytics
from .real_time_analytics import RealTimeAnalytics, EventType, get_analytics

logger = logging.getLogger(__name__)


class FunnelStepType(Enum):
    """Tipos de passos em um funnel."""
    EVENT = "event"
    CONDITION = "condition"
    TIME_WINDOW = "time_window"
    USER_ACTION = "user_action"


@dataclass
class FunnelStep:
    """Definição de um passo em um funnel."""
    name: str
    step_type: FunnelStepType
    event_type: Optional[EventType] = None
    condition: Optional[Dict[str, Any]] = None
    time_window_minutes: Optional[int] = None
    description: Optional[str] = None
    order: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o passo para dicionário."""
        return {
            "name": self.name,
            "step_type": self.step_type.value,
            "event_type": self.event_type.value if self.event_type else None,
            "condition": self.condition,
            "time_window_minutes": self.time_window_minutes,
            "description": self.description,
            "order": self.order
        }


@dataclass
class FunnelDefinition:
    """Definição completa de um funnel."""
    name: str
    description: str
    steps: List[FunnelStep]
    time_window_hours: int = 24
    segment_by: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o funnel para dicionário."""
        return {
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "time_window_hours": self.time_window_hours,
            "segment_by": self.segment_by,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class FunnelResult:
    """Resultado da análise de um funnel."""
    funnel_name: str
    analysis_time: datetime
    time_window_start: datetime
    time_window_end: datetime
    total_users: int
    step_results: List[Dict[str, Any]]
    conversion_rates: List[float]
    drop_off_points: List[Dict[str, Any]]
    overall_conversion_rate: float
    segment_results: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado para dicionário."""
        return {
            "funnel_name": self.funnel_name,
            "analysis_time": self.analysis_time.isoformat(),
            "time_window_start": self.time_window_start.isoformat(),
            "time_window_end": self.time_window_end.isoformat(),
            "total_users": self.total_users,
            "step_results": self.step_results,
            "conversion_rates": self.conversion_rates,
            "drop_off_points": self.drop_off_points,
            "overall_conversion_rate": self.overall_conversion_rate,
            "segment_results": self.segment_results
        }


class FunnelAnalyzer:
    """
    Sistema de Análise de Funnels de Conversão.
    
    Características:
    - Definição de funnels customizáveis
    - Análise em tempo real
    - Segmentação por usuários
    - Relatórios automáticos
    - Integração com analytics
    """
    
    def __init__(self, analytics: Optional[RealTimeAnalytics] = None):
        """
        Inicializa o analisador de funnels.
        
        Args:
            analytics: Instância do sistema de analytics (opcional)
        """
        self.analytics = analytics or get_analytics()
        self.funnels: Dict[str, FunnelDefinition] = {}
        self.results_cache: Dict[str, FunnelResult] = {}
        self._lock = threading.RLock()
        
        # Configurações padrão
        self.default_time_window = 24  # horas
        self.cache_ttl = 3600  # 1 hora
        
        logger.info("[FUNNEL] Analisador de funnels inicializado")
    
    def create_funnel(self, funnel_def: FunnelDefinition) -> str:
        """
        Cria um novo funnel.
        
        Args:
            funnel_def: Definição do funnel
            
        Returns:
            ID do funnel criado
        """
        with self._lock:
            try:
                # Valida a definição
                self._validate_funnel_definition(funnel_def)
                
                # Gera ID único
                funnel_id = f"funnel_{int(time.time())}_{funnel_def.name.lower().replace(' ', '_')}"
                
                # Armazena o funnel
                self.funnels[funnel_id] = funnel_def
                
                logger.info(f"[FUNNEL] Funnel criado: {funnel_id} - {funnel_def.name}")
                return funnel_id
                
            except Exception as e:
                logger.error(f"[FUNNEL] Erro ao criar funnel: {e}")
                raise
    
    def get_funnel(self, funnel_id: str) -> Optional[FunnelDefinition]:
        """
        Retorna um funnel por ID.
        
        Args:
            funnel_id: ID do funnel
            
        Returns:
            Definição do funnel ou None
        """
        with self._lock:
            return self.funnels.get(funnel_id)
    
    def list_funnels(self) -> List[Dict[str, Any]]:
        """
        Lista todos os funnels disponíveis.
        
        Returns:
            Lista de funnels com metadados
        """
        with self._lock:
            return [
                {
                    "id": funnel_id,
                    "name": funnel.name,
                    "description": funnel.description,
                    "steps_count": len(funnel.steps),
                    "created_at": funnel.created_at.isoformat(),
                    "last_analysis": self._get_last_analysis_time(funnel_id)
                }
                for funnel_id, funnel in self.funnels.items()
            ]
    
    def analyze_funnel(self, 
                      funnel_id: str,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      force_refresh: bool = False) -> Optional[FunnelResult]:
        """
        Analisa um funnel específico.
        
        Args:
            funnel_id: ID do funnel
            start_time: Tempo inicial (opcional)
            end_time: Tempo final (opcional)
            force_refresh: Força recálculo mesmo com cache válido
            
        Returns:
            Resultado da análise ou None
        """
        with self._lock:
            try:
                # Verifica se o funnel existe
                funnel = self.funnels.get(funnel_id)
                if not funnel:
                    logger.error(f"[FUNNEL] Funnel não encontrado: {funnel_id}")
                    return None
                
                # Verifica cache
                if not force_refresh:
                    cached_result = self._get_cached_result(funnel_id, start_time, end_time)
                    if cached_result:
                        logger.info(f"[FUNNEL] Resultado em cache usado: {funnel_id}")
                        return cached_result
                
                # Define janela de tempo
                if not end_time:
                    end_time = datetime.now()
                if not start_time:
                    start_time = end_time - timedelta(hours=funnel.time_window_hours)
                
                # Executa análise
                result = self._execute_funnel_analysis(funnel, start_time, end_time)
                
                # Armazena em cache
                self._cache_result(funnel_id, result)
                
                logger.info(f"[FUNNEL] Análise concluída: {funnel_id} - {result.overall_conversion_rate:.2f}%")
                return result
                
            except Exception as e:
                logger.error(f"[FUNNEL] Erro na análise: {e}")
                return None
    
    def get_conversion_insights(self, funnel_id: str) -> Dict[str, Any]:
        """
        Gera insights de conversão para um funnel.
        
        Args:
            funnel_id: ID do funnel
            
        Returns:
            Insights de conversão
        """
        with self._lock:
            try:
                result = self.analyze_funnel(funnel_id)
                if not result:
                    return {"error": "Funnel não encontrado"}
                
                insights = {
                    "funnel_name": result.funnel_name,
                    "overall_conversion_rate": result.overall_conversion_rate,
                    "total_users": result.total_users,
                    "analysis_period": {
                        "start": result.time_window_start.isoformat(),
                        "end": result.time_window_end.isoformat()
                    },
                    "step_insights": [],
                    "recommendations": []
                }
                
                # Análise por passo
                for index, step_result in enumerate(result.step_results):
                    step_insight = {
                        "step_name": step_result["name"],
                        "users_reached": step_result["users_reached"],
                        "conversion_rate": result.conversion_rates[index] if index < len(result.conversion_rates) else 0,
                        "drop_off_count": step_result.get("drop_off_count", 0),
                        "drop_off_rate": step_result.get("drop_off_rate", 0)
                    }
                    insights["step_insights"].append(step_insight)
                
                # Recomendações
                insights["recommendations"] = self._generate_recommendations(result)
                
                return insights
                
            except Exception as e:
                logger.error(f"[FUNNEL] Erro ao gerar insights: {e}")
                return {"error": str(e)}
    
    def compare_funnels(self, funnel_ids: List[str], 
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Compara múltiplos funnels.
        
        Args:
            funnel_ids: Lista de IDs dos funnels
            start_time: Tempo inicial (opcional)
            end_time: Tempo final (opcional)
            
        Returns:
            Comparação entre funnels
        """
        with self._lock:
            try:
                comparison = {
                    "comparison_time": datetime.now().isoformat(),
                    "funnels": [],
                    "summary": {}
                }
                
                results = []
                for funnel_id in funnel_ids:
                    result = self.analyze_funnel(funnel_id, start_time, end_time)
                    if result:
                        results.append(result)
                        comparison["funnels"].append({
                            "id": funnel_id,
                            "name": result.funnel_name,
                            "overall_conversion_rate": result.overall_conversion_rate,
                            "total_users": result.total_users,
                            "steps_count": len(result.step_results)
                        })
                
                # Resumo da comparação
                if results:
                    conversion_rates = [r.overall_conversion_rate for r in results]
                    comparison["summary"] = {
                        "best_performing": max(results, key=lambda value: value.overall_conversion_rate).funnel_name,
                        "worst_performing": min(results, key=lambda value: value.overall_conversion_rate).funnel_name,
                        "avg_conversion_rate": sum(conversion_rates) / len(conversion_rates),
                        "conversion_rate_range": max(conversion_rates) - min(conversion_rates)
                    }
                
                return comparison
                
            except Exception as e:
                logger.error(f"[FUNNEL] Erro na comparação: {e}")
                return {"error": str(e)}
    
    def export_funnel_data(self, funnel_id: str,
                          format: str = "json") -> Union[str, Dict[str, Any]]:
        """
        Exporta dados de um funnel.
        
        Args:
            funnel_id: ID do funnel
            format: Formato de exportação (json, csv)
            
        Returns:
            Dados exportados
        """
        with self._lock:
            try:
                result = self.analyze_funnel(funnel_id)
                if not result:
                    return {"error": "Funnel não encontrado"}
                
                if format.lower() == "json":
                    return result.to_dict()
                elif format.lower() == "csv":
                    return self._export_to_csv(result)
                else:
                    return {"error": "Formato não suportado"}
                
            except Exception as e:
                logger.error(f"[FUNNEL] Erro na exportação: {e}")
                return {"error": str(e)}
    
    def _validate_funnel_definition(self, funnel_def: FunnelDefinition) -> None:
        """Valida a definição de um funnel."""
        if not funnel_def.name:
            raise ValueError("Nome do funnel é obrigatório")
        
        if not funnel_def.steps or len(funnel_def.steps) < 2:
            raise ValueError("Funnel deve ter pelo menos 2 passos")
        
        # Valida ordem dos passos
        step_orders = [step.order for step in funnel_def.steps]
        if len(set(step_orders)) != len(step_orders):
            raise ValueError("Ordem dos passos deve ser única")
        
        if sorted(step_orders) != step_orders:
            raise ValueError("Passos devem estar em ordem crescente")
    
    def _execute_funnel_analysis(self, 
                                funnel: FunnelDefinition,
                                start_time: datetime,
                                end_time: datetime) -> FunnelResult:
        """Executa a análise de um funnel."""
        try:
            # Obtém eventos do período
            events_data = self.analytics.export_data(start_time, end_time)
            events = events_data.get("events", [])
            
            # Agrupa eventos por usuário
            user_events = defaultdict(list)
            for event_data in events:
                user_id = event_data.get("user_id")
                if user_id:
                    user_events[user_id].append(event_data)
            
            # Analisa cada passo do funnel
            step_results = []
            conversion_rates = []
            drop_off_points = []
            
            users_at_step = set(user_events.keys())  # Usuários que chegaram ao passo
            previous_users_count = len(users_at_step)
            
            for step in sorted(funnel.steps, key=lambda value: value.order):
                step_result = self._analyze_funnel_step(
                    step, user_events, users_at_step, start_time, end_time
                )
                
                step_results.append(step_result)
                
                # Calcula conversão
                current_users_count = step_result["users_reached"]
                if previous_users_count > 0:
                    conversion_rate = (current_users_count / previous_users_count) * 100
                else:
                    conversion_rate = 0
                
                conversion_rates.append(conversion_rate)
                
                # Identifica drop-off
                drop_off_count = previous_users_count - current_users_count
                if drop_off_count > 0:
                    drop_off_points.append({
                        "step_name": step.name,
                        "step_order": step.order,
                        "users_lost": drop_off_count,
                        "drop_off_rate": (drop_off_count / previous_users_count) * 100
                    })
                
                previous_users_count = current_users_count
            
            # Taxa de conversão geral
            total_users = len(user_events)
            if total_users > 0:
                overall_conversion_rate = (step_results[-1]["users_reached"] / total_users) * 100
            else:
                overall_conversion_rate = 0
            
            # Segmentação (se aplicável)
            segment_results = None
            if funnel.segment_by:
                segment_results = self._analyze_segments(funnel, user_events, start_time, end_time)
            
            return FunnelResult(
                funnel_name=funnel.name,
                analysis_time=datetime.now(),
                time_window_start=start_time,
                time_window_end=end_time,
                total_users=total_users,
                step_results=step_results,
                conversion_rates=conversion_rates,
                drop_off_points=drop_off_points,
                overall_conversion_rate=overall_conversion_rate,
                segment_results=segment_results
            )
            
        except Exception as e:
            logger.error(f"[FUNNEL] Erro na execução da análise: {e}")
            raise
    
    def _analyze_funnel_step(self,
                            step: FunnelStep,
                            user_events: Dict[str, List[Dict[str, Any]]],
                            users_at_step: set,
                            start_time: datetime,
                            end_time: datetime) -> Dict[str, Any]:
        """Analisa um passo específico do funnel."""
        try:
            users_reached = 0
            step_events = []
            
            for user_id, events in user_events.items():
                if user_id not in users_at_step:
                    continue
                
                # Verifica se o usuário completou o passo
                if self._user_completed_step(step, events, start_time, end_time):
                    users_reached += 1
                    step_events.extend(events)
            
            # Calcula drop-off
            drop_off_count = len(users_at_step) - users_reached
            drop_off_rate = 0
            if len(users_at_step) > 0:
                drop_off_rate = (drop_off_count / len(users_at_step)) * 100
            
            return {
                "name": step.name,
                "step_type": step.step_type.value,
                "users_reached": users_reached,
                "drop_off_count": drop_off_count,
                "drop_off_rate": drop_off_rate,
                "events_count": len(step_events),
                "description": step.description
            }
            
        except Exception as e:
            logger.error(f"[FUNNEL] Erro na análise do passo {step.name}: {e}")
            return {
                "name": step.name,
                "users_reached": 0,
                "drop_off_count": 0,
                "drop_off_rate": 0,
                "events_count": 0,
                "error": str(e)
            }
    
    def _user_completed_step(self,
                            step: FunnelStep,
                            user_events: List[Dict[str, Any]],
                            start_time: datetime,
                            end_time: datetime) -> bool:
        """Verifica se um usuário completou um passo específico."""
        try:
            if step.step_type == FunnelStepType.EVENT:
                # Verifica se o evento ocorreu
                for event in user_events:
                    if (event.get("event_type") == step.event_type.value and
                        start_time <= datetime.fromisoformat(event["timestamp"]) <= end_time):
                        return True
                return False
            
            elif step.step_type == FunnelStepType.CONDITION:
                # Verifica condição customizada
                if not step.condition:
                    return False
                
                # Implementa lógica de condição baseada nos metadados
                for event in user_events:
                    if self._check_condition(step.condition, event):
                        return True
                return False
            
            elif step.step_type == FunnelStepType.TIME_WINDOW:
                # Verifica se usuário permaneceu ativo na janela de tempo
                if not step.time_window_minutes:
                    return False
                
                event_times = [
                    datetime.fromisoformat(event["timestamp"])
                    for event in user_events
                    if start_time <= datetime.fromisoformat(event["timestamp"]) <= end_time
                ]
                
                if len(event_times) < 2:
                    return False
                
                # Verifica se há eventos separados pela janela de tempo
                for index in range(len(event_times) - 1):
                    time_diff = (event_times[index+1] - event_times[index]).total_seconds() / 60
                    if time_diff >= step.time_window_minutes:
                        return True
                
                return False
            
            else:
                return False
                
        except Exception as e:
            logger.error(f"[FUNNEL] Erro ao verificar conclusão do passo: {e}")
            return False
    
    def _check_condition(self, condition: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Verifica se um evento atende a uma condição."""
        try:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            if not all([field, operator, value]):
                return False
            
            event_value = event.get("metadata", {}).get(field)
            if event_value is None:
                return False
            
            if operator == "equals":
                return event_value == value
            elif operator == "contains":
                return str(value) in str(event_value)
            elif operator == "greater_than":
                return event_value > value
            elif operator == "less_than":
                return event_value < value
            else:
                return False
                
        except Exception as e:
            logger.error(f"[FUNNEL] Erro ao verificar condição: {e}")
            return False
    
    def _analyze_segments(self,
                         funnel: FunnelDefinition,
                         user_events: Dict[str, List[Dict[str, Any]]],
                         start_time: datetime,
                         end_time: datetime) -> Dict[str, Any]:
        """Analisa segmentação de usuários."""
        try:
            if not funnel.segment_by:
                return None
            
            segments = defaultdict(list)
            
            # Agrupa usuários por segmento
            for user_id, events in user_events.items():
                segment_value = self._get_user_segment(user_id, events, funnel.segment_by)
                segments[segment_value].append(user_id)
            
            # Analisa cada segmento
            segment_results = {}
            for segment_value, user_ids in segments.items():
                segment_user_events = {uid: user_events[uid] for uid in user_ids}
                
                # Executa análise do funnel para o segmento
                segment_funnel = FunnelDefinition(
                    name=f"{funnel.name} - {segment_value}",
                    description=f"Segmento: {segment_value}",
                    steps=funnel.steps,
                    time_window_hours=funnel.time_window_hours
                )
                
                segment_result = self._execute_funnel_analysis(
                    segment_funnel, start_time, end_time
                )
                
                segment_results[segment_value] = {
                    "users_count": len(user_ids),
                    "overall_conversion_rate": segment_result.overall_conversion_rate,
                    "step_results": segment_result.step_results
                }
            
            return segment_results
            
        except Exception as e:
            logger.error(f"[FUNNEL] Erro na análise de segmentos: {e}")
            return None
    
    def _get_user_segment(self,
                         user_id: str,
                         events: List[Dict[str, Any]],
                         segment_by: str) -> str:
        """Determina o segmento de um usuário."""
        try:
            # Implementa lógica de segmentação baseada em eventos
            if segment_by == "user_type":
                # Segmenta por tipo de usuário (novo, ativo, inativo)
                event_count = len(events)
                if event_count < 5:
                    return "novo"
                elif event_count < 20:
                    return "ativo"
                else:
                    return "power_user"
            
            elif segment_by == "source":
                # Segmenta por origem (primeiro evento)
                if events:
                    return events[0].get("source", "unknown")
                return "unknown"
            
            else:
                return "default"
                
        except Exception as e:
            logger.error(f"[FUNNEL] Erro ao determinar segmento: {e}")
            return "unknown"
    
    def _generate_recommendations(self, result: FunnelResult) -> List[str]:
        """Gera recomendações baseadas na análise do funnel."""
        recommendations = []
        
        try:
            # Análise de conversão geral
            if result.overall_conversion_rate < 10:
                recommendations.append("Taxa de conversão muito baixa. Considere simplificar o processo.")
            
            # Análise de drop-off
            if result.drop_off_points:
                worst_drop_off = max(result.drop_off_points, key=lambda value: value["drop_off_rate"])
                if worst_drop_off["drop_off_rate"] > 50:
                    recommendations.append(
                        f"Drop-off crítico no passo '{worst_drop_off['step_name']}'. "
                        f"Investigue e otimize este ponto."
                    )
            
            # Análise de volume
            if result.total_users < 100:
                recommendations.append("Volume baixo de usuários. Considere aumentar o tráfego para análise mais precisa.")
            
            # Análise de passos
            if len(result.step_results) > 5:
                recommendations.append("Funnel muito longo. Considere reduzir o número de passos.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"[FUNNEL] Erro ao gerar recomendações: {e}")
            return ["Erro ao gerar recomendações"]
    
    def _get_cached_result(self,
                          funnel_id: str,
                          start_time: Optional[datetime],
                          end_time: Optional[datetime]) -> Optional[FunnelResult]:
        """Obtém resultado em cache se válido."""
        try:
            cached_result = self.results_cache.get(funnel_id)
            if not cached_result:
                return None
            
            # Verifica se o cache ainda é válido
            cache_age = (datetime.now() - cached_result.analysis_time).total_seconds()
            if cache_age > self.cache_ttl:
                return None
            
            # Verifica se a janela de tempo é compatível
            if start_time and cached_result.time_window_start > start_time:
                return None
            if end_time and cached_result.time_window_end < end_time:
                return None
            
            return cached_result
            
        except Exception as e:
            logger.error(f"[FUNNEL] Erro ao verificar cache: {e}")
            return None
    
    def _cache_result(self, funnel_id: str, result: FunnelResult) -> None:
        """Armazena resultado em cache."""
        try:
            self.results_cache[funnel_id] = result
        except Exception as e:
            logger.error(f"[FUNNEL] Erro ao armazenar cache: {e}")
    
    def _get_last_analysis_time(self, funnel_id: str) -> Optional[str]:
        """Obtém tempo da última análise."""
        try:
            cached_result = self.results_cache.get(funnel_id)
            if cached_result:
                return cached_result.analysis_time.isoformat()
            return None
        except Exception as e:
            logger.error(f"[FUNNEL] Erro ao obter tempo da última análise: {e}")
            return None
    
    def _export_to_csv(self, result: FunnelResult) -> str:
        """Exporta resultado para CSV."""
        try:
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                "Funnel", "Step", "Users Reached", "Conversion Rate (%)", 
                "Drop-off Count", "Drop-off Rate (%)"
            ])
            
            # Dados dos passos
            for index, step_result in enumerate(result.step_results):
                conversion_rate = result.conversion_rates[index] if index < len(result.conversion_rates) else 0
                writer.writerow([
                    result.funnel_name,
                    step_result["name"],
                    step_result["users_reached"],
                    f"{conversion_rate:.2f}",
                    step_result.get("drop_off_count", 0),
                    f"{step_result.get('drop_off_rate', 0):.2f}"
                ])
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"[FUNNEL] Erro na exportação CSV: {e}")
            return f"Erro na exportação: {e}"


# Instância global do analisador de funnels
_funnel_analyzer_instance: Optional[FunnelAnalyzer] = None


def get_funnel_analyzer() -> FunnelAnalyzer:
    """
    Retorna instância global do analisador de funnels.
    
    Returns:
        Instância do FunnelAnalyzer
    """
    global _funnel_analyzer_instance
    if _funnel_analyzer_instance is None:
        _funnel_analyzer_instance = FunnelAnalyzer()
    return _funnel_analyzer_instance


# Funnels pré-definidos para casos comuns
def create_user_onboarding_funnel() -> str:
    """Cria funnel de onboarding de usuários."""
    analyzer = get_funnel_analyzer()
    
    steps = [
        FunnelStep(
            name="Registro",
            step_type=FunnelStepType.EVENT,
            event_type=EventType.USER_LOGIN,
            description="Usuário se registra no sistema",
            order=1
        ),
        FunnelStep(
            name="Primeira Busca",
            step_type=FunnelStepType.EVENT,
            event_type=EventType.KEYWORD_SEARCH,
            description="Usuário faz primeira busca de keywords",
            order=2
        ),
        FunnelStep(
            name="Exportação",
            step_type=FunnelStepType.EVENT,
            event_type=EventType.KEYWORD_EXPORT,
            description="Usuário exporta resultados",
            order=3
        )
    ]
    
    funnel_def = FunnelDefinition(
        name="Onboarding de Usuários",
        description="Funnel de onboarding completo do usuário",
        steps=steps,
        time_window_hours=24,
        segment_by="user_type"
    )
    
    return analyzer.create_funnel(funnel_def)


def create_keyword_analysis_funnel() -> str:
    """Cria funnel de análise de keywords."""
    analyzer = get_funnel_analyzer()
    
    steps = [
        FunnelStep(
            name="Adicionar Blog",
            step_type=FunnelStepType.EVENT,
            event_type=EventType.BLOG_ADDED,
            description="Usuário adiciona blog para análise",
            order=1
        ),
        FunnelStep(
            name="Iniciar Execução",
            step_type=FunnelStepType.EVENT,
            event_type=EventType.EXECUTION_STARTED,
            description="Usuário inicia execução da análise",
            order=2
        ),
        FunnelStep(
            name="Execução Completa",
            step_type=FunnelStepType.EVENT,
            event_type=EventType.EXECUTION_COMPLETED,
            description="Execução é concluída com sucesso",
            order=3
        ),
        FunnelStep(
            name="Exportar Resultados",
            step_type=FunnelStepType.EVENT,
            event_type=EventType.KEYWORD_EXPORT,
            description="Usuário exporta resultados da análise",
            order=4
        )
    ]
    
    funnel_def = FunnelDefinition(
        name="Análise de Keywords",
        description="Funnel completo de análise de keywords",
        steps=steps,
        time_window_hours=48,
        segment_by="source"
    )
    
    return analyzer.create_funnel(funnel_def) 