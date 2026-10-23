# Incident & Log Analyzer API

![CI](https://github.com/lenahabdulrahman/incident-api/actions/workflows/ci.yml/badge.svg)

A small REST API built with **FastAPI** for log analysis and incident SLA checking, based on my experience in production support and incident management.

**Live API (try it in the browser):** https://incident-api-one.vercel.app/docs

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check (suitable for liveness/readiness probes) |
| POST | `/analyze` | Parse logs: counts by level, top errors, peak error hour |
| POST | `/sla` | Check if an incident is within its SLA by priority (P1-P4) |

## Examples

Analyze logs:

```bash
curl -X POST https://incident-api-one.vercel.app/analyze \
  -H "Content-Type: application/json" \
  -d '{"logs": "2026-10-20 10:05:11 ERROR Database connection timeout\n2026-10-20 10:07:45 ERROR Database connection timeout\n2026-10-20 11:03:00 CRITICAL Disk full"}'
```

Check SLA:

```bash
curl -X POST https://incident-api-one.vercel.app/sla \
  -H "Content-Type: application/json" \
  -d '{"priority": "P1", "opened_at": "2026-10-20T08:00:00", "resolved_at": "2026-10-20T14:00:00"}'
```

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn api.index:app --reload
```

Open http://127.0.0.1:8000/docs

## Tests

```bash
pytest
```

Tests run automatically on every push with GitHub Actions.

## Roadmap

- [x] REST API with Swagger docs, deployed on Vercel
- [x] Unit tests and CI (GitHub Actions)
- [x] Dockerfile
- [x] Kubernetes manifests with health probes (minikube)
- [ ] Helm chart
- [ ] GitLab CI pipeline
