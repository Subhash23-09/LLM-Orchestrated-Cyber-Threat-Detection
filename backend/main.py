import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON, Float
from celery import Celery
from dotenv import load_dotenv
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from virustotal_python import Virustotal
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

load_dotenv()

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://root:password@localhost/acd_sdi")
VT_API_KEY = os.getenv("VIRUSTOTAL_API")

# --- Database Setup ---
from database import engine, AsyncSessionLocal, Base
import models_v2

# --- Celery Setup ---
from celery_app import celery_app

# --- Metrics ---
LOG_INGEST_COUNTER = Counter("log_ingest_total", "Total logs ingested")
SIGNAL_GEN_COUNTER = Counter("signal_gen_total", "Total signals generated")

# --- Phase 2: Drain3 Setup ---
config = TemplateMinerConfig()
# In a real app, persistence for Drain3 (Redis/S3) is better
template_miner = TemplateMiner(config=config)

# --- FastAPI App ---
app = FastAPI(title="ACD-SDI Unified Platform")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api_v2.ingestion import router as ingestion_router
from api_v2.processing import router as processing_router
from api_v2.memory import router as memory_router
from api_v2.orchestration import router as orchestration_router
from api_v2.narrative import router as narrative_router
from api_v2.auth import router as auth_router
from api_v2.agents import router as agents_router

from api_v2.mitigation import router as mitigation_router
from api_v2.reporting import router as reporting_router

# Add a simple adapter for Auth if needed, but let's focus on main routers
app.include_router(ingestion_router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(processing_router, prefix="/api/v1/processing", tags=["Processing"])
app.include_router(memory_router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(orchestration_router, prefix="/api/v1/orchestration", tags=["Orchestration"])
app.include_router(narrative_router, prefix="/api/v1/narrative", tags=["Narrative / Reporting"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])

app.include_router(mitigation_router, prefix="/api/v1/mitigation", tags=["Mitigation"])
app.include_router(reporting_router, prefix="/api/v1/reporting", tags=["Reporting"])

@app.get("/")
async def root():
    return {"message": "ACD-SDI Unified Platform (FastAPI) is Running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
