Here’s a clean and professional `README.md` you can use for your Istio Ingress + Local Kubernetes setup:

---

# Istio Ingress Gateway – Local Kubernetes Setup

This project demonstrates how to access and test an Istio Ingress Gateway running in a local Kubernetes cluster (Docker-based environment).

## 📌 Environment

* Kubernetes running inside Docker (Docker Desktop / kind / kubeadm in Docker)
* Istio installed
* `istio-ingressgateway` Service type: `LoadBalancer`
* Local testing via NodePort and port-forward

---

## 🔎 Service Details

```
NAME                   TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
istio-ingressgateway   LoadBalancer   10.96.86.100    172.18.0.6    15021:30401/TCP,
                                                              80:32250/TCP,
                                                              443:32395/TCP,
                                                              31400:30928/TCP,
                                                              15443:30683/TCP
```

### Important Ports

| Service Port | NodePort | Purpose            |
| ------------ | -------- | ------------------ |
| 80           | 32250    | HTTP traffic       |
| 443          | 32395    | HTTPS traffic      |
| 15021        | 30401    | Health/Status port |
| 31400        | 30928    | TLS passthrough    |
| 15443        | 30683    | mTLS passthrough   |

---

## ⚠️ Understanding the External IP

The `EXTERNAL-IP` (`172.18.0.6`) is **not a public IP**.

Since Kubernetes is running inside Docker, this IP belongs to Docker’s internal bridge network. It is only accessible from inside that network — not directly from your host machine.

---

## ❌ Why `http://localhost:32250` Shows Connection Refused

In Docker-based clusters:

* NodePorts exist inside the Docker network.
* They are **not automatically exposed to localhost**.
* Unless ports were explicitly mapped during cluster creation, direct NodePort access will fail.

---

## ✅ Recommended Way to Access Istio Ingress (Local)

Use port forwarding:

```bash
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

Then access:

```
http://localhost:8080
```

This bypasses Docker networking complexity and tunnels traffic directly to the service.

---

## 🧠 Traffic Flow (Local Setup)

```
Browser
   ↓
localhost:8080 (port-forward)
   ↓
Istio Ingress Gateway (Envoy)
   ↓
VirtualService routing
   ↓
Backend Service
   ↓
Pod
```

---

## 🔍 Useful Debug Commands

Check ingress gateway service:

```bash
kubectl get svc istio-ingressgateway -n istio-system
```

Check pods:

```bash
kubectl get pods -n istio-system
```

Check node details:

```bash
kubectl get nodes -o wide
```

Inspect service selectors:

```bash
kubectl get svc istio-ingressgateway -n istio-system -o yaml
```

---

## 🚀 Notes

* In a real cloud environment (e.g., AWS EKS), a true external load balancer would be provisioned automatically.
* In local Docker-based clusters, LoadBalancer is simulated.
* For development and experimentation, `kubectl port-forward` is the most reliable approach.

---

## 🎯 Goal

This setup enables:

* Testing Istio VirtualService routing
* Canary deployments
* Fault injection experiments
* Observability testing with Kiali / Prometheus

---

This README documents how traffic reaches your applications through the Istio Ingress Gateway in a local Kubernetes environment.

