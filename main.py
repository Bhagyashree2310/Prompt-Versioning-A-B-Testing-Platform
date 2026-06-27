from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging, request_id_var
from app.database.session import engine
from app.routers import auth, prompts, experiments, analytics, profiles, projects, prompt_executions, evaluations, feedback
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limit import rate_limiter

# 1. Initialize Structured JSON Logging
setup_logging()

# 2. Register Lifespan context for DB Pool disposal
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables in local SQLite database if Postgres is offline
    if engine and "sqlite" in str(engine.url):
        from app.models.base import Base
        Base.metadata.create_all(bind=engine)
    yield
    if engine:
        # Dispose of engine connection pools on graceful shutdown
        engine.dispose()

# 3. Create FastAPI app with rich metadata
app = FastAPI(
    title="PromptOps - AI Prompt Versioning & A/B Testing Platform",
    description=(
        "Production-ready backend API managing AI prompts, version histories, playground executions, "
        "A/B testing comparisons, automated AI judges, human feedback loops, and performance analytics curves."
    ),
    version="1.0.0",
    contact={
        "name": "PromptOps Engineering",
        "email": "engineering@promptops.ai"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {"name": "auth", "description": "Supabase JWT session validation and active profile loaders"},
        {"name": "profiles", "description": "Manage user profiles and roles"},
        {"name": "projects", "description": "Scoping folders CRUD for prompts"},
        {"name": "prompts", "description": "Prompt templates creation, restore, and tag managers"},
        {"name": "prompt-executions", "description": "Playground LLM completions logs and sandbox runner"},
        {"name": "experiments", "description": "A/B comparisons and parallel runs loops"},
        {"name": "evaluations", "description": "AI quality assessment evaluations"},
        {"name": "feedback", "description": "Human feedback ratings and review text logs"},
        {"name": "analytics", "description": "Real-time cost, latency, success rate, and leaderboards aggregation query services"}
    ],
    lifespan=lifespan
)

# 4. Standardized Custom Exception Handlers capturing Request IDs
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    request_id = request_id_var.get("N/A")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_class": exc.__class__.__name__,
            "status_code": exc.status_code,
            "request_id": request_id
        },
        headers={"X-Request-ID": request_id}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    request_id = request_id_var.get("N/A")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error_class": exc.__class__.__name__,
            "status_code": 422,
            "request_id": request_id
        },
        headers={"X-Request-ID": request_id}
    )

# 5. Add Global Exception and Request ID Middleware
app.add_middleware(ErrorHandlerMiddleware)

# 6. Add CORS Middleware (Outer middleware to ensure all error/success responses have CORS headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 7. Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR, dependencies=[Depends(rate_limiter)])
app.include_router(profiles.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(prompts.router, prefix=settings.API_V1_STR)
app.include_router(prompts.versions_router, prefix=settings.API_V1_STR)
app.include_router(prompt_executions.router, prefix=settings.API_V1_STR, dependencies=[Depends(rate_limiter)])
app.include_router(experiments.router, prefix=settings.API_V1_STR, dependencies=[Depends(rate_limiter)])
app.include_router(evaluations.router, prefix=settings.API_V1_STR, dependencies=[Depends(rate_limiter)])
app.include_router(feedback.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
def health_check():
    """
    App health checkpoint to verify FastAPI services are running.
    """
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "phase": 9
    }
