import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FeedbackMetrics:
    total_feedbacks: int
    average_rating: float
    category_distribution: Dict[str, int]
    recent_trend: float
    sentiment_score: float

class FeedbackProcessor:
    """Processador de feedback para análise e insights"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um novo feedback"""
        try:
            # Análise de sentimento básica
            sentiment = self._analyze_sentiment(feedback_data.get('feedback', ''))
            
            # Categorização automática
            category = self._auto_categorize(feedback_data.get('feedback', ''))
            
            # Priorização
            priority = self._calculate_priority(feedback_data, sentiment)
            
            # Tags automáticas
            tags = self._extract_tags(feedback_data.get('feedback', ''))
            
            processed_data = {
                **feedback_data,
                'sentiment_score': sentiment,
                'auto_category': category,
                'priority': priority,
                'auto_tags': tags,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Feedback processado: {processed_data['id']}")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Erro ao processar feedback: {e}")
            raise
    
    def _analyze_sentiment(self, text: str) -> float:
        """Análise básica de sentimento (0-1, onde 1 é positivo)"""
        positive_words = ['bom', 'excelente', 'ótimo', 'gostei', 'funciona', 'útil']
        negative_words = ['ruim', 'péssimo', 'não funciona', 'problema', 'erro', 'bug']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.5
        
        sentiment = (positive_count - negative_count) / total_words
        return max(0, min(1, sentiment + 0.5))  # Normalizar para 0-1
    
    def _auto_categorize(self, text: str) -> str:
        """Categorização automática baseada no conteúdo"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['bug', 'erro', 'problema', 'não funciona']):
            return 'bug'
        elif any(word in text_lower for word in ['sugestão', 'feature', 'funcionalidade', 'adicionar']):
            return 'feature'
        elif any(word in word in text_lower for word in ['lento', 'performance', 'velocidade']):
            return 'performance'
        elif any(word in text_lower for word in ['interface', 'design', 'ui', 'ux']):
            return 'ui_ux'
        else:
            return 'general'
    
    def _calculate_priority(self, feedback_data: Dict[str, Any], sentiment: float) -> str:
        """Calcula prioridade do feedback"""
        rating = feedback_data.get('rating', 3)
        
        # Prioridade alta para ratings baixos ou sentimentos negativos
        if rating <= 2 or sentiment < 0.3:
            return 'high'
        elif rating <= 3 or sentiment < 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extrai tags relevantes do texto"""
        tags = []
        text_lower = text.lower()
        
        # Tags baseadas em palavras-chave
        keyword_tags = {
            'api': ['api', 'endpoint', 'request'],
            'dashboard': ['dashboard', 'interface', 'tela'],
            'performance': ['lento', 'rápido', 'velocidade'],
            'mobile': ['mobile', 'celular', 'app'],
            'export': ['exportar', 'download', 'csv']
        }
        
        for tag, keywords in keyword_tags.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    async def generate_insights(self, feedbacks: List[Dict[str, Any]]) -> FeedbackMetrics:
        """Gera insights a partir de uma lista de feedbacks"""
        if not feedbacks:
            return FeedbackMetrics(0, 0.0, {}, 0.0, 0.0)
        
        total = len(feedbacks)
        ratings = [f.get('rating', 0) for f in feedbacks]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Distribuição por categoria
        category_dist = {}
        for feedback in feedbacks:
            category = feedback.get('category', 'general')
            category_dist[category] = category_dist.get(category, 0) + 1
        
        # Tendência recente (últimos 7 dias vs anterior)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_feedbacks = [f for f in feedbacks if f.get('timestamp') >= week_ago.isoformat()]
        older_feedbacks = [f for f in feedbacks if f.get('timestamp') < week_ago.isoformat()]
        
        recent_avg = sum(f.get('rating', 0) for f in recent_feedbacks) / len(recent_feedbacks) if recent_feedbacks else 0
        older_avg = sum(f.get('rating', 0) for f in older_feedbacks) / len(older_feedbacks) if older_feedbacks else 0
        recent_trend = recent_avg - older_avg
        
        # Sentimento médio
        sentiments = [f.get('sentiment_score', 0.5) for f in feedbacks]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
        
        return FeedbackMetrics(
            total_feedbacks=total,
            average_rating=average_rating,
            category_distribution=category_dist,
            recent_trend=recent_trend,
            sentiment_score=avg_sentiment
        )
    
    async def send_notifications(self, feedback_data: Dict[str, Any]):
        """Envia notificações para feedbacks importantes"""
        priority = feedback_data.get('priority', 'low')
        
        if priority == 'high':
            # Notificar equipe imediatamente
            await self._send_urgent_notification(feedback_data)
        elif priority == 'medium':
            # Notificar em horário comercial
            await self._send_standard_notification(feedback_data)
    
    async def _send_urgent_notification(self, feedback_data: Dict[str, Any]):
        """Envia notificação urgente"""
        # Implementar integração com Slack, email, etc.
        self.logger.info(f"Notificação urgente enviada para feedback: {feedback_data.get('id')}")
    
    async def _send_standard_notification(self, feedback_data: Dict[str, Any]):
        """Envia notificação padrão"""
        # Implementar notificação em horário comercial
        self.logger.info(f"Notificação padrão enviada para feedback: {feedback_data.get('id')}") 