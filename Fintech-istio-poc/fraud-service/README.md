# fraud-service

A small FastAPI service that scores an incoming transaction for fraud risk and returns a decision. It is the **downstream** service in this POC — it is never called directly from outside the mesh; `transaction-service` calls it internally.

It doubles as the demo target for most of the Istio traffic-management features in this repo: canary routing, weighted traffic splitting, fault injection, and circuit breaking are all configured against `fraud-service`'s two versions.

## Endpoint

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/check` | `Transaction` — `transaction_id`, `user_id`, `amount`, `country`, `merchant` | `FraudResponse` — `transaction_id`, `decision` (`ALLOW` / `REVIEW` / `BLOCK`), `score` (0–1), `model_version` |

Decision logic (`app/rules.py`, `app/config.py`) is intentionally simple and additive:

- `amount > 100000` → `+0.7`
- `country` not in `["IN", "US"]` → `+0.3`
- `merchant` in `["shady-store", "dark-market"]` (case-insensitive) → `+0.9`
- score is capped at `1.0`; `score > 0.8` → `BLOCK`, `score > 0.5` → `REVIEW`, else `ALLOW`

There is no persistence, no real ML model, and no per-user history — this is a rules stub built to be fast and deterministic for demo traffic, not a production fraud engine.

## Running locally (without Kubernetes)

```bash
cd app
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Container

Built from `Dockerfile` (Python 3.11-slim base), listens on port `8001` inside the container. Pre-built images referenced by the manifests are pushed to Docker Hub as `shahid9741/fraud-service:v2` (v1 subset) and `shahid9741/fraud-service:v3` (v2 subset) — replace with your own registry/tag when rebuilding.

## Kubernetes / Istio manifests (`kubernetes/`)

| File | Purpose |
|---|---|
| `deploy.yaml` | `Deployment` + `Service` for the `v1` version (`version: fraud-v1` label — required for Istio subset matching). NodePort `30080`. |
| `deploy-2.yaml` | Second `Deployment` for the `v2` version (`version: fraud-v2` label), sharing the same `Service`. |
| `destination-rules.yaml` | Baseline `DestinationRule` defining the `v1`/`v2` subsets by label — no traffic-policy extras. |
| `destination-rules-circuitbreaking.yaml` | Alternative `DestinationRule` adding connection-pool limits (`maxConnections: 1`, `http1MaxPendingRequests: 1`, `maxRequestsPerConnection: 1`) and outlier detection (`consecutive5xxErrors: 1`, 5s interval, 30s ejection, up to 100% ejectable) to the `v2` subset, to demonstrate Istio circuit breaking under burst traffic. |
| `virtualservice.yaml` | Baseline `VirtualService`: static 90/10 weighted split between `v1`/`v2`. |
| `virtualservice-latency-v2.yaml`, `-v3.yaml`, `-v4 copy.yaml` | Iterative variants that add an `x-canary: true` header match forcing traffic to `v2` with an injected fixed delay (2s or 5s depending on the variant), alongside the 90/10 baseline split for unmatched traffic. |
| `virtualservice-error-injection-v5.yaml` | Variant that instead forces `x-canary: true` traffic to `v2` **and** aborts it with an HTTP 500 (100% of matched requests), to demonstrate error injection rather than latency injection. |
| `enforce-mtls-only.yaml` | Mesh-wide `PeerAuthentication` (`STRICT` mTLS) — applies to the whole mesh, not just this service, since it's named `default` in the `istio-system` root namespace. |
| `ingress-gateway.yaml` | `Gateway` + `VirtualService` routing external `/transaction` traffic (matched by URI prefix) to `transaction-service`. Despite living in this folder, this configures ingress for `transaction-service`, not `fraud-service`. |
| `ingress-gateway-fault-tolerance.yaml` | Alternative ingress `Gateway`/`VirtualService` pair that instead injects a 10% synthetic `503` abort at the gateway, for testing client-side fault tolerance. **Defines an object with the same name as `ingress-gateway.yaml`** — apply only one of the two. |
| `ingress-gateway-readme-docker-desktop.readme.md` | Notes on why NodePort access to the ingress gateway often fails on Docker-based local clusters, and why `kubectl port-forward` is the reliable local workaround. |
| `opentelemetry-collector.yaml` | An OpenTelemetry Collector `Deployment` (captured via `kubectl get -o yaml`, so it includes live cluster metadata/status fields) — sidecar injection explicitly disabled on this workload (`sidecar.istio.io/inject: "false"`), OTLP ports `4317`/`4318` exposed for optional tracing/metrics collection. |

> Only one variant of the `VirtualService`/`DestinationRule` for `fraud-service`, and only one of the two `Gateway`/`VirtualService` ingress pairs, should be applied at a time — several of these files define objects with the same `metadata.name` and are meant to be swapped in one at a time to demonstrate a specific behavior.
