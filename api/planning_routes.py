# api/planning_routes.py
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from models.db_models import MigrationPlanRecord, AuditLog
from models.pydantic_schemas import MigrationContext
from agent.planner import generate_dynamic_migration_plan

router = APIRouter(prefix="/plan", tags=["Planning"])

@router.post("/generate")
async def create_plan(context: MigrationContext, db: Session = Depends(get_db)):
    """Triggers the AI agent and logs the plan generation."""
    
    # 1. Generate the AI Proposal
    ai_proposal = generate_dynamic_migration_plan(context)
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"
    
    # 2. Save Plan to Database
    plan_record = MigrationPlanRecord(
        id=plan_id,
        context_payload=context.model_dump(),
        ai_proposal=ai_proposal.model_dump(),
        status="pending"
    )
    db.add(plan_record)
    
    # 3. Create Audit Log
    audit_log = AuditLog(
        plan_id=plan_id,
        event_type="PLAN_GENERATED",
        metrics={"total_source_fields": len(context.source_schema)}
    )
    db.add(audit_log)
    
    db.commit()
    
    return {
        "plan_id": plan_id,
        "proposal": ai_proposal
    }