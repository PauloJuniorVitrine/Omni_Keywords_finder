from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database import get_db
from ..models.survey import Survey, SurveyCreate, SurveyResponse, SurveyStats
from ..services.survey_service import SurveyService
from ..auth.auth_bearer import JWTBearer

router = APIRouter(prefix="/api/surveys", tags=["Surveys"])

@router.post("/", response_model=Survey)
async def create_survey_response(
    survey_data: SurveyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Criar uma nova resposta de pesquisa de satisfação
    """
    service = SurveyService(db)
    return service.create_survey_response(survey_data, current_user["user_id"])

@router.get("/", response_model=List[Survey])
async def get_survey_responses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    survey_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Listar respostas de pesquisas com filtros
    """
    service = SurveyService(db)
    return service.get_survey_responses(
        skip=skip,
        limit=limit,
        survey_type=survey_type,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{survey_id}", response_model=Survey)
async def get_survey_response(
    survey_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter detalhes de uma resposta específica
    """
    service = SurveyService(db)
    survey = service.get_survey_response(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey response not found")
    return survey

@router.get("/user/responses", response_model=List[Survey])
async def get_user_survey_responses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter todas as respostas do usuário atual
    """
    service = SurveyService(db)
    return service.get_user_survey_responses(current_user["user_id"])

@router.get("/stats/overview", response_model=SurveyStats)
async def get_survey_stats(
    period: str = Query("30d", regex="^(7d|30d|90d|1y|all)$"),
    survey_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter estatísticas gerais das pesquisas
    """
    service = SurveyService(db)
    return service.get_survey_stats(period, survey_type)

@router.get("/stats/nps", response_model=dict)
async def get_nps_stats(
    period: str = Query("30d", regex="^(7d|30d|90d|1y|all)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter estatísticas de NPS (Net Promoter Score)
    """
    service = SurveyService(db)
    return service.get_nps_stats(period)

@router.get("/stats/satisfaction", response_model=dict)
async def get_satisfaction_stats(
    period: str = Query("30d", regex="^(7d|30d|90d|1y|all)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter estatísticas de satisfação geral
    """
    service = SurveyService(db)
    return service.get_satisfaction_stats(period)

@router.get("/stats/trends", response_model=dict)
async def get_satisfaction_trends(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter tendências de satisfação ao longo do tempo
    """
    service = SurveyService(db)
    return service.get_satisfaction_trends(days)

@router.post("/trigger/onboarding")
async def trigger_onboarding_survey(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Disparar pesquisa de onboarding para usuário
    """
    service = SurveyService(db)
    return service.trigger_onboarding_survey(current_user["user_id"])

@router.post("/trigger/periodic")
async def trigger_periodic_survey(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Disparar pesquisa periódica para usuário
    """
    service = SurveyService(db)
    return service.trigger_periodic_survey(current_user["user_id"])

@router.post("/trigger/feature")
async def trigger_feature_survey(
    feature_name: str = Query(..., description="Nome da funcionalidade"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Disparar pesquisa específica de funcionalidade
    """
    service = SurveyService(db)
    return service.trigger_feature_survey(current_user["user_id"], feature_name)

@router.post("/trigger/exit")
async def trigger_exit_survey(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Disparar pesquisa de saída para usuário
    """
    service = SurveyService(db)
    return service.trigger_exit_survey(current_user["user_id"])

@router.get("/settings", response_model=dict)
async def get_survey_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Obter configurações de pesquisa do usuário
    """
    service = SurveyService(db)
    return service.get_survey_settings(current_user["user_id"])

@router.put("/settings")
async def update_survey_settings(
    settings: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Atualizar configurações de pesquisa do usuário
    """
    service = SurveyService(db)
    return service.update_survey_settings(current_user["user_id"], settings)

@router.delete("/{survey_id}")
async def delete_survey_response(
    survey_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    """
    Excluir uma resposta de pesquisa (apenas admin ou criador)
    """
    service = SurveyService(db)
    # Verificar se o usuário é admin ou criador da resposta
    survey = service.get_survey_response(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey response not found")
    
    if not current_user.get("is_admin") and survey.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this survey response")
    
    success = service.delete_survey_response(survey_id)
    if not success:
        raise HTTPException(status_code=404, detail="Survey response not found")
    
    return {"message": "Survey response deleted successfully"} 