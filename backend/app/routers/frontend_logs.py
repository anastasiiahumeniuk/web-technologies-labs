from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional, Dict
import json

from app.core.frontend_logging import frontend_logger

router = APIRouter(
    prefix="/logs",
    tags=["Frontend Logs"]
)

class FrontendLog(BaseModel):
    level: str
    message: str
    metadata: Optional[Dict] = None

@router.post("/frontend", status_code=status.HTTP_204_NO_CONTENT)
def receive_frontend_log(log: FrontendLog):
    payload = {
        "message": log.message,
        "metadata": log.metadata
    }

    msg = json.dumps(payload, ensure_ascii=False)

    match log.level.lower():
        case "error":
            frontend_logger.error(msg)
        case "warning":
            frontend_logger.warning(msg)
        case "debug":
            frontend_logger.debug(msg)
        case _:
            frontend_logger.info(msg)
