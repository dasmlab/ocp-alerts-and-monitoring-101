# Alert Trigger App - Live Demo Guide

This guide provides step-by-step instructions for demonstrating alert triggering during Module 3 presentations.

## Prerequisites

- Alert Trigger App deployed and running
- Port-forward active: `http://localhost:8081`
- Prometheus accessible: `https://prometheus.infra.dasmlab.lab`
- PrometheusRules applied and active

## Quick Status Check

```bash
# Check app is running
oc get pods -n demo-app -l app=alert-trigger-app

# Check ServiceMonitor
oc get servicemonitor alert-trigger-app-monitor -n demo-app

# Check PrometheusRules
oc get prometheusrule alert-trigger-demo-alerts -n demo-app

# Access the app
# Port-forward: oc port-forward -n demo-app svc/alert-trigger-app 8081:8080
# Then open: http://localhost:8081
```

## Live Demo Flow

### Part 1: Show Normal State (2-3 minutes)

**Goal**: Demonstrate the app is running and metrics are normal.

1. **Open the Alert Trigger App UI**:
   - URL: `http://localhost:8081`
   - Show current metrics (should all be normal):
     - CPU Usage: ~50%
     - Memory Usage: ~50%
     - Error Rate: ~0%

2. **Show Metrics in Prometheus**:
   - Go to: `https://prometheus.infra.dasmlab.lab`
   - Query: `alert_demo_cpu_usage_percent`
   - Expected: Value around 50
   - Query: `alert_demo_memory_usage_percent`
   - Expected: Value around 50
   - Query: `alert_demo_error_rate_percent`
   - Expected: Value around 0

3. **Check Alerts Status**:
   - Go to: Prometheus → Alerts
   - Show: No alerts firing (all should be inactive)

### Part 2: Trigger High CPU Alert (3-4 minutes)

**Goal**: Demonstrate triggering a warning-level alert.

1. **Trigger High CPU**:
   - In Alert Trigger App UI: Click "Trigger High CPU Alert"
   - OR visit: `http://localhost:8081/trigger?action=high_cpu`
   - Show: CPU Usage jumps to 85%

2. **Watch Metrics Change**:
   - In Prometheus, query: `alert_demo_cpu_usage_percent`
   - Show: Value increases to 85%
   - Switch to Graph view to show the spike

3. **Wait for Alert to Fire**:
   - Wait 1 minute (alert has `for: 1m`)
   - Go to: Prometheus → Alerts
   - Show: `HighCPUUsageDemo` alert
     - Status: Pending → Firing
     - Severity: warning
     - Component: cpu

4. **Show Alert Details**:
   - Click on the alert to show:
     - Summary: "High CPU usage detected in demo app"
     - Description: "CPU usage is 85% which is above the threshold of 80%"
     - Labels: severity=warning, component=cpu

### Part 3: Trigger High Memory Alert (3-4 minutes)

**Goal**: Demonstrate another warning-level alert.

1. **Trigger High Memory**:
   - In Alert Trigger App UI: Click "Trigger High Memory Alert"
   - OR visit: `http://localhost:8081/trigger?action=high_memory`
   - Show: Memory Usage jumps to 95%

2. **Watch Alert Fire**:
   - Wait 1 minute
   - Show: `HighMemoryUsageDemo` alert firing
   - Severity: warning
   - Component: memory

### Part 4: Trigger Critical Error Rate Alert (3-4 minutes)

**Goal**: Demonstrate a critical-level alert.

1. **Trigger High Error Rate**:
   - In Alert Trigger App UI: Click "Trigger High Error Rate"
   - OR visit: `http://localhost:8081/trigger?action=high_errors`
   - Show: Error Rate jumps to 10%

2. **Watch Critical Alert Fire**:
   - Wait 1 minute
   - Show: `HighErrorRateDemo` alert firing
   - Severity: **critical** (highlight this!)
   - Component: application

3. **Show Alert Routing**:
   - Explain: Critical alerts go to different receivers
   - Show AlertManager routing (if configured):
     - Critical → Email + Slack + Webhook
     - Warning → Slack only

### Part 5: Reset and Show Resolution (2-3 minutes)

**Goal**: Demonstrate alert resolution.

1. **Reset Metrics**:
   - In Alert Trigger App UI: Click "Reset All Metrics"
   - OR visit: `http://localhost:8081/trigger?action=reset`
   - Show: All metrics return to normal

2. **Watch Alerts Resolve**:
   - Wait for metrics to drop below thresholds
   - Show: Alerts transition from Firing → Pending → Inactive
   - Explain: AlertManager sends "resolved" notifications

