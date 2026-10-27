# Rubric-to-file mapping

| Rubric section | Implementation |
|---|---|
| M1 Application (10) | `frontend/`, `backend/app/`, `backend/alembic/versions/`, `docker-compose.yml` |
| M2 Testing (10) | `backend/tests/test_api.py` (8 tests), `backend/pytest.ini`, `backend/tests/conftest.py` |
| M3 Git/GitHub (5) | `.gitignore`, root `README.md`; push repository and make genuine commits |
| M4 Docker (10) | `backend/Dockerfile`, `frontend/Dockerfile` (multi-stage), `docker-compose.yml` |
| M5 CI/CD (15) | `.github/workflows/ci-cd.yml`, SHA-tagged GHCR images |
| M6 Trivy (5) | Trivy scans for both images; HIGH/CRITICAL gate enabled |
| M7 Terraform (15) | `terraform/*.tf`, `terraform.tfvars.example` |
| M8 Kubernetes/Helm (15) | `k8s/namespace.yaml`, `helm/resolvehub/` |
| M9 Monitoring (10) | FastAPI `/metrics`, `monitoring/` |
| M10 Presentation/docs (5) | `README.md`, this checklist; user must capture evidence and demo |

A repository cannot honestly include proof of live cloud resources, successful GitHub Actions runs, screenshots, or a populated Grafana dashboard before those steps have been executed in the user's accounts. Complete those checklist items in the real environment.
