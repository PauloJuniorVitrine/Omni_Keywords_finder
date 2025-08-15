from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from ..models.bug_report import BugReport, BugReportCreate, BugReportUpdate
from ..services.bug_report_service import BugReportService
from ..auth.auth_bearer import get_current_user

router = APIRouter(prefix="/api/bug-reports", tags=["bug-reports"])

class BugReportCreateRequest(BaseModel):
    title: str
    description: str
    steps: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    severity: str = "medium"
    browser: Optional[str] = None
    os: Optional[str] = None
    url: Optional[str] = None
    error: Optional[dict] = None
    userAgent: Optional[str] = None

class BugReportResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    timestamp: datetime
    message: str

@router.post("/", response_model=BugReportResponse)
async def create_bug_report(
    bug_report_data: BugReportCreateRequest,
    current_user = Depends(get_current_user)
):
    """Criar novo report de bug"""
    try:
        bug_report_service = BugReportService()
        
        bug_report = BugReportCreate(
            id=str(uuid.uuid4()),
            title=bug_report_data.title,
            description=bug_report_data.description,
            steps=bug_report_data.steps,
            expected=bug_report_data.expected,
            actual=bug_report_data.actual,
            severity=bug_report_data.severity,
            browser=bug_report_data.browser,
            os=bug_report_data.os,
            url=bug_report_data.url,
            error=bug_report_data.error,
            userAgent=bug_report_data.userAgent,
            userId=current_user.id if current_user else None,
            timestamp=datetime.utcnow(),
            status="open"
        )
        
        created_bug_report = await bug_report_service.create_bug_report(bug_report)
        
        return BugReportResponse(
            id=created_bug_report.id,
            title=created_bug_report.title,
            description=created_bug_report.description,
            severity=created_bug_report.severity,
            status=created_bug_report.status,
            timestamp=created_bug_report.timestamp,
            message="Bug report enviado com sucesso!"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[BugReportResponse])
async def get_bug_reports(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Listar bug reports com filtros"""
    try:
        bug_report_service = BugReportService()
        filters = {}
        
        if severity:
            filters["severity"] = severity
        if status:
            filters["status"] = status
            
        bug_reports = await bug_report_service.get_bug_reports(filters, limit, offset)
        
        return [
            BugReportResponse(
                id=br.id,
                title=br.title,
                description=br.description,
                severity=br.severity,
                status=br.status,
                timestamp=br.timestamp,
                message=""
            ) for br in bug_reports
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_bug_report_stats(
    current_user = Depends(get_current_user)
):
    """Obter estatísticas de bug reports"""
    try:
        bug_report_service = BugReportService()
        stats = await bug_report_service.get_stats()
        
        return {
            "total": stats.total,
            "bySeverity": stats.bySeverity,
            "byStatus": stats.byStatus,
            "recentReports": stats.recentReports
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{bug_report_id}")
async def update_bug_report(
    bug_report_id: str,
    bug_report_update: BugReportUpdate,
    current_user = Depends(get_current_user)
):
    """Atualizar bug report (apenas admin)"""
    try:
        bug_report_service = BugReportService()
        updated_bug_report = await bug_report_service.update_bug_report(bug_report_id, bug_report_update)
        
        return {
            "message": "Bug report atualizado com sucesso!",
            "bug_report": updated_bug_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/error-reporting")
async def report_error(
    error_data: dict,
    current_user = Depends(get_current_user)
):
    """Reportar erro automático do frontend"""
    try:
        bug_report_service = BugReportService()
        
        # Criar bug report automático para erros
        bug_report = BugReportCreate(
            id=str(uuid.uuid4()),
            title=f"Erro: {error_data.get('message', 'Erro desconhecido')}",
            description=f"Erro reportado automaticamente: {error_data.get('message')}",
            steps="Erro ocorreu automaticamente",
            severity="high",
            browser=error_data.get('userAgent', ''),
            url=error_data.get('url', ''),
            error=error_data,
            userId=current_user.id if current_user else None,
            timestamp=datetime.utcnow(),
            status="open"
        )
        
        created_bug_report = await bug_report_service.create_bug_report(bug_report)
        
        return {
            "message": "Erro reportado com sucesso!",
            "bug_report_id": created_bug_report.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 