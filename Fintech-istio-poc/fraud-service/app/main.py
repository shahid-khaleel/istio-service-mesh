from fastapi import FastAPI
import time

from app.models import Transaction, FraudResponse
from app.rules import calculate_fraud_score
from app.config import MODEL_VERSION, BLOCK_THRESHOLD, REVIEW_THRESHOLD

app = FastAPI(title="Fraud Detection Service")


@app.post("/check", response_model=FraudResponse)
def check_fraud(txn: Transaction):
    """
    Evaluates transaction risk and returns a decision.
    """

    # Start latency measurement
    start = time.time()

    # Calculate fraud score
    score = calculate_fraud_score(txn)

    # Convert score into a business decision
    if score > BLOCK_THRESHOLD:
        decision = "BLOCK"
    elif score > REVIEW_THRESHOLD:
        decision = "REVIEW"
    else:
        decision = "ALLOW"

    latency_ms = round((time.time() - start) * 1000, 2)

    # Structured logging for audits and debugging
    print({
        "transaction_id": txn.transaction_id,
        "decision": decision,
        "score": score,
        "latency_ms": latency_ms,
        "model": MODEL_VERSION
    })

    return FraudResponse(
        transaction_id=txn.transaction_id,
        decision=decision,
        score=score,
        model_version=MODEL_VERSION
    )
