# execution/live_runner.py
import hashlib
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from execution.dynamic_db import get_dynamic_tables
from core.database import engine
from models.pydantic_schemas import MigrationContext

def generate_record_hash(batch_id: str, unique_payload: dict) -> str:
    # Hash the entire source row to ensure exact data idempotency
    raw_string = f"{batch_id}::{str(unique_payload)}"
    return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

def execute_dynamic_live_migration(context: MigrationContext, batch_id: str, valid_records: list, quarantined_records: list):
    # Use the renamed function and pass the target schema details
    target_table, quarantine_table = get_dynamic_tables(context.target_schema, context.target_table_name)
    
    inserted_count = 0
    skipped_count = 0
    
    # Use the shared engine from core.database
    with engine.begin() as conn:
        # 1. Write Quarantine Records
        if quarantined_records:
            conn.execute(insert(quarantine_table), [
                {
                    "migration_batch_id": batch_id,
                    "raw_payload": q['raw_payload'],
                    "field_errors": q['field_errors']
                } for q in quarantined_records
            ])
            
        # 2. Write Valid Records
        for record in valid_records:
            rec_hash = generate_record_hash(batch_id, record)
            
            # Idempotency check using SQLAlchemy Core
            stmt = select(target_table.c._source_record_hash).where(target_table.c._source_record_hash == rec_hash)
            existing = conn.execute(stmt).fetchone()
            
            if existing:
                skipped_count += 1
                continue
                
            record['_migration_batch_id'] = batch_id
            record['_source_record_hash'] = rec_hash
            
            try:
                conn.execute(insert(target_table).values(record))
                inserted_count += 1
            except IntegrityError:
                skipped_count += 1
                
    return {"status": "success", "inserted": inserted_count, "skipped": skipped_count}