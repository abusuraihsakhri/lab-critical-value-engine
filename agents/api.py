"""FastAPI backend for synthetic demonstration tasks; not for patient care."""
import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")
app = FastAPI(
    title="Lab Critical Value Engine Demo API",
    description="Unvalidated generic demonstration thresholds; not for clinical decisions.",
    version="3.0.1",
)

def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Fail closed when no API key is configured."""
    expected = os.environ.get("LAB_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="LAB_API_KEY is not configured")
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

class ChatRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "lab-critical-value-engine",
            "mode": "DEMONSTRATION_ONLY", "version": "3.0.1"}

@app.get("/metrics")
def metrics():
    return {"dossiers_processed_total": len(supervisor.dossier_registry),
            "audit_blocks_total": len(AuditLogger.get_trail()),
            "mode": "DEMONSTRATION_ONLY"}

@app.post("/api/audit", dependencies=[Depends(require_api_key)])
def api_audit(payload: SystemTaskPayload):
    try:
        return supervisor.process_task(payload).to_dict()
    except SecurityException:
        raise HTTPException(status_code=400, detail="Sensitive identifier pattern detected")

@app.post("/api/chat", dependencies=[Depends(require_api_key)])
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query)}
    except SecurityException:
        raise HTTPException(status_code=400, detail="Sensitive identifier pattern detected")

@app.get("/api/audit/logs", dependencies=[Depends(require_api_key)])
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
