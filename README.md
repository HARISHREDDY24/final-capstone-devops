# ResolveHub — DevOps Final Capstone

ResolveHub is a support-ticket operations dashboard built to demonstrate the end-to-end software delivery lifecycle: a React frontend, FastAPI REST API, PostgreSQL persistence, automated tests, Docker, CI/CD, container scanning, Terraform, Kubernetes/Helm, and Prometheus/Grafana observability.

> **Important:** This repository is a project implementation scaffold. Local code and tests should be verified on your machine; cloud provisioning, GHCR publication, live monitoring, and screenshots can only be completed in your own GitHub/AWS/Kubernetes environment. Do not claim a deployment succeeded until you have run and captured it.

## Architecture

```text
Browser :3000
    |
    v
Nginx / React (frontend container)
    | /api/*
    v
FastAPI :8000 ---- PostgreSQL :5432
    | /metrics
    v
Prometheus ---- Grafana

Git push -> GitHub Actions -> pytest + frontend build -> Docker images
                                      -> Trivy scan -> GHCR
Terraform -> AWS VPC + EKS -> Helm -> frontend/backend/PostgreSQL
```

## Features

- Support tickets with title, description, requester, category, priority, and status.
- Search and status filtering; create, update-status, and delete actions.
- Dashboard counts, priority breakdown, responsive layout, loading and API-unavailable states.
- REST API with list, detail, create, update, delete, statistics, health, readiness, and Prometheus metrics endpoints.
- SQLAlchemy ORM and Alembic migration for PostgreSQL schema management.
- Eight automated API tests using an isolated SQLite test database.
- Docker Compose stack with PostgreSQL health checks and container health checks.
- Non-root runtime users, multi-stage frontend image, GitHub Actions, SHA-tagged GHCR images, Trivy scanning, Terraform VPC/EKS, Helm, Ingress, HPA, and monitoring configuration.

## Video recording

For a step-by-step screen-recording plan, realistic demo data, a suggested narration, and a checklist, see [`VIDEO_DEMO_GUIDE.md`](VIDEO_DEMO_GUIDE.md). Start the stack and verify it is live before recording; do not claim cloud resources are deployed unless you have verified them.

## 1. Prerequisites

For the recommended local run, install Docker Desktop (Windows/macOS) or Docker Engine + Docker Compose plugin (Linux). Ensure Docker is running. Git is recommended for version control.

Optional for individual components: Python 3.12+, Node.js 22+, npm, PostgreSQL, Terraform 1.6+, AWS CLI, kubectl, Helm 3, and an AWS account with sufficient permissions/quotas.

## 2. Run the complete application locally (recommended)

From the repository root:

```bash
# Optional: create your local environment file
cp .env.example .env
# On Windows PowerShell use: Copy-Item .env.example .env

# Build and start frontend, backend and PostgreSQL
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- FastAPI Swagger: http://localhost:8000/docs
- API health: http://localhost:8000/health
- Readiness (includes DB check): http://localhost:8000/ready
- Metrics: http://localhost:8000/metrics

Try creating a ticket in the UI. It should be persisted in PostgreSQL. Stop with `Ctrl+C`, then run `docker compose down`. To delete the local database volume and all local ticket data too, run `docker compose down -v`.

The default password is only for local classroom use. Change it in `.env` before sharing the project. Never use the example password in a public deployment.

## 3. Run backend tests

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

Tests use a temporary in-memory SQLite database; they do not connect to the development or production database. Expected: all 8 tests pass. If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process Bypass` for that terminal or invoke `.venv\Scripts\python.exe -m pytest -v` directly.

## 4. Run frontend separately (optional)

The frontend expects an API at `/api` by default. For local frontend-only development, start the backend on port 8000 and use Vite's proxy. The simplest full-stack development path is Docker Compose. To run the Vite dev server against a backend, add this proxy to `frontend/vite.config.js`:

```js
server: { proxy: { '/api': 'http://localhost:8000', '/health': 'http://localhost:8000', '/ready': 'http://localhost:8000', '/metrics': 'http://localhost:8000' } }
```

Then from `frontend/`: `npm install`, `npm run dev`, open the URL Vite prints. For the built Docker deployment, Nginx routes `/api` to the backend service.

## 5. API quick reference

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/ready` | Database readiness check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/tickets` | List/search/filter tickets |
| GET | `/api/tickets/{id}` | Read one ticket |
| POST | `/api/tickets` | Create ticket |
| PUT | `/api/tickets/{id}` | Update ticket fields/status |
| DELETE | `/api/tickets/{id}` | Delete ticket |
| GET | `/api/tickets/stats` | Dashboard counts |

Use Swagger at `/docs` to explore requests and responses.

## 6. GitHub repository and CI/CD

1. Create a new **public** GitHub repository named `resolvehub-devops-capstone` (or another unique name).
2. From the project root:

   ```bash
   git init
   git add .
   git commit -m "Build ResolveHub support ticket application"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/resolvehub-devops-capstone.git
   git push -u origin main
   ```
3. In repository **Settings → Actions → General**, allow GitHub Actions and ensure the workflow has package write permissions (the workflow declares `packages: write`).
4. Open **Actions** and inspect the run. The workflow tests and builds on pushes/PRs. On pushes to `main`, it builds both images, scans them with Trivy, and pushes SHA-tagged images to GHCR.
5. If Trivy finds an unfixed HIGH/CRITICAL issue, the job intentionally fails. Inspect the finding, update the affected base image/dependency, and rerun. Do not disable the security gate just to make the workflow green.
6. GitHub may make GHCR packages private by default. Set package visibility appropriately for your evaluator, or configure Kubernetes image pull credentials if keeping packages private.

