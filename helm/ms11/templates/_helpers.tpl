{{/*
Expand the name of the chart.
*/}}
{{- define "ms11.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ms11.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ms11.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ms11.labels" -}}
helm.sh/chart: {{ include "ms11.chart" . }}
{{ include "ms11.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ms11.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ms11.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ms11.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ms11.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
PostgreSQL fullname
*/}}
{{- define "ms11.postgresql.fullname" -}}
{{- printf "%s-postgres" (include "ms11.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Redis fullname
*/}}
{{- define "ms11.redis.fullname" -}}
{{- printf "%s-redis" (include "ms11.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
XVFB fullname
*/}}
{{- define "ms11.xvfb.fullname" -}}
{{- printf "%s-xvfb" (include "ms11.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "ms11.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
postgresql://{{ .Values.postgresql.auth.username }}:{{ .Values.postgresql.auth.password }}@{{ include "ms11.postgresql.fullname" . }}-service:5432/{{ .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.url }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "ms11.redisUrl" -}}
{{- if .Values.redis.enabled }}
redis://{{ include "ms11.redis.fullname" . }}-service:6379/0
{{- else }}
{{- .Values.externalRedis.url }}
{{- end }}
{{- end }}

{{/*
Image name
*/}}
{{- define "ms11.image" -}}
{{- $registry := default .Values.ms11.image.registry .Values.global.imageRegistry }}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry .Values.ms11.image.repository .Values.ms11.image.tag }}
{{- else }}
{{- printf "%s:%s" .Values.ms11.image.repository .Values.ms11.image.tag }}
{{- end }}
{{- end }}

{{/*
Storage class
*/}}
{{- define "ms11.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else }}
{{- .Values.storageClass | default "default" }}
{{- end }}
{{- end }}

{{/*
Environment variables
*/}}
{{- define "ms11.env" -}}
- name: MS11_ENVIRONMENT
  value: {{ .Values.ms11.environment | quote }}
- name: MS11_LOG_LEVEL
  value: {{ .Values.ms11.logLevel | quote }}
- name: PYTHONPATH
  value: "/app"
- name: DISPLAY
  value: ":99"
- name: MS11_DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ include "ms11.fullname" . }}-secrets
      key: database-url
- name: MS11_REDIS_URL
  valueFrom:
    secretKeyRef:
      name: {{ include "ms11.fullname" . }}-secrets
      key: redis-url
- name: MS11_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "ms11.fullname" . }}-secrets
      key: secret-key
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
- name: POD_NAMESPACE
  valueFrom:
    fieldRef:
      fieldPath: metadata.namespace
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
{{- end }}

{{/*
Volume mounts
*/}}
{{- define "ms11.volumeMounts" -}}
{{- if .Values.ms11.persistence.data.enabled }}
- name: data
  mountPath: /app/data
{{- end }}
{{- if .Values.ms11.persistence.logs.enabled }}
- name: logs
  mountPath: /app/logs
{{- end }}
{{- if .Values.ms11.persistence.backups.enabled }}
- name: backups
  mountPath: /app/backups
{{- end }}
- name: x11-socket
  mountPath: /tmp/.X11-unix
{{- end }}

{{/*
Volumes
*/}}
{{- define "ms11.volumes" -}}
{{- if .Values.ms11.persistence.data.enabled }}
- name: data
  persistentVolumeClaim:
    claimName: {{ include "ms11.fullname" . }}-data
{{- end }}
{{- if .Values.ms11.persistence.logs.enabled }}
- name: logs
  persistentVolumeClaim:
    claimName: {{ include "ms11.fullname" . }}-logs
{{- end }}
{{- if .Values.ms11.persistence.backups.enabled }}
- name: backups
  persistentVolumeClaim:
    claimName: {{ include "ms11.fullname" . }}-backups
{{- end }}
- name: x11-socket
  emptyDir: {}
{{- end }}