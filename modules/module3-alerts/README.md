# Module 3: Custom Alert Writing and Service Monitor

## Overview

This module covers creating custom alert rules for Prometheus and implementing ServiceMonitor resources to monitor your applications. You'll learn how to write effective alert rules, configure ServiceMonitor resources, and set up alert routing and notifications.

## Prerequisites

- Completed Modules 1 and 2
- Understanding of PromQL queries
- Access to create Kubernetes resources in your OCP cluster
- Basic understanding of alerting concepts

## Understanding Prometheus Alerting

### Alert Rule Components

Prometheus alert rules consist of several key components:

1. **Alert Name**: Unique identifier for the alert
2. **Expression**: PromQL query that defines the alert condition
3. **Labels**: Key-value pairs that provide context
4. **Annotations**: Human-readable information about the alert

### Alert States

- **Inactive**: Alert condition is not met
- **Pending**: Alert condition is met but not yet fired
- **Firing**: Alert is active and being sent to AlertManager

## Writing Custom Alert Rules

### Basic Alert Rule Structure

```yaml
groups:
- name: example
  rules:
  - alert: ExampleAlert
    expr: up == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Instance {{ $labels.instance }} is down"
      description: "{{ $labels.instance }} has been down for more than 5 minutes."
```

### Alert Rule Best Practices

#### 1. Use Meaningful Names
```yaml
# Good
- alert: HighCPUUsage

# Bad
- alert: Alert1
```

#### 2. Set Appropriate Durations
```yaml
# Use 'for' to prevent flapping
- alert: HighMemoryUsage
  expr: container_memory_usage_bytes > 1000000000
  for: 2m  # Wait 2 minutes before firing
```

#### 3. Use Descriptive Labels
```yaml
- alert: PodCrashLooping
  expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
  labels:
    severity: warning
    team: platform
    component: kubernetes
```

#### 4. Provide Clear Annotations
```yaml
- alert: NodeNotReady
  annotations:
    summary: "Node {{ $labels.node }} is not ready"
    description: "Node {{ $labels.node }} has been in NotReady state for more than 5 minutes. This may indicate hardware issues or network problems."
    runbook_url: "https://wiki.company.com/runbooks/node-not-ready"
```

## Creating Alert Rules for OCP

### 1. Cluster Health Alerts

#### Node Health
```yaml
groups:
- name: cluster-health
  rules:
  - alert: NodeNotReady
    expr: kube_node_status_condition{condition="Ready",status="false"} == 1
    for: 5m
    labels:
      severity: critical
      component: node
    annotations:
      summary: "Node {{ $labels.node }} is not ready"
      description: "Node {{ $labels.node }} has been in NotReady state for more than 5 minutes."

  - alert: HighNodeCPUUsage
    expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 10m
    labels:
      severity: warning
      component: node
    annotations:
      summary: "High CPU usage on node {{ $labels.instance }}"
      description: "Node {{ $labels.instance }} has CPU usage above 80% for more than 10 minutes."
```

#### Pod Health
```yaml
  - alert: PodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
    for: 5m
    labels:
      severity: warning
      component: pod
    annotations:
      summary: "Pod {{ $labels.pod }} is crash looping"
      description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is restarting frequently."

  - alert: PodNotReady
    expr: kube_pod_status_phase{phase="Pending"} > 0
    for: 10m
    labels:
      severity: warning
      component: pod
    annotations:
      summary: "Pod {{ $labels.pod }} is stuck in Pending state"
      description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has been in Pending state for more than 10 minutes."
```

### 2. Resource Utilization Alerts

#### Memory Alerts
```yaml
  - alert: HighMemoryUsage
    expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100 > 90
    for: 5m
    labels:
      severity: warning
      component: memory
    annotations:
      summary: "High memory usage in container {{ $labels.container }}"
      description: "Container {{ $labels.container }} in pod {{ $labels.pod }} is using more than 90% of its memory limit."

  - alert: NodeMemoryPressure
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 10m
    labels:
      severity: critical
      component: node
    annotations:
      summary: "High memory usage on node {{ $labels.instance }}"
      description: "Node {{ $labels.instance }} has memory usage above 85% for more than 10 minutes."
```

