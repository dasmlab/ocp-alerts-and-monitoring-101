# Prometheus Query Exercises

This document contains 10 exercises to help you explore and understand the Prometheus metrics available from your OCP cluster. These exercises are designed to be run in the Prometheus UI at `https://prometheus.infra.dasmlab.lab`.

## Prerequisites

- Access to the Prometheus instance at `https://prometheus.infra.dasmlab.lab`
- Understanding that there are two federate targets configured:
  - **Cluster endpoint**: Scrapes cluster-level metrics from `openshift-monitoring`
  - **User Workload endpoint**: Scrapes application metrics from user namespaces

---

## Cluster Metrics Exercises (5 queries)

These queries explore cluster-level metrics from the `openshift-monitoring` namespace.

### Exercise 1: Check Cluster Node Status
**Goal**: Verify all nodes in the cluster are ready and available.

**Query**:
```promql
kube_node_status_condition{condition="Ready",status="true"}
```

**What to look for**:
- Count the number of results - this should match your cluster node count
- All nodes should have `status="true"` for the Ready condition
- Check the `node` label to see individual node names

**Expected Result**: One time series per node with value `1` indicating the node is ready.

---

### Exercise 2: Calculate Node CPU Utilization
**Goal**: Understand CPU usage across cluster nodes.

**Query**:
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**What to look for**:
- Values represent CPU utilization percentage (0-100%)
- Higher values indicate more CPU usage
- Compare different nodes to see which are under more load
- Values above 80% may indicate high load

**Expected Result**: Time series showing CPU utilization percentage for each node instance.

---

### Exercise 3: Find Pods in CrashLoopBackOff
**Goal**: Identify pods that are restarting frequently (potential issues).

**Query**:
```promql
rate(kube_pod_container_status_restarts_total[15m]) > 0
```

**What to look for**:
- Any results indicate pods that have restarted in the last 15 minutes
- Check the `pod` and `namespace` labels to identify problematic pods
- Higher values indicate more frequent restarts
- Combine with `kube_pod_status_phase{phase="Failed"}` to see failed pods

**Expected Result**: Time series for pods that have restarted, with values showing restart rate per second.

---

### Exercise 4: Monitor Container Memory Usage
**Goal**: Track memory consumption of containers across the cluster.

**Query**:
```promql
container_memory_working_set_bytes{container!="",container!="POD"}
```

**What to look for**:
- Values are in bytes (divide by 1024^3 for GB)
- Filter by namespace: `container_memory_working_set_bytes{namespace="openshift-monitoring"}`
- Compare memory usage across different containers
- Look for containers using excessive memory

**Expected Result**: Memory usage in bytes for each running container (excluding POD containers).

---

### Exercise 5: Check Deployment Replica Status
**Goal**: Verify deployments have the correct number of ready replicas.

**Query**:
```promql
kube_deployment_status_replicas_available / kube_deployment_spec_replicas
```

**What to look for**:
- Values should be `1` when all replicas are available
- Values less than `1` indicate some replicas are not ready
- Check the `deployment` and `namespace` labels to identify which deployments have issues
- Compare with `kube_deployment_status_replicas_unavailable` to see how many are down

**Expected Result**: Ratio of available to desired replicas (should be 1.0 for healthy deployments).

---

## User Workload Metrics Exercises (5 queries)

These queries explore application-level metrics from user namespaces (not `openshift-*` namespaces).

### Exercise 6: List All Available Metrics from User Workloads
**Goal**: Discover what metrics are available from your applications.

**Query**:
```promql
{__name__=~".+",job!~"prometheus.*|thanos.*",namespace!~"openshift-.*"}
```

**What to look for**:
- This shows all metrics from user workloads
- Use the metric browser or autocomplete to explore available metric names
- Look for application-specific metrics like `http_requests_total`, `go_goroutines`, etc.
- Check the `namespace` label to see which namespaces have metrics

**Expected Result**: All time series from user workload monitoring (excluding cluster monitoring).

---

### Exercise 7: Find HTTP Request Rates
**Goal**: Monitor HTTP request rates from applications that expose HTTP metrics.

**Query**:
```promql
rate(http_requests_total{namespace!~"openshift-.*"}[5m])
```

**What to look for**:
- Values represent requests per second
- Check different `status` label values (200, 404, 500, etc.) to see error rates
- Filter by specific namespace: `rate(http_requests_total{namespace="my-app"}[5m])`
- Compare request rates across different services using the `job` or `service` labels

**Expected Result**: HTTP request rate per second for each unique combination of labels.

---

### Exercise 8: Monitor Application Memory Allocation (Go apps)
**Goal**: Track memory allocation for Go-based applications.

**Query**:
```promql
go_memstats_alloc_bytes{namespace!~"openshift-.*"}
```

**What to look for**:
- Values are in bytes (divide by 1024^2 for MB, 1024^3 for GB)
- Monitor for memory leaks (gradually increasing values)
- Compare memory usage across different Go applications
- Combine with `go_memstats_sys_bytes` to see total memory used by the process

**Expected Result**: Currently allocated memory in bytes for Go applications.

---

### Exercise 9: Check Goroutine Counts
**Goal**: Monitor goroutine counts for Go applications (indicator of concurrency).

**Query**:
```promql
go_goroutines{namespace!~"openshift-.*"}
```

**What to look for**:
- Values represent the number of active goroutines
- Sudden spikes may indicate issues or high load
- Compare goroutine counts across different applications
- Values above 1000 may indicate potential issues (depending on application)
- Filter by namespace to focus on specific applications

**Expected Result**: Number of active goroutines for each Go application instance.

---

### Exercise 10: Calculate Error Rate Percentage
**Goal**: Determine the percentage of HTTP requests that result in errors.

**Query**:
```promql
sum(rate(http_requests_total{namespace!~"openshift-.*",status=~"5.."}[5m])) / sum(rate(http_requests_total{namespace!~"openshift-.*"}[5m])) * 100
```

**What to look for**:
- Values represent error percentage (0-100%)
- Values above 5% may indicate application issues
- Break down by service: add `by (job)` or `by (service)` to see per-service error rates
- Monitor trends over time to catch degradation
- Filter by specific namespace to focus on particular applications

**Expected Result**: Percentage of HTTP requests that return 5xx status codes.

---

## Tips for Using These Exercises

1. **Start Simple**: Begin with Exercise 1 and work through them sequentially
2. **Use the Graph View**: Switch to the Graph tab to see trends over time
3. **Adjust Time Ranges**: Try different time ranges (1h, 6h, 24h) to see patterns
4. **Add Filters**: Modify queries to filter by specific namespaces, pods, or labels
5. **Compare Metrics**: Use multiple queries in the same graph to compare different metrics
6. **Explore Labels**: Click on result labels to filter and explore related metrics

## Next Steps

After completing these exercises, you should:
- Understand the difference between cluster and user workload metrics
- Be comfortable writing basic PromQL queries
- Know how to filter and aggregate metrics
- Be ready to create custom alert rules based on these queries

For more advanced queries and alert creation, proceed to the Module 3 content on creating custom alert rules.

