{{- define "resolvehub.labels" -}}
app.kubernetes.io/name: resolvehub
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
