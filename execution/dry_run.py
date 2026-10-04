# execution/dry_run.py
import pandas as pd
from typing import Dict, Any, Tuple
from execution.transformer import apply_transformations
from models.pydantic_schemas import MigrationPlanProposal

def validate_row(row: pd.Series) -> list:
    """Validates against Target Schema Constraints."""
    errors = []
    # Constraints: email is NOT NULL and length <= 255
    if pd.isna(row.get('email')) or not row.get('email'):
        errors.append({"field": "email", "error": "Cannot be null"})
    elif len(str(row.get('email'))) > 255:
        errors.append({"field": "email", "error": "Exceeds 255 chars"})
        
    # Constraints: status is NOT NULL
    if pd.isna(row.get('status')):
        errors.append({"field": "status", "error": "Cannot be null"})
        
    return errors

def execute_dry_run(source_records: list, plan: MigrationPlanProposal) -> Tuple[list, list, dict]:
    """Runs transformations and isolates invalid records."""
    
    # 1. Transform the data
    df = apply_transformations(source_records, [m.dict() for m in plan.mappings])
    
    valid_records = []
    quarantined_records = []
    
    # 2. Validate row by row
    for _, row in df.iterrows():
        errors = validate_row(row)
        raw_source = row.pop('_raw_source') # Remove before final validation
        
        if errors:
            quarantined_records.append({
                "raw_payload": raw_source,
                "field_errors": errors
            })
        else:
            # Clean NaNs to None for DB insertion
            valid_dict = row.where(pd.notna(row), None).to_dict()
            valid_records.append(valid_dict)
            
    metrics = {
        "total_source_records": len(source_records),
        "transformed_successfully": len(valid_records),
        "quarantined": len(quarantined_records)
    }
    
    return valid_records, quarantined_records, metrics