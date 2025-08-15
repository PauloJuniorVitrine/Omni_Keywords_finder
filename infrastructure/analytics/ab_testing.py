"""
Sistema de A/B Testing - Omni Keywords Finder

Implementação completa do sistema de A/B Testing com:
- Criação de experimentos
- Tracking de conversões
- Análise estatística
- Dashboard de resultados
- Segmentação de usuários
- Notificações de resultados

Autor: Sistema Omni Keywords Finder
Data: 2024-12-19
Versão: 1.0.0
"""

import uuid
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from scipy import stats
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from prometheus_client import Counter, Histogram, Gauge

# Configuração de logging
logger = logging.getLogger(__name__)

# Métricas Prometheus
EXPERIMENT_CREATED = Counter('ab_testing_experiments_created_total', 'Total de experimentos criados')
EXPERIMENT_STARTED = Counter('ab_testing_experiments_started_total', 'Total de experimentos iniciados')
EXPERIMENT_COMPLETED = Counter('ab_testing_experiments_completed_total', 'Total de experimentos concluídos')
CONVERSION_TRACKED = Counter('ab_testing_conversions_tracked_total', 'Total de conversões registradas', ['experiment_id', 'variant_id'])
PARTICIPANT_ADDED = Counter('ab_testing_participants_added_total', 'Total de participantes adicionados', ['experiment_id'])
STATISTICAL_ANALYSIS = Counter('ab_testing_statistical_analyses_total', 'Total de análises estatísticas realizadas')
EXPERIMENT_DURATION = Histogram('ab_testing_experiment_duration_hours', 'Duração dos experimentos em horas')
ACTIVE_EXPERIMENTS = Gauge('ab_testing_active_experiments', 'Número de experimentos ativos')

