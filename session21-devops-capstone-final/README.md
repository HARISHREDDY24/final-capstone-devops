# TaskBoard — DevOps Final Capstone

**Project owner:** Harish  
**Session:** 21 — Python / DevOps Final Capstone  
**Application:** TaskBoard, a small SaaS-style project and task management dashboard

TaskBoard demonstrates the path from application code to a containerized, tested, scanned and deployable Kubernetes workload. The repository is organized as a runnable classroom project, with cloud deployment kept optional so local development does not require AWS spending.

## Features

- Responsive React + Vite dashboard with task creation, status changes, search, filtering, priorities and summary metrics.
- FastAPI REST API with task CRUD, statistics, liveness/readiness checks, and Prometheus metrics.
- PostgreSQL database, SQLAlchemy ORM and an Alembic migration.
- Pytest API tests that use an isolated SQLite database.
- Dockerfiles and Docker Compose for the complete local stack.
- GitHub Actions for tests, frontend build, container builds, Trivy scans and GHCR publishing.
- Terraform modules for an AWS VPC and EKS cluster.
- Helm chart for frontend, backend, PostgreSQL, Ingress, HPA and ServiceMonitor.
- Prometheus/Grafana values and a starter dashboard.
- Intentionally broken Kubernetes resources for controlled troubleshooting exercises.

## Architecture

```text
Browser
  | http://localhost:3000
  v
React static build (Nginx)
  | /api/* reverse proxy
  v
FastAPI :8000  -----> PostgreSQL :5432
  | /metrics
  v
Prometheus -----> Grafana

Git push -> GitHub Actions -> pytest + frontend build -> Docker builds
          -> Trivy scan -> GHCR -> (optional manual) Helm deploy to EKS
Terraform provisions AWS networking and EKS; Helm manages application resources.
```

## 1. Run the full application locally (recommended)

### Prerequisites

- Docker Desktop / Docker Engine with Docker Compose v2
- Git
- A browser

You do **not** need AWS, Terraform, Kubernetes, Node.js or Python installed for the Docker Compose demo.

### Start

```bash
# If you downloaded the ZIP, extract it and enter its folder first.
cd session21-devops-capstone-final
cp .env.example .env
docker compose up --build

# If cloning your own GitHub repository instead, enter that repository's folder
# (the folder name may differ from the example above), then run the last two commands.
```

Open:

- Dashboard: <http://localhost:3000>
- FastAPI Swagger: <http://localhost:8000/docs>
- Liveness: <http://localhost:8000/health>
- Readiness (checks PostgreSQL): <http://localhost:8000/ready>
- Prometheus metrics: <http://localhost:8000/metrics>

The API and frontend are both routed by Nginx/Compose, so the browser uses relative `/api/...` URLs and does not need to know the backend container hostname.

For a populated dashboard screenshot or presentation demo, seed five sample tasks after the containers are healthy:

```bash
docker compose exec backend python -m app.seed
```

The seed command is idempotent: it skips seeding when any task already exists. It does not run automatically, so your database remains under your control.

Stop the containers:

```bash
docker compose down
```

Remove the local PostgreSQL data volume too (destructive; deletes demo tasks):

```bash
docker compose down -v
```

## 2. Run the backend directly (optional)

Prerequisites: Python 3.12+ and PostgreSQL. Run commands from the repository root.

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DATABASE_URL = "postgresql+psycopg://taskboard:taskboard-local-only@localhost:5432/taskboard"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://taskboard:taskboard-local-only@localhost:5432/taskboard'
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Run the backend tests separately using the test instructions below. Tests use SQLite and do not need a PostgreSQL server.

## 3. Run the frontend directly (optional)

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` requests to `http://localhost:8000`. Make sure the backend is running first.

## API reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Service metadata |
| `GET` | `/health` | Liveness check |
| `GET` | `/ready` | Readiness check including database connectivity |
| `GET` | `/metrics` | Prometheus-format HTTP counters and latency histogram |
| `GET` | `/api/tasks` | List tasks; optional `status`, `q`, `skip`, `limit` parameters |
| `POST` | `/api/tasks` | Create a task |
| `GET` | `/api/tasks/{id}` | Read one task |
| `PUT` | `/api/tasks/{id}` | Update a task |
| `DELETE` | `/api/tasks/{id}` | Delete a task |
| `GET` | `/api/tasks/stats` | Dashboard aggregate statistics |

