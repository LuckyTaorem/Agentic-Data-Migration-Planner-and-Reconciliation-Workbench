# agent/planner.py
import os
import json
from dotenv import load_dotenv
from groq import Groq
from models.pydantic_schemas import MigrationPlanProposal, MigrationContext

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_dynamic_migration_plan(context: MigrationContext) -> MigrationPlanProposal:
    # 1. Extract the exact JSON schema from our Pydantic model
    schema_rules = json.dumps(MigrationPlanProposal.model_json_schema(), indent=2)

    # 2. Inject it into the system prompt with strict overrides
    system_prompt = (
        "You are an expert Data Migration Architect. "
        "Analyze the provided source schema, target schema, rules, and sample data. "
        "You MUST output valid JSON strictly matching the exact JSON schema provided below.\n\n"
        f"REQUIRED JSON SCHEMA:\n{schema_rules}\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Do NOT wrap the JSON in a parent object (like {'migration_plan': ...}). Output the flat object.\n"
        "2. For mappings, use EXACT key names: 'source_field' and 'target_field' (NOT 'source' or 'target').\n"
        "3. 'incompatible_or_missing_fields' MUST be a flat array of strings.\n"
        "4. 'clarification_questions' MUST be an array of objects, each containing exact 'field' and 'question' string keys."
    )

    user_prompt = f"""
    Source Schema: {json.dumps([f.model_dump() for f in context.source_schema])}
    Target Schema: {json.dumps([f.model_dump() for f in context.target_schema])}
    Allowed Transformations: {json.dumps(context.transformation_rules)}
    Sample Data: {json.dumps(context.sample_data)}
    
    Generate the migration plan proposal strictly following the REQUIRED JSON SCHEMA.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1, # Extremely low temperature for strict deterministic JSON formatting
    )
    
    raw_json = response.choices[0].message.content
    parsed = json.loads(raw_json)
    
    # Fail-safe unwrapper if the LLM still hallucinates a parent key
    if "migration_plan" in parsed and "mappings" not in parsed:
        parsed = parsed["migration_plan"]
    elif "MigrationPlanProposal" in parsed:
        parsed = parsed["MigrationPlanProposal"]
        
    return MigrationPlanProposal(**parsed)