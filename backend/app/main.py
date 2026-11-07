
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from pydantic import BaseModel
from app.workflows.graph import voc_graph

from app.database.connection import engine
from app.services.analytics_service import get_analytics_overview

class AnalysisRequest(BaseModel):
    query: str

app = FastAPI(
    title="VOC Intelligence 360 API",
    description="AI-powered Voice of Customer Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to VOC Intelligence 360 API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FastAPI"
    }


@app.get("/health/database")
def database_health():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT COUNT(*) FROM enriched_unified_data")
        )

        total_records = result.scalar_one()

    return {
        "status": "connected",
        "database": "voc_db",
        "table": "enriched_unified_data",
        "total_records": total_records
    }

@app.get("/api/analytics/overview")
def analytics_overview():
    return get_analytics_overview()

@app.post("/api/analysis")
def analyze_voc(request: AnalysisRequest):

    result = voc_graph.invoke({
        "user_query": request.query
    })

    return {
        "query": request.query,
        "intent": result.get("intent"),
        "executive_summary": result.get("executive_summary", ""),
        "key_findings": result.get("key_findings", []),
        "recommendations": result.get("recommendations", []),
        "sql_query": result.get("sql_query"),
        "sql_results": result.get("query_results", []),
        "customer_quotes": result.get("customer_quotes", []),
        "source_distribution": result.get("source_distribution", []),
        "errors": {
            "sql": result.get("sql_error"),
            "verbatim": result.get("verbatim_error"),
            "source": result.get("source_error"),
            "synthesis": result.get("synthesis_error")
        },
        "final_answer": result.get("final_answer", "")
    }