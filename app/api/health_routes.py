from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "warehouse-ai-backend",
        "timestamp": datetime.utcnow().isoformat()
    }