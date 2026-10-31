"""
SuRI SaaS Billing Layer — Stripe Checkout + Webhooks
Secrets are read only from environment variables.
Never put bank account / routing numbers or raw Stripe keys in source.
"""
import os
from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel, EmailStr
import stripe
import db
import invoice

router = APIRouter(prefix="/v1/billing", tags=["SaaS Billing Layer"])

# ---------------------------------------------------------------------------
# Stripe configuration (set these in your cloud environment / secrets manager)
# ---------------------------------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")  # sk_live_... or sk_test_...
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")  # whsec_...
SUCCESS_URL = os.environ.get(
    "STRIPE_SUCCESS_URL", "https://example.com/success?session_id={CHECKOUT_SESSION_ID}"
)
CANCEL_URL = os.environ.get("STRIPE_CANCEL_URL", "https://example.com/cancel")

# Optional: map internal tiers to Stripe Price IDs created in the Dashboard.
# If not set, we fall back to price_data (ad-hoc one-time prices).
STRIPE_PRICE_IDS = {
    "remediation_starter": os.environ.get("STRIPE_PRICE_STARTER"),
    "manufacturing_mesh": os.environ.get("STRIPE_PRICE_MESH"),
}

SURI_PLANS = {
    "remediation_starter": {
        "name": "SuRI Core Intake",
        "price_usd": 49.00,
        "limits": "Up to 10k particle frame traces / day",
        "features": "Standard microplastic fluidic tracking + daily logging",
    },
    "manufacturing_mesh": {
        "name": "SuRI Industrial Mesh",
        "price_usd": 199.00,
        "limits": "Unlimited telemetry ingestion + Decentralized manufacturing link",
        "features": "Real-time raw telemetry outputs + automated OpenUSD mesh scene syncing",
    },
}


class SessionIntentRequest(BaseModel):
    account_id: str
    email: EmailStr
    tier: str


@router.get("/plans")
async def get_commercial_plans():
    return {"currency": "USD", "plans": SURI_PLANS}


@router.post("/checkout")
async def create_billing_intent(payload: SessionIntentRequest):
    """Create a real Stripe Checkout Session and return its URL."""
    if not stripe.api_key:
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY in the environment.",
        )
    if payload.tier not in SURI_PLANS:
        raise HTTPException(status_code=400, detail="Requested operational tier does not exist.")

    plan = SURI_PLANS[payload.tier]
    price_id = STRIPE_PRICE_IDS.get(payload.tier)

    line_items = []
    if price_id:
        # Preferred: use a Price created in the Stripe Dashboard (supports subscriptions later)
        line_items.append({"price": price_id, "quantity": 1})
    else:
        # Fallback: one-time price_data (no pre-created Price needed)
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": plan["name"],
                        "description": plan["features"],
                    },
                    "unit_amount": int(plan["price_usd"] * 100),  # cents
                },
                "quantity": 1,
            }
        )

    try:
        session = stripe.checkout.Session.create(
            mode="payment",  # change to "subscription" when you create recurring Prices
            customer_email=payload.email,
            client_reference_id=payload.account_id,
            metadata={"tier": payload.tier, "account_id": payload.account_id},
            line_items=line_items,
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {str(e)}") from e

    return {
        "status": "active",
        "checkout_url": session.url,
        "session_id": session.id,
        "amount_usd": plan["price_usd"],
    }


@router.post("/webhook")
async def process_stripe_event(request: Request, stripe_signature: str = Header(None)):
    """
    Stripe webhook endpoint.
    Configure this URL in the Stripe Dashboard → Developers → Webhooks.
    Example: https://your-app.fly.dev/v1/billing/webhook
    """
    payload = await request.body()

    if STRIPE_WEBHOOK_SECRET and stripe_signature:
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        # Development fallback (never use in production without signature check)
        import json
        event = json.loads(payload)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        account_id = session.get("client_reference_id") or session.get("metadata", {}).get(
            "account_id", "unknown_client"
        )
        email = (session.get("customer_details") or {}).get("email") or session.get(
            "customer_email", "client@suri-ecosystem.io"
        )
        tier = (session.get("metadata") or {}).get("tier", "remediation_starter")
        customer_id = session.get("customer") or "cus_unknown"

        db.update_consumer_subscription(account_id, email, tier, "active", customer_id)
        return {"status": "synchronized"}

    return {"status": "ignored"}


@router.get("/invoice/{account_id}", response_class=PlainTextResponse)
async def fetch_invoice(account_id: str):
    profile = db.get_consumer_profile(account_id)
    if not profile or profile["status"] != "active":
        raise HTTPException(status_code=404, detail="No active paid registration located for account.")

    amount = SURI_PLANS.get(profile["tier"], {"price_usd": 0.00})["price_usd"]
    return invoice.generate_suri_receipt(
        profile["account_id"], profile["email"], profile["tier"], amount
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html><head><title>SuRI Billing</title></head>
    <body>
      <h1>SuRI Billing Dashboard</h1>
      <p>Use POST /v1/billing/checkout with JSON body to start a Stripe Checkout session.</p>
      <p>GET /v1/billing/plans for available tiers.</p>
    </body></html>
    """
