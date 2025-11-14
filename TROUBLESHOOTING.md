# OCP Prometheus Connectivity Troubleshooting Guide

This guide helps you diagnose and fix common connectivity issues between your external Prometheus instance and your OpenShift Container Platform cluster.

## Common Issues and Solutions

### 1. "Context Deadline Exceeded" Errors

**Symptoms:**
- Prometheus targets show "DOWN" status
- Error message: "context deadline exceeded"
- Targets were working previously but stopped working

**Causes:**
- Network connectivity issues
- OCP cluster endpoint changes
- Token expiration or authentication problems
- Prometheus timeout configuration too low

**Solutions:**

#### Step 1: Run the Troubleshooting Script
```bash
./troubleshoot-connectivity.sh
```

This script will:
- Check OCP cluster connectivity
- Verify service account and token
- Get current cluster endpoints
- Test connectivity to available endpoints
- Generate an updated Prometheus configuration

#### Step 2: Check Current Cluster Endpoints
```bash
# Get current Thanos Querier endpoint
oc -n openshift-monitoring get route thanos-querier -o jsonpath='{.spec.host}'

# Get current Prometheus endpoint
oc -n openshift-monitoring get route prometheus-k8s -o jsonpath='{.spec.host}'

# Get User Workload Monitoring endpoint
oc -n openshift-user-workload-monitoring get route prometheus-user-workload -o jsonpath='{.spec.host}'
```

#### Step 3: Test Connectivity Manually
```bash
# Test Thanos Querier
curl -k -H "Authorization: Bearer $(cat ocp-federate.token)" \
  "https://<thanos-querier-endpoint>/api/v1/query?query=up"

# Test User Workload Monitoring
curl -k -H "Authorization: Bearer $(cat ocp-federate.token)" \
  "https://<uwm-endpoint>/federate?match[]={__name__=\"up\"}"
```

#### Step 4: Update Prometheus Configuration
If endpoints have changed, update your `prometheus.yaml`:

```yaml
scrape_configs:
  - job_name: 'ocp-cluster-federation'
    bearer_token_file: '/etc/prometheus/secrets/ocp-federate.token'
    scheme: https
    tls_config:
      insecure_skip_verify: true
    static_configs:
      - targets: 
        - 'your-actual-endpoint.com'  # Update this
    metrics_path: '/federate'
    scrape_interval: 30s
    scrape_timeout: 30s  # Increase timeout
```

#### Step 5: Restart Prometheus
```bash
sudo systemctl restart prometheus
```

### 2. "NXDOMAIN" or DNS Resolution Errors

**Symptoms:**
- Error: "server can't find <endpoint>: NXDOMAIN"
- Targets show "DOWN" status immediately

**Causes:**
- OCP cluster routes were deleted or changed
- DNS configuration issues
- Cluster was reconfigured

**Solutions:**

#### Check Available Routes
```bash
# List all routes in openshift-monitoring
oc -n openshift-monitoring get routes

# List all routes in openshift-user-workload-monitoring
oc -n openshift-user-workload-monitoring get routes
```

#### Recreate Missing Routes
If routes are missing, they may need to be recreated. Contact your cluster administrator or check OCP documentation for route recreation procedures.

### 3. Authentication Errors

**Symptoms:**
- HTTP 401 or 403 errors
- "Unauthorized" messages in Prometheus logs

**Causes:**
- Service account token expired
- Service account deleted
- RBAC permissions changed

**Solutions:**

#### Regenerate Token
```bash
# Delete old service account
./delete-service-account.sh

# Create new service account and token
./setup-service-account.sh
```

#### Verify Service Account Permissions
```bash
# Check if service account exists
oc get sa federator -n openshift-monitoring

# Check RBAC permissions
oc auth can-i get prometheuses --as=system:serviceaccount:openshift-monitoring:federator
```

### 4. Network Connectivity Issues

**Symptoms:**
- Connection refused errors
- Timeout errors
- Intermittent connectivity

**Causes:**
- Firewall rules blocking access
- Network policies restricting traffic
- Load balancer issues

**Solutions:**

#### Test Basic Connectivity
```bash
# Test if the endpoint is reachable
ping <your-ocp-endpoint>

# Test HTTPS connectivity
openssl s_client -connect <your-ocp-endpoint>:443 -servername <your-ocp-endpoint>
```

#### Check Network Policies
```bash
# List network policies that might affect monitoring
oc get networkpolicies -n openshift-monitoring
oc get networkpolicies -n openshift-user-workload-monitoring
```

### 5. Prometheus Configuration Issues

**Symptoms:**
- Configuration validation errors
- Prometheus fails to start
- Targets not appearing

**Solutions:**

#### Validate Configuration
```bash
# Check Prometheus configuration syntax
promtool check config /etc/prometheus/prometheus.yaml

# Check alert rules syntax
promtool check rules /etc/prometheus/rules/*.yml
```

#### Check Prometheus Logs
```bash
# View Prometheus logs
sudo journalctl -u prometheus -f

# Check for configuration errors
sudo journalctl -u prometheus | grep -i error
```

## Quick Fix Checklist

When your Prometheus targets suddenly stop working:

1. **Run the troubleshooting script**: `./troubleshoot-connectivity.sh`
2. **Check if endpoints changed**: Compare current endpoints with your configuration
3. **Test token validity**: Verify the service account token is still valid
4. **Increase timeouts**: Update `scrape_timeout` to 30s or higher
5. **Restart Prometheus**: `sudo systemctl restart prometheus`
6. **Check Prometheus logs**: Look for specific error messages

## Prevention

To prevent these issues in the future:

1. **Monitor endpoint changes**: Set up alerts for route changes in your OCP cluster
2. **Use long-lived tokens**: Create tokens with extended expiration (87600h = 10 years)
3. **Implement health checks**: Monitor Prometheus target health
4. **Document endpoints**: Keep a record of your cluster endpoints
5. **Regular testing**: Periodically test connectivity to your OCP cluster

## Getting Help

If you're still experiencing issues:

1. **Check OCP cluster status**: Ensure your cluster is healthy
2. **Review cluster logs**: Check for any cluster-level issues
3. **Contact cluster administrator**: For route or RBAC issues
4. **Check Prometheus community**: For Prometheus-specific issues

## Useful Commands

```bash
# Get all monitoring routes
oc get routes -n openshift-monitoring
oc get routes -n openshift-user-workload-monitoring

# Check service account status
oc get sa federator -n openshift-monitoring
oc describe sa federator -n openshift-monitoring

# Test token validity
oc auth can-i get prometheuses --as=system:serviceaccount:openshift-monitoring:federator

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Validate Prometheus configuration
promtool check config /etc/prometheus/prometheus.yaml
```


