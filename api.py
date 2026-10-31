import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import billing
import db

app = FastAPI(
    title="SuRI Ecosystem API",
    description="AI-powered microplastic remediation and localized manufacturing telemetry backbone.",
    version="1.0.0"
)

# Enable broad cross-origin structural routing compatibility 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automatically initialize SQLite schemas on system boot sequence
try:
    db.init_db()
except Exception as e:
    print(f"⚠️ Warning during database structural load: {e}")

# Register SaaS payment billing engine endpoints 
app.include_router(billing.router)

@app.get("/health")
def liveness_check():
    return {
        "status": "healthy",
        "service": "suri-ecosystem-backbone",
        "environment": os.getenv("MANTAGU_LOG_LEVEL", "PRODUCTION")
    }

@app.get("/")
def root_index():
    return {
        "message": "SuRI Ecosystem Telemetry Cloud Node Active.",
        "documentation": "/docs"
    }
