"""
audit_analytics.py

Análise de Auditoria - Omni Keywords Finder

Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 6
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19

Funcionalidades:
- Análise de padrões de comportamento
- Detecção de anomalias avançada
- Análise de risco em tempo real
- Relatórios de segurança
- Machine Learning para detecção
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import logging
from dataclasses import dataclass
from enum import Enum
import sqlite3
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Tipos de análise"""
    BEHAVIOR_PATTERN = "behavior_pattern"
    ANOMALY_DETECTION = "anomaly_detection"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_ANALYSIS = "compliance_analysis"
    SECURITY_THREAT = "security_threat"

class ThreatLevel(Enum):
    """Níveis de ameaça"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class BehaviorPattern:
    """Padrão de comportamento identificado"""
    id: str
    user_id: str
    pattern_type: str
    confidence: float
    frequency: int
    time_window: timedelta
    features: Dict[str, Any]
    risk_score: float
    created_at: datetime

@dataclass
class AnomalyResult:
    """Resultado de detecção de anomalia"""
    id: str
    event_id: str
    anomaly_type: str
    confidence: float
    severity: ThreatLevel
    description: str
    evidence: Dict[str, Any]
    detected_at: datetime

@dataclass
class RiskAssessment:
    """Avaliação de risco"""
    id: str
    user_id: str
    overall_risk: float
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    assessed_at: datetime
    valid_until: datetime

class AuditAnalytics:
    """
    Sistema de análise de auditoria
    
    Fornece análise avançada de padrões, detecção de anomalias
    e avaliação de risco em tempo real.
    """
    
    def __init__(self, db_path: str = "audit_logs.db"):
        self.db_path = db_path
        self.behavior_models = {}
        self.anomaly_detectors = {}
        self.risk_thresholds = self._load_risk_thresholds()
        self.pattern_cache = defaultdict(list)
        
        # Inicializar modelos ML
        self._init_ml_models()
        
        logger.info("Sistema de Análise de Auditoria inicializado")
    
    def _load_risk_thresholds(self) -> Dict[str, float]:
        """Carregar thresholds de risco"""
        return {
            "failed_login": 0.7,
            "unusual_time": 0.5,
            "rapid_actions": 0.6,
            "privilege_escalation": 0.9,
            "data_access": 0.4,
            "configuration_change": 0.8,
            "api_abuse": 0.7,
            "geographic_anomaly": 0.6
        }
    
    def _init_ml_models(self):
        """Inicializar modelos de Machine Learning"""
        # Modelo de detecção de anomalias
        self.anomaly_detectors['isolation_forest'] = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        # Modelo de clustering para padrões
        self.anomaly_detectors['dbscan'] = DBSCAN(
            eps=0.5,
            min_samples=5
        )
        
        # Scaler para normalização
        self.scaler = StandardScaler()
        
        logger.info("Modelos de ML inicializados")
    
    def analyze_user_behavior(
        self,
        user_id: str,
        time_window: timedelta = timedelta(days=30)
    ) -> List[BehaviorPattern]:
        """
        Analisar comportamento do usuário
        
        Args:
            user_id: ID do usuário
            time_window: Janela de tempo para análise
            
        Returns:
            Lista de padrões identificados
        """
        # Buscar eventos do usuário
        events = self._get_user_events(user_id, time_window)
        
        if not events:
            return []
        
        # Extrair features
        features = self._extract_behavior_features(events)
        
        # Identificar padrões
        patterns = self._identify_patterns(user_id, features, events)
        
        # Calcular scores de risco
        for pattern in patterns:
            pattern.risk_score = self._calculate_pattern_risk(pattern, features)
        
        # Armazenar no cache
        self.pattern_cache[user_id].extend(patterns)
        
        return patterns
    
    def _get_user_events(self, user_id: str, time_window: timedelta) -> List[Dict[str, Any]]:
        """Buscar eventos do usuário no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_time = datetime.now() - time_window
        
        cursor.execute("""
            SELECT * FROM audit_events 
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp
        """, (user_id, start_time.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append({
                'id': row[0],
                'timestamp': datetime.fromisoformat(row[1]),
                'action': row[6],
                'resource': row[7],
                'category': row[8],
                'level': row[9],
                'details': json.loads(row[10]),
                'risk_score': row[14]
            })
        
        return events
    
    def _extract_behavior_features(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrair features de comportamento dos eventos"""
        if not events:
            return {}
        
        # Features temporais
        timestamps = [e['timestamp'] for e in events]
        hours = [t.hour for t in timestamps]
        days_of_week = [t.weekday() for t in timestamps]
        
        # Features de ação
        actions = [e['action'] for e in events]
        resources = [e['resource'] for e in events]
        categories = [e['category'] for e in events]
        levels = [e['level'] for e in events]
        risk_scores = [e['risk_score'] for e in events]
        
        # Features de frequência
        action_freq = Counter(actions)
        resource_freq = Counter(resources)
        category_freq = Counter(categories)
        
        # Features de tempo
        time_between_events = []
        for index in range(1, len(timestamps)):
            time_diff = (timestamps[index] - timestamps[index-1]).total_seconds()
            time_between_events.append(time_diff)
        
        # Features de risco
        avg_risk = np.mean(risk_scores) if risk_scores else 0
        max_risk = np.max(risk_scores) if risk_scores else 0
        risk_std = np.std(risk_scores) if len(risk_scores) > 1 else 0
        
        return {
            'total_events': len(events),
            'unique_actions': len(action_freq),
            'unique_resources': len(resource_freq),
            'unique_categories': len(category_freq),
            'avg_risk_score': avg_risk,
            'max_risk_score': max_risk,
            'risk_std': risk_std,
            'avg_time_between_events': np.mean(time_between_events) if time_between_events else 0,
            'std_time_between_events': np.std(time_between_events) if len(time_between_events) > 1 else 0,
            'most_common_hour': Counter(hours).most_common(1)[0][0] if hours else 0,
            'most_common_day': Counter(days_of_week).most_common(1)[0][0] if days_of_week else 0,
            'action_entropy': self._calculate_entropy(action_freq),
            'resource_entropy': self._calculate_entropy(resource_freq),
            'category_entropy': self._calculate_entropy(category_freq),
            'high_risk_events_ratio': sum(1 for r in risk_scores if r > 0.7) / len(risk_scores) if risk_scores else 0,
            'security_events_ratio': sum(1 for c in categories if c == 'security_event') / len(categories) if categories else 0
        }
    
    def _calculate_entropy(self, counter: Counter) -> float:
        """Calcular entropia de uma distribuição"""
        total = sum(counter.values())
        if total == 0:
            return 0
        
        entropy = 0
        for count in counter.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy
    
    def _identify_patterns(
        self,
        user_id: str,
        features: Dict[str, Any],
        events: List[Dict[str, Any]]
    ) -> List[BehaviorPattern]:
        """Identificar padrões de comportamento"""
        patterns = []
        
        # Padrão de horário
        if features.get('most_common_hour', 0) in [23, 0, 1, 2, 3, 4, 5, 6]:
            patterns.append(BehaviorPattern(
                id=f"pattern_{user_id}_unusual_time",
                user_id=user_id,
                pattern_type="unusual_time",
                confidence=0.8,
                frequency=features.get('total_events', 0),
                time_window=timedelta(days=30),
                features={'most_common_hour': features.get('most_common_hour')},
                risk_score=0.0,  # Será calculado depois
                created_at=datetime.now()
            ))
        
        # Padrão de alta frequência
        if features.get('avg_time_between_events', 0) < 60:  # Menos de 1 minuto entre eventos
            patterns.append(BehaviorPattern(
                id=f"pattern_{user_id}_rapid_actions",
                user_id=user_id,
                pattern_type="rapid_actions",
                confidence=0.9,
                frequency=features.get('total_events', 0),
                time_window=timedelta(days=30),
                features={'avg_time_between_events': features.get('avg_time_between_events')},
                risk_score=0.0,
                created_at=datetime.now()
            ))
        
        # Padrão de alto risco
        if features.get('high_risk_events_ratio', 0) > 0.3:  # Mais de 30% de eventos de alto risco
            patterns.append(BehaviorPattern(
                id=f"pattern_{user_id}_high_risk",
                user_id=user_id,
                pattern_type="high_risk",
                confidence=0.85,
                frequency=features.get('total_events', 0),
                time_window=timedelta(days=30),
                features={'high_risk_ratio': features.get('high_risk_events_ratio')},
                risk_score=0.0,
                created_at=datetime.now()
            ))
        
        # Padrão de eventos de segurança
        if features.get('security_events_ratio', 0) > 0.2:  # Mais de 20% de eventos de segurança
            patterns.append(BehaviorPattern(
                id=f"pattern_{user_id}_security_focused",
                user_id=user_id,
                pattern_type="security_focused",
                confidence=0.75,
                frequency=features.get('total_events', 0),
                time_window=timedelta(days=30),
                features={'security_ratio': features.get('security_events_ratio')},
                risk_score=0.0,
                created_at=datetime.now()
            ))
        
        return patterns
    
    def _calculate_pattern_risk(self, pattern: BehaviorPattern, features: Dict[str, Any]) -> float:
        """Calcular score de risco do padrão"""
        base_risk = 0.3
        
        if pattern.pattern_type == "unusual_time":
            base_risk += 0.3
        elif pattern.pattern_type == "rapid_actions":
            base_risk += 0.4
        elif pattern.pattern_type == "high_risk":
            base_risk += 0.6
        elif pattern.pattern_type == "security_focused":
            base_risk += 0.2
        
        # Ajustar pela confiança
        base_risk *= pattern.confidence
        
        # Ajustar pela frequência
        if pattern.frequency > 100:
            base_risk += 0.2
        elif pattern.frequency > 50:
            base_risk += 0.1
        
        return min(base_risk, 1.0)
    
    def detect_anomalies(
        self,
        events: List[Dict[str, Any]],
        user_id: Optional[str] = None
    ) -> List[AnomalyResult]:
        """
        Detectar anomalias nos eventos
        
        Args:
            events: Lista de eventos
            user_id: ID do usuário (opcional)
            
        Returns:
            Lista de anomalias detectadas
        """
        if not events:
            return []
        
        anomalies = []
        
        # Converter eventos para features
        features_matrix = self._events_to_features_matrix(events)
        
        if len(features_matrix) < 5:  # Muito poucos eventos para análise
            return []
        
        # Normalizar features
        features_scaled = self.scaler.fit_transform(features_matrix)
        
        # Detectar anomalias com Isolation Forest
        anomaly_labels = self.anomaly_detectors['isolation_forest'].fit_predict(features_scaled)
        
        # Identificar eventos anômalos
        for index, label in enumerate(anomaly_labels):
            if label == -1:  # Anomalia detectada
                event = events[index]
                
                # Calcular confiança baseada na distância do centro
                confidence = self._calculate_anomaly_confidence(features_scaled[index])
                
                # Determinar severidade
                severity = self._determine_anomaly_severity(event, confidence)
                
                # Criar resultado
                anomaly = AnomalyResult(
                    id=f"anomaly_{event['id']}",
                    event_id=event['id'],
                    anomaly_type="ml_detected",
                    confidence=confidence,
                    severity=severity,
                    description=f"Anomalia detectada por ML: {event['action']}",
                    evidence={
                        'event_data': event,
                        'features': features_matrix[index].tolist(),
                        'detection_method': 'isolation_forest'
                    },
                    detected_at=datetime.now()
                )
                
                anomalies.append(anomaly)
        
        # Detectar anomalias baseadas em regras
        rule_anomalies = self._detect_rule_based_anomalies(events)
        anomalies.extend(rule_anomalies)
        
        return anomalies
    
    def _events_to_features_matrix(self, events: List[Dict[str, Any]]) -> np.ndarray:
        """Converter eventos para matriz de features"""
        features = []
        
        for event in events:
            # Features numéricas
            event_features = [
                event['risk_score'],
                event['timestamp'].hour,
                event['timestamp'].weekday(),
                len(event['action']),
                len(event['resource']),
                len(event.get('details', {}))
            ]
            
            # Features categóricas (one-hot encoding simplificado)
            categories = ['user_action', 'system_action', 'security_event', 'data_access', 
                         'configuration_change', 'api_call', 'authentication', 'authorization', 
                         'data_modification', 'system_performance']
            
            for cat in categories:
                event_features.append(1.0 if event['category'] == cat else 0.0)
            
            levels = ['info', 'warning', 'error', 'critical', 'security']
            for level in levels:
                event_features.append(1.0 if event['level'] == level else 0.0)
            
            features.append(event_features)
        
        return np.array(features)
    
    def _calculate_anomaly_confidence(self, features: np.ndarray) -> float:
        """Calcular confiança da anomalia"""
        # Simular cálculo de confiança baseado na distância
        distance = np.linalg.norm(features)
        confidence = min(distance / 10.0, 1.0)  # Normalizar para [0, 1]
        return confidence
    
    def _determine_anomaly_severity(self, event: Dict[str, Any], confidence: float) -> ThreatLevel:
        """Determinar severidade da anomalia"""
        base_severity = event.get('risk_score', 0.5)
        combined_score = (base_severity + confidence) / 2
        
        if combined_score > 0.8:
            return ThreatLevel.CRITICAL
        elif combined_score > 0.6:
            return ThreatLevel.HIGH
        elif combined_score > 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _detect_rule_based_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyResult]:
        """Detectar anomalias baseadas em regras"""
        anomalies = []
        
        for event in events:
            # Verificar tentativas de login falhadas
            if 'login' in event['action'].lower() and 'failed' in event['action'].lower():
                anomalies.append(AnomalyResult(
                    id=f"rule_anomaly_{event['id']}_failed_login",
                    event_id=event['id'],
                    anomaly_type="failed_login",
                    confidence=0.9,
                    severity=ThreatLevel.MEDIUM,
                    description="Tentativa de login falhada detectada",
                    evidence={'event_data': event},
                    detected_at=datetime.now()
                ))
            
            # Verificar acesso a recursos sensíveis
            if any(sensitive in event['resource'].lower() for sensitive in ['admin', 'config', 'password']):
                anomalies.append(AnomalyResult(
                    id=f"rule_anomaly_{event['id']}_sensitive_access",
                    event_id=event['id'],
                    anomaly_type="sensitive_access",
                    confidence=0.8,
                    severity=ThreatLevel.HIGH,
                    description="Acesso a recurso sensível detectado",
                    evidence={'event_data': event},
                    detected_at=datetime.now()
                ))
            
            # Verificar ações em horário incomum
            if event['timestamp'].hour in [23, 0, 1, 2, 3, 4, 5, 6]:
                anomalies.append(AnomalyResult(
                    id=f"rule_anomaly_{event['id']}_unusual_time",
                    event_id=event['id'],
                    anomaly_type="unusual_time",
                    confidence=0.7,
                    severity=ThreatLevel.LOW,
                    description="Ação em horário incomum detectada",
                    evidence={'event_data': event},
                    detected_at=datetime.now()
                ))
        
        return anomalies
    
    def assess_user_risk(
        self,
        user_id: str,
        time_window: timedelta = timedelta(days=30)
    ) -> RiskAssessment:
        """
        Avaliar risco do usuário
        
        Args:
            user_id: ID do usuário
            time_window: Janela de tempo para análise
            
        Returns:
            Avaliação de risco
        """
        # Buscar eventos do usuário
        events = self._get_user_events(user_id, time_window)
        
        if not events:
            return RiskAssessment(
                id=f"risk_{user_id}",
                user_id=user_id,
                overall_risk=0.0,
                risk_factors=[],
                recommendations=["Usuário sem atividade recente"],
                assessed_at=datetime.now(),
                valid_until=datetime.now() + timedelta(days=7)
            )
        
        # Analisar comportamento
        patterns = self.analyze_user_behavior(user_id, time_window)
        
        # Detectar anomalias
        anomalies = self.detect_anomalies(events, user_id)
        
        # Calcular risco geral
        overall_risk = self._calculate_overall_risk(events, patterns, anomalies)
        
        # Identificar fatores de risco
        risk_factors = self._identify_risk_factors(events, patterns, anomalies)
        
        # Gerar recomendações
        recommendations = self._generate_risk_recommendations(risk_factors)
        
        return RiskAssessment(
            id=f"risk_{user_id}",
            user_id=user_id,
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            recommendations=recommendations,
            assessed_at=datetime.now(),
            valid_until=datetime.now() + timedelta(days=7)
        )
    
    def _calculate_overall_risk(
        self,
        events: List[Dict[str, Any]],
        patterns: List[BehaviorPattern],
        anomalies: List[AnomalyResult]
    ) -> float:
        """Calcular risco geral"""
        base_risk = 0.1
        
        # Risco baseado nos eventos
        if events:
            avg_risk = np.mean([e['risk_score'] for e in events])
            base_risk += avg_risk * 0.3
        
        # Risco baseado nos padrões
        if patterns:
            pattern_risk = np.mean([p.risk_score for p in patterns])
            base_risk += pattern_risk * 0.3
        
        # Risco baseado nas anomalias
        if anomalies:
            anomaly_risk = len(anomalies) / len(events) if events else 0
            base_risk += anomaly_risk * 0.4
        
        return min(base_risk, 1.0)
    
    def _identify_risk_factors(
        self,
        events: List[Dict[str, Any]],
        patterns: List[BehaviorPattern],
        anomalies: List[AnomalyResult]
    ) -> List[Dict[str, Any]]:
        """Identificar fatores de risco"""
        factors = []
        
        # Fatores baseados em eventos
        high_risk_events = [e for e in events if e['risk_score'] > 0.7]
        if high_risk_events:
            factors.append({
                'type': 'high_risk_events',
                'description': f"{len(high_risk_events)} eventos de alto risco",
                'severity': 'high',
                'count': len(high_risk_events)
            })
        
        # Fatores baseados em padrões
        for pattern in patterns:
            if pattern.risk_score > 0.5:
                factors.append({
                    'type': 'behavior_pattern',
                    'description': f"Padrão de comportamento: {pattern.pattern_type}",
                    'severity': 'medium' if pattern.risk_score < 0.8 else 'high',
                    'confidence': pattern.confidence,
                    'risk_score': pattern.risk_score
                })
        
        # Fatores baseados em anomalias
        critical_anomalies = [a for a in anomalies if a.severity == ThreatLevel.CRITICAL]
        if critical_anomalies:
            factors.append({
                'type': 'critical_anomalies',
                'description': f"{len(critical_anomalies)} anomalias críticas detectadas",
                'severity': 'critical',
                'count': len(critical_anomalies)
            })
        
        return factors
    
    def _generate_risk_recommendations(self, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Gerar recomendações baseadas nos fatores de risco"""
        recommendations = []
        
        for factor in risk_factors:
            if factor['type'] == 'high_risk_events':
                recommendations.append(
                    f"Investigar {factor['count']} eventos de alto risco recentes"
                )
            
            elif factor['type'] == 'behavior_pattern':
                recommendations.append(
                    f"Monitorar padrão de comportamento: {factor['description']}"
                )
            
            elif factor['type'] == 'critical_anomalies':
                recommendations.append(
                    f"Ação imediata necessária: {factor['count']} anomalias críticas"
                )
        
        # Recomendações gerais
        if len(risk_factors) > 5:
            recommendations.append("Considerar revisão completa de permissões do usuário")
        
        if not recommendations:
            recommendations.append("Nenhuma ação específica necessária no momento")
        
        return recommendations
    
    def generate_security_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Gerar relatório de segurança
        
        Args:
            start_date: Data de início
            end_date: Data de fim
            
        Returns:
            Relatório de segurança
        """
        # Buscar todos os eventos do período
        events = self._get_events_period(start_date, end_date)
        
        # Estatísticas gerais
        total_events = len(events)
        unique_users = len(set(e.get('user_id') for e in events if e.get('user_id')))
        
        # Análise por categoria
        categories = Counter(e['category'] for e in events)
        
        # Análise por nível
        levels = Counter(e['level'] for e in events)
        
        # Eventos de alto risco
        high_risk_events = [e for e in events if e['risk_score'] > 0.7]
        
        # Detectar anomalias
        anomalies = self.detect_anomalies(events)
        
        # Análise de usuários
        user_analysis = self._analyze_users(events)
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': total_events,
                'unique_users': unique_users,
                'high_risk_events': len(high_risk_events),
                'anomalies_detected': len(anomalies),
                'critical_anomalies': len([a for a in anomalies if a.severity == ThreatLevel.CRITICAL])
            },
            'categories': dict(categories),
            'levels': dict(levels),
            'anomalies': [
                {
                    'id': a.id,
                    'type': a.anomaly_type,
                    'severity': a.severity.value,
                    'description': a.description,
                    'confidence': a.confidence
                }
                for a in anomalies
            ],
            'user_analysis': user_analysis,
            'recommendations': self._generate_security_recommendations(events, anomalies)
        }
    
    def _get_events_period(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Buscar eventos de um período"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_events 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        """, (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append({
                'id': row[0],
                'timestamp': datetime.fromisoformat(row[1]),
                'user_id': row[2],
                'action': row[6],
                'resource': row[7],
                'category': row[8],
                'level': row[9],
                'risk_score': row[14]
            })
        
        return events
    
    def _analyze_users(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisar comportamento dos usuários"""
        user_stats = defaultdict(lambda: {
            'total_events': 0,
            'avg_risk': 0.0,
            'high_risk_events': 0,
            'categories': Counter(),
            'last_activity': None
        })
        
        for event in events:
            user_id = event.get('user_id', 'unknown')
            stats = user_stats[user_id]
            
            stats['total_events'] += 1
            stats['avg_risk'] += event['risk_score']
            
            if event['risk_score'] > 0.7:
                stats['high_risk_events'] += 1
            
            stats['categories'][event['category']] += 1
            
            if not stats['last_activity'] or event['timestamp'] > stats['last_activity']:
                stats['last_activity'] = event['timestamp']
        
        # Calcular médias
        for user_id, stats in user_stats.items():
            if stats['total_events'] > 0:
                stats['avg_risk'] /= stats['total_events']
                stats['last_activity'] = stats['last_activity'].isoformat() if stats['last_activity'] else None
                stats['categories'] = dict(stats['categories'])
        
        return dict(user_stats)
    
    def _generate_security_recommendations(
        self,
        events: List[Dict[str, Any]],
        anomalies: List[AnomalyResult]
    ) -> List[str]:
        """Gerar recomendações de segurança"""
        recommendations = []
        
        # Análise de eventos de alto risco
        high_risk_events = [e for e in events if e['risk_score'] > 0.7]
        if len(high_risk_events) > 10:
            recommendations.append(
                f"Investigar {len(high_risk_events)} eventos de alto risco no período"
            )
        
        # Análise de anomalias
        critical_anomalies = [a for a in anomalies if a.severity == ThreatLevel.CRITICAL]
        if critical_anomalies:
            recommendations.append(
                f"Ação imediata: {len(critical_anomalies)} anomalias críticas detectadas"
            )
        
        # Análise de categorias
        categories = Counter(e['category'] for e in events)
        if categories.get('security_event', 0) > 50:
            recommendations.append(
                "Aumentar monitoramento de eventos de segurança"
            )
        
        # Análise de usuários
        user_events = defaultdict(int)
        for event in events:
            if event.get('user_id'):
                user_events[event['user_id']] += 1
        
        high_activity_users = [uid for uid, count in user_events.items() if count > 100]
        if high_activity_users:
            recommendations.append(
                f"Revisar atividade de {len(high_activity_users)} usuários com alta atividade"
            )
        
        if not recommendations:
            recommendations.append("Nenhuma recomendação específica no período")
        
        return recommendations


# Instância global do sistema de análise
audit_analytics = AuditAnalytics() 