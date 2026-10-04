# core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Fetch cloud database URL if available
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # 2. Local fallback: Use SQLite
    DATA_DIR = os.path.join(os.getcwd(), "data")
    os.makedirs(DATA_DIR, exist_ok=True)
    DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'workbench.db')}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # 3. Production: Use Cloud Postgres (SQLAlchemy requires 'postgresql://')
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()