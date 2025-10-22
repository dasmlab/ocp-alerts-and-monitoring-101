# Module 2: Basic Connectivity and Sample Queries

## Overview

This module focuses on validating your Prometheus setup and exploring the available metrics from your OCP cluster. You'll learn how to test connectivity, understand metric namespaces, and use sample queries to verify that everything is working correctly.

## Prerequisites

- Completed Module 1 setup
- Prometheus instance running and configured
- Service account token available
- Access to Prometheus web UI or API

## Validating Connectivity

### Step 1: Basic Connectivity Test

First, let's verify that Prometheus can connect to your OCP cluster:

#### Using Prometheus Web UI
1. Navigate to your Prometheus instance (e.g., `http://192.168.1.234:9999`)
2. Go to **Status > Targets**
3. Verify that your OCP targets show as **UP**

#### Using Prometheus API
```bash
# Test basic connectivity
curl -G 'http://192.168.1.234:9999/api/v1/query' \
  --data-urlencode 'query=up{job="ocp-cluster-federation"}'
```

#### Using cURL with Token (Direct to OCP)
```bash
# Test direct connectivity to OCP cluster
curl -H "Authorization: Bearer $(cat ocp-federate.token)" \
  -k "https://thanos-querier.openshift-monitoring.svc.cluster.local:9091/api/v1/query?query=up"
```

### Step 2: Verify Target Status

Check the status of your scraping targets:

```promql
# Check if targets are up
up

# Check specific OCP targets
up{job=~"ocp-cluster.*"}

# Check target health with labels
up{job="ocp-cluster-federation", instance="thanos-querier.openshift-monitoring.svc.cluster.local:9091"}
```

## Understanding OCP Metrics

### Metric Namespaces and Labels

OCP metrics follow specific naming conventions and include rich labeling:

#### Common Metric Prefixes
- **`kube_*`**: Kubernetes core metrics (nodes, pods, deployments, etc.)
- **`container_*`**: Container-level metrics (CPU, memory, filesystem)
- **`node_*`**: Node-level metrics (hardware, OS)
- **`apiserver_*`**: Kubernetes API server metrics
- **`etcd_*`**: etcd database metrics
- **`openshift_*`**: OpenShift-specific metrics

#### Important Labels
- **`cluster`**: Cluster identifier
- **`namespace`**: Kubernetes namespace
- **`pod`**: Pod name
- **`container`**: Container name
- **`node`**: Node name
- **`job`**: Scraping job name
- **`instance`**: Target instance

## Sample Queries for Validation

### 1. Cluster Health Queries

#### Node Status
```promql
# Check if all nodes are ready
kube_node_status_condition{condition="Ready",status="true"}

# Count total nodes
count(kube_node_status_condition{condition="Ready",status="true"})

# Check for not-ready nodes
kube_node_status_condition{condition="Ready",status="false"}
```

#### Pod Status
```promql
# Check pod phases
kube_pod_status_phase

# Count pods by phase
count by (phase) (kube_pod_status_phase)

# Check for failed pods
kube_pod_status_phase{phase="Failed"}

# Check for pending pods
kube_pod_status_phase{phase="Pending"}
```

### 2. Resource Utilization Queries

#### CPU Usage
```promql
# Node CPU usage percentage
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Container CPU usage
rate(container_cpu_usage_seconds_total[5m])

# Top CPU consuming containers
topk(10, rate(container_cpu_usage_seconds_total[5m]))
```

#### Memory Usage
```promql
# Node memory usage percentage
100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)

# Container memory usage
container_memory_usage_bytes

# Top memory consuming containers
topk(10, container_memory_usage_bytes)
```

### 3. Application Health Queries

#### HTTP Metrics (if available)
```promql
# HTTP request rate
rate(http_requests_total[5m])

# HTTP error rate
rate(http_requests_total{status=~"5.."}[5m])

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

#### Go Application Metrics
```promql
# Go goroutines
go_goroutines

# Go memory usage
go_memstats_alloc_bytes