**Note:** GHCR image paths use the lowercase GitHub owner and image names `resolvehub-backend` and `resolvehub-frontend`; the image tag is the commit SHA, not `latest`.

## 7. Terraform: AWS VPC + EKS

**Cost warning:** EKS, EC2 worker nodes, NAT Gateway, storage, and data transfer may incur charges. Confirm the current price and quotas before provisioning. Restrict the cluster API endpoint to your IP before applying. Never commit credentials or Terraform state.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars if needed; keep it out of Git.
aws configure
terraform init
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
aws eks update-kubeconfig --region ap-south-1 --name resolvehub-eks
kubectl get nodes
```

The configuration creates a VPC with public/private subnets, a NAT Gateway, an EKS control plane, and a managed worker node group. Before apply, replace the example `203.0.113.10/32` in `terraform.tfvars` with your own public IP followed by `/32`; the example address is reserved for documentation and will not allow your connection. AWS permissions, region support, quotas, and EKS version availability can affect provisioning.

When finished with the cloud demonstration:

```bash
terraform destroy
```

Run destroy from the same Terraform directory/state. Save a screenshot of destroy completion for the rubric.

## 8. Deploy to Kubernetes with Helm

1. Publish the images via GitHub Actions first. Copy the exact SHA tag from GHCR.
2. Edit `helm/resolvehub/values.yaml` (or create a private override file) with your lowercase GHCR owner and exact image SHA tags. Replace the database password with a strong secret. Do not commit real secrets.
3. Install an Ingress controller (for example, ingress-nginx) and Metrics Server in the cluster. HPA requires Metrics Server and resource requests.
4. Deploy:

   ```bash
   kubectl apply -f k8s/namespace.yaml
   helm upgrade --install resolvehub ./helm/resolvehub \
     --namespace resolvehub --create-namespace \
     --set backend.image=ghcr.io/YOUR_GITHUB_USERNAME/resolvehub-backend \
     --set frontend.image=ghcr.io/YOUR_GITHUB_USERNAME/resolvehub-frontend \
     --set backend.tag=YOUR_COMMIT_SHA \
     --set frontend.tag=YOUR_COMMIT_SHA \
     --set database.password='REPLACE_WITH_STRONG_PASSWORD'
   kubectl get pods,svc,ingress,hpa -n resolvehub
   helm list -n resolvehub
   ```

5. For local name resolution, add the Ingress address and `resolvehub.local` to your hosts file. Or use the Ingress LoadBalancer hostname/IP if your controller provisions one. Open `http://resolvehub.local`.

For a quick in-cluster learning demo, PostgreSQL runs with a PVC in Kubernetes. This is not a highly available production database design. For production, consider managed PostgreSQL such as Amazon RDS, a managed secret store, private cluster access, TLS, and backup/restore procedures.

## 9. Prometheus and Grafana

Follow `monitoring/README.md`. Install `kube-prometheus-stack`, check Prometheus **Status → Targets**, and confirm `resolvehub-backend` is `UP`. Access Grafana with port-forwarding, add a panel from the available metrics, and capture screenshots. Use `kubectl get svc -n monitoring` to confirm the actual service names for your installed chart version.

## 10. Troubleshooting lab

These files are intentionally broken examples. Apply them only to the test namespace and clean them up afterwards.

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n resolvehub
kubectl describe pod broken-image-lab -n resolvehub
kubectl get events -n resolvehub --sort-by=.lastTimestamp
kubectl delete -f troubleshooting/broken-image.yaml

kubectl apply -f troubleshooting/broken-service.yaml
kubectl get endpoints broken-backend-service-lab -n resolvehub
kubectl get pods -n resolvehub --show-labels
kubectl delete -f troubleshooting/broken-service.yaml
```

Expected lessons: invalid image tags lead to `ImagePullBackOff`; Service selectors that do not match Pod labels produce no endpoints.

## 11. Submission evidence checklist

- [ ] Browser screenshot showing ResolveHub with data and working create-ticket flow.
- [ ] `pytest -v` output showing all tests passing.
- [ ] Public repository URL and meaningful commit history (aim for 10+ genuine incremental commits; do not fabricate history).
- [ ] Successful `docker compose up --build` terminal and browser screenshot.
- [ ] GitHub Actions green run and GHCR package screenshots with SHA tags.
- [ ] Trivy output and 2–3 sentence explanation of the scan.
- [ ] Terraform plan, AWS VPC/EKS, and terraform destroy screenshots.
- [ ] `kubectl get pods -n resolvehub`, `kubectl get svc -n resolvehub`, and `helm list -n resolvehub` screenshots.
- [ ] Application accessed through Ingress.
- [ ] `/metrics`, Prometheus target `UP`, and Grafana populated-panel screenshots.
- [ ] Final short demo: create a ticket, show API/docs and database, commit a change, inspect CI, demonstrate Kubernetes and monitoring, then explain a troubleshooting issue.

## Security notes

This is an educational capstone, not a hardened production service. It intentionally omits authentication/authorization and multi-tenant access controls. Before real use, add authentication, authorization, request rate limits, audit logging, robust secret management, TLS, backups, and data retention controls. Do not expose a real support-ticket system publicly as-is.
