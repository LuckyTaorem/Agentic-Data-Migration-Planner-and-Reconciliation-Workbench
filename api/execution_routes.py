# api/execution_routes.py
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.database import get_db
from models.db_models import MigrationPlanRecord, AuditLog
from models.pydantic_schemas import MigrationContext, MigrationPlanProposal
from execution.dry_run import execute_dry_run
from execution.live_runner import execute_dynamic_live_migration
from execution.reconciliation import run_dynamic_reconciliation

router = APIRouter(prefix="/execute", tags=["Execution Engine"])

def get_plan_and_context(db: Session, plan_id: str):
    plan_record = db.query(MigrationPlanRecord).filter(MigrationPlanRecord.id == plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan_record.status != "approved":
        raise HTTPException(status_code=400, detail="Plan must be approved before execution")
        
    context = MigrationContext(**plan_record.context_payload)
    proposal = MigrationPlanProposal(**plan_record.ai_proposal)
    return context, proposal

@router.post("/{plan_id}/dry-run")
async def trigger_dry_run(plan_id: str, db: Session = Depends(get_db)):
    context, proposal = get_plan_and_context(db, plan_id)
    
    # Execute deterministic logic
    valid, quarantined, metrics = execute_dry_run(context.sample_data, proposal)
    
    # Log the dry run
    audit_log = AuditLog(
        plan_id=plan_id,
        event_type="DRY_RUN_EXECUTED",
        metrics=metrics
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "status": "completed",
        "metrics": metrics,
        "sample_valid": valid[:1] if valid else [],
        "sample_quarantined": quarantined[:1] if quarantined else []
    }

@router.post("/{plan_id}/live")
async def trigger_live_execution(plan_id: str, db: Session = Depends(get_db)):
    context, proposal = get_plan_and_context(db, plan_id)
    batch_id = f"batch_{plan_id}_{int(datetime.datetime.utcnow().timestamp())}"
    
    # 1. Transform Data
    valid, quarantined, _ = execute_dry_run(context.sample_data, proposal)
    
    # 2. Dynamic Insert
    execution_result = execute_dynamic_live_migration(context, batch_id, valid, quarantined)
    
    # 3. Mathematically Compare Totals (Reconciliation)
    recon_result = run_dynamic_reconciliation(context, batch_id, len(context.sample_data))
    
    # 4. Log the live execution AND reconciliation proof
    audit_log = AuditLog(
        plan_id=plan_id,
        batch_id=batch_id,
        event_type="LIVE_EXECUTION",
        metrics={"execution": execution_result, "reconciliation": recon_result}
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "execution": execution_result, 
        "reconciliation": recon_result,
        "batch_id": batch_id
    }

@router.post("/{plan_id}/rollback/{batch_id}")
async def rollback_execution(plan_id: str, batch_id: str, db: Session = Depends(get_db)):
    from execution.dynamic_db import get_dynamic_tables, engine
    from sqlalchemy import delete
    
    # Fetch context to know which target table to roll back
    context, _ = get_plan_and_context(db, plan_id)
    target_table, quarantine_table = get_dynamic_tables(context.target_schema, context.target_table_name)
    
    # Perform deletion
    with engine.begin() as conn:
        conn.execute(delete(target_table).where(target_table.c._migration_batch_id == batch_id))
        conn.execute(delete(quarantine_table).where(quarantine_table.c.migration_batch_id == batch_id))
        
    # Log the rollback
    audit_log = AuditLog(
        plan_id=plan_id,
        batch_id=batch_id,
        event_type="ROLLBACK_EXECUTED"
    )
    db.add(audit_log)
    db.commit()
    
    return {"status": "rolled_back", "batch_id": batch_id}

@router.get("/{plan_id}/audit")
async def get_audit_logs(plan_id: str, db: Session = Depends(get_db)):
    """Fetches the complete immutable audit trail for a migration plan."""
    logs = db.query(AuditLog).filter(AuditLog.plan_id == plan_id).order_by(desc(AuditLog.timestamp)).all()
    
    return [
        {
            "id": log.id,
            "event_type": log.event_type,
            "batch_id": log.batch_id,
            "metrics": log.metrics,
            "timestamp": log.timestamp.isoformat()
        } for log in logs
    ]