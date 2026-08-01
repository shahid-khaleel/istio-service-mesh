# Fintech-istio-poc

This directory contains the authored proof-of-concept: two FastAPI microservices (`fraud-service`, `transaction-service`) plus the Istio/Kubernetes manifests, test scripts, and a Kiali screenshot used to demonstrate Istio service-mesh capabilities against them.

See the [repository root README](../README.md) for the full architecture diagram, quick start, and security notes. This file focuses on what lives specifically in this directory.

## Contents

| Path | Purpose |
|---|---|
| `fraud-service/` | Risk-scoring microservice. See [`fraud-service/README.md`](fraud-service/README.md). |
| `transaction-service/` | Transaction-orchestration microservice. See [`transaction-service/README.md`](transaction-service/README.md). |
| `test.sh` | Randomized load-generation script hitting `transaction-service` directly. |
| `test2.sh` | Same, via a fixed NodePort, with ~10% of requests carrying an `x-canary` header. |
| `test-ingress.gateway.sh` | Same load pattern, routed through the Istio ingress gateway (`kubectl port-forward svc/istio-ingressgateway`). |
| `Kiali-svc.PNG` | Kiali service-graph screenshot captured during a test run — a visual snapshot of the mesh topology and traffic split, not a live/regenerated artifact. |

## How the pieces fit together

```
client --> Istio ingress gateway --> transaction-service --(mTLS)--> fraud-service (v1/v2 subsets)
```

- `transaction-service` is the only service exposed through the ingress gateway's `VirtualService` (`/transaction` prefix).
- `transaction-service` calls `fraud-service` internally over the cluster DNS name `fraud-service.default.svc.cluster.local`; this call is transparently encrypted by Istio's sidecar-to-sidecar mTLS (mesh-wide `STRICT` policy, see `fraud-service/kubernetes/enforce-mtls-only.yaml`).
- `fraud-service` runs two versions (`v1`, `v2`) as separate `Deployment`s mapped to `DestinationRule` subsets, normally split 90/10 by weight, with `v2` also used as the target for canary/fault-injection/circuit-breaking experiments.

Run the test scripts from this directory (or reference them with a relative/absolute path) after deploying — see the root README's Quick Start for the full `kubectl apply` sequence.
