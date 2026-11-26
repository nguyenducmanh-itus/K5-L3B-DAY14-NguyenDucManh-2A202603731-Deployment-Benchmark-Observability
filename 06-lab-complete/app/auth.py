"""
API Key authentication (tiêu chí 6).

Yêu cầu:
  • Client gửi header  X-API-Key: <key>
  • Key phải trùng biến môi trường AGENT_API_KEY
  • Thiếu hoặc sai key → HTTP 401 (không phải 403 hay 422)
"""


import hmac
from fastapi import Header, HTTPException
from app.config import settings


def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    """Dependency cho FastAPI — dùng trong /ask: Depends(verify_api_key)."""
    if not x_api_key or not settings.agent_api_key or not hmac.compare_digest(
        x_api_key, settings.agent_api_key
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing API key",
                            headers={"WWW-Authenticate": "ApiKey"})
    return x_api_key
