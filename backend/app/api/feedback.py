from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from ..models.feedback import Feedback, FeedbackCreate, FeedbackUpdate
from ..services.feedback_service import FeedbackService
from ..auth.auth_bearer import get_current_user

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class FeedbackCreateRequest(BaseModel):
    rating: int
    feedback: str
    category: str
    email: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None

class FeedbackResponse(BaseModel):
    id: str
    rating: int
    feedback: str
    category: str
    email: Optional[str]
    timestamp: datetime
    status: str
    message: str

@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreateRequest,
    current_user = Depends(get_current_user)
):
    """Criar novo feedback"""
    try:
        feedback_service = FeedbackService()
        
        feedback = FeedbackCreate(
            id=str(uuid.uuid4()),
            rating=feedback_data.rating,
            feedback=feedback_data.feedback,
            category=feedback_data.category,
            email=feedback_data.email,
            userId=current_user.id if current_user else None,
            timestamp=datetime.utcnow(),
            status="pending",
            tags=feedback_data.tags or [],
            metadata=feedback_data.metadata or {}
        )
        
        created_feedback = await feedback_service.create_feedback(feedback)
        
        return FeedbackResponse(
            id=created_feedback.id,
            rating=created_feedback.rating,
            feedback=created_feedback.feedback,
            category=created_feedback.category,
            email=created_feedback.email,
            timestamp=created_feedback.timestamp,
            status=created_feedback.status,
            message="Feedback enviado com sucesso!"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[FeedbackResponse])
async def get_feedbacks(
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Listar feedbacks com filtros"""
    try:
        feedback_service = FeedbackService()
        filters = {}
        
        if category:
            filters["category"] = category
        if status:
            filters["status"] = status
            
        feedbacks = await feedback_service.get_feedbacks(filters, limit, offset)
        
        return [
            FeedbackResponse(
                id=f.id,
                rating=f.rating,
                feedback=f.feedback,
                category=f.category,
                email=f.email,
                timestamp=f.timestamp,
                status=f.status,
                message=""
            ) for f in feedbacks
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_feedback_stats(
    current_user = Depends(get_current_user)
):
    """Obter estatísticas de feedback"""
    try:
        feedback_service = FeedbackService()
        stats = await feedback_service.get_stats()
        
        return {
            "total": stats.total,
            "averageRating": stats.averageRating,
            "byCategory": stats.byCategory,
            "byStatus": stats.byStatus,
            "recentSubmissions": stats.recentSubmissions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{feedback_id}")
async def update_feedback(
    feedback_id: str,
    feedback_update: FeedbackUpdate,
    current_user = Depends(get_current_user)
):
    """Atualizar feedback (apenas admin)"""
    try:
        feedback_service = FeedbackService()
        updated_feedback = await feedback_service.update_feedback(feedback_id, feedback_update)
        
        return {
            "message": "Feedback atualizado com sucesso!",
            "feedback": updated_feedback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 