Example create request:

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Prepare capstone demo","description":"Show the CI pipeline","status":"In Progress","priority":"High","assignee":"Harish"}'
```

Allowed statuses: `Todo`, `In Progress`, `Done`. Allowed priorities: `Low`, `Medium`, `High`.

## 4. Tests and quality checks

Backend tests:

```bash
cd backend
python -m pip install -r requirements.txt
pytest -q
```

Frontend production build:

```bash
cd frontend
npm install
npm run build
```

Docker build checks:

```bash
docker build -t taskboard-backend:local ./backend
docker build -t taskboard-frontend:local ./frontend
```

The GitHub Actions workflow runs backend tests and builds the frontend on pull requests and pushes. On pushes to `main`, it builds container images, scans both images with Trivy for HIGH/CRITICAL vulnerabilities (ignoring unfixed findings), and pushes images tagged with the Git commit SHA to GitHub Container Registry (GHCR). A scan failure blocks the publish step.

## 5. Push this project to your GitHub repository

Create an **empty** repository on GitHub first. Then run the following from this project folder (replace the URL):

```bash
git init
git add .
git commit -m "Build TaskBoard DevOps capstone"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
git push -u origin main
```

If you are adding this project inside an existing repository, do not run `git init` again. Copy this folder's contents into your chosen assignment folder, then commit and push from the existing repository root.

### Configure GitHub Actions / GHCR

1. Push the project to the default branch named `main`.
2. Open **Actions** in GitHub and allow workflows if prompted.
3. On the first successful `main` push, check **Actions** for tests, builds and Trivy results.
4. Check the repository's **Packages** page for `taskboard-backend` and `taskboard-frontend` images.
5. For an easy classroom deployment, set both GHCR packages to **public**. If you keep packages private, create a namespace `imagePullSecret` and configure `imagePullSecrets` in Helm values before deployment.

No cloud credentials are needed for the CI build/scan/push workflow. The EKS deployment workflow is manually triggered and requires the AWS/GitHub configuration described below.

## 6. Optional AWS infrastructure with Terraform

> **Cost warning:** EKS control-plane hours, EC2 worker nodes, NAT Gateway hours/data, EBS volumes, load balancers, public IPv4 addresses and network transfer can cost money. Do not run `terraform apply` unless you have checked current AWS pricing and your account's budget. Always run `terraform destroy` when the demo is finished, then verify the resources were removed.

Prerequisites: AWS CLI configured for the target account, Terraform 1.6+, and an IAM identity allowed to create the listed resources. Use a non-production account.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform plan
# Only after reviewing all planned resources and estimated costs:
terraform apply
```

The sample creates a VPC with public/private subnets, a single NAT Gateway, an EKS 1.36 cluster, and a managed node group. The Kubernetes version is a variable; use a version supported in your AWS region/account. Infrastructure module versions are pinned in `main.tf` / `versions.tf`.

After apply, configure `kubectl` using the output command or run:

```bash
aws eks update-kubeconfig --region ap-south-1 --name taskboard-eks
kubectl get nodes
```

Destroy the sample stack when finished:

```bash
terraform destroy
```

Keep `terraform.tfvars`, state files, AWS credentials, tokens and secrets out of Git. `.gitignore` excludes Terraform state and local tfvars files.

## 7. Deploy with Helm to Kubernetes

Install `kubectl`, Helm, an AWS CLI, and an NGINX Ingress Controller in the target cluster. The Terraform-created EKS cluster is not automatically configured with the ingress controller or Prometheus/Grafana; install those components as described in `monitoring/README.md` and below.

Create the namespace and deploy the chart:

```bash
kubectl apply -f k8s/namespace.yaml
helm upgrade --install taskboard ./helm/taskboard \
  --namespace taskboard --create-namespace \
  -f helm/taskboard/values-dev.yaml
kubectl get pods,svc,hpa -n taskboard
```

The chart's default image names are local/demo placeholders. Install Metrics Server if your cluster does not already expose the resource metrics API (required for CPU-based HPA): `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`. For a published deployment, set `backend.image.repository`, `frontend.image.repository` and both tags to the images from GHCR, for example:

```bash
helm upgrade --install taskboard ./helm/taskboard \
  --namespace taskboard --create-namespace \
  --set backend.image.repository=ghcr.io/<owner>/<repo>-backend \
  --set frontend.image.repository=ghcr.io/<owner>/<repo>-frontend \
  --set backend.image.tag=<git-sha> \
  --set frontend.image.tag=<git-sha> \
  --set ingress.enabled=true
```

If using private GHCR packages, create an `imagePullSecret` in the `taskboard` namespace and add its name to `imagePullSecrets` in your Helm override file. Do not place a token directly in Git or in a committed values file.

The two Ingress resources expect an NGINX Ingress Controller and host `taskboard.local`. To test locally, point `taskboard.local` to the Ingress address in your hosts file. For a public demo, configure a real DNS name and TLS before sharing it. Check the route configuration in `helm/taskboard/templates/ingress.yaml` if your controller differs.

### Optional manually triggered GitHub deployment workflow