class ExperimentStatus(Enum):
    """Status dos experimentos"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"

class ExperimentType(Enum):
    """Tipos de experimento"""
    FEATURE = "feature"
    UI = "ui"
    ALGORITHM = "algorithm"
    CONTENT = "content"

class EventType(Enum):
    """Tipos de evento"""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    CONVERSION = "conversion"
    METRIC = "metric"
    CUSTOM = "custom"

@dataclass
class ExperimentConfig:
    """Configuração de um experimento"""
    id: str
    name: str
    description: str
    type: ExperimentType
    area: str
    traffic_percentage: float = 100.0
    duration_days: int = 30
    primary_metrics: List[str] = None
    secondary_metrics: List[str] = None
    hypothesis: str = ""
    significance_level: float = 0.05
    statistical_power: float = 0.8
    min_sample_size: int = 100
    created_by: str = ""
    owner: str = ""

@dataclass
class Variant:
    """Variante de um experimento"""
    id: str
    experiment_id: str
    name: str
    description: str
    type: str  # 'control' ou 'test'
    configuration: Dict[str, Any]
    weight: float = 50.0
    active: bool = True

@dataclass
class Participant:
    """Participante de um experimento"""
    id: str
    experiment_id: str
    variant_id: str
    user_id: str
    session_id: str = ""
    device_id: str = ""
    ip_address: str = ""
    user_agent: str = ""
    location: str = ""
    active: bool = True
    entry_date: datetime = None
    last_activity: datetime = None

@dataclass
class ConversionEvent:
    """Evento de conversão"""
    id: str
    participant_id: str
    experiment_id: str
    variant_id: str
    event_type: EventType
    event_name: str
    value: float = 0.0
    data: Dict[str, Any] = None
    url: str = ""
    element: str = ""
    context: Dict[str, Any] = None
    timestamp: datetime = None

@dataclass
class StatisticalResult:
    """Resultado estatístico de uma análise"""
    metric: str
    variant_id: str
    mean_value: float
    std_deviation: float
    sample_size: int
    standard_error: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    p_value: float
    test_statistic: float
    significant: bool
    difference_from_control: float
    improvement_percentage: float
    calculated_at: datetime = None

@dataclass
class ExperimentResult:
    """Resultado completo de um experimento"""
    experiment_id: str
    status: ExperimentStatus
    start_date: datetime
    end_date: datetime
    total_participants: int
    total_conversions: int
    statistical_results: List[StatisticalResult]
    winner_variant: Optional[str] = None
    confidence_level: float = 0.0
    recommendation: str = ""

class ABTestingSystem:
    """
    Sistema principal de A/B Testing
    
    Fornece funcionalidades completas para criação, execução e análise
    de experimentos A/B com análise estatística robusta.
    """
    
    def __init__(self, db_path: str = "ab_testing.db"):
        """
        Inicializa o sistema de A/B Testing
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.active_experiments = {}
        self.participant_cache = {}
        self.conversion_cache = {}
        
        # Inicializar banco de dados
        self._init_database()
        
        # Carregar experimentos ativos
        self._load_active_experiments()
        
        logger.info("Sistema de A/B Testing inicializado")
    
    def _init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de experimentos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS experiments (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        description TEXT,
                        type TEXT NOT NULL,
                        area TEXT NOT NULL,
                        traffic_percentage REAL DEFAULT 100.0,
                        duration_days INTEGER DEFAULT 30,
                        primary_metrics TEXT,
                        secondary_metrics TEXT,
                        hypothesis TEXT,
                        significance_level REAL DEFAULT 0.05,
                        statistical_power REAL DEFAULT 0.8,
                        min_sample_size INTEGER DEFAULT 100,
                        status TEXT DEFAULT 'draft',
                        active BOOLEAN DEFAULT 1,
                        start_date DATETIME,
                        end_date DATETIME,
                        planned_end_date DATETIME,
                        created_by TEXT,
                        owner TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de variantes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS variants (
                        id TEXT PRIMARY KEY,
                        experiment_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        type TEXT DEFAULT 'test',
                        configuration TEXT,
                        weight REAL DEFAULT 50.0,
                        active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (experiment_id) REFERENCES experiments (id)
                    )
                """)
                
                # Tabela de participantes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS participants (
                        id TEXT PRIMARY KEY,
                        experiment_id TEXT NOT NULL,
                        variant_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT,
                        device_id TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        location TEXT,
                        active BOOLEAN DEFAULT 1,
                        entry_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        exit_date DATETIME,
                        last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (experiment_id) REFERENCES experiments (id),
                        FOREIGN KEY (variant_id) REFERENCES variants (id)
                    )
                """)
                
                # Tabela de eventos de conversão
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversion_events (
                        id TEXT PRIMARY KEY,
                        participant_id TEXT NOT NULL,
                        experiment_id TEXT NOT NULL,
                        variant_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        event_name TEXT NOT NULL,
                        value REAL DEFAULT 0.0,
                        data TEXT,
                        url TEXT,
                        element TEXT,
                        context TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (participant_id) REFERENCES participants (id),
                        FOREIGN KEY (experiment_id) REFERENCES experiments (id),
                        FOREIGN KEY (variant_id) REFERENCES variants (id)
                    )
                """)
                
                # Tabela de resultados estatísticos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS statistical_results (
                        id TEXT PRIMARY KEY,
                        experiment_id TEXT NOT NULL,
                        metric TEXT NOT NULL,
                        variant_id TEXT NOT NULL,
                        mean_value REAL,
                        std_deviation REAL,
                        sample_size INTEGER,
                        standard_error REAL,
                        confidence_interval_lower REAL,
                        confidence_interval_upper REAL,
                        p_value REAL,
                        test_statistic REAL,
                        significant BOOLEAN,
                        difference_from_control REAL,
                        improvement_percentage REAL,
                        calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (experiment_id) REFERENCES experiments (id),
                        FOREIGN KEY (variant_id) REFERENCES variants (id)
                    )
                """)
                
                # Tabela de segmentos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS segments (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        description TEXT,
                        criteria TEXT NOT NULL,
                        active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_participants_experiment ON participants(experiment_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversions_experiment ON conversion_events(experiment_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversions_variant ON conversion_events(variant_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversions_timestamp ON conversion_events(timestamp)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            raise
    
    def _load_active_experiments(self):
        """Carrega experimentos ativos na memória"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, status FROM experiments 
                    WHERE active = 1 AND status = 'running'
                """)
                
                for row in cursor.fetchall():
                    experiment_id, name, status = row
                    self.active_experiments[experiment_id] = {
                        'name': name,
                        'status': status
                    }
                
                ACTIVE_EXPERIMENTS.set(len(self.active_experiments))
                
        except Exception as e:
            logger.error(f"Erro ao carregar experimentos ativos: {str(e)}")
    
    def create_experiment(self, config: ExperimentConfig) -> str:
        """
        Cria um novo experimento
        
        Args:
            config: Configuração do experimento
            
        Returns:
            ID do experimento criado
        """
        try:
            experiment_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Inserir experimento
                cursor.execute("""
                    INSERT INTO experiments (
                        id, name, description, type, area, traffic_percentage,
                        duration_days, primary_metrics, secondary_metrics,
                        hypothesis, significance_level, statistical_power,
                        min_sample_size, created_by, owner
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    experiment_id, config.name, config.description, config.type.value,
                    config.area, config.traffic_percentage, config.duration_days,
                    json.dumps(config.primary_metrics or []),
                    json.dumps(config.secondary_metrics or []),
                    config.hypothesis, config.significance_level,
                    config.statistical_power, config.min_sample_size,
                    config.created_by, config.owner
                ))
                
                # Criar variante de controle automaticamente
                control_variant_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO variants (
                        id, experiment_id, name, description, type, configuration, weight
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    control_variant_id, experiment_id, "Controle",
                    "Variante de controle (padrão)", "control",
                    json.dumps({}), 50.0
                ))
                
                conn.commit()
            
            EXPERIMENT_CREATED.inc()
            logger.info(f"Experimento criado: {config.name} (ID: {experiment_id})")
            
            return experiment_id
            
        except Exception as e:
            logger.error(f"Erro ao criar experimento: {str(e)}")
            raise
    
    def add_variant(self, experiment_id: str, variant: Variant) -> str:
        """
        Adiciona uma variante a um experimento
        
        Args:
            experiment_id: ID do experimento
            variant: Configuração da variante
            
        Returns:
            ID da variante criada
        """
        try:
            variant_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO variants (
                        id, experiment_id, name, description, type,
                        configuration, weight
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    variant_id, experiment_id, variant.name,
                    variant.description, variant.type,
                    json.dumps(variant.configuration), variant.weight
                ))
                
                conn.commit()
            
            logger.info(f"Variante adicionada: {variant.name} (ID: {variant_id})")
            return variant_id
            
        except Exception as e:
            logger.error(f"Erro ao adicionar variante: {str(e)}")
            raise
    
    def start_experiment(self, experiment_id: str) -> bool:
        """
        Inicia um experimento
        
        Args:
            experiment_id: ID do experimento
            
        Returns:
            True se iniciado com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar se experimento existe e está em draft
                cursor.execute("""
                    SELECT status FROM experiments WHERE id = ?
                """, (experiment_id,))
                
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"Experimento não encontrado: {experiment_id}")
                
                if result[0] != 'draft':
                    raise ValueError(f"Experimento não pode ser iniciado. Status atual: {result[0]}")
                
                # Atualizar status e datas
                start_date = datetime.now()
                planned_end_date = start_date + timedelta(days=30)  # Padrão 30 dias
                
                cursor.execute("""
                    UPDATE experiments 
                    SET status = 'running', start_date = ?, planned_end_date = ?
                    WHERE id = ?
                """, (start_date, planned_end_date, experiment_id))
                
                conn.commit()
            
            # Atualizar cache
            self.active_experiments[experiment_id] = {
                'name': 'Unknown',
                'status': 'running'
            }
            ACTIVE_EXPERIMENTS.set(len(self.active_experiments))
            
            EXPERIMENT_STARTED.inc()
            logger.info(f"Experimento iniciado: {experiment_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar experimento: {str(e)}")
            raise
    
    def assign_participant(self, experiment_id: str, user_id: str, 
                          session_id: str = "", device_id: str = "",
                          ip_address: str = "", user_agent: str = "",
                          location: str = "") -> Optional[str]:
        """
        Atribui um participante a uma variante de um experimento
        
        Args:
            experiment_id: ID do experimento
            user_id: ID do usuário
            session_id: ID da sessão
            device_id: ID do dispositivo
            ip_address: Endereço IP
            user_agent: User agent
            location: Localização
            
        Returns:
            ID da variante atribuída ou None se não elegível
        """
        try:
            # Verificar se experimento está ativo
            if experiment_id not in self.active_experiments:
                return None
            
            # Verificar se usuário já participa
            participant_id = self._get_existing_participant(experiment_id, user_id)
            if participant_id:
                return self._get_participant_variant(participant_id)
            
            # Selecionar variante
            variant_id = self._select_variant(experiment_id)
            if not variant_id:
                return None
            
            # Criar participante
            participant_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO participants (
                        id, experiment_id, variant_id, user_id, session_id,
                        device_id, ip_address, user_agent, location
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    participant_id, experiment_id, variant_id, user_id,
                    session_id, device_id, ip_address, user_agent, location
                ))
                
                conn.commit()
            
            # Atualizar cache
            self.participant_cache[f"{experiment_id}:{user_id}"] = {
                'participant_id': participant_id,
                'variant_id': variant_id
            }
            
            PARTICIPANT_ADDED.labels(experiment_id=experiment_id).inc()
            logger.info(f"Participante atribuído: {user_id} -> {variant_id}")
            
            return variant_id
            
        except Exception as e:
            logger.error(f"Erro ao atribuir participante: {str(e)}")
            return None
    
    def track_conversion(self, experiment_id: str, user_id: str,
                        event_type: EventType, event_name: str,
                        value: float = 0.0, data: Dict[str, Any] = None,
                        url: str = "", element: str = "",
                        context: Dict[str, Any] = None) -> bool:
        """
        Registra uma conversão/evento para um participante
        
        Args:
            experiment_id: ID do experimento
            user_id: ID do usuário
            event_type: Tipo do evento
            event_name: Nome do evento
            value: Valor do evento
            data: Dados adicionais
            url: URL da página
            element: Elemento HTML
            context: Contexto adicional
            
        Returns:
            True se registrado com sucesso
        """
        try:
            # Buscar participante
            participant_info = self._get_participant_info(experiment_id, user_id)
            if not participant_info:
                return False
            
            participant_id = participant_info['participant_id']
            variant_id = participant_info['variant_id']
            
            # Criar evento
            event_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO conversion_events (
                        id, participant_id, experiment_id, variant_id,
                        event_type, event_name, value, data, url, element, context
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id, participant_id, experiment_id, variant_id,
                    event_type.value, event_name, value,
                    json.dumps(data or {}),
                    url, element, json.dumps(context or {})
                ))
                
                # Atualizar última atividade do participante
                cursor.execute("""
                    UPDATE participants 
                    SET last_activity = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (participant_id,))
                
                conn.commit()
            
            CONVERSION_TRACKED.labels(
                experiment_id=experiment_id,
                variant_id=variant_id
            ).inc()
            
            logger.info(f"Conversão registrada: {event_name} para {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar conversão: {str(e)}")
            return False
    
    def analyze_experiment(self, experiment_id: str) -> ExperimentResult:
        """
        Analisa os resultados de um experimento
        
        Args:
            experiment_id: ID do experimento
            
        Returns:
            Resultado da análise
        """
        try:
            # Buscar dados do experimento
            experiment_data = self._get_experiment_data(experiment_id)
            if not experiment_data:
                raise ValueError(f"Experimento não encontrado: {experiment_id}")
            
            # Buscar dados de conversão por variante
            conversion_data = self._get_conversion_data(experiment_id)
            
            # Realizar análise estatística
            statistical_results = []
            winner_variant = None
            max_improvement = 0.0
            
            for metric in experiment_data['primary_metrics']:
                for variant_id in experiment_data['variant_ids']:
                    if variant_id == experiment_data['control_variant_id']:
                        continue
                    
                    result = self._perform_statistical_test(
                        experiment_id, metric, variant_id,
                        experiment_data['control_variant_id']
                    )
                    
                    if result:
                        statistical_results.append(result)
                        
                        # Verificar se é o melhor resultado
                        if result.improvement_percentage > max_improvement:
                            max_improvement = result.improvement_percentage
                            winner_variant = variant_id
            
            # Calcular nível de confiança geral
            confidence_level = self._calculate_overall_confidence(statistical_results)
            
            # Gerar recomendação
            recommendation = self._generate_recommendation(
                statistical_results, winner_variant, confidence_level
            )
            
            # Criar resultado
            result = ExperimentResult(
                experiment_id=experiment_id,
                status=ExperimentStatus(experiment_data['status']),
                start_date=experiment_data['start_date'],
                end_date=experiment_data['end_date'],
                total_participants=experiment_data['total_participants'],
                total_conversions=experiment_data['total_conversions'],
                statistical_results=statistical_results,
                winner_variant=winner_variant,
                confidence_level=confidence_level,
                recommendation=recommendation
            )
            
            # Salvar resultados
            self._save_statistical_results(statistical_results)
            
            STATISTICAL_ANALYSIS.inc()
            logger.info(f"Análise concluída para experimento: {experiment_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao analisar experimento: {str(e)}")
            raise
    
    def _select_variant(self, experiment_id: str) -> Optional[str]:
        """Seleciona uma variante baseado nos pesos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, weight FROM variants 
                    WHERE experiment_id = ? AND active = 1
                """, (experiment_id,))
                
                variants = cursor.fetchall()
                if not variants:
                    return None
                
                # Seleção baseada em peso
                total_weight = sum(value[1] for value in variants)
                if total_weight == 0:
                    return variants[0][0]  # Primeira variante se pesos zerados
                
                # Seleção aleatória baseada em peso
                rand = np.random.random() * total_weight
                cumulative_weight = 0
                
                for variant_id, weight in variants:
                    cumulative_weight += weight
                    if rand <= cumulative_weight:
                        return variant_id
                
                return variants[0][0]  # Fallback
                
        except Exception as e:
            logger.error(f"Erro ao selecionar variante: {str(e)}")
            return None
    
    def _perform_statistical_test(self, experiment_id: str, metric: str,
                                 test_variant_id: str, control_variant_id: str) -> Optional[StatisticalResult]:
        """Realiza teste estatístico entre duas variantes"""
        try:
            # Buscar dados das variantes
            test_data = self._get_variant_metric_data(experiment_id, test_variant_id, metric)
            control_data = self._get_variant_metric_data(experiment_id, control_variant_id, metric)
            
            if len(test_data) < 10 or len(control_data) < 10:
                return None  # Amostra muito pequena
            
            # Teste t de Student
            t_stat, p_value = stats.ttest_ind(test_data, control_data)
            
            # Calcular estatísticas
            test_mean = np.mean(test_data)
            control_mean = np.mean(control_data)
            test_std = np.std(test_data, ddof=1)
            control_std = np.std(control_data, ddof=1)
            
            # Erro padrão
            test_se = test_std / np.sqrt(len(test_data))
            control_se = control_std / np.sqrt(len(control_data))
            
            # Intervalo de confiança (95%)
            test_ci = stats.t.interval(0.95, len(test_data)-1, loc=test_mean, scale=test_se)
            control_ci = stats.t.interval(0.95, len(control_data)-1, loc=control_mean, scale=control_se)
            
            # Diferença e percentual de melhoria
            difference = test_mean - control_mean
            improvement_percentage = (difference / control_mean * 100) if control_mean != 0 else 0
            
            # Significância estatística
            significant = p_value < 0.05
            
            return StatisticalResult(
                metric=metric,
                variant_id=test_variant_id,
                mean_value=test_mean,
                std_deviation=test_std,
                sample_size=len(test_data),
                standard_error=test_se,
                confidence_interval_lower=test_ci[0],
                confidence_interval_upper=test_ci[1],
                p_value=p_value,
                test_statistic=t_stat,
                significant=significant,
                difference_from_control=difference,
                improvement_percentage=improvement_percentage,
                calculated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro no teste estatístico: {str(e)}")
            return None
    
    def _get_experiment_data(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Busca dados completos de um experimento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Dados do experimento
                cursor.execute("""
                    SELECT name, description, type, area, status, start_date, end_date,
                           primary_metrics, secondary_metrics, significance_level
                    FROM experiments WHERE id = ?
                """, (experiment_id,))
                
                exp_row = cursor.fetchone()
                if not exp_row:
                    return None
                
                # Variantes
                cursor.execute("""
                    SELECT id, name, type FROM variants 
                    WHERE experiment_id = ? AND active = 1
                """, (experiment_id,))
                
                variants = cursor.fetchall()
                variant_ids = [value[0] for value in variants]
                control_variant_id = next((value[0] for value in variants if value[2] == 'control'), None)
                
                # Participantes
                cursor.execute("""
                    SELECT COUNT(*) FROM participants 
                    WHERE experiment_id = ? AND active = 1
                """, (experiment_id,))
                
                total_participants = cursor.fetchone()[0]
                
                # Conversões
                cursor.execute("""
                    SELECT COUNT(*) FROM conversion_events 
                    WHERE experiment_id = ?
                """, (experiment_id,))
                
                total_conversions = cursor.fetchone()[0]
                
                return {
                    'name': exp_row[0],
                    'description': exp_row[1],
                    'type': exp_row[2],
                    'area': exp_row[3],
                    'status': exp_row[4],
                    'start_date': exp_row[5],
                    'end_date': exp_row[6],
                    'primary_metrics': json.loads(exp_row[7] or '[]'),
                    'secondary_metrics': json.loads(exp_row[8] or '[]'),
                    'significance_level': exp_row[9],
                    'variant_ids': variant_ids,
                    'control_variant_id': control_variant_id,
                    'total_participants': total_participants,
                    'total_conversions': total_conversions
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados do experimento: {str(e)}")
            return None
    
    def _get_variant_metric_data(self, experiment_id: str, variant_id: str, metric: str) -> List[float]:
        """Busca dados de uma métrica específica para uma variante"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT value FROM conversion_events 
                    WHERE experiment_id = ? AND variant_id = ? AND event_name = ?
                """, (experiment_id, variant_id, metric))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados da variante: {str(e)}")
            return []
    
    def _get_participant_info(self, experiment_id: str, user_id: str) -> Optional[Dict[str, str]]:
        """Busca informações de um participante"""
        # Verificar cache primeiro
        cache_key = f"{experiment_id}:{user_id}"
        if cache_key in self.participant_cache:
            return self.participant_cache[cache_key]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, variant_id FROM participants 
                    WHERE experiment_id = ? AND user_id = ? AND active = 1
                """, (experiment_id, user_id))
                
                row = cursor.fetchone()
                if row:
                    result = {
                        'participant_id': row[0],
                        'variant_id': row[1]
                    }
                    # Atualizar cache
                    self.participant_cache[cache_key] = result
                    return result
                
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar participante: {str(e)}")
            return None
    
    def _get_existing_participant(self, experiment_id: str, user_id: str) -> Optional[str]:
        """Verifica se usuário já participa do experimento"""
        info = self._get_participant_info(experiment_id, user_id)
        return info['participant_id'] if info else None
    
    def _get_participant_variant(self, participant_id: str) -> Optional[str]:
        """Busca a variante de um participante"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT variant_id FROM participants WHERE id = ?
                """, (participant_id,))
                
                row = cursor.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            logger.error(f"Erro ao buscar variante do participante: {str(e)}")
            return None
    
    def _calculate_overall_confidence(self, results: List[StatisticalResult]) -> float:
        """Calcula nível de confiança geral baseado nos resultados"""
        if not results:
            return 0.0
        
        # Média dos níveis de confiança (1 - p_value)
        confidence_levels = [1 - result.p_value for result in results if result.significant]
        
        if not confidence_levels:
            return 0.0
        
        return np.mean(confidence_levels)
    
    def _generate_recommendation(self, results: List[StatisticalResult], 
                                winner_variant: Optional[str], 
                                confidence_level: float) -> str:
        """Gera recomendação baseada nos resultados"""
        if not results:
            return "Dados insuficientes para análise"
        
        if not winner_variant:
            return "Nenhuma variante mostrou melhoria significativa"
        
        if confidence_level < 0.8:
            return f"Variante {winner_variant} pode ser melhor, mas confiança baixa ({confidence_level:.1%})"
        
        return f"Recomenda-se implementar variante {winner_variant} (confiança: {confidence_level:.1%})"
    
    def _save_statistical_results(self, results: List[StatisticalResult]):
        """Salva resultados estatísticos no banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for result in results:
                    cursor.execute("""
                        INSERT INTO statistical_results (
                            id, experiment_id, metric, variant_id, mean_value,
                            std_deviation, sample_size, standard_error,
                            confidence_interval_lower, confidence_interval_upper,
                            p_value, test_statistic, significant,
                            difference_from_control, improvement_percentage
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(uuid.uuid4()), result.metric, result.variant_id,
                        result.mean_value, result.std_deviation, result.sample_size,
                        result.standard_error, result.confidence_interval_lower,
                        result.confidence_interval_upper, result.p_value,
                        result.test_statistic, result.significant,
                        result.difference_from_control, result.improvement_percentage
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao salvar resultados estatísticos: {str(e)}")
    
    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """Retorna resumo de um experimento"""
        try:
            experiment_data = self._get_experiment_data(experiment_id)
            if not experiment_data:
                return {}
            
            # Buscar estatísticas por variante
            variant_stats = {}
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for variant_id in experiment_data['variant_ids']:
                    cursor.execute("""
                        SELECT COUNT(*) FROM participants 
                        WHERE experiment_id = ? AND variant_id = ? AND active = 1
                    """, (experiment_id, variant_id))
                    
                    participants = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM conversion_events 
                        WHERE experiment_id = ? AND variant_id = ?
                    """, (experiment_id, variant_id))
                    
                    conversions = cursor.fetchone()[0]
                    
                    variant_stats[variant_id] = {
                        'participants': participants,
                        'conversions': conversions,
                        'conversion_rate': (conversions / participants * 100) if participants > 0 else 0
                    }
            
            return {
                'experiment': experiment_data,
                'variant_stats': variant_stats,
                'total_participants': experiment_data['total_participants'],
                'total_conversions': experiment_data['total_conversions'],
                'overall_conversion_rate': (
                    experiment_data['total_conversions'] / experiment_data['total_participants'] * 100
                ) if experiment_data['total_participants'] > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {str(e)}")
            return {}
    
    def stop_experiment(self, experiment_id: str) -> bool:
        """Para um experimento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE experiments 
                    SET status = 'completed', end_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (experiment_id,))
                
                conn.commit()
            
            # Remover do cache
            if experiment_id in self.active_experiments:
                del self.active_experiments[experiment_id]
                ACTIVE_EXPERIMENTS.set(len(self.active_experiments))
            
            EXPERIMENT_COMPLETED.inc()
            logger.info(f"Experimento parado: {experiment_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar experimento: {str(e)}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Remove dados antigos do sistema"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remover eventos antigos
                cursor.execute("""
                    DELETE FROM conversion_events 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                # Remover participantes inativos
                cursor.execute("""
                    DELETE FROM participants 
                    WHERE last_activity < ? AND active = 0
                """, (cutoff_date,))
                
                conn.commit()
            
            logger.info(f"Limpeza concluída. Dados anteriores a {cutoff_date} removidos")
            
        except Exception as e:
            logger.error(f"Erro na limpeza: {str(e)}")

# Instância global do sistema
ab_testing_system = ABTestingSystem() 