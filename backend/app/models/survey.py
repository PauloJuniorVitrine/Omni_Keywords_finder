from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class SurveyTypeEnum(str, Enum):
    onboarding = "onboarding"
    periodic = "periodic"
    feature = "feature"
    exit = "exit"

class ExitReasonEnum(str, Enum):
    too_expensive = "too-expensive"
    missing_features = "missing-features"
    difficult_to_use = "difficult-to-use"
    poor_performance = "poor-performance"
    other = "other"

class SurveyBase(BaseModel):
    survey_type: SurveyTypeEnum
    overall_satisfaction: int = Field(..., ge=1, le=5, description="Satisfação geral (1-5)")
    ease_of_use: int = Field(..., ge=1, le=5, description="Facilidade de uso (1-5)")
    feature_completeness: int = Field(..., ge=1, le=5, description="Completude das funcionalidades (1-5)")
    performance: int = Field(..., ge=1, le=5, description="Performance (1-5)")
    support_quality: int = Field(..., ge=1, le=5, description="Qualidade do suporte (1-5)")
    likelihood_to_recommend: int = Field(..., ge=1, le=5, description="Probabilidade de recomendação (1-5)")
    comments: Optional[str] = Field(None, max_length=2000, description="Comentários gerais")
    improvement_suggestions: Optional[str] = Field(None, max_length=2000, description="Sugestões de melhoria")
    email: Optional[str] = Field(None, description="Email para acompanhamento")
    trigger_reason: Optional[str] = Field(None, description="Motivo do disparo da pesquisa")

class SurveyCreate(SurveyBase):
    pass

class SurveyUpdate(BaseModel):
    overall_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    ease_of_use: Optional[int] = Field(None, ge=1, le=5)
    feature_completeness: Optional[int] = Field(None, ge=1, le=5)
    performance: Optional[int] = Field(None, ge=1, le=5)
    support_quality: Optional[int] = Field(None, ge=1, le=5)
    likelihood_to_recommend: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=2000)
    improvement_suggestions: Optional[str] = Field(None, max_length=2000)
    exit_reason: Optional[ExitReasonEnum] = None
    exit_comments: Optional[str] = Field(None, max_length=2000)

class Survey(SurveyBase):
    id: str
    user_id: str
    user_name: str
    created_at: datetime
    updated_at: datetime
    exit_reason: Optional[ExitReasonEnum] = None
    exit_comments: Optional[str] = None
    
    class Config:
        from_attributes = True

class SurveyResponse(BaseModel):
    survey_id: str
    user_id: str
    response_data: Dict[str, Any]
    created_at: datetime

class SurveyStats(BaseModel):
    total_responses: int
    average_satisfaction: float
    average_ease_of_use: float
    average_performance: float
    average_support_quality: float
    nps_score: float
    response_rate: float
    recent_responses: int  # Últimos 30 dias
    survey_type_distribution: Dict[str, int]
    satisfaction_trend: Dict[str, float]

class NPSScore(BaseModel):
    promoters: int  # 9-10
    passives: int   # 7-8
    detractors: int # 0-6
    total: int
    nps_score: float  # (promoters - detractors) / total * 100

class SatisfactionTrend(BaseModel):
    date: str
    average_satisfaction: float
    response_count: int

class SurveySettings(BaseModel):
    user_id: str
    enable_onboarding_survey: bool = True
    enable_periodic_survey: bool = True
    enable_feature_survey: bool = True
    enable_exit_survey: bool = True
    survey_frequency_days: int = 90
    last_survey_date: Optional[datetime] = None
    email_notifications: bool = True

class SurveyTrigger(BaseModel):
    user_id: str
    survey_type: SurveyTypeEnum
    trigger_reason: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    is_sent: bool = False
    sent_at: Optional[datetime] = None

class SurveyAnalytics(BaseModel):
    period: str
    total_surveys: int
    completion_rate: float
    average_satisfaction: float
    nps_score: float
    top_improvement_areas: List[str]
    satisfaction_by_feature: Dict[str, float]
    response_time_distribution: Dict[str, int] 