# Lab 10 — Operations: observability + deployment (Kubernetes intro)

## Learning goals
- Identify the “golden signals”: latency, traffic, errors, saturation.
- Add basic metrics/logs/traces to a service.
- Deploy, scale, and roll back using Kubernetes.

## In-class walkthrough
1. **Instrumentation**
   - Add structured logs and basic metrics to the RPC service.
   - Introduce traces with OpenTelemetry SDK (minimal setup).
2. **Run a local cluster**
   - Create a kind cluster and verify `kubectl` connectivity.
3. **Deploy + scale**
   - Apply a Deployment + Service manifest.
   - Scale replicas and watch rolling updates.
4. **Observe**
   - Use `kubectl logs`, `kubectl describe`, and metrics output.

## Student deliverable
- A kind cluster running the service.
- A one-command deploy script (e.g., `make deploy`).
- Short notes on how to scale and roll back.

## Instructor notes
- Keep observability minimal: focus on what signals mean.
- Emphasize reproducible environments for grading.
- Encourage students to clean up resources (`kind delete cluster`).

## Tools (free + open source)
- kind (Kubernetes in Docker).
- kubectl.
- OpenTelemetry SDK + Collector (optional).

## Suggested reading & sources
- kind quick start: https://kind.sigs.k8s.io/docs/user/quick-start/
- Kubernetes Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- OpenTelemetry Collector: https://opentelemetry.io/docs/collector/
