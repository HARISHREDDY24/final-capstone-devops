# Monitoring setup

Install kube-prometheus-stack after the ResolveHub chart is healthy. The included `dashboard-configmap.yaml` is picked up by the Grafana dashboard sidecar and provisions the ResolveHub Application Overview dashboard automatically:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/prometheus-values.yaml
kubectl apply -f monitoring/dashboard-configmap.yaml
```

Port-forward Grafana: `kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80` and open `http://localhost:3001`. The default username is `admin`; retrieve or set the password securely rather than committing it. Port-forward Prometheus using the service name shown by `kubectl get svc -n monitoring`.

The extra scrape target configures Prometheus to scrape `/metrics` from the backend Service. Confirm it on Prometheus **Status → Targets**. Open the automatically provisioned **ResolveHub Application Overview** dashboard. It includes request-rate, p95 latency, and 5xx count panels. Metric names may vary by instrumentation version; if a panel is empty, inspect `/metrics` first and adjust the query to match the exposed metric names.
