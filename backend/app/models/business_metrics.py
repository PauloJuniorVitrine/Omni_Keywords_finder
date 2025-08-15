from typing import Dict, List, Optional, Any
"""
Modelo de dados para métricas de Business Intelligence
Tracking de ROI, conversões, rankings e insights preditivos
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import JSONB
from .nicho import db

class KeywordMetrics(db.Model):
    """Métricas detalhadas por keyword"""
    __tablename__ = 'keyword_metrics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.String(255), nullable=False, index=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Métricas de Volume
    search_volume = db.Column(db.Integer, nullable=True)
    search_volume_change = db.Column(db.Float, nullable=True)  # % de mudança
    
    # Métricas de Ranking
    current_ranking = db.Column(db.Integer, nullable=True)
    previous_ranking = db.Column(db.Integer, nullable=True)
    ranking_improvement = db.Column(db.Float, nullable=True)  # % de melhoria
    
    # Métricas de Conversão
    click_through_rate = db.Column(db.Float, nullable=True)  # CTR %
    conversion_rate = db.Column(db.Float, nullable=True)  # CR %
    cost_per_click = db.Column(db.Float, nullable=True)  # CPC
    cost_per_conversion = db.Column(db.Float, nullable=True)  # CPA
    
    # Métricas de ROI
    revenue_generated = db.Column(db.Float, nullable=True)
    cost_incurred = db.Column(db.Float, nullable=True)
    roi_percentage = db.Column(db.Float, nullable=True)
    profit_margin = db.Column(db.Float, nullable=True)
    
    # Métricas de Performance
    impressions = db.Column(db.Integer, nullable=True)
    clicks = db.Column(db.Integer, nullable=True)
    conversions = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    data_coleta = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)
    
    # Relacionamentos
    categoria = db.relationship('Categoria', backref='keyword_metrics')
    
    def __repr__(self):
        return f"<KeywordMetrics(keyword='{self.keyword}', roi={self.roi_percentage}%)>"

class CategoryROI(db.Model):
    """ROI agregado por categoria"""
    __tablename__ = 'category_roi'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Métricas de ROI
    total_revenue = db.Column(db.Float, default=0.0, nullable=False)
    total_cost = db.Column(db.Float, default=0.0, nullable=False)
    total_roi = db.Column(db.Float, default=0.0, nullable=False)
    roi_percentage = db.Column(db.Float, default=0.0, nullable=False)
    
    # Métricas de Performance
    total_keywords = db.Column(db.Integer, default=0, nullable=False)
    active_keywords = db.Column(db.Integer, default=0, nullable=False)
    avg_ranking = db.Column(db.Float, nullable=True)
    avg_conversion_rate = db.Column(db.Float, nullable=True)
    
    # Período
    periodo_inicio = db.Column(db.Date, nullable=False)
    periodo_fim = db.Column(db.Date, nullable=False)
    
    # Timestamps
    data_calculo = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    
    # Relacionamentos
    categoria = db.relationship('Categoria', backref='roi_metrics')
    
    def __repr__(self):
        return f"<CategoryROI(categoria={self.categoria_id}, roi={self.roi_percentage}%)>"

class ConversionTracking(db.Model):
    """Tracking detalhado de conversões"""
    __tablename__ = 'conversion_tracking'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.String(255), nullable=False, index=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Dados da Conversão
    conversion_id = db.Column(db.String(255), nullable=False, unique=True)
    conversion_type = db.Column(db.String(50), nullable=False)  # 'sale', 'lead', 'signup'
    conversion_value = db.Column(db.Float, nullable=False)
    conversion_currency = db.Column(db.String(3), default='BRL', nullable=False)
    
    # Dados do Usuário
    user_id = db.Column(db.String(255), nullable=True)
    session_id = db.Column(db.String(255), nullable=True)
    
    # Dados de Origem
    source = db.Column(db.String(50), nullable=True)  # 'organic', 'paid', 'direct'
    medium = db.Column(db.String(50), nullable=True)  # 'cpc', 'organic', 'email'
    campaign = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    data_conversao = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    
    # Relacionamentos
    categoria = db.relationship('Categoria', backref='conversions')
    
    def __repr__(self):
        return f"<ConversionTracking(conversion_id='{self.conversion_id}', value={self.conversion_value})>"

class RankingHistory(db.Model):
    """Histórico de rankings para análise temporal"""
    __tablename__ = 'ranking_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.String(255), nullable=False, index=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Dados do Ranking
    ranking_position = db.Column(db.Integer, nullable=False)
    search_engine = db.Column(db.String(50), default='google', nullable=False)
    device_type = db.Column(db.String(20), default='desktop', nullable=False)  # desktop, mobile, tablet
    
    # Métricas Adicionais
    search_volume = db.Column(db.Integer, nullable=True)
    click_through_rate = db.Column(db.Float, nullable=True)
    
    # Timestamps
    data_ranking = db.Column(db.Date, nullable=False)
    data_coleta = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    
    # Relacionamentos
    categoria = db.relationship('Categoria', backref='ranking_history')
    
    def __repr__(self):
        return f"<RankingHistory(keyword='{self.keyword}', position={self.ranking_position})>"

class PredictiveInsights(db.Model):
    """Insights preditivos baseados em ML"""
    __tablename__ = 'predictive_insights'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.String(255), nullable=False, index=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Previsões
    predicted_ranking_30d = db.Column(db.Integer, nullable=True)
    predicted_ranking_60d = db.Column(db.Integer, nullable=True)
    predicted_ranking_90d = db.Column(db.Integer, nullable=True)
    
    predicted_search_volume_30d = db.Column(db.Integer, nullable=True)
    predicted_search_volume_60d = db.Column(db.Integer, nullable=True)
    predicted_search_volume_90d = db.Column(db.Integer, nullable=True)
    
    predicted_conversion_rate_30d = db.Column(db.Float, nullable=True)
    predicted_conversion_rate_60d = db.Column(db.Float, nullable=True)
    predicted_conversion_rate_90d = db.Column(db.Float, nullable=True)
    
    # Confiança das Previsões
    confidence_score = db.Column(db.Float, nullable=True)  # 0-1
    model_version = db.Column(db.String(50), nullable=True)
    
    # Recomendações
    recommendations = db.Column(JSONB, nullable=True)  # JSON com recomendações
    risk_score = db.Column(db.Float, nullable=True)  # 0-1
    
    # Timestamps
    data_previsao = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)
    
    # Relacionamentos
    categoria = db.relationship('Categoria', backref='predictive_insights')
    
    def __repr__(self):
        return f"<PredictiveInsights(keyword='{self.keyword}', confidence={self.confidence_score})>"

class BusinessReport(db.Model):
    """Relatórios automáticos de negócio"""
    __tablename__ = 'business_reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_type = db.Column(db.String(50), nullable=False)  # 'daily', 'weekly', 'monthly', 'quarterly'
    report_period = db.Column(db.String(20), nullable=False)  # '2024-01', '2024-Q1'
    
    # Dados do Relatório
    report_data = db.Column(JSONB, nullable=False)  # JSON com dados do relatório
    summary = db.Column(db.Text, nullable=True)
    
    # Métricas Principais
    total_revenue = db.Column(db.Float, default=0.0, nullable=False)
    total_cost = db.Column(db.Float, default=0.0, nullable=False)
    total_roi = db.Column(db.Float, default=0.0, nullable=False)
    total_conversions = db.Column(db.Integer, default=0, nullable=False)
    avg_conversion_rate = db.Column(db.Float, default=0.0, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='generated', nullable=False)  # generated, sent, archived
    recipients = db.Column(JSONB, nullable=True)  # Lista de destinatários
    
    # Timestamps
    data_geracao = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    data_envio = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f"<BusinessReport(type='{self.report_type}', period='{self.report_period}', roi={self.total_roi})>" 