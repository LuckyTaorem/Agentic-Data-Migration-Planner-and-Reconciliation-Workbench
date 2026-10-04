# Agentic Data Migration Planner and Reconciliation Workbench

An AI-driven application that helps plan, validate, and execute the migration of a bounded dataset from a source schema to a target schema. It strictly separates non-deterministic AI planning from deterministic execution, ensuring complete data safety, idempotency, and auditability.

## Features
* **AI Discovery & Planning:** Automatically maps source fields to target fields, identifies incompatibilities, and assesses data truncation risks using Groq LLMs.
* **Human-in-the-Loop Approval:** AI proposals are paused until a human reviews and approves the migration plan.
* **Deterministic Dry Run:** Simulates the migration in-memory using Pandas to validate constraints without touching the live database.
* **Quarantine Store:** Isolates invalid records with field-level error evidence (e.g., missing emails, constraint violations) for easy review.
* **Idempotent Live Execution:** Prevents duplicate insertions using cryptographic hashing, allowing safe retries if a batch fails mid-flight.
* **Automated Reconciliation:** Mathematically verifies that Target Inserts + Quarantined Records == Total Source Records.
* **Rollback Manager:** Instantly reverts specific migration batches using isolated signature IDs.
* **Immutable Audit Trail:** Preserves execution, approval, retry, and rollback history in a database ledger.

## Tech Stack
* **Backend:** FastAPI, Python, Pandas, SQLAlchemy
* **Database:** SQLite (Local fallback) / PostgreSQL (Cloud production)
* **AI Engine:** Groq API (`openai/gpt-oss-120b`)
* **Frontend:** Vanilla JS, HTML, Tailwind CSS (Served via FastAPI)

## Prerequisites
* [Python](https://www.python.org/downloads/) (3.9 or higher)
* A [Groq API Key](https://console.groq.com/keys)

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/LuckyTaorem/Agentic-Data-Migration-Planner-and-Reconciliation-Workbench
cd migration-workbench
```

### 2. Install Dependencies
Create a virtual environment and install the required Python packages:
```bash
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
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

## Usage Guide
The frontend UI comes **pre-filled with demo data** (Source Schema, Target Schema, Sample Data, and Rules) so you can test the pipeline immediately out of the box without any manual configuration!

1. **Phase 0:** Click **Save Configuration** (leaves the pre-filled demo data intact).
2. **Phase 1:** Click **Generate AI Migration Plan** to let Groq map the schemas and identify missing fields.
3. **Phase 2:** Review the AI's mapping proposals, risks, and clarification questions, then click **Approve Plan v1.0**.
4. **Phase 3:** Click **Execute Dry Run Validation**. Notice how 1 record is correctly routed to the Quarantine due to an intentional missing email constraint in the demo data!
5. **Phase 4:** Click **Execute Live Migration** to deterministically insert valid records into the database and perform an automated reconciliation check (verifying source and target counts).
6. *(Optional)* Click **Execute Live Migration** again to see the idempotency engine safely skip duplicate insertions using SHA-256 hashes.
7. **Phase 5:** Check the **Audit Trail** table at the bottom to view the immutable ledger of your planning, approval, execution, and any rollbacks.