from fastapi import FastAPI
import billing 

app = FastAPI(
title="SuRI AI Remediation API",
description="Microplastic Fluidic Filtration & Decentralized Manufacturing Mesh Tracking Layer Core."
) 

### Route the core billing module layers into the runtime path structure

app.include_router(billing.router) 

@app.get("/health")
def liveness_check():
return {"status": "healthy", "service": "suri-ecosystem-backbone"}
