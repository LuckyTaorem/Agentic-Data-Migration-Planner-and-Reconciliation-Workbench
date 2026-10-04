# execution/transformer.py
import pandas as pd
import numpy as np
from datetime import datetime

def apply_transformations(source_data: list, plan_mappings: list) -> pd.DataFrame:
    """Deterministically transforms source data to target schema."""
    df = pd.DataFrame(source_data)
    target_df = pd.DataFrame()
    
    # 1. Clean the raw source (Convert NaN to None for JSON safety)
    df = df.astype(object).where(pd.notnull(df), None)
    raw_sources = df.to_dict(orient='records')
    
    for mapping in plan_mappings:
        src = mapping.get('source_field')
        tgt = mapping.get('target_field')
        rule = mapping.get('transformation_rule')
        
        if "split_name" in str(rule):
            split_names = df[src].str.split(' ', n=1, expand=True)
            if tgt == "first_name":
                target_df[tgt] = split_names[0]
            elif tgt == "last_name":
                target_df[tgt] = split_names[1] if split_names.shape[1] > 1 else ""
                
        elif "cast_to_timestamp" in str(rule):
            # Convert to Pandas datetime, then map to Native Python datetime or None
            dt_series = pd.to_datetime(df[src], errors='coerce')
            target_df[tgt] = dt_series.apply(lambda x: x.to_pydatetime() if pd.notnull(x) else None)
            
        elif "default_value" in str(rule):
            target_df[tgt] = "ACTIVE"
            
        else:
            if src in df.columns:
                target_df[tgt] = df[src]

    # 2. Clean the transformed data (Convert any remaining NaN/NaT to None)
    target_df = target_df.astype(object).where(pd.notnull(target_df), None)
    
    # 3. Attach the clean raw payload
    target_df['_raw_source'] = raw_sources
    return target_df