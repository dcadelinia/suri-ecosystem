import os
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
import db
import invoice

router = APIRouter(prefix="/v1/billing", tags=["SaaS Billing Engine"])

# Pull configuration parameters safely from runtime environment environments
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "mock_fallback_secret_key")

SURI_PLANS = {
    "remediation_starter": {
        "name": "SuRI Core Intake",
        "price_usd": 49.00,
        "limits": "Up to 10k particle frame traces / day"
    },
    "manufacturing_mesh": {
        "name": "SuRI Industrial Mesh",
        "price_usd": 199.00,
        "limits": "Unlimited telemetry ingestion + Decentralized manufacturing link"
    }
}

class SessionIntentRequest(BaseModel):
    account_id: str
    email: str
    tier: str

@router.get("/plans")
async def get_commercial_plans():
    return {"currency": "USD", "plans": SURI_PLANS}

@router.post("/checkout")
async def create_billing_intent(payload: SessionIntentRequest):
    if payload.tier not in SURI_PLANS:
        raise HTTPException(status_code=400, detail="Requested operational tier does not exist.")
    
    checkout_url = f"https://stripe.com_{payload.tier}_{payload.account_id}"
    return {
        "status": "active",
        "checkout_url": checkout_url,
        "amount_usd": SURI_PLANS[payload.tier]["price_usd"]
    }

@router.post("/webhook")
async def process_stripe_event(payload: dict):
    if payload.get("type") == "checkout.session.completed":
        event_obj = payload.get("data", {}).get("object", {})
        account_id = event_obj.get("client_reference_id", "unknown_client")
        email = event_obj.get("customer_details", {}).get("email", "client@suri-ecosystem.io")
        tier = event_obj.get("metadata", {}).get("tier", "remediation_starter")
        customer_id = event_obj.get("customer", "cus_suri_default")
        
        db.update_consumer_subscription(account_id, email, tier, "active", customer_id)
        return {"status": "synchronized"}
    return {"status": "ignored"}

@router.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>SuRI Commercial Portal</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #0b0f19; color: #f3f4f6; padding: 50px; text-align: center; }
            .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 30px; max-width: 460px; margin: 0 auto 20px; }
            button { background: #10b981; border: none; color: white; padding: 12px 30px; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 16px; }
            button:hover { background: #059669; }
            input, select { width: 90%; padding: 12px; margin: 10px 0; background: #1f2937; border: 1px solid #374151; color: white; border-radius: 6px; }
            h2 { color: #10b981; margin-top:0; }
        </style>
    </head>
    <body>
        <h2>SuRI Remediation Infrastructure Provisioning</h2>
        <div class="card">
            <h3>Activate Fluidic Edge Node</h3>
            <input type="text" id="accId" placeholder="Account ID / Node ID">
            <input type="email" id="email" placeholder="Corporate Billing Email">
            <select id="tier">
                <option value="remediation_starter">SuRI Core Intake - \$49/mo</option>
                <option value="manufacturing_mesh">SuRI Industrial Mesh - \$199/mo</option>
            </select>
            <button onclick="triggerCheckout()">Initialize Deployment Node</button>
            <div id="feedback" style="margin-top:25px; color:#10b981; font-weight:500;"></div>
        </div>
        <script>
            async function triggerCheckout() {
                const accId = document.getElementById('accId').value;
                const email = document.getElementById('email').value;
                const tier = document.getElementById('tier').value;
                if(!accId || !email) { alert('Please enter parameters.'); return; }
                const res = await fetch('/v1/billing/checkout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_id: accId, email: email, tier: tier })
                });
                const data = await res.json();
                document.getElementById('feedback').innerHTML = `Portal Active! <br><a href="${data.checkout_url}" target="_blank" style="color:#ffffff; text-decoration:underline;">Proceed to Stripe Card Portal ($${data.amount_usd})</a>`;
            }
        </script>
    </body>
    </html>
    """
