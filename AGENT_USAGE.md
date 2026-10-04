# Agent Usage & Verification

## Tools
* **Groq API SDK:** Utilized to interact with the LLM.
* **Model:** `openai/gpt-oss-120b` (Chosen for high-parameter reasoning and strict JSON compliance).
* **Pydantic:** Used to dynamically enforce JSON schema structures during AI generation.

## Representative Prompts
**System Prompt for AI Planner:**
> "You are an expert Data Migration Architect. Analyze the provided source schema, target schema, rules, and sample data. You MUST output valid JSON strictly matching the exact JSON schema provided below. 
> REQUIRED JSON SCHEMA: {injected_pydantic_schema}
> CRITICAL INSTRUCTIONS:
> 1. Do NOT wrap the JSON in a parent object. Output the flat object.
> 2. For mappings, use EXACT key names: 'source_field' and 'target_field'.
> 3. 'incompatible_or_missing_fields' MUST be a flat array of strings."

## Delegated Work
The AI is strictly limited to the **Discovery and Planning Phase**. It is responsible for semantic reasoning:
* Interpreting legacy field names (e.g., matching `email_address` to `email`).
* Identifying when required target fields (like `status`) do not exist in the source schema.
* Suggesting safe transformation rules from the predefined list.
* Asking the human operator clarification questions when context is missing.

The AI is explicitly **barred from the Execution Phase**. It does not write SQL, it does not evaluate Python code, and it does not touch the live data payload.

## Important Agent Mistakes & Rejected Suggestions
1. **JSON Wrapper Hallucination:** The agent initially wrapped the requested output in an arbitrary parent key (e.g., `{"migration_plan": {...}}`), which broke the Pydantic validation. 
   * *Resolution:* Implemented a failsafe JSON unwrapper in the backend and added strict negative constraints to the system prompt to prevent nesting.
2. **Schema Key Deviation:** The agent simplified `source_field` and `target_field` to `source` and `target`.
   * *Resolution:* Replaced static prompt instructions with a dynamically injected `model_json_schema()` dump from Pydantic to force exact key adherence.
3. **Empty Array Handling:** When no risks or incompatibilities were found, the agent would return `"none"` or omit the key, causing frontend rendering errors.
   * *Resolution:* Added robust UI fallback logic in the frontend to handle empty arrays, null values, and string variants of "none", displaying a positive confirmation message instead of breaking the UI.

## How Output Was Verified
1. **Pydantic Validation:** Every AI response is passed through a strict Pydantic model (`MigrationPlanProposal`). If the agent hallucinates data types, the request fails before reaching the user.
2. **Human-in-the-Loop (HITL):** The AI's plan is rendered in a read-only dashboard. The system requires explicit human approval before unlocking the execution engine.
3. **Deterministic Dry Run:** The actual data transformation is executed by Pandas, not the LLM. 
4. **Idempotency & Reconciliation:** Hashes are generated for every row, and SQL `COUNT()` queries mathematically prove the AI's approved plan did not result in data loss during the transition.