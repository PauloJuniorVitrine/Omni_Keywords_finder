from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class FeedbackCategory(str, Enum):
    GENERAL = "general"
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    PERFORMANCE = "performance"
    UI_UX = "ui_ux"
    API = "api"
    INTEGRATION = "integration"

class FeedbackStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class FeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating de 1 a 5 estrelas")
    feedback: str = Field(..., min_length=1, max_length=2000, description="Texto do feedback")
    category: FeedbackCategory = Field(..., description="Categoria do feedback")
    email: Optional[str] = Field(None, description="Email do usuário (opcional)")
    tags: Optional[List[str]] = Field(default=[], description="Tags para categorização")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadados adicionais")

class FeedbackCreate(FeedbackBase):
    id: str = Field(..., description="ID único do feedback")
    userId: Optional[str] = Field(None, description="ID do usuário (se autenticado)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    status: FeedbackStatus = Field(default=FeedbackStatus.PENDING, description="Status do feedback")

class FeedbackUpdate(BaseModel):
    status: Optional[FeedbackStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    admin_notes: Optional[str] = None

class Feedback(FeedbackBase):
    id: str
    userId: Optional[str]
    timestamp: datetime
    status: FeedbackStatus
    admin_notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class FeedbackStats(BaseModel):
    total: int
    averageRating: float
    byCategory: Dict[FeedbackCategory, int]
    byStatus: Dict[FeedbackStatus, int]
    recentSubmissions: int 