## Key Talking Points

### During Normal State
- "Here we see the app running normally with all metrics within acceptable ranges"
- "No alerts are firing because all conditions are met"

### When Triggering Alerts
- "I'm going to simulate a problem by triggering high CPU usage"
- "Watch how the metric changes in real-time in Prometheus"
- "The alert rule evaluates every 15 seconds, but won't fire until the condition persists for 1 minute"

### When Alert Fires
- "Notice the alert goes from Pending to Firing after 1 minute"
- "This is the `for: 1m` duration preventing alert flapping"
- "The alert has labels that will be used for routing"

### Alert Routing
- "Critical alerts have `severity: critical` label"
- "This label is used by AlertManager to route to the appropriate receiver"
- "Warning alerts go to Slack, critical alerts go to Email + Slack + Webhook"

### Alert Resolution
- "When the condition clears, the alert resolves"
- "AlertManager sends a 'resolved' notification to the same receivers"

## Prometheus Queries for Demo

### Before Triggering
```promql
# Show normal metrics
alert_demo_cpu_usage_percent
alert_demo_memory_usage_percent
alert_demo_error_rate_percent

# Show no alerts
ALERTS{alertname=~"High.*Demo"}
```

### After Triggering
```promql
# Show elevated metrics
alert_demo_cpu_usage_percent > 80
alert_demo_memory_usage_percent > 90
alert_demo_error_rate_percent > 5

# Show firing alerts
ALERTS{alertstate="firing",alertname=~"High.*Demo"}
```

### Alert Details
```promql
# All demo alerts
ALERTS{alertname=~"High.*Demo"}

# By severity
ALERTS{severity="critical"}
ALERTS{severity="warning"}

# By component
ALERTS{component="cpu"}
ALERTS{component="memory"}
ALERTS{component="application"}
```

## Troubleshooting

### App Not Accessible
```bash
# Check pod status
oc get pods -n demo-app -l app=alert-trigger-app

# Check logs
oc logs -n demo-app -l app=alert-trigger-app --tail=20

# Restart port-forward
oc port-forward -n demo-app svc/alert-trigger-app 8081:8080
```

### Metrics Not Appearing
```bash
# Check ServiceMonitor
oc get servicemonitor alert-trigger-app-monitor -n demo-app

# Check if Prometheus is scraping
# (Internal Prometheus - requires exec access)
oc exec -n openshift-user-workload-monitoring prometheus-user-workload-0 -c prometheus -- \
  wget -qO- 'http://localhost:9090/api/v1/targets' | \
  jq '.data.activeTargets[] | select(.labels.job == "alert-trigger-app")'
```

### Alerts Not Firing
```bash
# Check PrometheusRule
oc get prometheusrule alert-trigger-demo-alerts -n demo-app -o yaml

# Verify alert expressions
# Query directly: alert_demo_cpu_usage_percent > 80
```

## Timing Reference

- **App startup**: ~5-10 seconds
- **Metric update**: Immediate (when triggered)
- **Prometheus scrape**: Every 30 seconds
- **Alert evaluation**: Every 15 seconds (evaluation_interval)
- **Alert firing**: After 1 minute (`for: 1m`)
- **Federation sync**: Every 30 seconds

## Tips for Smooth Demo

1. **Pre-check everything** before the presentation
2. **Have Prometheus open** in multiple tabs:
   - Query tab for metrics
   - Alerts tab for alert status
   - Graph view for trends
3. **Use browser bookmarks** for quick access:
   - Alert Trigger App: `http://localhost:8081`
   - Prometheus: `https://prometheus.infra.dasmlab.lab`
4. **Practice the timing** - know when to wait for alerts
5. **Have backup queries ready** in case something doesn't work
6. **Explain what you're doing** as you do it - helps if something goes wrong

## Expected Results Summary

| Action | Metric Change | Alert Fires After | Alert Name | Severity |
|--------|---------------|-------------------|------------|----------|
| Trigger High CPU | CPU → 85% | 1 minute | HighCPUUsageDemo | warning |
| Trigger High Memory | Memory → 95% | 1 minute | HighMemoryUsageDemo | warning |
| Trigger High Errors | Error Rate → 10% | 1 minute | HighErrorRateDemo | critical |
| Reset | All → Normal | Immediate | All resolve | - |

## Next Steps After Demo

1. Show AlertManager routing configuration
2. Demonstrate alert notifications (if configured)
3. Explain how to create custom alert rules
4. Show ServiceMonitor best practices