#### CPU Alerts
```yaml
  - alert: HighCPUUsage
    expr: rate(container_cpu_usage_seconds_total[5m]) * 100 > 80
    for: 10m
    labels:
      severity: warning
      component: cpu
    annotations:
      summary: "High CPU usage in container {{ $labels.container }}"
      description: "Container {{ $labels.container }} in pod {{ $labels.pod }} has CPU usage above 80% for more than 10 minutes."
```

### 3. Application-Specific Alerts

#### HTTP Metrics
```yaml
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
    for: 5m
    labels:
      severity: critical
      component: application
    annotations:
      summary: "High error rate for {{ $labels.job }}"
      description: "Error rate for {{ $labels.job }} is above 5% for more than 5 minutes."

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
      component: application
    annotations:
      summary: "High response time for {{ $labels.job }}"
      description: "95th percentile response time for {{ $labels.job }} is above 1 second for more than 5 minutes."
```

## ServiceMonitor Configuration

### What is ServiceMonitor?

ServiceMonitor is a Kubernetes custom resource that tells Prometheus how to scrape metrics from your applications. It's part of the Prometheus Operator and provides a declarative way to configure monitoring.

### Basic ServiceMonitor Structure

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app-monitor
  namespace: my-namespace
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### ServiceMonitor Best Practices

#### 1. Use Appropriate Selectors
```yaml
spec:
  selector:
    matchLabels:
      app: my-app
      monitoring: enabled
```

#### 2. Configure Scraping Intervals
```yaml
spec:
  endpoints:
  - port: metrics
    interval: 30s  # Scrape every 30 seconds
    scrapeTimeout: 10s  # Timeout after 10 seconds
```

#### 3. Use Multiple Endpoints
```yaml
spec:
  endpoints:
  - port: metrics
    path: /metrics
  - port: health
    path: /health
    interval: 60s
```

### Example ServiceMonitor Configurations

#### 1. Basic Application Monitoring
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: web-app-monitor
  namespace: production
  labels:
    app: web-app
spec:
  selector:
    matchLabels:
      app: web-app
      monitoring: enabled
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
    scheme: http
```

#### 2. Advanced Application Monitoring
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: api-service-monitor
  namespace: production
  labels:
    app: api-service
    team: backend
spec:
  selector:
    matchLabels:
      app: api-service
  endpoints:
  - port: metrics
    interval: 15s
    path: /metrics
    scheme: https
    tlsConfig:
      insecureSkipVerify: true
  - port: health
    interval: 60s
    path: /health
    scheme: http
```

#### 3. Database Monitoring
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: postgres-monitor
  namespace: database
spec:
  selector:
    matchLabels:
      app: postgres
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
    basicAuth:
      name: postgres-monitor-auth
      key: password
```

## Implementing Alert Rules in OCP

### Method 1: Using PrometheusRule CRD

Create a PrometheusRule resource in your OCP cluster:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: custom-alerts
  namespace: openshift-monitoring
  labels:
    prometheus: k8s
    role: alert-rules
spec:
  groups:
  - name: custom.rules
    rules:
    - alert: HighCPUUsage
      expr: rate(container_cpu_usage_seconds_total[5m]) * 100 > 80
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage detected"
        description: "Container {{ $labels.container }} has high CPU usage"
```

### Method 2: External Prometheus Configuration

Add alert rules to your external Prometheus configuration:

```yaml
# In prometheus.yaml
rule_files:
  - "/etc/prometheus/rules/*.yml"

# Create alert rules file
# /etc/prometheus/rules/custom-alerts.yml
groups:
- name: custom-alerts
  rules:
  - alert: HighCPUUsage
    expr: rate(container_cpu_usage_seconds_total[5m]) * 100 > 80
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
```

