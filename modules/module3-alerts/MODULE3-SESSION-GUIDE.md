# Module 3 Session Guide

This guide provides an overview of the materials created for Module 3 presentation and hands-on exercises.

## Overview

Module 3 covers:
1. **Custom Alert Writing** - Creating PrometheusRule resources
2. **ServiceMonitor Configuration** - Monitoring application endpoints
3. **Alert Routing** - Configuring AlertManager to route alerts to Slack, Email, and Webhooks

## Session Structure

### Part 1: Query Exercises (10-15 minutes)

**File**: `prometheus-query-exercises.md`

Before diving into alert creation, have students explore the Prometheus instance at `https://prometheus.infra.dasmlab.lab` with 10 pre-written queries:

- **5 Cluster Queries**: Explore cluster-level metrics
  - Node status
  - CPU utilization
  - Pod health
  - Memory usage
  - Deployment status

- **5 User Workload Queries**: Explore application metrics
  - Available metrics discovery
  - HTTP request rates
  - Go application metrics
  - Error rates

**How to use**:
1. Share the `prometheus-query-exercises.md` file with students
2. Have them run queries in the Prometheus UI
3. Discuss results and what they observe
4. This builds familiarity with PromQL before creating alerts

### Part 2: ServiceMonitor Demonstration (20-30 minutes)

**Files**: `demo-app/` directory

Demonstrate ServiceMonitor functionality with a step-by-step approach:

**Step 1**: Deploy app without ServiceMonitor
- Show pod is running but not ready
- Webpage shows "I'm not started yet"
- Prometheus is NOT scraping this app

**Step 2**: Add ServiceMonitor with `/health` only
- Show that webpage becomes available when `/health` returns OK
- Prometheus starts scraping the `/health` endpoint
- Demonstrate readiness probe behavior

**Step 3**: Add `/metrics` endpoint (Best Practice)
- Show both `/health` and `/metrics` being scraped
- Query metrics in Prometheus
- Demonstrate best practice of monitoring both

**Files needed**:
- `demo-app/deployment.yaml` - Deployment and Service
- `demo-app/servicemonitor-step1.yaml` - No ServiceMonitor (for reference)
- `demo-app/servicemonitor-step2.yaml` - Health only
- `demo-app/servicemonitor-step3.yaml` - Health + Metrics (best practice)

### Part 3: Alert Rules and Routing (30-40 minutes)

**Files**: 
- `example-alert-rules.yml` - Comprehensive alert examples
- `example-alertmanager-cr.yaml` - Complete AlertManager CRD example
- `example-alertmanager-cr-simple.yaml` - Simplified example

**Topics to cover**:

1. **Creating PrometheusRules**:
   - Show example PrometheusRule structure
   - Explain alert components (name, expr, for, labels, annotations)
   - Demonstrate creating alerts for cluster and user workloads

2. **AlertManager Configuration**:
   - Explain AlertManager CRD approach (OpenShift native)
   - Show Secret + Alertmanager CR pattern
   - Demonstrate routing to:
     - **Slack** - For warning alerts
     - **Email** - For critical alerts
     - **Webhook** - For custom integrations

3. **Live Alert Triggering** (Optional):
   - Use `alert-trigger-app/` to trigger alerts
   - Show alerts firing in Prometheus
   - Show alerts in AlertManager
   - Show notifications being sent

### Part 4: Hands-On Practice (15-20 minutes)

Have students:
1. Create a simple PrometheusRule
2. Verify alert appears in Prometheus
3. Trigger an alert using the demo app
4. Verify alert routing works

## Files Reference

### Query Exercises
- `prometheus-query-exercises.md` - 10 query exercises with explanations

### Demo Applications
- `demo-app/` - ServiceMonitor demonstration app
  - `app.py` - Python web server
  - `Dockerfile` - Container image
  - `deployment.yaml` - Kubernetes resources
  - `servicemonitor-step*.yaml` - Progressive ServiceMonitor examples
  - `README.md` - Detailed instructions

- `alert-trigger-app/` - Alert triggering demo app
  - `app.py` - Python web server with trigger controls
  - `Dockerfile` - Container image
  - `deployment.yaml` - Kubernetes resources + ServiceMonitor + PrometheusRule
  - `README.md` - Usage instructions

### Examples
- `example-alert-rules.yml` - Comprehensive alert rule examples
- `example-alertmanager-cr.yaml` - Complete AlertManager CRD with all receiver types
- `example-alertmanager-cr-simple.yaml` - Simplified AlertManager CRD example
- `example-servicemonitors.yml` - Various ServiceMonitor examples

### Documentation
- `README.md` - Main Module 3 documentation (updated with AlertManager CRD section)

## Quick Start Checklist

Before the session:

- [ ] Prometheus instance accessible at `https://prometheus.infra.dasmlab.lab`
- [ ] Two federate targets configured (cluster and user workload)
- [ ] Build and push demo app images (or use local registry)
- [ ] Build and push alert-trigger app images
- [ ] Review AlertManager CRD examples
- [ ] Test ServiceMonitor demo flow
- [ ] Test alert triggering flow

During the session:

- [ ] Start with query exercises (10-15 min)
- [ ] Present ServiceMonitor concepts
- [ ] Live demo: ServiceMonitor steps
- [ ] Present Alert Rules concepts
- [ ] Present AlertManager routing
- [ ] Live demo: Trigger alerts and show routing
- [ ] Hands-on practice time

## Key Learning Objectives

By the end of Module 3, students should be able to:

1. ✅ Write PromQL queries to explore metrics
2. ✅ Create PrometheusRule resources for custom alerts
3. ✅ Create ServiceMonitor resources to monitor applications
4. ✅ Configure AlertManager to route alerts to different channels
5. ✅ Understand the relationship between alerts, AlertManager, and receivers
6. ✅ Apply best practices for alert design and routing

## Troubleshooting Tips

**Prometheus not scraping**:
- Check ServiceMonitor labels match Service labels
- Verify namespace is allowed for user workload monitoring
- Check Prometheus Operator logs

**Alerts not firing**:
- Verify PrometheusRule is in correct namespace with correct labels
- Check alert expression in Prometheus UI
- Verify metrics exist and have data

**Alerts not routing**:
- Verify AlertManager CR is applied
- Check Secret contains valid alertmanager.yaml
- Verify receiver configurations (Slack webhook URL, SMTP settings, etc.)
- Check AlertManager logs

**Demo app not working**:
- Verify pod is running: `oc get pods -n demo-app`
- Check pod logs for errors
- Verify ServiceMonitor is applied
- Check Prometheus targets page

## Additional Resources

- Prometheus Query Language: https://prometheus.io/docs/prometheus/latest/querying/basics/
- AlertManager Configuration: https://prometheus.io/docs/alerting/latest/configuration/
- ServiceMonitor API: https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/api.md#servicemonitor
- PrometheusRule API: https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/api.md#prometheusrule

