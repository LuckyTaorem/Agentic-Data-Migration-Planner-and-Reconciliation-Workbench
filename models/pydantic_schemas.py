# models/pydantic_schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SchemaField(BaseModel):
    name: str
    type: str
    constraints: Optional[str] = None

class MigrationContext(BaseModel):
    source_schema: List[SchemaField]
    target_schema: List[SchemaField]
    target_table_name: str
    transformation_rules: List[str]
    sample_data: List[Dict[str, Any]]
    target_db_url: str = Field(
        default="sqlite:///production_target.db", 
        description="e.g., postgresql://user:pass@localhost/db"
    )

class FieldMapping(BaseModel):
    source_field: str
    target_field: str
    transformation_rule: Optional[str] = Field(None, description="e.g., 'uppercase', 'cast_to_int', 'none'")
    risk_warning: Optional[str] = Field(None, description="Truncation or data loss risks")

class ClarificationQuestion(BaseModel):
    field: str
    question: str

class MigrationPlanProposal(BaseModel):
    plan_version: str = "v1.0"
    mappings: List[FieldMapping]
    incompatible_or_missing_fields: List[str]
    clarification_questions: List[ClarificationQuestion]
    summary: str

class ApprovalRequest(BaseModel):
    status: str = Field(..., description="'approved' or 'rejected'")
    answers_to_clarifications: Optional[Dict[str, str]] = None
    manual_overrides: Optional[List[FieldMapping]] = None