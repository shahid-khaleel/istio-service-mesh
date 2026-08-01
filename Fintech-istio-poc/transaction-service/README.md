# transaction-service

A small FastAPI service that acts as the entry point for the POC: it receives a transaction request, generates a transaction ID, and synchronously delegates the fraud decision to `fraud-service`. It is the **only** service exposed through the Istio ingress gateway in this repo.

## Endpoint

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/transaction` | `TransactionRequest` — `user_id`, `amount`, `country`, `merchant` | `TransactionResponse` — `transaction_id`, `decision`, `fraud_score` |

Behavior (`app/main.py`):

1. Generates a `transaction_id` (`uuid4`) — used for tracing/audit/logging.
2. Calls `fraud-service` at `POST /check` (URL from `FRAUD_SERVICE_URL`, defaulting to `http://fraud-service:8001/check`; the deployed manifest overrides this to the fully-qualified cluster DNS name `http://fraud-service.default.svc.cluster.local/check`) with a hard timeout (`HTTP_TIMEOUT_SECONDS`, default `1.5`s).
3. **Fails open on any request exception** (timeout, connection error, non-2xx): returns `decision: "REVIEW"`, `fraud_score: 0.0`, rather than blocking or erroring out the transaction. This is a deliberate business tradeoff called out in code comments — "blocking all payments is worse than reviewing them" — and it means that faults injected by Istio (delays, 500s) on the `fraud-service` call surface as `REVIEW` decisions here rather than as errors returned to the client.

Note: incoming request headers (e.g. a client-supplied `x-canary` header) are **not** forwarded on the outbound call to `fraud-service` — only the fields in `TransactionRequest` are passed through as the `Transaction` payload. This matters if you're trying to exercise `fraud-service`'s header-based canary routing rules via a request sent to `transaction-service` — see the root README's "Known gap" note.

## Running locally (without Kubernetes)

```bash
cd app
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
# set FRAUD_SERVICE_URL to point at a locally running fraud-service if needed
```

## Container

Built from `Dockerfile` (Python 3.11-slim base), listens on port `8000` inside the container. Pre-built image referenced by the manifest is `shahid9741/transaction-service:v2` on Docker Hub — replace with your own registry/tag when rebuilding.

## Kubernetes manifest (`kubernetes/deploy.yaml`)

Single `Deployment` + `Service`:

- `version: transaction-v1` label on both the `Deployment` and pod template (kept for consistency with Istio telemetry conventions, though this service has no traffic-split configuration of its own — only `fraud-service` does).
- `FRAUD_SERVICE_URL` env var set to the fraud-service cluster DNS name.
- `Service` type `NodePort`, container port `8000`, exposed at NodePort `30081`.

This is the service targeted by the ingress gateway's `transaction-vs` `VirtualService` (defined in `../fraud-service/kubernetes/ingress-gateway.yaml`, despite living in the `fraud-service` folder) and by all three test scripts in the parent directory.
