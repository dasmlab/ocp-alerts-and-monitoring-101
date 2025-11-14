# Alert Visibility in External Prometheus - Explanation

## How Alerts Work in Your Setup

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  OCP Cluster (Internal)                                │
│                                                          │
│  ┌──────────────────────────────────────┐             │
│  │ Prometheus user-workload              │             │
│  │  - Discovers ServiceMonitors          │             │
│  │  - Scrapes metrics                    │             │
│  │  - Evaluates PrometheusRules          │             │
│  │  - Generates ALERTS metric            │             │
│  └──────────────────────────────────────┘             │
│           │                                             │
│           │ Federation (/federate endpoint)             │
│           ▼                                             │
└─────────────────────────────────────────────────────────┘
           │
           │ HTTPS
           ▼
┌─────────────────────────────────────────────────────────┐
│  External Prometheus                                    │
│  - Receives federated metrics                           │
│  - ALERTS metric included                              │
│  - Shows in Alerts tab                                 │
└─────────────────────────────────────────────────────────┘
```

## Key Points

### 1. Alert Evaluation Location
- **Alerts are evaluated on the OCP side** (internal Prometheus user-workload)
- The external Prometheus does NOT evaluate alerts
- The external Prometheus receives the `ALERTS` metric via federation

### 2. ALERTS Metric
- When an alert fires, Prometheus generates an `ALERTS` metric
- This metric has labels like `alertname`, `alertstate`, `severity`, etc.
- The `ALERTS` metric is federated to your external Prometheus

### 3. Federation Configuration
Your federation config includes:
```yaml
match[]:
  - '{__name__=~"ALERTS|ALERTS_FOR_STATE"}'
```

This means alerts SHOULD be federated to your external Prometheus.

### 4. Querying Alerts

**In External Prometheus:**
```promql
# All alerts
ALERTS

# Specific alert
ALERTS{alertname="HighCPUUsageDemo"}

# Firing alerts
ALERTS{alertstate="firing"}

# Demo alerts
ALERTS{alertname=~"High.*Demo"}
```

**In Internal Prometheus (if you have access):**
```promql
# Same queries work
ALERTS{alertname=~"High.*Demo"}
```

### 5. Alerts Tab in Prometheus UI

- The "Alerts" tab shows alerts from the `ALERTS` metric
- If `ALERTS` metric is not federated, you won't see alerts there
- The tab queries: `ALERTS{alertstate="firing"}`

## Troubleshooting

### Alerts Not Showing in External Prometheus

1. **Check if PrometheusRule is loaded:**
   ```bash
   oc exec -n openshift-user-workload-monitoring prometheus-user-workload-0 -c prometheus -- \
     wget -qO- 'http://localhost:9090/api/v1/rules' | \
     jq '.data.groups[] | select(.name | contains("demo"))'
   ```

2. **Check if alerts are firing in internal Prometheus:**
   ```bash
   oc exec -n openshift-user-workload-monitoring prometheus-user-workload-0 -c prometheus -- \
     wget -qO- 'http://localhost:9090/api/v1/query?query=ALERTS{alertname=~"High.*Demo"}' | \
     jq '.data.result'
   ```

3. **Check if ALERTS metric is being federated:**
   ```promql
   # In external Prometheus
   ALERTS
   # Should return results if any alerts exist
   ```

4. **Verify federation config:**
   - Check `/etc/prometheus/prometheus.yaml`
   - Ensure `{__name__=~"ALERTS|ALERTS_FOR_STATE"}` is in match rules
   - Reload Prometheus after changes

### PrometheusRule Not Being Loaded

**Check labels:**
- PrometheusRule must have: `prometheus: user-workload` and `role: alert-rules`
- PrometheusRule should have: `openshift.io/user-monitoring: "true"`
- Namespace must have: `openshift.io/user-monitoring: "true"`

**Verify selection:**
```bash
oc get prometheus user-workload -n openshift-user-workload-monitoring -o yaml | \
  grep -A 10 "ruleSelector\|ruleNamespaceSelector"
```

## Expected Behavior

### When Alert Fires

1. **Internal Prometheus:**
   - Evaluates alert condition
   - If condition persists for `for: 1m`, alert fires
   - Generates `ALERTS` metric with `alertstate="firing"`

2. **Federation:**
   - `ALERTS` metric is included in federation scrape
   - Sent to external Prometheus every 30 seconds

3. **External Prometheus:**
   - Receives `ALERTS` metric
   - Query `ALERTS{alertstate="firing"}` shows firing alerts
   - Alerts tab displays the alerts

### When Alert Resolves

1. Condition clears (metric drops below threshold)
2. `ALERTS` metric changes to `alertstate="pending"` then disappears
3. External Prometheus receives updated `ALERTS` metric
4. Alert disappears from Alerts tab

## Common Issues

### Issue: "ALERTS metric not found"
- **Cause**: PrometheusRule not loaded or alerts not firing
- **Fix**: Check PrometheusRule labels and namespace labels

### Issue: "Alerts not in Alerts tab"
- **Cause**: `ALERTS` metric not federated
- **Fix**: Verify federation config includes `{__name__=~"ALERTS|ALERTS_FOR_STATE"}`

### Issue: "Query returns no results"
- **Cause**: Alert hasn't fired yet (needs to persist for `for: 1m`)
- **Fix**: Wait 1 minute after triggering, or check if condition is actually met

## Verification Steps

1. **Trigger an alert** (e.g., high CPU)
2. **Wait 1 minute** (for `for: 1m` duration)
3. **Check internal Prometheus:**
   ```bash
   oc exec -n openshift-user-workload-monitoring prometheus-user-workload-0 -c prometheus -- \
     wget -qO- 'http://localhost:9090/api/v1/query?query=ALERTS{alertname="HighCPUUsageDemo"}'
   ```
4. **Check external Prometheus:**
   ```promql
   ALERTS{alertname="HighCPUUsageDemo"}
   ```
5. **Check Alerts tab:**
   - Should show the alert in "FIRING" state

## Summary

- ✅ Alerts ARE evaluated on OCP side (internal Prometheus)
- ✅ ALERTS metric SHOULD be federated to external Prometheus
- ✅ You SHOULD see alerts in the Alerts tab
- ✅ Query `ALERTS{alertname=~"High.*Demo"}` SHOULD work

If alerts aren't showing:
1. Check PrometheusRule is loaded
2. Check alerts are actually firing
3. Check ALERTS metric is being federated
4. Wait for federation sync (30s interval)

