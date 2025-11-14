# Prometheus Queries for Demo App

This document provides the queries you can use in Prometheus UI (`https://prometheus.infra.dasmlab.lab`) to monitor the demo-app during the ServiceMonitor demonstration.

## Step 1: No ServiceMonitor (Current State)

**What to check:**
- Go to: `https://prometheus.infra.dasmlab.lab/targets`
- **Expected**: You should NOT see `demo-app-monitor` in the targets list
- This demonstrates that without a ServiceMonitor, Prometheus doesn't know about the app

**Queries to try:**
```promql
# This will return no results (app not being scraped)
demo_app_ready

# Check if any metrics exist for demo-app
{job=~".*demo-app.*"}

# Check all targets
up
```

## Step 2: ServiceMonitor with /health Only

**After applying `servicemonitor-step2.yaml`:**

**Check Targets:**
- Go to: `https://prometheus.infra.dasmlab.lab/targets`
- **Expected**: You should see `demo-app-monitor` target
- **Endpoint**: Should show `/health` endpoint being scraped
- **Status**: Should be "UP" once the app is ready

**Queries to use:**

```promql
# Check if the target is up
up{job="demo-app-monitor"}

# Check the specific endpoint
up{job="demo-app-monitor", endpoint="http"}

# Note: At this step, you won't see demo_app_* metrics yet
# because we're only scraping /health, not /metrics
```

**What you should see:**
- Target appears in Prometheus targets page
- `up{job="demo-app-monitor"}` returns `1` (target is up)
- But `demo_app_ready` still returns no results (not scraping /metrics yet)

## Step 3: ServiceMonitor with Both /health and /metrics (Best Practice)

**After applying `servicemonitor-step3.yaml`:**

**Check Targets:**
- Go to: `https://prometheus.infra.dasmlab.lab/targets`
- **Expected**: You should see `demo-app-monitor` with TWO endpoints:
  - `/metrics` endpoint (scraped every 30s)
  - `/health` endpoint (scraped every 60s)

**Queries to use:**

### Basic App Metrics

```promql
# Check if app is ready (0 = not ready, 1 = ready)
demo_app_ready

# App uptime in seconds
demo_app_uptime_seconds

# App info
demo_app_info
```

### During Startup (First 60 seconds)

```promql
# App readiness status (should be 0 during startup)
demo_app_ready

# Watch uptime increase
demo_app_uptime_seconds

# Check if metrics are being scraped
up{job="demo-app-monitor", endpoint="/metrics"}
```

### After App Becomes Ready

```promql
# Should return 1 after 60 seconds
demo_app_ready

# Uptime should be increasing
demo_app_uptime_seconds

# Both endpoints should be up
up{job="demo-app-monitor"}
```

### Target Status Queries

```promql
# Check if both endpoints are being scraped
up{job="demo-app-monitor"}

# Check specific endpoint
up{job="demo-app-monitor", endpoint="/metrics"}
up{job="demo-app-monitor", endpoint="/health"}

# See all labels for the target
up{job="demo-app-monitor"}
```

### Advanced Queries

```promql
# Rate of readiness changes (should be 0 after initial startup)
rate(demo_app_ready[5m])

# Time since app started (if ready)
demo_app_uptime_seconds * demo_app_ready

# Check if app has been ready for more than 1 minute
demo_app_ready == 1 and demo_app_uptime_seconds > 60
```

## Demonstration Flow Queries

### 1. Before ServiceMonitor (Step 1)
```promql
# Should return empty (no results)
demo_app_ready

# Should return empty
{job=~".*demo-app.*"}
```

### 2. After Step 2 ServiceMonitor (health only)
```promql
# Target should be up
up{job="demo-app-monitor"}

# But metrics still empty (only scraping /health)
demo_app_ready
```

### 3. After Step 3 ServiceMonitor (health + metrics)
```promql
# Both endpoints up
up{job="demo-app-monitor"}

# Now metrics are available!
demo_app_ready
demo_app_uptime_seconds
demo_app_info
```

## Graph View Tips

1. **Switch to Graph tab** to see trends over time
2. **Set time range** to see the transition:
   - When app starts: `demo_app_ready` = 0
   - After 60 seconds: `demo_app_ready` = 1
3. **Use multiple queries** in the same graph to compare:
   ```promql
   demo_app_ready
   demo_app_uptime_seconds / 60  # Convert to minutes
   ```

## Troubleshooting Queries

```promql
# Check if ServiceMonitor is discovered
up{job="demo-app-monitor"}

# Check all targets in demo-app namespace
up{namespace="demo-app"}

# Check for any errors
up{job="demo-app-monitor"} == 0

# See all available metrics from demo-app
{__name__=~"demo_app.*"}
```

## Expected Timeline

1. **0-60 seconds**: `demo_app_ready = 0`, `demo_app_uptime_seconds` increasing
2. **After 60 seconds**: `demo_app_ready = 1`, app is ready
3. **Ongoing**: `demo_app_uptime_seconds` continues to increase

## Quick Reference

| Step | ServiceMonitor | Targets Visible | Metrics Available |
|------|---------------|-----------------|-------------------|
| 1 | None | ❌ No | ❌ No |
| 2 | `/health` only | ✅ Yes | ❌ No |
| 3 | `/health` + `/metrics` | ✅ Yes | ✅ Yes |

