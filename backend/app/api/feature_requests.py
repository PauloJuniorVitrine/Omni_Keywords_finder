from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models.feature_request import FeatureRequest, FeatureRequestCreate, FeatureRequestUpdate
from ..services.feature_request_service import FeatureRequestService
from ..auth.auth_bearer import JWTBearer

router = APIRouter(prefix="/api/feature-requests", tags=["Feature Requests"])

@router.post("/", response_model=FeatureRequest)
async def create_feature_request(
    feature_request: FeatureRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Criar uma nova solicitação de funcionalidade
    """
    service = FeatureRequestService(db)
    return service.create_feature_request(feature_request, current_user["user_id"])

@router.get("/", response_model=List[FeatureRequest])
async def get_feature_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = Query("votes", regex="^(votes|date|priority)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Listar solicitações de funcionalidades com filtros e ordenação
    """
    service = FeatureRequestService(db)
    return service.get_feature_requests(
        skip=skip,
        limit=limit,
        category=category,
        status=status,
        sort_by=sort_by
    )

@router.get("/{feature_id}", response_model=FeatureRequest)
async def get_feature_request(
    feature_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter detalhes de uma solicitação específica
    """
    service = FeatureRequestService(db)
    feature = service.get_feature_request(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature request not found")
    return feature

@router.put("/{feature_id}", response_model=FeatureRequest)
async def update_feature_request(
    feature_id: str,
    feature_request: FeatureRequestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Atualizar uma solicitação de funcionalidade (apenas admin)
    """
    service = FeatureRequestService(db)
    # Verificar se o usuário é admin
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    updated_feature = service.update_feature_request(feature_id, feature_request)
    if not updated_feature:
        raise HTTPException(status_code=404, detail="Feature request not found")
    return updated_feature

@router.post("/{feature_id}/vote")
async def vote_feature_request(
    feature_id: str,
    vote: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Votar em uma solicitação de funcionalidade
    """
    service = FeatureRequestService(db)
    result = service.vote_feature_request(feature_id, current_user["user_id"], vote)
    if not result:
        raise HTTPException(status_code=404, detail="Feature request not found")
    return {"message": "Vote recorded successfully", "feature_id": feature_id}

@router.get("/{feature_id}/votes")
async def get_feature_votes(
    feature_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter estatísticas de votos de uma solicitação
    """
    service = FeatureRequestService(db)
    votes = service.get_feature_votes(feature_id)
    if votes is None:
        raise HTTPException(status_code=404, detail="Feature request not found")
    return votes

@router.get("/user/votes")
async def get_user_votes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter todas as solicitações votadas pelo usuário atual
    """
    service = FeatureRequestService(db)
    return service.get_user_votes(current_user["user_id"])

@router.delete("/{feature_id}")
async def delete_feature_request(
    feature_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Excluir uma solicitação de funcionalidade (apenas admin ou criador)
    """
    service = FeatureRequestService(db)
    # Verificar se o usuário é admin ou criador da solicitação
    feature = service.get_feature_request(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature request not found")
    
    if not current_user.get("is_admin") and feature.created_by != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this feature request")
    
    success = service.delete_feature_request(feature_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feature request not found")
    
    return {"message": "Feature request deleted successfully"}

@router.get("/stats/overview")
async def get_feature_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter estatísticas gerais das solicitações de funcionalidades
    """
    service = FeatureRequestService(db)
    return service.get_feature_stats()

@router.post("/{feature_id}/comment")
async def add_feature_comment(
    feature_id: str,
    comment: str = Query(..., min_length=1, max_length=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Adicionar comentário a uma solicitação de funcionalidade
    """
    service = FeatureRequestService(db)
    result = service.add_comment(feature_id, current_user["user_id"], comment)
    if not result:
        raise HTTPException(status_code=404, detail="Feature request not found")
    return {"message": "Comment added successfully", "feature_id": feature_id} 