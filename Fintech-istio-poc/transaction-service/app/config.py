import os

# This is the internal DNS name of the fraud service in Kubernetes.
# We DO NOT hardcode IPs because pods are ephemeral.
FRAUD_SERVICE_URL = os.getenv(
    "FRAUD_SERVICE_URL",
    "http://fraud-service:8001/check"
)

# Hard timeout is mandatory.
# Without this, your service can hang forever and pile up requests.
HTTP_TIMEOUT_SECONDS = float(
    os.getenv("HTTP_TIMEOUT_SECONDS", "1.5")
)