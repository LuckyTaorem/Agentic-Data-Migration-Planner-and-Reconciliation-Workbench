# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from core.database import Base, engine
from models.db_models import MigrationPlanRecord, AuditLog
from api.planning_routes import router as planning_router
from api.approval_routes import router as approval_router
from api.execution_routes import router as execution_router

# Initialize inbuilt database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic Data Migration Workbench")

app.include_router(planning_router)
app.include_router(approval_router)
app.include_router(execution_router)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")

# Run with: uvicorn main:app --reload