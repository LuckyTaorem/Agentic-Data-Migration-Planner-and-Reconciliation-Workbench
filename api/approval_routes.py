# api/approval_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.db_models import MigrationPlanRecord, AuditLog
from models.pydantic_schemas import ApprovalRequest

router = APIRouter(prefix="/plan", tags=["Human-in-the-Loop Approval"])

@router.post("/{plan_id}/review")
async def review_plan(plan_id: str, request: ApprovalRequest, db: Session = Depends(get_db)):
    """Human reviews and approves the plan."""
    
    plan_record = db.query(MigrationPlanRecord).filter(MigrationPlanRecord.id == plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    # Update Status
    plan_record.status = request.status
    
    # Log the Approval or Rejection
    event_type = "PLAN_APPROVED" if request.status == "approved" else "PLAN_REJECTED"
    audit_log = AuditLog(
        plan_id=plan_id,
        event_type=event_type,
        metrics={"answers_provided": bool(request.answers_to_clarifications)}
    )
    db.add(audit_log)
    
    db.commit()
    
    return {"status": request.status, "message": f"Plan {plan_id} is now {request.status}."}