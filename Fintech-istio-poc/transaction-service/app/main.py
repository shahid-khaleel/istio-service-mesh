from fastapi import FastAPI
import uuid
import requests


from app.models import TransactionRequest, TransactionResponse
from app.config import FRAUD_SERVICE_URL, HTTP_TIMEOUT_SECONDS

app = FastAPI(title="Transaction Service")

@app.post("/transaction", response_model=TransactionResponse)
def process_transcation(req: TransactionRequest):
    """
    Orchestrates a transaction.
    Does NOT implement fraud logic.
    """
    # Generate a globally unique transaction ID.
    # This ID is used for tracing, logs, audits, and debugging.
    transaction_id = str(uuid.uuid4())
    # Prepare payload for the fraud service.
    payload = {
        "transaction_id": transaction_id,
        "user_id": req.user_id,
        "amount": req.amount,
        "country": req.country,
        "merchant": req.merchant
    }
    try:
        # Call the fraud service synchronously.
        # Istio may retry this call transparently.
        response = requests.post(
            FRAUD_SERVICE_URL,
            json=payload,
            timeout=HTTP_TIMEOUT_SECONDS
        )
        # Convert HTTP errors into Python exceptions.
        response.raise_for_status()
        fraud_result = response.json()        
    except requests.exceptions.RequestException as exc:
        # If fraud service is down or slow:
        # We FAIL OPEN → REVIEW
        # Blocking all payments is worse than reviewing them.
        print(f"[WARN] Fraud service unavailable: {exc}")
        return TransactionResponse(
            transaction_id=transaction_id,
            decision="REVIEW",
            fraud_score=0.0
        )
       # Normal successful path
    return TransactionResponse(
        transaction_id=transaction_id,
        decision=fraud_result["decision"],
        fraud_score=fraud_result["score"]
    )
