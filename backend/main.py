from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn

# Using relative imports here because this is meant to run as part of the backend package
from .models import QueryRequest, QueryResponse, SchemaInfo, HealthResponse
from .database import DatabaseManager
from .agents import MultiAgentSystem

# Load env vars early so everything below can rely on them
# I’ve been bitten before by forgetting this 🙂
load_dotenv()

# ---- App setup ----
app = FastAPI(
    title="Multi-Agent Text-to-SQL API",
    description="Conversational database query system using multiple AI agents",
    version="1.0.0"   # bump this later if we add auth or streaming
)

# CORS is wide open for now.
# This is intentional during development — should be tightened before prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Configuration ----
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/adventureworks.db")

if not GROQ_API_KEY:
    # Fail fast so we don’t get weird runtime errors later
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Initialize core services
db_manager = DatabaseManager(DATABASE_PATH)
agent_system = MultiAgentSystem(GROQ_API_KEY, db_manager)


@app.get("/", tags=["Root"])
async def root():
    """Basic landing endpoint just to confirm the API is alive"""
    return {
        "message": "Multi-Agent Text-to-SQL API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "query": "/query (POST)",
            "schema": "/schema",
            "tables": "/tables"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Simple health check.
    If the DB is down, the API is technically still up,
    so we mark it as degraded instead of dead.
    """
    db_connected = db_manager.test_connection()

    # Slight redundancy here, but it reads clearly
    if db_connected:
        table_count = db_manager.get_table_count()
    else:
        table_count = 0

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        message="API is running" if db_connected else "Database connection failed",
        database_connected=db_connected,
        total_tables=table_count
    )


@app.get("/schema", response_model=SchemaInfo, tags=["Database"])
async def get_schema():
    """Return full schema details for debugging / inspection"""
    try:
        schema_details = db_manager.get_schema_info()
        tables = list(schema_details.keys())

        return SchemaInfo(
            tables=tables,
            schema_details=schema_details,
            total_tables=len(tables)
        )
    except Exception as exc:
        # Catch-all for now; might want to narrow this later
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/tables", tags=["Database"])
async def get_tables():
    """Lightweight endpoint when you only need table names"""
    try:
        table_names = db_manager.get_table_names()
        return {
            "tables": table_names,
            "count": len(table_names)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def process_query(request: QueryRequest):
    """
    Main entry point for natural language questions.

    Internally this fans out to multiple agents:
    - schema analysis
    - SQL generation
    - execution
    - response formatting

    All of that is hidden behind `process_query`.
    """
    try:
        # Defensive check — Pydantic already helps, but this avoids empty strings
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Let the agent system do its thing
        result = agent_system.process_query(request.question)

        return QueryResponse(
            answer=result.get("answer"),
            sql_query=result.get("sql_query"),
            results=result.get("results"),
            error=result.get("error"),
            agent_logs=result.get("agent_logs", [])
        )

    except HTTPException:
        # Re-raise HTTP errors as-is
        raise
    except Exception as exc:
        # Anything unexpected ends up here
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/test", tags=["Testing"])
async def test_query():
    """
    Quick sanity check endpoint.
    This is mostly for local testing and demos.
    """
    sample_question = "How many employees do we have?"
    result = agent_system.process_query(sample_question)

    return {
        "test_question": sample_question,
        "result": result
    }


# ---- Local dev entrypoint ----
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Multi-Agent Text-to-SQL Backend")
    print("=" * 60)
    print(f"📁 Database: {DATABASE_PATH}")
    print(f"🔑 Groq API Key: {'✓ Configured' if GROQ_API_KEY else '✗ Missing'}")
    print("🌐 Backend URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)

    # Using reload=True because this is primarily for local development
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
