from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class CategoryEnum(str, Enum):
    general = "general"
    analytics = "analytics"
    integration = "integration"
    ui_ux = "ui_ux"
    api = "api"
    export = "export"
    automation = "automation"
    reporting = "reporting"

class StatusEnum(str, Enum):
    pending = "pending"
    under_review = "under_review"
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"

class FeatureRequestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Título da funcionalidade")
    description: str = Field(..., min_length=10, max_length=2000, description="Descrição detalhada")
    use_case: Optional[str] = Field(None, max_length=1000, description="Caso de uso específico")
    category: CategoryEnum = Field(default=CategoryEnum.general, description="Categoria da funcionalidade")
    priority: PriorityEnum = Field(default=PriorityEnum.medium, description="Prioridade da solicitação")
    email: Optional[str] = Field(None, description="Email para notificações")

class FeatureRequestCreate(FeatureRequestBase):
    pass

class FeatureRequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    use_case: Optional[str] = Field(None, max_length=1000)
    category: Optional[CategoryEnum] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    admin_notes: Optional[str] = Field(None, max_length=1000, description="Notas administrativas")

class FeatureComment(BaseModel):
    id: str
    feature_request_id: str
    user_id: str
    user_name: str
    comment: str
    created_at: datetime
    is_admin: bool = False

class FeatureVote(BaseModel):
    feature_request_id: str
    user_id: str
    voted_at: datetime

class FeatureRequest(FeatureRequestBase):
    id: str
    created_by: str
    created_by_name: str
    status: StatusEnum = StatusEnum.pending
    votes: int = 0
    user_voted: bool = False
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    comments: List[FeatureComment] = []
    
    class Config:
        from_attributes = True

class FeatureRequestStats(BaseModel):
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    completed_requests: int
    total_votes: int
    most_voted_category: str
    most_voted_request: Optional[str] = None
    recent_requests: int  # Últimos 30 dias

class FeatureRequestList(BaseModel):
    features: List[FeatureRequest]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

class VoteResponse(BaseModel):
    feature_id: str
    vote_count: int
    user_voted: bool
    message: str 