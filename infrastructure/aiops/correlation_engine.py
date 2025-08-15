"""
Engine de Correlação Inteligente - Omni Keywords Finder
Detecta padrões temporais, causalidade e gera alertas inteligentes

Prompt: item 2.2 - Engine de Correlação
Ruleset: enterprise_control_layer.yaml
Data/hora: 2025-01-27T00:00
Tracing ID: CORRELATION_ENGINE_20250127_001

Baseado no código real do sistema Omni Keywords Finder
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from .intelligent_collector import Event, EventType, EventSeverity

logger = logging.getLogger(__name__)

class CorrelationMethod(Enum):
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    FREQUENCY = "frequency"
    CUSTOM = "custom"

class CorrelationEngine:
    """
    Engine de correlação de eventos para AIOps.
    Detecta padrões temporais, causalidade e gera alertas inteligentes.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.methods = self.config.get('methods', [CorrelationMethod.TEMPORAL, CorrelationMethod.CAUSAL])
        self.window_minutes = self.config.get('window_minutes', 10)
        self.min_correlation_events = self.config.get('min_correlation_events', 2)
        self.alert_threshold = self.config.get('alert_threshold', 0.8)
        logger.info(f"Engine de correlação inicializada. Métodos: {self.methods}")

    def correlate(self, events: List[Event]) -> List[Dict[str, Any]]:
        """
        Executa correlação de eventos usando os métodos configurados.
        Retorna lista consolidada de correlações detectadas.
        """
        if not events:
            logger.info("Nenhum evento para correlacionar.")
            return []

        logger.info(f"Correlacionando {len(events)} eventos usando métodos: {[m.value for m in self.methods]}")
        
        all_correlations = []
        
        # Executar cada método de correlação configurado
        for method in self.methods:
            if method == CorrelationMethod.TEMPORAL:
                temporal_correlations = self.detect_temporal_patterns(events)
                all_correlations.extend(temporal_correlations)
                logger.debug(f"Método temporal: {len(temporal_correlations)} correlações detectadas")
                
            elif method == CorrelationMethod.CAUSAL:
                causal_correlations = self.detect_causality(events)
                all_correlations.extend(causal_correlations)
                logger.debug(f"Método causal: {len(causal_correlations)} correlações detectadas")
                
            elif method == CorrelationMethod.FREQUENCY:
                # Placeholder para implementação futura
                logger.debug("Método frequency não implementado ainda")
                
            elif method == CorrelationMethod.CUSTOM:
                # Placeholder para implementação futura
                logger.debug("Método custom não implementado ainda")
        
        # Remover duplicatas baseado em correlation_id e método
        unique_correlations = []
        seen = set()
        for correlation in all_correlations:
            key = (correlation.get('correlation_id'), correlation.get('method'))
            if key not in seen:
                seen.add(key)
                unique_correlations.append(correlation)
        
        logger.info(f"Total de {len(unique_correlations)} correlações únicas detectadas.")
        return unique_correlations

    def detect_temporal_patterns(self, events: List[Event]) -> List[Dict[str, Any]]:
        """
        Detecta padrões temporais entre eventos reais agrupando por correlation_id e janela de tempo.
        Retorna lista de correlações temporais detectadas.
        """
        if not events:
            return []

        # Agrupar eventos por correlation_id (ou por tipo se não houver)
        events_by_correlation = {}
        for event in events:
            key = event.correlation_id or f"{event.type.value}:{event.source}"
            if key not in events_by_correlation:
                events_by_correlation[key] = []
            events_by_correlation[key].append(event)

        correlations = []
        window = timedelta(minutes=self.window_minutes)

        for correlation_id, grouped_events in events_by_correlation.items():
            # Ordenar por timestamp
            grouped_events.sort(key=lambda e: e.timestamp)
            start_idx = 0
            while start_idx < len(grouped_events):
                window_start = grouped_events[start_idx].timestamp
                window_events = [grouped_events[start_idx]]
                for idx in range(start_idx + 1, len(grouped_events)):
                    if grouped_events[idx].timestamp - window_start <= window:
                        window_events.append(grouped_events[idx])
                    else:
                        break
                if len(window_events) >= self.min_correlation_events:
                    correlation = {
                        'correlation_id': correlation_id,
                        'event_ids': [e.id for e in window_events],
                        'start_time': window_events[0].timestamp,
                        'end_time': window_events[-1].timestamp,
                        'duration': (window_events[-1].timestamp - window_events[0].timestamp).total_seconds(),
                        'event_types': list(set(e.type.value for e in window_events)),
                        'severities': list(set(e.severity.value for e in window_events)),
                        'method': CorrelationMethod.TEMPORAL.value
                    }
                    correlations.append(correlation)
                start_idx += 1
        logger.info(f"Detectadas {len(correlations)} correlações temporais.")
        return correlations

    def detect_causality(self, events: List[Event]) -> List[Dict[str, Any]]:
        """
        Detecta relações de causalidade entre eventos reais analisando sequências e dependências temporais.
        Retorna lista de relações causais prováveis.
        """
        if not events:
            return []

        # Ordenar eventos por timestamp globalmente
        events_sorted = sorted(events, key=lambda e: e.timestamp)
        causal_relations = []
        window = timedelta(minutes=self.window_minutes)

        # Para cada evento, buscar possíveis causas anteriores na janela
        for idx, effect_event in enumerate(events_sorted):
            for j in range(max(0, idx - 20), idx):  # Limitar busca para performance
                cause_event = events_sorted[j]
                # Causalidade: evento anterior, dentro da janela, tipos diferentes
                if (effect_event.timestamp - cause_event.timestamp <= window and
                    effect_event.timestamp > cause_event.timestamp and
                    effect_event.type != cause_event.type):
                    relation = {
                        'cause_event_id': cause_event.id,
                        'effect_event_id': effect_event.id,
                        'cause_type': cause_event.type.value,
                        'effect_type': effect_event.type.value,
                        'cause_time': cause_event.timestamp,
                        'effect_time': effect_event.timestamp,
                        'delta_seconds': (effect_event.timestamp - cause_event.timestamp).total_seconds(),
                        'correlation_id': effect_event.correlation_id or cause_event.correlation_id,
                        'method': CorrelationMethod.CAUSAL.value
                    }
                    causal_relations.append(relation)
        logger.info(f"Detectadas {len(causal_relations)} relações causais prováveis.")
        return causal_relations

    def generate_alerts(self, correlations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Gera alertas inteligentes a partir das correlações detectadas, baseado em severidade, frequência e padrões.
        Retorna lista de alertas gerados.
        """
        if not correlations:
            return []

        alerts = []
        for correlation in correlations:
            # Calcular score de alerta baseado em múltiplos fatores
            alert_score = self._calculate_alert_score(correlation)
            
            if alert_score >= self.alert_threshold:
                alert = {
                    'alert_id': f"alert_{correlation.get('correlation_id', 'unknown')}_{int(datetime.now().timestamp())}",
                    'correlation_id': correlation.get('correlation_id'),
                    'alert_type': self._determine_alert_type(correlation),
                    'severity': self._determine_alert_severity(correlation),
                    'message': self._generate_alert_message(correlation),
                    'score': alert_score,
                    'timestamp': datetime.now(),
                    'correlation_data': correlation
                }
                alerts.append(alert)
        
        logger.info(f"Gerados {len(alerts)} alertas inteligentes.")
        return alerts

    def _calculate_alert_score(self, correlation: Dict[str, Any]) -> float:
        """
        Calcula score de alerta baseado em fatores como número de eventos, severidade, duração.
        """
        score = 0.0
        
        # Fator: número de eventos correlacionados
        event_count = len(correlation.get('event_ids', []))
        score += min(event_count * 0.1, 0.3)  # Máximo 0.3
        
        # Fator: severidade dos eventos
        severities = correlation.get('severities', [])
        if 'critical' in severities:
            score += 0.4
        elif 'high' in severities:
            score += 0.3
        elif 'medium' in severities:
            score += 0.2
        
        # Fator: duração da correlação
        duration = correlation.get('duration', 0)
        if duration > 300:  # Mais de 5 minutos
            score += 0.2
        elif duration > 60:  # Mais de 1 minuto
            score += 0.1
        
        # Fator: tipos de eventos envolvidos
        event_types = correlation.get('event_types', [])
        if 'error_event' in event_types or 'security_event' in event_types:
            score += 0.2
        
        return min(score, 1.0)  # Normalizar para 0-1

    def _determine_alert_type(self, correlation: Dict[str, Any]) -> str:
        """
        Determina o tipo de alerta baseado na correlação.
        """
        method = correlation.get('method', '')
        event_types = correlation.get('event_types', [])
        
        if 'error_event' in event_types:
            return 'error_correlation'
        elif 'security_event' in event_types:
            return 'security_correlation'
        elif method == CorrelationMethod.CAUSAL.value:
            return 'causal_chain'
        else:
            return 'temporal_pattern'

    def _determine_alert_severity(self, correlation: Dict[str, Any]) -> str:
        """
        Determina a severidade do alerta baseado na correlação.
        """
        severities = correlation.get('severities', [])
        score = self._calculate_alert_score(correlation)
        
        if 'critical' in severities or score > 0.9:
            return 'critical'
        elif 'high' in severities or score > 0.7:
            return 'high'
        elif 'medium' in severities or score > 0.5:
            return 'medium'
        else:
            return 'low'

    def _generate_alert_message(self, correlation: Dict[str, Any]) -> str:
        """
        Gera mensagem de alerta descritiva baseada na correlação.
        """
        method = correlation.get('method', '')
        event_count = len(correlation.get('event_ids', []))
        event_types = correlation.get('event_types', [])
        duration = correlation.get('duration', 0)
        
        if method == CorrelationMethod.TEMPORAL.value:
            return f"Padrão temporal detectado: {event_count} eventos de tipos {event_types} em {duration:.1f}s"
        elif method == CorrelationMethod.CAUSAL.value:
            cause_type = correlation.get('cause_type', 'unknown')
            effect_type = correlation.get('effect_type', 'unknown')
            return f"Relação causal detectada: {cause_type} -> {effect_type} (delta: {correlation.get('delta_seconds', 0):.1f}s)"
        else:
            return f"Correlação detectada: {event_count} eventos correlacionados" 