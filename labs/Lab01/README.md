# Lab 01 — Distributed playground with Docker Compose

## Learning goals
- Distinguish containers from processes and how namespaces isolate resources.
- Use Compose to orchestrate multiple services with a shared network.
- Observe DNS-based service discovery in a Compose network.
- Practice scaling and inspecting logs for a distributed system.
- Connect the “mental model”: nodes are processes + imperfect networks.

## In-class walkthrough
1. **Build a tiny node service**
   - Node prints its ID at startup and serves `GET /health`.
   - Use an env var for node ID to make instances distinct.
2. **Compose stack**
   - Create a `compose.yaml` with `node` service and a `driver` service.
   - Explain default network creation and service name DNS.
3. **Demonstrate features**
   - `docker compose up --build --scale node=5`.
   - `docker compose logs -f` to aggregate logs.
   - `docker compose exec driver` to ping all nodes.
4. **Fault injection basics**
   - Stop one node and show the driver’s failure path.
   - Restart to show recovery and transient failures.

## Student deliverable
- A Compose stack that launches 5 nodes plus a driver container that pings each node and reports success/failure.
- A short `README.md` with commands to run, scale, and stop the system.

## Instructor notes
- Stress reproducibility: same Compose file, same topology for grading.
- Show that `node` is just a process in a container; the network is imperfect.
- Encourage students to read logs instead of guessing.

## Tools (free + open source)
- Docker Engine + Docker Compose.
- Python 3.11+ or Go 1.21+ (any is fine for the node service).
- curl or httpie for quick HTTP checks.

## Suggested reading & sources
- Docker Compose docs: https://docs.docker.com/compose/
- Compose file spec: https://docs.docker.com/compose/compose-file/
