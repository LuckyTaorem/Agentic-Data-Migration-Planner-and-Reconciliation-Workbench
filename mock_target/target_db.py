# mock_target/target_db.py
from sqlalchemy import create_engine, Column, String, DateTime, Integer, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# We use a local SQLite file to persist data across test runs
engine = create_engine('sqlite:///mock_target.db', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AppUser(Base):
    """The Target Schema"""
    __tablename__ = 'app_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime)
    status = Column(String(20), nullable=False)
    
    # Audit column required for Rollbacks and Idempotency
    _migration_batch_id = Column(String(100), index=True)
    _source_record_hash = Column(String(255), unique=True, index=True)

class QuarantineRecord(Base):
    """The Quarantine Store for rejected records"""
    __tablename__ = 'quarantine_store'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    migration_batch_id = Column(String(100))
    raw_payload = Column(JSON)      # The original source row
    field_errors = Column(JSON)     # Evidence of why it failed
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)