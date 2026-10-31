# SuRI Ecosystem — Stripe-ready SaaS Billing

AI-powered microplastic remediation prototype with **production Stripe Checkout + webhooks**.

This package fixes the original repository so it can accept real payments on any cloud (Fly.io, AWS, GCP, Azure, Render, Railway, Docker, Kubernetes, etc.) using Stripe.  
**No bank routing or account numbers are stored or required in the application.**

## Quick start (local)

```bash
# 1. Python 3.11+
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure secrets
cp .env.example .env
# Edit .env → put your Stripe test keys (Dashboard → Developers → API keys)

# 3. Run
uvicorn api:app --reload --port 8080
```

- Health: http://localhost:8080/health  
- Plans: http://localhost:8080/v1/billing/plans  
- Create checkout (POST JSON):

```bash
curl -X POST http://localhost:8080/v1/billing/checkout \
  -H "Content-Type: application/json" \
  -d '{"account_id":"user_123","email":"you@example.com","tier":"remediation_starter"}'
```

Returns a real `checkout_url` → open it in a browser (use Stripe test card `4242 4242 4242 4242`).

## Stripe setup (required once)

1. Create a Stripe account → https://dashboard.stripe.com  
2. **API keys** → copy `sk_test_...` into `STRIPE_SECRET_KEY`  
3. **Webhooks** → Add endpoint  
   `https://YOUR_PUBLIC_URL/v1/billing/webhook`  
   Events: `checkout.session.completed`  
   Copy the signing secret (`whsec_...`) into `STRIPE_WEBHOOK_SECRET`  
4. (Optional but recommended) Create Products + Prices in the Dashboard and set  
   `STRIPE_PRICE_STARTER` / `STRIPE_PRICE_MESH` so you can switch to `mode="subscription"` later.

## Deploy on any cloud

### Docker / docker-compose
```bash
export STRIPE_SECRET_KEY=sk_...
export STRIPE_WEBHOOK_SECRET=whsec_...
docker compose up --build -d
```

### Fly.io
```bash
fly launch          # uses the included fly.toml + Dockerfile
fly secrets set STRIPE_SECRET_KEY=sk_... STRIPE_WEBHOOK_SECRET=whsec_...
fly deploy
```

### Render / Railway / Google Cloud Run / AWS App Runner / Azure Container Apps
- Build from the Dockerfile  
- Set the same environment variables as secrets  
- Point a public HTTPS URL at the service and register it as the Stripe webhook endpoint  

### Kubernetes
See `DEPLOYMENT/KUBERNETES/` — inject secrets via Secret objects and expose the service with an Ingress that terminates TLS.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | `sk_test_...` or `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Yes (prod) | Webhook signing secret |
| `STRIPE_SUCCESS_URL` | No | Redirect after successful payment |
| `STRIPE_CANCEL_URL` | No | Redirect if customer cancels |
| `STRIPE_PRICE_STARTER` | No | Dashboard Price ID for starter tier |
| `STRIPE_PRICE_MESH` | No | Dashboard Price ID for mesh tier |
| `DATA_DIR` | No | Directory for SQLite file (default `/data`) |

## Security notes

- Never commit `.env` or real keys.  
- Always verify webhook signatures in production (`STRIPE_WEBHOOK_SECRET`).  
- Prefer Stripe Price IDs over ad-hoc `price_data` for recurring billing.  
- For production data use Postgres (or any managed DB) instead of SQLite; the current `db.py` is intentionally simple and cloud-portable.

## Original project

Upstream concept: AI-powered microplastic remediation & localized manufacturing using NVIDIA edge compute.  
This package focuses on making the billing layer production-ready with Stripe.
