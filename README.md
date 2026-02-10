# Distributed Systems Labs (Skeleton)

Starter template for a 10-lab Distributed Systems course with:
- **In-class labs** under `labs/`
- **Autograded take-home assignments** under `assignments/`
- **Pattern spotlights** under `patterns/`

## Run locally (instructor)
Prereqs: Docker + Docker Compose plugin, Python 3.10+

```bash
make deps
make grade
```

## Key ideas
- Students implement **only** under `assignments/*/submission/`
- Autograding uses:
  - unit tests (fast)
  - docker-compose integration tests (black-box)
