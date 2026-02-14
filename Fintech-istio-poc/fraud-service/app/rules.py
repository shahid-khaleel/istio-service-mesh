def calculate_fraud_score(txn) -> float:
    """
    Calculates a fraud risk score between 0 and 1.
    Rules are additive and intentionally simple.
    """

    score = 0.0

    # High-value transactions are risky
    if txn.amount > 100000:
        score += 0.7

    # Unexpected countries increase risk
    if txn.country not in ["IN", "US"]:
        score += 0.3

    # Known bad merchants are strong signals
    if txn.merchant.lower() in ["shady-store", "dark-market"]:
        score += 0.9

    # Ensure score never exceeds 1
    return min(score, 1.0)
