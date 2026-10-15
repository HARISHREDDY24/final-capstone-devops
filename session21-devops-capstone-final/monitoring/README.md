# TaskBoard Monitoring

This folder includes a `kube-prometheus-stack` values file, a Prometheus dashboard JSON export, and a Grafana sidecar ConfigMap.

1. Install the Prometheus Operator / Grafana stack using the commands in the root README.
2. Deploy the TaskBoard Helm chart with `--set serviceMonitor.enabled=true`. The chart creates a `ServiceMonitor` labelled `release: monitoring`, matching the included Prometheus selector.
3. Apply `taskboard-dashboard-configmap.yaml` after the `monitoring` namespace exists.
4. Port-forward Grafana rather than exposing it publicly for a classroom demo:

   ```bash
   kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
   ```

   Then open <http://localhost:3000>. Obtain the admin password using the secret name produced by your Helm release; defaults can vary with chart versions.

The dashboard shows request rate, 5xx response rate, and p95 request latency. These panels can be empty until Prometheus has discovered the ServiceMonitor and at least one request has been made to the API. Also check that the Prometheus Operator CRDs exist and that the ServiceMonitor selector matches `release: monitoring`.
