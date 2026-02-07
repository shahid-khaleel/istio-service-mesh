from pydantic import BaseModel, ConfigDict

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    country: str
    merchant: str

class FraudResponse(BaseModel):
    transaction_id: str
    decision: str
    score: float
    model_version: str
    # Remove protected namespace warning
    model_config = ConfigDict(protected_namespaces=())