## Alert Routing and Notifications

### AlertManager Configuration in OpenShift

In OpenShift, AlertManager is configured using the **Alertmanager Custom Resource (CR)**. The configuration is provided as a Secret that contains the `alertmanager.yaml` content, which is then referenced by the Alertmanager CR.

#### Method 1: Using Alertmanager CRD (Recommended for OpenShift)

This is the recommended approach for OpenShift clusters:

**Step 1: Create a Secret with AlertManager configuration**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: alertmanager-main
  namespace: openshift-monitoring
type: Opaque
stringData:
  alertmanager.yaml: |
    global:
      # SMTP configuration for email notifications
      smtp_smarthost: 'smtp.example.com:587'
      smtp_from: 'alerts@example.com'
      smtp_auth_username: 'alerts@example.com'
      smtp_auth_password: 'your-smtp-password'
      smtp_require_tls: true
    
    route:
      group_by: ['alertname', 'cluster', 'service']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'default-receiver'
      routes:
      - match:
          severity: critical
        receiver: 'critical-alerts'
      - match:
          severity: warning
        receiver: 'warning-alerts'
    
    receivers:
    # Default receiver - Webhook
    - name: 'default-receiver'
      webhook_configs:
      - url: 'http://webhook-receiver.example.com:5001/alerts'
        send_resolved: true
    
    # Critical alerts - Email, Slack, and Webhook
    - name: 'critical-alerts'
      email_configs:
      - to: 'oncall@example.com'
        subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
        html: |
          <h2>Critical Alert</h2>
          <p><strong>Alert:</strong> {{ .GroupLabels.alertname }}</p>
          <p><strong>Summary:</strong> {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}</p>
          <p><strong>Description:</strong> {{ range .Alerts }}{{ .Annotations.description }}{{ end }}</p>
        send_resolved: true
      
      slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#critical-alerts'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        text: |
          *Alert:* {{ .GroupLabels.alertname }}
          {{ range .Alerts }}
          *Summary:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          {{ end }}
        send_resolved: true
        color: 'danger'
      
      webhook_configs:
      - url: 'http://critical-webhook.example.com:5001/alerts'
        send_resolved: true
    
    # Warning alerts - Slack
    - name: 'warning-alerts'
      slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        title: '⚠️ WARNING: {{ .GroupLabels.alertname }}'
        text: |
          *Alert:* {{ .GroupLabels.alertname }}
          {{ range .Alerts }}
          *Summary:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          {{ end }}
        send_resolved: true
        color: 'warning'
```

**Step 2: Create the Alertmanager Custom Resource**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Alertmanager
metadata:
  name: main
  namespace: openshift-monitoring
spec:
  # Reference to the Secret containing alertmanager.yaml
  configSecret: alertmanager-main
  
  # Number of AlertManager replicas (for HA)
  replicas: 3
  
  # Resource limits
  resources:
    requests:
      memory: "200Mi"
      cpu: "100m"
    limits:
      memory: "1Gi"
      cpu: "500m"
```

**Complete examples are available in:**
- `example-alertmanager-cr.yaml` - Comprehensive example with all three receiver types
- `example-alertmanager-cr-simple.yaml` - Simplified example focusing on the basics

#### Method 2: Traditional alertmanager.yml (For External Prometheus)

If you're using an external Prometheus instance (not OCP's built-in monitoring), you can configure AlertManager using the traditional `alertmanager.yml` file:

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@company.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
  - match:
      severity: warning
    receiver: 'warning-alerts'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://127.0.0.1:5001/'

- name: 'critical-alerts'
  email_configs:
  - to: 'oncall@company.com'
    subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}

- name: 'warning-alerts'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts'
    title: 'Warning Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

### Receiver Types

AlertManager supports multiple receiver types for routing alerts:

