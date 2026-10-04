# Agentic Data Migration Planner and Reconciliation Workbench

An AI-driven application that plans, validates, and executes data migrations. Developed by Taorem Lucky Singh, this workbench strictly separates non-deterministic AI planning from deterministic execution to guarantee data safety, idempotency, and full auditability.

## Architecture
The system utilizes a Human-in-the-Loop (HITL) pipeline:
* **Frontend:** Vanilla JS and Tailwind CSS, served directly via FastAPI.
* **Backend:** FastAPI handles API routing, session management, and UI delivery.
* **AI Planner (Non-Deterministic Phase):** Groq API (`openai/gpt-oss-120b`) analyzes JSON schemas and proposes mapping rules.
* **Execution Engine (Deterministic Phase):** Pandas applies mapping transformations, validates data types, and manages the in-memory Dry Run.
* **Storage & Idempotency:** SQLAlchemy Core dynamically generates tables and handles idempotent UPSERTs using SHA-256 cryptographic hashes of the source payloads.

## Tech Stack
* **Backend:** FastAPI, Python, Pandas, SQLAlchemy
* **Database:** SQLite (Local fallback) / PostgreSQL (Cloud production)
* **AI Engine:** Groq API (`openai/gpt-oss-120b`)
* **Frontend:** Vanilla JS, HTML, Tailwind CSS (Served via FastAPI)

## Prerequisites
* [Python](https://www.python.org/downloads/) (3.9 or higher)
* A [Groq API Key](https://console.groq.com/keys)

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/LuckyTaorem/Agentic-Data-Migration-Planner-and-Reconciliation-Workbench
cd migration-workbench
```

### 2. Install Dependencies
Create a virtual environment and install the required Python packages:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` (or create a `.env` file) and add your Groq API key:
```text
GROQ_API_KEY=gsk_your_api_key_here
```
*(Optional)* Add a Postgres database URL to `DATABASE_URL` if hosting in production. Otherwise, it defaults to a local SQLite database in the `/data` folder.

## Running the Application
Start the FastAPI server (which handles the backend API and serves the frontend UI simultaneously):
```bash
uvicorn main:app --reload
```
*Open your browser and navigate to `http://127.0.0.1:8000`*

## Completed Scope
* **AI Discovery:** Automatic semantic mapping of source to target schemas.
* **Human Approval:** Mappings are locked until a human answers clarifications and approves the plan.
* **Deterministic Dry Run:** In-memory validation that flags constraint violations.
* **Quarantine Store:** Failed records are isolated with field-level evidence alongside successful records.
* **Idempotency:** Re-running a live batch mathematically skips previously inserted rows.
* **Reconciliation:** Automated verification proving Target Inserts + Quarantined Records = Total Source Records.
* **Rollback:** Single-click batch deletion using isolated `_migration_batch_id` signatures.
* **Audit Trail:** Immutable database ledger tracking planning, approvals, executions, and rollbacks.

## Excluded Scope
* Distributed or multi-node migration streaming.
* Execution of arbitrary/custom Python transformation code submitted by the user.
* Live cloud connectors (OAuth, live syncing).
* Production database direct integration (the system requires a provided DB URL or uses its own mock SQLite store).

## Tests
The application is validated using the pre-filled demo data in the UI:
1. Initialize the pre-filled configuration.
2. Generate the AI plan to verify schema mapping.
3. Execute the Dry Run to verify that the intentional missing-email record is correctly quarantined.
4. Execute the Live Migration to verify database insertion.
5. Execute the Live Migration a second time to verify the idempotency engine skips the duplicate records.
6. Verify the automated reconciliation counts match the source inputs.

## Limitations
* **Memory Constraints:** Because the Dry Run Engine processes data using Pandas in-memory, the application is bounded by available RAM and is not suited for multi-gigabyte datasets without chunking.
* **SQLite Concurrency:** If run locally, SQLite is limited in handling concurrent heavy-write workloads.
* **Transformation Rules:** The current deterministic engine relies on predefined rule string matching (e.g., `split_name`, `cast_to_timestamp`) rather than evaluating dynamic code.

## Deployment Details
This application is designed to be hosted on platforms like Render or Railway.
1. Deploy the repository as a Python Web Service.
2. Set the build command to `pip install -r requirements.txt`.
3. Set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Define the `GROQ_API_KEY` environment variable.
5. Define the `DATABASE_URL` environment variable using a PostgreSQL connection string (e.g., Neon or Supabase) equipped with the `psycopg[binary]` driver to ensure persistent data storage across server restarts.