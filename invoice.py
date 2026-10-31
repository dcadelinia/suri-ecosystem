import datetime

def generate_suri_receipt(account_id, email, tier, amount):
    """Generates standard industrial ledger receipts for compliance documentation."""
    receipt_id = f"SURI-INV-{int(datetime.datetime.utcnow().timestamp())}"
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return f"""# SYSTEM RECEIPT STATEMENT: SuRI ECOSYSTEM NETWORKS
**Transaction Reference:** {receipt_id}
**Timestamp:** {timestamp}
**Account Provisioning Status:** ACTIVE / RECONCILED

### Customer Node Context:

* **Target Account Reference ID:** {account_id}
* **Registered Communication Endpoint:** {email}

### Computational Service Allotments

Infrastructure System Feature | Distribution Interval | Net Rate (USD)
---|---|---
SuRI Intelligent Ingestion Platform Layer ({tier.replace('_', ' ').upper()}) | Monthly Recurring | ${amount:.2f}

### Financial Compliance Audit Summary

* **Currency Metric:** United States Dollar (USD)
* **Net Base Balance:** ${amount:.2f}
* **Applied Processing Surcharges:** 0.00%
* **Total Certified Paid Amount:** ${amount:.2f}

*Thank you for deploying autonomous Sustainable Remediation & Innovation systems.
Your edge filtration data pipeline nodes are cleared for tracking operational usage.*
"""
