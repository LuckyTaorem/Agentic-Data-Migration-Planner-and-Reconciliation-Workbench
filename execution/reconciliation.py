# execution/reconciliation.py
from sqlalchemy import select, func
from execution.dynamic_db import get_dynamic_tables
from core.database import engine
from models.pydantic_schemas import MigrationContext

def run_dynamic_reconciliation(context: MigrationContext, batch_id: str, total_source_records: int) -> dict:
    """
    Validates that Target Inserts + Quarantined Records == Total Source Records.
    """
    target_table, quarantine_table = get_dynamic_tables(context.target_schema, context.target_table_name)
    
    with engine.connect() as conn:
        # Count successful inserts for this specific batch
        target_count = conn.execute(
            select(func.count()).where(target_table.c._migration_batch_id == batch_id)
        ).scalar()
        
        # Count rejected records for this specific batch
        quarantine_count = conn.execute(
            select(func.count()).where(quarantine_table.c.migration_batch_id == batch_id)
        ).scalar()
        
    total_accounted_for = target_count + quarantine_count
    is_balanced = total_accounted_for == total_source_records
    
    return {
        "batch_id": batch_id,
        "reconciliation_status": "PASSED" if is_balanced else "FAILED",
        "metrics": {
            "total_source_records": total_source_records,
            "target_inserts": target_count,
            "quarantined_records": quarantine_count,
            "total_accounted_for": total_accounted_for,
            "missing_records": total_source_records - total_accounted_for
        }
    }