# Go GC duration
rate(go_gc_duration_seconds_sum[5m])
```

### 4. OpenShift-Specific Queries

#### Route Metrics
```promql
# Route availability
route_availability

# Route response time
route_response_time_seconds
```

#### Build Metrics
```promql
# Build status
openshift_build_status

# Build duration
openshift_build_duration_seconds
```

## Creating Sample Queries File

Let's create a comprehensive set of sample queries for easy reference:

```yaml
# Sample Prometheus Queries for OCP
# Save this as sample-queries.yml for reference

cluster_health:
  - name: "Total Nodes"
    query: "count(kube_node_status_condition{condition=\"Ready\",status=\"true\"})"
  
  - name: "Ready Nodes"
    query: "kube_node_status_condition{condition=\"Ready\",status=\"true\"}"
  
  - name: "Not Ready Nodes"
    query: "kube_node_status_condition{condition=\"Ready\",status=\"false\"}"

pod_status:
  - name: "Pods by Phase"
    query: "count by (phase) (kube_pod_status_phase)"
  
  - name: "Failed Pods"
    query: "kube_pod_status_phase{phase=\"Failed\"}"
  
  - name: "Pending Pods"
    query: "kube_pod_status_phase{phase=\"Pending\"}"

resource_usage:
  - name: "Node CPU Usage %"
    query: "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
  
  - name: "Node Memory Usage %"
    query: "100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)"
  
  - name: "Top CPU Containers"
    query: "topk(10, rate(container_cpu_usage_seconds_total[5m]))"
  
  - name: "Top Memory Containers"
    query: "topk(10, container_memory_usage_bytes)"
```

## Testing Your Queries

### Using Prometheus Web UI
1. Navigate to **Graph** tab
2. Enter your query in the query box
3. Click **Execute** to see results
4. Use **Graph** tab to visualize time-series data

### Using Prometheus API
```bash
# Query via API
curl -G 'http://192.168.1.234:9999/api/v1/query' \
  --data-urlencode 'query=up{job="ocp-cluster-federation"}'

# Query range for time-series data
curl -G 'http://192.168.1.234:9999/api/v1/query_range' \
  --data-urlencode 'query=up{job="ocp-cluster-federation"}' \
  --data-urlencode 'start=2024-01-01T00:00:00Z' \
  --data-urlencode 'end=2024-01-01T01:00:00Z' \
  --data-urlencode 'step=15s'
```

## Troubleshooting Common Issues

### No Data Returned
1. **Check target status**: Verify targets are UP in Status > Targets
2. **Verify token**: Ensure the service account token is valid
3. **Check network**: Test connectivity to OCP cluster
4. **Review logs**: Check Prometheus logs for errors

### Partial Data
1. **Check time range**: Ensure you're querying within the data retention period
2. **Verify labels**: Check if metric labels match your query
3. **Review federation**: Ensure federation is working correctly

### Authentication Errors
1. **Token validity**: Check if the token has expired
2. **RBAC permissions**: Verify service account has correct permissions
3. **Token format**: Ensure token is properly formatted

## Validation Checklist

Before proceeding to Module 3, ensure you can:

- [ ] Access Prometheus web UI
- [ ] See OCP targets as UP in Status > Targets
- [ ] Execute basic queries (e.g., `up`)
- [ ] Query cluster health metrics (nodes, pods)
- [ ] Query resource utilization metrics (CPU, memory)
- [ ] Understand metric namespaces and labels
- [ ] Use both web UI and API for queries

## Next Steps

After completing this module, you should have:

1. ✅ Validated Prometheus connectivity to OCP
2. ✅ Understanding of available metrics
3. ✅ Working knowledge of PromQL queries
4. ✅ Ability to troubleshoot connectivity issues

**Proceed to [Module 3: Custom Alert Writing and Service Monitor](../module3-alerts/README.md)** to learn how to create custom alert rules and ServiceMonitor configurations.

## References

- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus API](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [OpenShift Monitoring Metrics](https://docs.openshift.com/container-platform/latest/monitoring/understanding-the-monitoring-stack.html)
