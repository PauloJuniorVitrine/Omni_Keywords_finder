from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class BugSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BugStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    DUPLICATE = "duplicate"

class BugReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Título do bug")
    description: str = Field(..., min_length=1, max_length=2000, description="Descrição detalhada")
    steps: str = Field(..., min_length=1, max_length=2000, description="Passos para reproduzir")
    expected: Optional[str] = Field(None, max_length=1000, description="Comportamento esperado")
    actual: Optional[str] = Field(None, max_length=1000, description="Comportamento atual")
    severity: BugSeverity = Field(default=BugSeverity.MEDIUM, description="Severidade do bug")
    browser: Optional[str] = Field(None, description="Navegador onde ocorreu")
    os: Optional[str] = Field(None, description="Sistema operacional")
    url: Optional[str] = Field(None, description="URL onde ocorreu")
    error: Optional[Dict[str, Any]] = Field(None, description="Detalhes do erro (se aplicável)")
    userAgent: Optional[str] = Field(None, description="User agent do navegador")

class BugReportCreate(BugReportBase):
    id: str = Field(..., description="ID único do bug report")
    userId: Optional[str] = Field(None, description="ID do usuário que reportou")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    status: BugStatus = Field(default=BugStatus.OPEN, description="Status do bug")

class BugReportUpdate(BaseModel):
    status: Optional[BugStatus] = None
    severity: Optional[BugSeverity] = None
    assignedTo: Optional[str] = None
    admin_notes: Optional[str] = None
    resolution: Optional[str] = None
    tags: Optional[list] = None

class BugReport(BugReportBase):
    id: str
    userId: Optional[str]
    timestamp: datetime
    status: BugStatus
    assignedTo: Optional[str] = None
    admin_notes: Optional[str] = None
    resolution: Optional[str] = None
    tags: Optional[list] = None
    
    class Config:
        from_attributes = True

class BugReportStats(BaseModel):
    total: int
    bySeverity: Dict[BugSeverity, int]
    byStatus: Dict[BugStatus, int]
    recentReports: int
    averageResolutionTime: Optional[float] = None 