`.github/workflows/deploy-eks.yml` deploys a selected image SHA. Configure GitHub repository secrets/variables for AWS OIDC before running it:

- Secret `AWS_ROLE_ARN`: IAM role trusted by GitHub OIDC and authorized to update the EKS cluster.
- Variable `AWS_REGION`: target AWS region, for example `ap-south-1`.
- Variable `EKS_CLUSTER_NAME`: Terraform-created cluster name, for example `taskboard-eks`.
- Optional secrets `GHCR_USERNAME` and `GHCR_TOKEN` if the images are private. Prefer a narrowly scoped token with package read permission; public images need no token.

The role must be granted EKS access in AWS. The workflow will not succeed until these account-specific prerequisites exist.

## 8. Prometheus and Grafana

Install `kube-prometheus-stack` into a `monitoring` namespace using the provided values file:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack-values.yaml
```

Enable the chart's `ServiceMonitor`, then install the dashboard ConfigMap:

```bash
helm upgrade --install taskboard ./helm/taskboard \
  --namespace taskboard --reuse-values \
  --set serviceMonitor.enabled=true
kubectl apply -f monitoring/taskboard-dashboard-configmap.yaml
```

Open Grafana through your chosen safe access method (for a classroom cluster, use `kubectl port-forward` rather than exposing Grafana publicly), and select the **TaskBoard API** dashboard. The dashboard uses the custom counters and latency histogram from `/metrics`.

## 9. Autoscaling and load testing

The backend HPA targets average CPU utilization. Kubernetes needs Metrics Server and resource requests before HPA can scale. The EKS module installs standard EKS add-ons, but verify Metrics Server is available in your cluster. Then:

```bash
kubectl get hpa -n taskboard
kubectl top pods -n taskboard
python scripts/load_test.py --url http://localhost:8000 --seconds 60 --workers 12
```

For Kubernetes, port-forward the service or use the Ingress URL as the load test URL. Simple health checks may not generate sufficient CPU usage to scale; record the observed metrics rather than claiming scale-out if it does not occur.

## 10. Troubleshooting lab

**Broken image / `ImagePullBackOff`:**

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n taskboard
kubectl describe pod -n taskboard -l app=troubleshooting-broken-image
kubectl get events -n taskboard --sort-by=.lastTimestamp
```

**Service without endpoints:**

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get svc -n taskboard
kubectl get endpoints -n taskboard troubleshooting-empty-service
kubectl get pods -n taskboard --show-labels
```

These manifests create separate lab resources and are designed not to replace the Helm-managed application. Clean them up when done:

```bash
kubectl delete -f troubleshooting/broken-image.yaml
kubectl delete -f troubleshooting/broken-service.yaml
```

## 11. Submission checklist

- [ ] README includes project overview, architecture, setup, API, testing and troubleshooting.
- [ ] `docker compose up --build` runs the UI, API and database.
- [ ] At least four REST operations are demonstrated; this project includes all CRUD routes plus stats and health endpoints.
- [ ] `pytest -q` passes.
- [ ] Frontend production build passes.
- [ ] GitHub Actions CI succeeds.
- [ ] Trivy scan output is visible in Actions; resolve any blocking HIGH/CRITICAL issue instead of hiding it.
- [ ] GHCR contains backend and frontend images tagged with the commit SHA.
- [ ] Terraform formatting/validation succeeds; infrastructure plan is captured if AWS is not provisioned.
- [ ] Helm templates install successfully in a disposable cluster.
- [ ] Ingress, HPA, Prometheus/Grafana and the two troubleshooting scenarios are demonstrated if cluster resources are available.
- [ ] Add your own screenshots to `docs/screenshots/` after running the project. Do not submit mock screenshots as proof of a deployment.
- [ ] Record a short demo or prepare a presentation showing code → commit → CI → images → deployment → monitoring → troubleshooting.

## Suggested screenshots to capture yourself

1. Dashboard with tasks and KPI cards (`01-dashboard.png`).
2. FastAPI Swagger page and a successful create/read/update/delete flow (`02-api.png`).
3. Passing Pytest + frontend build in GitHub Actions (`03-ci.png`).
4. Trivy scan and GHCR images (`04-security-registry.png`).
5. Terraform plan or AWS EKS resources (`05-infrastructure.png`).
6. Pods, Services, HPA and Ingress (`06-kubernetes.png`).
7. Prometheus target and Grafana dashboard (`07-monitoring.png`).
8. `ImagePullBackOff` / no-endpoints troubleshooting and the corrective commands (`08-troubleshooting.png`).

## Important honesty note for the final report

Only mark a stage complete after you have actually run it and captured evidence. A local Docker Compose success does not prove an EKS deployment, and Terraform files do not prove that AWS infrastructure was created. Include the CI run URL, image tags, cluster output and screenshots that you observed yourself.
