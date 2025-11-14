# Demo App for ServiceMonitor Demonstration

This demo application is designed to demonstrate ServiceMonitor functionality in a step-by-step manner.

## Overview

The demo app is a simple Python web server that:
- Exposes three endpoints: `/`, `/health`, and `/metrics`
- Sleeps for 60 seconds on startup before becoming ready
- Shows "I'm not started yet" on the main page until ready
- Demonstrates the importance of health checks and metrics endpoints

## Application Behavior

1. **On Startup**: The app prints "I'm sleeping for 60 seconds..." and waits
2. **During Startup**: 
   - `/` returns "I'm not started yet"
   - `/health` returns HTTP 503 (Service Unavailable)
   - `/metrics` is available but shows `demo_app_ready 0`
3. **After 60 seconds**:
   - `/` returns the normal application page
   - `/health` returns HTTP 200 with `{"status": "ready"}`
   - `/metrics` shows `demo_app_ready 1`

## Demonstration Steps

### Step 1: Deploy App Without ServiceMonitor

**Goal**: Show that we can reach the pod, but it's not ready yet.

1. Build and push the container image (or use a registry):
   ```bash
   docker build -t demo-app:latest .
   # Tag and push to your registry if needed
   ```

2. Deploy the application:
   ```bash
   oc apply -f deployment.yaml
   ```

3. Port-forward to access the app:
   ```bash
   oc port-forward -n demo-app svc/demo-app 8080:8080
   ```

4. Open http://localhost:8080/ in your browser
   - You should see "I'm not started yet"
   - This shows the pod is running but not ready

5. Check Prometheus:
   - Go to Prometheus UI → Status → Targets
   - You should NOT see the demo-app target (no ServiceMonitor yet)

### Step 2: Add ServiceMonitor with /health Only

**Goal**: Show that the webpage becomes available only when `/health` returns OK.

1. Apply the ServiceMonitor with only `/health`:
   ```bash
   oc apply -f servicemonitor-step2.yaml
   ```

2. Wait for the app to become ready (60 seconds after pod start)

3. Check Prometheus targets:
   - Go to Prometheus UI → Status → Targets
   - You should see `demo-app-monitor` target
   - It should be scraping the `/health` endpoint

4. Refresh the webpage (http://localhost:8080/):
   - Now it should show "Application is ready and running!"
   - This demonstrates that the readiness probe waited for `/health` to return 200

5. Note: At this point, we're only monitoring health, not metrics

### Step 3: Add /metrics Endpoint (Best Practice)

**Goal**: Demonstrate best practice of monitoring both health and metrics.

1. Apply the ServiceMonitor with both endpoints:
   ```bash
   oc apply -f servicemonitor-step3.yaml
   ```

2. Check Prometheus targets:
   - You should see the demo-app target with both endpoints
   - One endpoint for `/metrics` (scraped every 30s)
   - One endpoint for `/health` (scraped every 60s)

3. Query metrics in Prometheus:
   ```promql
   demo_app_ready
   demo_app_uptime_seconds
   demo_app_info
   ```

4. This demonstrates best practice:
   - Monitor health checks for availability
   - Monitor metrics for detailed application insights
   - Use appropriate scrape intervals for each endpoint type

## Files

- `app.py` - The Python web server application
- `Dockerfile` - Container image definition
- `deployment.yaml` - Kubernetes Deployment, Service, and Namespace
- `servicemonitor-step1.yaml` - No ServiceMonitor (for demonstration)
- `servicemonitor-step2.yaml` - ServiceMonitor with /health only
- `servicemonitor-step3.yaml` - ServiceMonitor with both /metrics and /health (best practice)

## Key Learning Points

1. **Readiness Probes**: Kubernetes uses readiness probes to determine when a pod can receive traffic
2. **ServiceMonitor Discovery**: Prometheus discovers targets through ServiceMonitor resources
3. **Health vs Metrics**: 
   - Health endpoints indicate if the app is ready to serve traffic
   - Metrics endpoints provide detailed application metrics
4. **Best Practice**: Monitor both health and metrics for comprehensive observability

## Troubleshooting

- **Pod not starting**: Check pod logs with `oc logs -n demo-app -l app=demo-app`
- **ServiceMonitor not discovered**: 
  - Verify labels match: `app: demo-app` and `monitoring: enabled`
  - Check Prometheus Operator logs
  - Verify namespace is allowed for user workload monitoring
- **Can't access app**: 
  - Ensure port-forward is running
  - Check service selector matches pod labels
  - Verify pod is in Running state

## Cleanup

To remove all resources:

```bash
oc delete namespace demo-app
```

