import requests
import json

BASE_URL = "https://fly.dev"

def run_remediation_test():
    print("🛰️ Launching validation suite for SuRI integration...")
    payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": "test_node_01",
                "customer_details": {"email": "operator@suri-mesh.io"},
                "metadata": {"tier": "manufacturing_mesh"},
                "customer": "cus_test_suri_123"
            }
        }
    }
    
    res = requests.post(f"{BASE_URL}/v1/billing/webhook", json=payload)
    print(f"📬 Webhook Response ({res.status_code}): {json.dumps(res.json(), indent=2)}")

if __name__ == "__main__":
    run_remediation_test()
