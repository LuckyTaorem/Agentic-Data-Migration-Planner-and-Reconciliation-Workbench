# execution/dynamic_db.py
from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, JSON, Text
from core.database import engine

def map_sql_type(type_str: str):
    type_str = type_str.upper()
    if "VARCHAR" in type_str or "STRING" in type_str:
        return String(255)
    if "INT" in type_str:
        return Integer
    if "TIMESTAMP" in type_str or "DATE" in type_str:
        return DateTime
    return Text

def get_dynamic_tables(target_schema: list, target_table_name: str):
    """Reflects or creates dynamic tables in the inbuilt SQLite DB."""
    metadata = MetaData()
    
    # 1. Build the Target Table
    columns = [Column('id', Integer, primary_key=True, autoincrement=True)]
    for field in target_schema:
        # Assuming field is a dict or Pydantic model
        name = field.name if hasattr(field, 'name') else field['name']
        ftype = field.type if hasattr(field, 'type') else field['type']
        columns.append(Column(name, map_sql_type(ftype)))
        
    columns.extend([
        Column('_migration_batch_id', String(100), index=True),
        Column('_source_record_hash', String(255), unique=True, index=True)
    ])
    
    target_table = Table(target_table_name, metadata, *columns, extend_existing=True)
    
    # 2. Build the Quarantine Table
    quarantine_table = Table(
        'quarantine_store', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('migration_batch_id', String(100), index=True),
        Column('raw_payload', JSON),
        Column('field_errors', JSON),
        extend_existing=True
    )
    
    # Create them in the inbuilt DB
    metadata.create_all(engine)
    
    return target_table, quarantine_table