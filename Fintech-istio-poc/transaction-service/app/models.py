from pydantic import BaseModel, ConfigDict

#Incoming Client Request
class TransactionRequest(BaseModel):
    user_id: str
    amount: float
    country: str
    merchant: str
    # Remove protected namespace warning
    model_config = ConfigDict(protected_namespaces=())


#Outgoing response
class TransactionResponse(BaseModel):
    transaction_id: str
    decision: str
    fraud_score: float
    # Remove protected namespace warning
    model_config = ConfigDict(protected_namespaces=())

