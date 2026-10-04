# models/db_models.py
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from datetime import datetime
from core.database import Base

class MigrationPlanRecord(Base):
    """Stores the versioned JSON plans proposed by the AI."""
    __tablename__ = 'migration_plans'
    
    id = Column(String(50), primary_key=True) # e.g., "plan_12345"
    version = Column(String(20), default="v1.0")
    context_payload = Column(JSON)            # The source/target schema inputs
    ai_proposal = Column(JSON)                # The AI's generated plan
    status = Column(String(20), default="pending") # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    """Immutable ledger of all workbench events."""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String(50), ForeignKey('migration_plans.id'))
    event_type = Column(String(50)) # e.g., "PLAN_GENERATED", "APPROVED", "LIVE_EXECUTION", "ROLLBACK"
    batch_id = Column(String(100), nullable=True)
    metrics = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)