# PromptOps - Production-Ready AI Prompt Versioning & A/B Testing Platform

PromptOps is a professional AI development and version management platform similar to LangSmith or PromptLayer. It allows prompt engineers and developers to configure projects, manage prompt version histories, execute sandbox runs using the Groq API (Llama 3.3 70B), orchestrate parallel A/B experiments, run automated LLM-as-a-judge quality evaluations, and analyze cost, latency, and rating trends.

---

## Key Production Features

* **Structured JSON Logging & Traceability**: Configured with a context-local logging architecture that output logs as single-line JSON. Captures `timestamp`, `level`, `request_id`, `user_id` (JWT-derived), `endpoint`, and latency `duration` (milliseconds).
* **Unique Request ID middleware**: Generates UUIDv4 headers (`X-Request-ID`) on every incoming call, binding them to async thread-local context variables for automatic propagation in logging statements and standard error payloads.
* **Selective In-Memory Rate Limiting**: Enhances security by applying a 100 requests/minute limit specifically to sensitive operations (Authentication, LLM Sandbox Runs, A/B Testing, and AI Evaluations) while keeping public health checks (`/health`) and OpenAPI endpoints (`/docs`) open and unthrottled.
* **Comprehensive Swagger/OpenAPI Specs**: Configured with customized metadata (title, licensing details, tags, contacts) and fully documents JWT Bearer security models so that padlock auth indicators render cleanly next to protected endpoints.
* **Database Pagination**: Optimizes queries by implementing `page`/`limit` offsets on all bulk resource endpoints (Prompts, Executions, and Experiments).
* **Graceful Lifespan Event Handling**: Disposes of database connections pools correctly on Uvicorn worker shutdowns.
* **Orchestration**: A clean container architecture using `docker-compose.yml` to spin up frontend and backend services while integrating an external Postgres database (Supabase).
* **CI Workflow Validation**: Includes a pre-configured GitHub Actions CI pipeline (`ci.yml`) to test compilation, check styling formats, and execute validations on pushes or pull requests.

---

## Project Structure

```
prompt-ops/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI pipeline configurations
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py      # Environment configuration schemas
│   │   │   ├── logging_config.py # Structured JSON logs formatter
│   │   │   └── security.py    # JWT authorization decoders & provisioners
│   │   ├── database/          # Session managers & connection pool setup
│   │   ├── middleware/
│   │   │   ├── error_handler.py # Request tracing & exception handlers
│   │   │   └── rate_limit.py  # In-memory IP based rate limiter
│   │   ├── models/            # SQLAlchemy database tables
│   │   ├── routers/           # FastAPI controller endpoints
│   │   ├── schemas/           # Pydantic data serialization schemas
│   │   └── services/          # Business logic layers (caching, analytics)
│   ├── migrations/            # Alembic schema migration records
│   ├── Dockerfile             # Multi-stage production Python build
│   ├── verify_backend.py      # Entrypoint routing validation script
│   └── requirements.txt       # Python backend dependencies
├── frontend/
│   ├── src/                   # React web application components & state
│   ├── Dockerfile             # Nginx static compiler container build
│   └── package.json           # Node.js dependencies list
├── ARCHITECTURE.md            # Mermaid system diagrams and sequences
├── DEPLOYMENT.md              # Cloud setup instructions for staging/production
├── docker-compose.yml         # Containerized services orchestrator
└── README.md                  # Project landing page documentation
```

---

## Getting Started

### Local Development

#### 1. Setup Backend
1. Navigate to `backend/`.
2. Initialize virtual environment:
   ```bash
   python -m venv venv
   # Activate:
   # On Windows:
   .\venv\Scripts\activate
   # On Unix:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file from the template and configure your connection credentials:
   ```bash
   DATABASE_URL=postgresql://<user>:<password>@<host>:5432/postgres
   GROQ_API_KEY=gsk_...
   SUPABASE_JWT_SECRET=your_jwt_signing_secret
   ```
5. Boot Uvicorn development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
6. API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

#### 2. Setup Frontend
1. Navigate to `frontend/`.
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Copy `.env.example` to `.env` and adjust variables.
4. Launch the local development server:
   ```bash
   npm run dev
   ```
5. Open your browser to: [http://localhost:3000](http://localhost:3000)

### Running with Docker Compose

To test the entire containerized setup locally (orchestrating frontend and backend containers and pointing to your external Supabase/PostgreSQL instance):

1. Create a `.env` file in the root directory containing necessary Supabase and Groq keys.
2. Build and run the containers:
   ```bash
   docker-compose up --build
   ```
3. Access:
   * Frontend: [http://localhost:3000](http://localhost:3000)
   * API endpoints: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Architecture Diagrams

See [ARCHITECTURE.md](file:///C:/Users/bkapa/.gemini/antigravity-ide/scratch/prompt-ops/ARCHITECTURE.md) for detailed descriptions and flowcharts covering authentication pipelines, database mappings, execution loops, and A/B evaluations.
