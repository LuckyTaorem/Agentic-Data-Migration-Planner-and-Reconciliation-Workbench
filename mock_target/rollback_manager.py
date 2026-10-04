# mock_target/rollback_manager.py
from mock_target.target_db import SessionLocal, AppUser, QuarantineRecord

def execute_rollback(batch_id: str) -> dict:
    """
    Hard deletes all target records and quarantine logs associated with a specific migration batch.
    """
    session = SessionLocal()
    try:
        # 1. Delete from Target Table
        target_deletes = session.query(AppUser).filter(
            AppUser._migration_batch_id == batch_id
        ).delete(synchronize_session=False)
        
        # 2. Delete from Quarantine Store
        quarantine_deletes = session.query(QuarantineRecord).filter(
            QuarantineRecord.migration_batch_id == batch_id
        ).delete(synchronize_session=False)
        
        session.commit()
        
        return {
            "status": "rolled_back",
            "batch_id": batch_id,
            "records_removed": target_deletes,
            "quarantine_logs_cleared": quarantine_deletes
        }
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Rollback failed for batch {batch_id}: {str(e)}")
    finally:
        session.close()