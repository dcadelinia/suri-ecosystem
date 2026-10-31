from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import billing

app = FastAPI(
    title="SuRI AI Remediation API",
    description="Microplastic Fluidic Filtration & Decentralized Manufacturing Mesh Tracking Layer Core.",
    version="1.1.0",
)

# Allow browser-based frontends (tighten origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(billing.router)


@app.get("/health")
def liveness_check():
    return {"status": "healthy", "service": "suri-ecosystem-backbone"}
