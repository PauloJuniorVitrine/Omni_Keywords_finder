from fastapi import APIRouter
from .logs import router as logs_router
from typing import Dict, List, Optional, Any

router = APIRouter()
router.include_router(logs_router, prefix="/governanca") 