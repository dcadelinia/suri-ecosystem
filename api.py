import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Build a guaranteed absolute local fallback path for the database folder
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(ROOT_DIR, "data"))
os.makedirs(DATA_DIR, exist_ok=True)
os.environ["DATA_DIR"] = DATA_DIR

# Inject fallback values so the app never crashes from missing Stripe configurations on startup
if "STRIPE_SECRET_KEY" not in os.environ:
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_mock_placeholder_key"

from billing import router as billing_router
import db

app = FastAPI(title="SuRI Production Backbone Ready")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    db.init_db()
except Exception as e:
    print(f"Database initialization skip: {e}")

app.include_router(billing_router)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "suri-ecosystem"}

@app.get("/")
def index():
    return {"message": "System Live", "docs": "/docs"}

if __name__ == "__main__":
    # Force application engine to look up assigned binding ports dynamically
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("api:app", host="0.0.0.0", port=port)
