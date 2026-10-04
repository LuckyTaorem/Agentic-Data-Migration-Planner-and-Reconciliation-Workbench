# agent/tools.py
import json

def get_source_schema() -> str:
    return json.dumps({
        "table": "legacy_users",
        "fields": [
            {"name": "full_name", "type": "VARCHAR(255)"},
            {"name": "email_address", "type": "VARCHAR(255)"},
            {"name": "signup_date", "type": "STRING"} # Needs date casting
        ]
    })

def get_target_schema() -> str:
    return json.dumps({
        "table": "app_users",
        "fields": [
            {"name": "first_name", "type": "VARCHAR(50)"},
            {"name": "last_name", "type": "VARCHAR(50)"},
            {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE, NOT NULL"},
            {"name": "created_at", "type": "TIMESTAMP"},
            {"name": "status", "type": "VARCHAR(20)", "constraints": "NOT NULL"} # Missing in source
        ]
    })

def get_transformation_rules() -> str:
    return json.dumps([
        "split_name(full_name) -> first_name, last_name",
        "cast_to_timestamp(date_string) -> timestamp",
        "default_value(val) -> any"
    ])

def get_sample_records(limit: int = 2) -> str:
    return json.dumps([
        {"full_name": "John Doe", "email_address": "john@example.com", "signup_date": "10-24-2023"},
        {"full_name": "Jane Smith", "email_address": "jane@test.com", "signup_date": "11-02-2023"}
    ])