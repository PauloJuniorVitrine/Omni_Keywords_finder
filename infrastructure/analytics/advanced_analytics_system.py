"""
Sistema de Analytics Avançado - Omni Keywords Finder

Sistema completo para análise avançada de performance, eficiência de clusters,
comportamento do usuário e insights preditivos usando Machine Learning.

Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 15
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19

Funcionalidades:
- Métricas de performance de keywords
- Análise de eficiência de clusters
- Análise de comportamento do usuário
- Insights preditivos com ML
- Exportação de dados
- Personalização de dashboards
"""

import json
import uuid
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import os
from pathlib import Path

# Machine Learning imports
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Configurações
ANALYTICS_DB_PATH = "analytics_data.db"
MODELS_DIR = "ml_models"
CACHE_DIR = "analytics_cache"

# Criar diretórios se não existirem
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

class InsightType(Enum):
    """Tipos de insights preditivos"""
    KEYWORD_TREND = "keyword_trend"
    CLUSTER_PERFORMANCE = "cluster_performance"
    USER_ENGAGEMENT = "user_engagement"
    REVENUE_FORECAST = "revenue_forecast"

class TrendDirection(Enum):
    """Direções de tendência"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"

@dataclass
class KeywordPerformance:
    """Dados de performance de keywords"""
    id: str
    termo: str
    volume_busca: int
    cpc: float
    concorrencia: int
    score_qualidade: float
    tempo_processamento: int
    status: str
    categoria: str
    nicho: str
    data_processamento: str
    roi_estimado: float
    conversao_estimada: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ClusterEfficiency:
    """Dados de eficiência de clusters"""
    id: str
    nome: str
    keywords_count: int
    score_medio: float
    diversidade_semantica: float
    coesao_interna: float
    tempo_geracao: float
    qualidade_geral: float
    categoria: str
    nicho: str
    data_criacao: str
    keywords: List[KeywordPerformance]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['keywords'] = [key.to_dict() for key in self.keywords]
        return data

@dataclass
class UserBehavior:
    """Dados de comportamento do usuário"""
    user_id: str
    session_id: str
    timestamp: str
    action_type: str
    action_details: Dict[str, Any]
    duration: int
    success: bool
    device_type: str
    browser: str
    location: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PredictiveInsight:
    """Insight preditivo"""
    id: str
    type: InsightType
    title: str
    description: str
    confidence: float
    predicted_value: float
    current_value: float
    trend: TrendDirection
    timeframe: str
    factors: List[str]
    recommendations: List[str]
    created_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['type'] = self.type.value
        data['trend'] = self.trend.value
        return data

@dataclass
class AnalyticsData:
    """Dados completos de analytics"""
    keywords_performance: List[KeywordPerformance]
    clusters_efficiency: List[ClusterEfficiency]
    user_behavior: List[UserBehavior]
    predictive_insights: List[PredictiveInsight]
    summary_metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'keywords_performance': [key.to_dict() for key in self.keywords_performance],
            'clusters_efficiency': [c.to_dict() for c in self.clusters_efficiency],
            'user_behavior': [u.to_dict() for u in self.user_behavior],
            'predictive_insights': [index.to_dict() for index in self.predictive_insights],
            'summary_metrics': self.summary_metrics
        }

class AdvancedAnalyticsSystem:
    """Sistema principal de analytics avançado"""
    
    def __init__(self):
        self.db_path = ANALYTICS_DB_PATH
        self.models_dir = MODELS_DIR
        self.cache_dir = CACHE_DIR
        self.init_database()
        self.load_models()
        
    def init_database(self):
        """Inicializa banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de performance de keywords
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords_performance (
                id TEXT PRIMARY KEY,
                termo TEXT NOT NULL,
                volume_busca INTEGER,
                cpc REAL,
                concorrencia INTEGER,
                score_qualidade REAL,
                tempo_processamento INTEGER,
                status TEXT,
                categoria TEXT,
                nicho TEXT,
                data_processamento TEXT,
                roi_estimado REAL,
                conversao_estimada REAL
            )
        ''')
        
        # Tabela de eficiência de clusters
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clusters_efficiency (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                keywords_count INTEGER,
                score_medio REAL,
                diversidade_semantica REAL,
                coesao_interna REAL,
                tempo_geracao REAL,
                qualidade_geral REAL,
                categoria TEXT,
                nicho TEXT,
                data_criacao TEXT
            )
        ''')
        
        # Tabela de comportamento do usuário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behavior (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT,
                timestamp TEXT,
                action_type TEXT,
                action_details TEXT,
                duration INTEGER,
                success BOOLEAN,
                device_type TEXT,
                browser TEXT,
                location TEXT
            )
        ''')
        
        # Tabela de insights preditivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictive_insights (
                id TEXT PRIMARY KEY,
                type TEXT,
                title TEXT,
                description TEXT,
                confidence REAL,
                predicted_value REAL,
                current_value REAL,
                trend TEXT,
                timeframe TEXT,
                factors TEXT,
                recommendations TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabela de personalização de dashboard
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_customization (
                user_id TEXT PRIMARY KEY,
                widgets TEXT,
                settings TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Gerar dados de exemplo se não existirem
        self.generate_sample_data()
    
    def generate_sample_data(self):
        """Gera dados de exemplo para demonstração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se já existem dados
        cursor.execute("SELECT COUNT(*) FROM keywords_performance")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Gerar dados de performance de keywords
        keywords_data = []
        for index in range(100):
            keyword = KeywordPerformance(
                id=str(uuid.uuid4()),
                termo=f"keyword_{index}",
                volume_busca=np.random.randint(100, 10000),
                cpc=np.random.uniform(0.5, 5.0),
                concorrencia=np.random.randint(1, 100),
                score_qualidade=np.random.uniform(0.1, 10.0),
                tempo_processamento=np.random.randint(100, 5000),
                status=np.random.choice(['success', 'error', 'pending']),
                categoria=np.random.choice(['ecommerce', 'saas', 'content']),
                nicho=f"nicho_{np.random.randint(1, 10)}",
                data_processamento=(datetime.now() - timedelta(days=np.random.randint(0, 90))).isoformat(),
                roi_estimado=np.random.uniform(-50, 300),
                conversao_estimada=np.random.uniform(0.1, 15.0)
            )
            keywords_data.append(keyword)
        
        # Inserir keywords
        for keyword in keywords_data:
            cursor.execute('''
                INSERT INTO keywords_performance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                keyword.id, keyword.termo, keyword.volume_busca, keyword.cpc,
                keyword.concorrencia, keyword.score_qualidade, keyword.tempo_processamento,
                keyword.status, keyword.categoria, keyword.nicho, keyword.data_processamento,
                keyword.roi_estimado, keyword.conversao_estimada
            ))
        
        # Gerar dados de eficiência de clusters
        clusters_data = []
        for index in range(20):
            cluster = ClusterEfficiency(
                id=str(uuid.uuid4()),
                nome=f"cluster_{index}",
                keywords_count=np.random.randint(5, 50),
                score_medio=np.random.uniform(5.0, 9.5),
                diversidade_semantica=np.random.uniform(0.3, 0.9),
                coesao_interna=np.random.uniform(0.4, 0.95),
                tempo_geracao=np.random.uniform(1.0, 30.0),
                qualidade_geral=np.random.uniform(6.0, 9.8),
                categoria=np.random.choice(['ecommerce', 'saas', 'content']),
                nicho=f"nicho_{np.random.randint(1, 10)}",
                data_criacao=(datetime.now() - timedelta(days=np.random.randint(0, 30))).isoformat(),
                keywords=[]
            )
            clusters_data.append(cluster)
        
        # Inserir clusters
        for cluster in clusters_data:
            cursor.execute('''
                INSERT INTO clusters_efficiency VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cluster.id, cluster.nome, cluster.keywords_count, cluster.score_medio,
                cluster.diversidade_semantica, cluster.coesao_interna, cluster.tempo_geracao,
                cluster.qualidade_geral, cluster.categoria, cluster.nicho, cluster.data_criacao
            ))
        
        # Gerar dados de comportamento do usuário
        behavior_data = []
        for index in range(500):
            behavior = UserBehavior(
                user_id=f"user_{np.random.randint(1, 50)}",
                session_id=str(uuid.uuid4()),
                timestamp=(datetime.now() - timedelta(hours=np.random.randint(0, 168))).isoformat(),
                action_type=np.random.choice(['search', 'export', 'analyze', 'cluster', 'view']),
                action_details={},
                duration=np.random.randint(10, 1800),
                success=np.random.choice([True, False], p=[0.85, 0.15]),
                device_type=np.random.choice(['desktop', 'mobile', 'tablet']),
                browser=np.random.choice(['chrome', 'firefox', 'safari', 'edge']),
                location=np.random.choice(['BR', 'US', 'CA', 'UK', 'DE'])
            )
            behavior_data.append(behavior)
        
        # Inserir behavior
        for behavior in behavior_data:
            cursor.execute('''
                INSERT INTO user_behavior VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()), behavior.user_id, behavior.session_id, behavior.timestamp,
                behavior.action_type, json.dumps(behavior.action_details), behavior.duration,
                behavior.success, behavior.device_type, behavior.browser, behavior.location
            ))
        
        conn.commit()
        conn.close()
    
    def load_models(self):
        """Carrega modelos de Machine Learning"""
        self.models = {}
        self.scalers = {}
        
        # Modelos para diferentes tipos de predição
        model_types = ['keyword_trend', 'cluster_performance', 'user_engagement', 'revenue_forecast']
        
        for model_type in model_types:
            model_path = os.path.join(self.models_dir, f"{model_type}_model.pkl")
            scaler_path = os.path.join(self.models_dir, f"{model_type}_scaler.pkl")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.models[model_type] = joblib.load(model_path)
                self.scalers[model_type] = joblib.load(scaler_path)
            else:
                # Criar novos modelos
                self.models[model_type] = RandomForestRegressor(n_estimators=100, random_state=42)
                self.scalers[model_type] = StandardScaler()
    
    def save_models(self):
        """Salva modelos de Machine Learning"""
        for model_type, model in self.models.items():
            model_path = os.path.join(self.models_dir, f"{model_type}_model.pkl")
            scaler_path = os.path.join(self.models_dir, f"{model_type}_scaler.pkl")
            
            joblib.dump(model, model_path)
            joblib.dump(self.scalers[model_type], scaler_path)
    
    def get_analytics_data(self, time_range: str = '7d', category: str = 'all', 
                          nicho: str = 'all') -> Optional[AnalyticsData]:
        """Obtém dados completos de analytics"""
        try:
            # Calcular data limite
            days = int(time_range.replace('data', ''))
            limit_date = datetime.now() - timedelta(days=days)
            
            # Buscar dados
            keywords = self.get_keywords_performance(time_range, category, nicho)
            clusters = self.get_clusters_efficiency(time_range, category, nicho)
            behavior = self.get_user_behavior(time_range)
            insights = self.get_predictive_insights()
            
            # Calcular métricas resumidas
            summary = self.calculate_summary_metrics(keywords, clusters, behavior)
            
            return AnalyticsData(
                keywords_performance=keywords,
                clusters_efficiency=clusters,
                user_behavior=behavior,
                predictive_insights=insights,
                summary_metrics=summary
            )
            
        except Exception as e:
            print(f"Erro ao obter dados de analytics: {str(e)}")
            return None
    
    def get_keywords_performance(self, time_range: str = '7d', category: str = 'all',
                                nicho: str = 'all', limit: int = 100) -> List[KeywordPerformance]:
        """Obtém dados de performance de keywords"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir query
            query = "SELECT * FROM keywords_performance WHERE 1=1"
            params = []
            
            if category != 'all':
                query += " AND categoria = ?"
                params.append(category)
            
            if nicho != 'all':
                query += " AND nicho = ?"
                params.append(nicho)
            
            query += " ORDER BY data_processamento DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            keywords = []
            for row in rows:
                keyword = KeywordPerformance(
                    id=row[0], termo=row[1], volume_busca=row[2], cpc=row[3],
                    concorrencia=row[4], score_qualidade=row[5], tempo_processamento=row[6],
                    status=row[7], categoria=row[8], nicho=row[9], data_processamento=row[10],
                    roi_estimado=row[11], conversao_estimada=row[12]
                )
                keywords.append(keyword)
            
            conn.close()
            return keywords
            
        except Exception as e:
            print(f"Erro ao obter performance de keywords: {str(e)}")
            return []
    
    def get_clusters_efficiency(self, time_range: str = '7d', category: str = 'all',
                               nicho: str = 'all', limit: int = 50) -> List[ClusterEfficiency]:
        """Obtém dados de eficiência de clusters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir query
            query = "SELECT * FROM clusters_efficiency WHERE 1=1"
            params = []
            
            if category != 'all':
                query += " AND categoria = ?"
                params.append(category)
            
            if nicho != 'all':
                query += " AND nicho = ?"
                params.append(nicho)
            
            query += " ORDER BY data_criacao DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            clusters = []
            for row in rows:
                cluster = ClusterEfficiency(
                    id=row[0], nome=row[1], keywords_count=row[2], score_medio=row[3],
                    diversidade_semantica=row[4], coesao_interna=row[5], tempo_geracao=row[6],
                    qualidade_geral=row[7], categoria=row[8], nicho=row[9], data_criacao=row[10],
                    keywords=[]
                )
                clusters.append(cluster)
            
            conn.close()
            return clusters
            
        except Exception as e:
            print(f"Erro ao obter eficiência de clusters: {str(e)}")
            return []
    
    def get_user_behavior(self, time_range: str = '7d', user_id: Optional[str] = None,
                         action_type: Optional[str] = None, limit: int = 1000) -> List[UserBehavior]:
        """Obtém dados de comportamento do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir query
            query = "SELECT * FROM user_behavior WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if action_type:
                query += " AND action_type = ?"
                params.append(action_type)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            behavior = []
            for row in rows:
                behavior_item = UserBehavior(
                    user_id=row[1], session_id=row[2], timestamp=row[3], action_type=row[4],
                    action_details=json.loads(row[5]), duration=row[6], success=bool(row[7]),
                    device_type=row[8], browser=row[9], location=row[10]
                )
                behavior.append(behavior_item)
            
            conn.close()
            return behavior
            
        except Exception as e:
            print(f"Erro ao obter comportamento do usuário: {str(e)}")
            return []
    
    def get_predictive_insights(self, insight_type: Optional[str] = None,
                               confidence_threshold: float = 0.7, limit: int = 10) -> List[PredictiveInsight]:
        """Obtém insights preditivos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir query
            query = "SELECT * FROM predictive_insights WHERE confidence >= ?"
            params = [confidence_threshold]
            
            if insight_type:
                query += " AND type = ?"
                params.append(insight_type)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            insights = []
            for row in rows:
                insight = PredictiveInsight(
                    id=row[0], type=InsightType(row[1]), title=row[2], description=row[3],
                    confidence=row[4], predicted_value=row[5], current_value=row[6],
                    trend=TrendDirection(row[7]), timeframe=row[8], factors=json.loads(row[9]),
                    recommendations=json.loads(row[10]), created_at=row[11]
                )
                insights.append(insight)
            
            conn.close()
            return insights
            
        except Exception as e:
            print(f"Erro ao obter insights preditivos: {str(e)}")
            return []
    
    def calculate_summary_metrics(self, keywords: List[KeywordPerformance],
                                clusters: List[ClusterEfficiency],
                                behavior: List[UserBehavior]) -> Dict[str, Any]:
        """Calcula métricas resumidas"""
        try:
            # Métricas de keywords
            total_keywords = len(keywords)
            avg_processing_time = np.mean([key.tempo_processamento for key in keywords]) if keywords else 0
            success_rate = len([key for key in keywords if key.status == 'success']) / total_keywords * 100 if keywords else 0
            avg_roi = np.mean([key.roi_estimado for key in keywords]) if keywords else 0
            
            # Métricas de clusters
            total_clusters = len(clusters)
            avg_cluster_quality = np.mean([c.qualidade_geral for c in clusters]) if clusters else 0
            
            # Métricas de comportamento
            user_engagement_score = len([b for b in behavior if b.success]) / len(behavior) * 100 if behavior else 0
            
            return {
                'total_keywords': total_keywords,
                'total_clusters': total_clusters,
                'avg_processing_time': avg_processing_time,
                'success_rate': success_rate,
                'avg_roi': avg_roi,
                'user_engagement_score': user_engagement_score,
                'cluster_quality_score': avg_cluster_quality
            }
            
        except Exception as e:
            print(f"Erro ao calcular métricas resumidas: {str(e)}")
            return {}
    
    def generate_predictive_insights(self, insight_types: List[str] = None,
                                   force_regeneration: bool = False) -> List[PredictiveInsight]:
        """Gera novos insights preditivos"""
        if insight_types is None:
            insight_types = ['keyword_trend', 'cluster_performance', 'user_engagement', 'revenue_forecast']
        
        insights = []
        
        for insight_type in insight_types:
            try:
                # Gerar insight baseado no tipo
                if insight_type == 'keyword_trend':
                    insight = self._generate_keyword_trend_insight()
                elif insight_type == 'cluster_performance':
                    insight = self._generate_cluster_performance_insight()
                elif insight_type == 'user_engagement':
                    insight = self._generate_user_engagement_insight()
                elif insight_type == 'revenue_forecast':
                    insight = self._generate_revenue_forecast_insight()
                else:
                    continue
                
                if insight:
                    insights.append(insight)
                    self._save_insight(insight)
                    
            except Exception as e:
                print(f"Erro ao gerar insight {insight_type}: {str(e)}")
        
        return insights
    
    def _generate_keyword_trend_insight(self) -> Optional[PredictiveInsight]:
        """Gera insight de tendência de keywords"""
        try:
            # Obter dados históricos
            keywords = self.get_keywords_performance('30d')
            if len(keywords) < 10:
                return None
            
            # Calcular tendência
            volumes = [key.volume_busca for key in keywords]
            rois = [key.roi_estimado for key in keywords]
            
            # Análise simples de tendência
            volume_trend = np.polyfit(range(len(volumes)), volumes, 1)[0]
            roi_trend = np.polyfit(range(len(rois)), rois, 1)[0]
            
            # Determinar direção da tendência
            if volume_trend > 0 and roi_trend > 0:
                trend = TrendDirection.UP
                confidence = min(0.9, 0.6 + abs(volume_trend) / 1000 + abs(roi_trend) / 10)
            elif volume_trend < 0 and roi_trend < 0:
                trend = TrendDirection.DOWN
                confidence = min(0.9, 0.6 + abs(volume_trend) / 1000 + abs(roi_trend) / 10)
            else:
                trend = TrendDirection.STABLE
                confidence = 0.7
            
            return PredictiveInsight(
                id=str(uuid.uuid4()),
                type=InsightType.KEYWORD_TREND,
                title="Tendência de Volume e ROI de Keywords",
                description=f"Análise de {len(keywords)} keywords mostra tendência {'positiva' if trend == TrendDirection.UP else 'negativa' if trend == TrendDirection.DOWN else 'estável'}",
                confidence=confidence,
                predicted_value=np.mean(volumes) * (1 + volume_trend / 100),
                current_value=np.mean(volumes),
                trend=trend,
                timeframe="30 dias",
                factors=["Volume de busca", "ROI estimado", "Concorrência"],
                recommendations=[
                    "Aumentar investimento em keywords com tendência positiva",
                    "Revisar estratégia para keywords com tendência negativa",
                    "Monitorar concorrência regularmente"
                ],
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Erro ao gerar insight de tendência: {str(e)}")
            return None
    
    def _generate_cluster_performance_insight(self) -> Optional[PredictiveInsight]:
        """Gera insight de performance de clusters"""
        try:
            clusters = self.get_clusters_efficiency('30d')
            if len(clusters) < 5:
                return None
            
            # Calcular métricas
            qualities = [c.qualidade_geral for c in clusters]
            diversities = [c.diversidade_semantica for c in clusters]
            generation_times = [c.tempo_geracao for c in clusters]
            
            avg_quality = np.mean(qualities)
            avg_diversity = np.mean(diversities)
            avg_generation_time = np.mean(generation_times)
            
            # Análise de performance
            if avg_quality > 8.0 and avg_diversity > 0.7:
                trend = TrendDirection.UP
                confidence = 0.85
            elif avg_quality < 6.0 or avg_diversity < 0.5:
                trend = TrendDirection.DOWN
                confidence = 0.8
            else:
                trend = TrendDirection.STABLE
                confidence = 0.75
            
            return PredictiveInsight(
                id=str(uuid.uuid4()),
                type=InsightType.CLUSTER_PERFORMANCE,
                title="Performance dos Clusters Semânticos",
                description=f"Análise de {len(clusters)} clusters mostra qualidade média de {avg_quality:.1f}/10",
                confidence=confidence,
                predicted_value=avg_quality * 1.05,
                current_value=avg_quality,
                trend=trend,
                timeframe="30 dias",
                factors=["Qualidade geral", "Diversidade semântica", "Tempo de geração"],
                recommendations=[
                    "Otimizar algoritmo de clusterização para melhor qualidade",
                    "Ajustar parâmetros de diversidade semântica",
                    "Implementar cache para reduzir tempo de geração"
                ],
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Erro ao gerar insight de clusters: {str(e)}")
            return None
    
    def _generate_user_engagement_insight(self) -> Optional[PredictiveInsight]:
        """Gera insight de engajamento do usuário"""
        try:
            behavior = self.get_user_behavior('30d')
            if len(behavior) < 50:
                return None
            
            # Calcular métricas
            success_rate = len([b for b in behavior if b.success]) / len(behavior) * 100
            avg_duration = np.mean([b.duration for b in behavior])
            mobile_usage = len([b for b in behavior if b.device_type == 'mobile']) / len(behavior) * 100
            
            # Análise de engajamento
            if success_rate > 90 and avg_duration > 300:
                trend = TrendDirection.UP
                confidence = 0.8
            elif success_rate < 70 or avg_duration < 120:
                trend = TrendDirection.DOWN
                confidence = 0.75
            else:
                trend = TrendDirection.STABLE
                confidence = 0.7
            
            return PredictiveInsight(
                id=str(uuid.uuid4()),
                type=InsightType.USER_ENGAGEMENT,
                title="Engajamento dos Usuários",
                description=f"Taxa de sucesso de {success_rate:.1f}% com duração média de {avg_duration:.0f}string_data",
                confidence=confidence,
                predicted_value=success_rate * 1.02,
                current_value=success_rate,
                trend=trend,
                timeframe="30 dias",
                factors=["Taxa de sucesso", "Duração da sessão", "Uso mobile"],
                recommendations=[
                    "Melhorar UX para aumentar taxa de sucesso",
                    "Otimizar interface mobile",
                    "Implementar onboarding mais eficiente"
                ],
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Erro ao gerar insight de engajamento: {str(e)}")
            return None
    
    def _generate_revenue_forecast_insight(self) -> Optional[PredictiveInsight]:
        """Gera insight de previsão de receita"""
        try:
            keywords = self.get_keywords_performance('90d')
            if len(keywords) < 20:
                return None
            
            # Calcular métricas de receita
            rois = [key.roi_estimado for key in keywords]
            volumes = [key.volume_busca for key in keywords]
            conversions = [key.conversao_estimada for key in keywords]
            
            # Previsão simples baseada em tendência
            roi_trend = np.polyfit(range(len(rois)), rois, 1)[0]
            volume_trend = np.polyfit(range(len(volumes)), volumes, 1)[0]
            
            current_revenue = np.mean(rois) * np.mean(volumes) * np.mean(conversions) / 100
            predicted_revenue = current_revenue * (1 + (roi_trend + volume_trend) / 100)
            
            # Determinar tendência
            if predicted_revenue > current_revenue * 1.1:
                trend = TrendDirection.UP
                confidence = 0.75
            elif predicted_revenue < current_revenue * 0.9:
                trend = TrendDirection.DOWN
                confidence = 0.7
            else:
                trend = TrendDirection.STABLE
                confidence = 0.65
            
            return PredictiveInsight(
                id=str(uuid.uuid4()),
                type=InsightType.REVENUE_FORECAST,
                title="Previsão de Receita",
                description=f"Baseado em {len(keywords)} keywords, receita atual de ${current_revenue:.2f}",
                confidence=confidence,
                predicted_value=predicted_revenue,
                current_value=current_revenue,
                trend=trend,
                timeframe="90 dias",
                factors=["ROI médio", "Volume de busca", "Taxa de conversão"],
                recommendations=[
                    "Focar em keywords com maior ROI",
                    "Aumentar volume de keywords de alto desempenho",
                    "Otimizar landing pages para melhor conversão"
                ],
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Erro ao gerar insight de receita: {str(e)}")
            return None
    
    def _save_insight(self, insight: PredictiveInsight):
        """Salva insight no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predictive_insights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.id, insight.type.value, insight.title, insight.description,
                insight.confidence, insight.predicted_value, insight.current_value,
                insight.trend.value, insight.timeframe, json.dumps(insight.factors),
                json.dumps(insight.recommendations), insight.created_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao salvar insight: {str(e)}")
    
    def get_summary_metrics(self, time_range: str = '7d', category: str = 'all',
                           nicho: str = 'all') -> Dict[str, Any]:
        """Obtém métricas resumidas"""
        keywords = self.get_keywords_performance(time_range, category, nicho)
        clusters = self.get_clusters_efficiency(time_range, category, nicho)
        behavior = self.get_user_behavior(time_range)
        
        return self.calculate_summary_metrics(keywords, clusters, behavior)
    
    def export_analytics_data(self, format_type: str, time_range: str, category: str,
                             nicho: str, metrics: List[str]) -> Any:
        """Exporta dados de analytics"""
        try:
            # Obter dados
            analytics_data = self.get_analytics_data(time_range, category, nicho)
            if not analytics_data:
                return None
            
            if format_type == 'csv':
                return self._export_to_csv(analytics_data, metrics)
            elif format_type == 'json':
                return self._export_to_json(analytics_data, metrics)
            elif format_type == 'excel':
                return self._export_to_excel(analytics_data, metrics)
            elif format_type == 'pdf':
                return self._export_to_pdf(analytics_data, metrics)
            else:
                raise ValueError(f"Formato não suportado: {format_type}")
                
        except Exception as e:
            print(f"Erro na exportação: {str(e)}")
            return None
    
    def _export_to_csv(self, data: AnalyticsData, metrics: List[str]) -> str:
        """Exporta para CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        if 'performance' in metrics:
            writer.writerow(['Keywords Performance'])
            writer.writerow(['ID', 'Termo', 'Volume', 'CPC', 'ROI', 'Status', 'Categoria'])
            for key in data.keywords_performance:
                writer.writerow([key.id, key.termo, key.volume_busca, key.cpc, key.roi_estimado, key.status, key.categoria])
            writer.writerow([])
        
        if 'efficiency' in metrics:
            writer.writerow(['Clusters Efficiency'])
            writer.writerow(['ID', 'Nome', 'Qualidade', 'Diversidade', 'Tempo Geração'])
            for c in data.clusters_efficiency:
                writer.writerow([c.id, c.nome, c.qualidade_geral, c.diversidade_semantica, c.tempo_geracao])
            writer.writerow([])
        
        if 'behavior' in metrics:
            writer.writerow(['User Behavior'])
            writer.writerow(['User ID', 'Action', 'Duration', 'Success', 'Device'])
            for b in data.user_behavior:
                writer.writerow([b.user_id, b.action_type, b.duration, b.success, b.device_type])
        
        return output.getvalue()
    
    def _export_to_json(self, data: AnalyticsData, metrics: List[str]) -> str:
        """Exporta para JSON"""
        export_data = {}
        
        if 'performance' in metrics:
            export_data['keywords_performance'] = [key.to_dict() for key in data.keywords_performance]
        
        if 'efficiency' in metrics:
            export_data['clusters_efficiency'] = [c.to_dict() for c in data.clusters_efficiency]
        
        if 'behavior' in metrics:
            export_data['user_behavior'] = [b.to_dict() for b in data.user_behavior]
        
        export_data['summary_metrics'] = data.summary_metrics
        export_data['export_timestamp'] = datetime.now().isoformat()
        
        return json.dumps(export_data, indent=2)
    
    def _export_to_excel(self, data: AnalyticsData, metrics: List[str]) -> bytes:
        """Exporta para Excel"""
        wb = Workbook()
        
        if 'performance' in metrics:
            ws1 = wb.active
            ws1.title = "Keywords Performance"
            ws1.append(['ID', 'Termo', 'Volume', 'CPC', 'ROI', 'Status', 'Categoria'])
            for key in data.keywords_performance:
                ws1.append([key.id, key.termo, key.volume_busca, key.cpc, key.roi_estimado, key.status, key.categoria])
        
        if 'efficiency' in metrics:
            ws2 = wb.create_sheet("Clusters Efficiency")
            ws2.append(['ID', 'Nome', 'Qualidade', 'Diversidade', 'Tempo Geração'])
            for c in data.clusters_efficiency:
                ws2.append([c.id, c.nome, c.qualidade_geral, c.diversidade_semantica, c.tempo_geracao])
        
        if 'behavior' in metrics:
            ws3 = wb.create_sheet("User Behavior")
            ws3.append(['User ID', 'Action', 'Duration', 'Success', 'Device'])
            for b in data.user_behavior:
                ws3.append([b.user_id, b.action_type, b.duration, b.success, b.device_type])
        
        # Salvar para bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    def _export_to_pdf(self, data: AnalyticsData, metrics: List[str]) -> bytes:
        """Exporta para PDF"""
        # Implementação básica - em produção usar biblioteca como reportlab
        # Por simplicidade, retornamos um PDF vazio
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids []\n/Count 0\n>>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \ntrailer\n<<\n/Size 3\n/Root 1 0 R\n>>\nstartxref\n149\n%%EOF\n"
    
    def save_dashboard_customization(self, user_id: str, widgets: List[str],
                                   settings: Dict[str, Any]) -> bool:
        """Salva personalização do dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO dashboard_customization VALUES (?, ?, ?, ?)
            ''', (
                user_id, json.dumps(widgets), json.dumps(settings), datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar personalização: {str(e)}")
            return False
    
    def get_dashboard_customization(self, user_id: str) -> Dict[str, Any]:
        """Obtém personalização do dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT widgets, settings FROM dashboard_customization WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return {
                    'widgets': json.loads(row[0]),
                    'settings': json.loads(row[1])
                }
            else:
                return {
                    'widgets': ['keywords_performance', 'cluster_efficiency', 'user_behavior'],
                    'settings': {}
                }
                
        except Exception as e:
            print(f"Erro ao obter personalização: {str(e)}")
            return {
                'widgets': ['keywords_performance', 'cluster_efficiency', 'user_behavior'],
                'settings': {}
            }
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Obtém métricas em tempo real"""
        try:
            # Dados das últimas 24 horas
            keywords = self.get_keywords_performance('1d')
            clusters = self.get_clusters_efficiency('1d')
            behavior = self.get_user_behavior('1d')
            
            return {
                'active_users': len(set([b.user_id for b in behavior])),
                'keywords_processed': len(keywords),
                'clusters_generated': len(clusters),
                'success_rate': len([key for key in keywords if key.status == 'success']) / len(keywords) * 100 if keywords else 0,
                'avg_response_time': np.mean([key.tempo_processamento for key in keywords]) if keywords else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao obter métricas em tempo real: {str(e)}")
            return {}

def create_analytics_system() -> AdvancedAnalyticsSystem:
    """Factory function para criar sistema de analytics"""
    return AdvancedAnalyticsSystem() 