1. **Email** (`email_configs`): Send alerts via SMTP
2. **Slack** (`slack_configs`): Send alerts to Slack channels
3. **Webhook** (`webhook_configs`): Send alerts to HTTP endpoints
4. **PagerDuty** (`pagerduty_configs`): Send alerts to PagerDuty
5. **OpsGenie** (`opsgenie_configs`): Send alerts to OpsGenie
6. **WeChat** (`wechat_configs`): Send alerts to WeChat
7. **VictorOps** (`victorops_configs`): Send alerts to VictorOps

### Routing Rules

Routing rules allow you to:
- **Match alerts** by labels (e.g., `severity: critical`)
- **Route to different receivers** based on alert characteristics
- **Group alerts** to reduce notification noise
- **Set timing** for notification intervals

### Example: Three-Tier Routing

```yaml
route:
  receiver: 'default'
  routes:
  - match:
      severity: critical
    receiver: 'critical'  # Email + Slack + Webhook
  - match:
      severity: warning
    receiver: 'warning'   # Slack only
  - match:
      severity: info
    receiver: 'info'      # Webhook only
```

## Testing Your Alerts

### 1. Validate Alert Rules
```bash
# Check Prometheus configuration
promtool check config /etc/prometheus/prometheus.yaml

# Check alert rules
promtool check rules /etc/prometheus/rules/*.yml
```

### 2. Test Alert Conditions
```bash
# Query alert conditions manually
curl -G 'http://192.168.1.234:9999/api/v1/query' \
  --data-urlencode 'query=rate(container_cpu_usage_seconds_total[5m]) * 100 > 80'
```

### 3. Verify AlertManager
```bash
# Check AlertManager status
curl http://192.168.1.234:9999/api/v1/alerts

# Test webhook endpoint
curl -X POST http://127.0.0.1:5001/ \
  -H 'Content-Type: application/json' \
  -d '{"alerts": [{"status": "firing", "labels": {"alertname": "TestAlert"}}]}'
```

## Best Practices for Alert Design

### 1. Alert Hierarchy
- **Critical**: Immediate attention required
- **Warning**: Attention needed within hours
- **Info**: Informational only

### 2. Alert Grouping
- Group related alerts by service or component
- Use consistent labeling across alerts
- Implement alert dependencies

### 3. Alert Fatigue Prevention
- Set appropriate thresholds
- Use alert inhibition rules
- Implement alert grouping and timing

### 4. Documentation
- Provide runbook URLs in annotations
- Document alert conditions and responses
- Maintain alert rule documentation

## Troubleshooting Common Issues

### Alerts Not Firing
1. Check alert rule syntax
2. Verify PromQL expressions
3. Ensure metrics are available
4. Check alert rule evaluation

### Alerts Firing Too Frequently
1. Adjust alert thresholds
2. Increase alert duration (`for` field)
3. Implement alert inhibition
4. Review alert grouping

### ServiceMonitor Not Working
1. Verify service labels match selector
2. Check endpoint configuration
3. Ensure metrics endpoint is accessible
4. Review Prometheus target status

## Validation Checklist

Before considering this module complete, ensure you can:

- [ ] Write basic Prometheus alert rules
- [ ] Create ServiceMonitor resources
- [ ] Configure alert routing in AlertManager
- [ ] Test alert conditions manually
- [ ] Understand alert states and lifecycle
- [ ] Implement alert best practices
- [ ] Troubleshoot common alert issues

## Next Steps

After completing this module, you should have:

1. ✅ Understanding of Prometheus alerting concepts
2. ✅ Ability to write custom alert rules
3. ✅ Knowledge of ServiceMonitor configuration
4. ✅ Experience with alert routing and notifications
5. ✅ Best practices for alert design

**Congratulations!** You've completed the OCP Prometheus Alerting Tutorial. You now have the knowledge and tools to implement comprehensive monitoring and alerting for your OpenShift Container Platform cluster.

## References

- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [ServiceMonitor Documentation](https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/api.md#servicemonitor)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [OpenShift Monitoring User Guide](https://docs.openshift.com/container-platform/latest/monitoring/monitoring-your-own-services.html)
