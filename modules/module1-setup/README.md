# Module 1: OCP Monitoring Components and Prometheus Setup

## Overview

This module covers the fundamental components of OpenShift Container Platform's monitoring stack and how to configure an external Prometheus instance to scrape metrics from your OCP cluster.

## OCP Monitoring Stack Components

### Core Components

OpenShift Container Platform includes a comprehensive monitoring stack built on Prometheus and related technologies:

#### 1. **Prometheus Operator**
- Manages Prometheus instances and configurations
- Handles ServiceMonitor and PrometheusRule resources
- Automatically discovers and configures scraping targets
- Located in the `openshift-monitoring` namespace

#### 2. **Prometheus Instances**
- **Cluster Monitoring Prometheus**: Monitors core cluster components
- **User Workload Monitoring Prometheus**: Monitors user applications (when enabled)
- Both instances are managed by the Prometheus Operator

#### 3. **Thanos**
- Provides long-term storage and querying capabilities
- Enables federation and global querying across multiple Prometheus instances
- Includes Thanos Querier, Store, and other components

#### 4. **AlertManager**
- Handles alert routing and notification
- Manages alert grouping, inhibition, and silencing
- Integrates with various notification channels (email, Slack, PagerDuty, etc.)

#### 5. **Grafana** (Optional)
- Provides visualization and dashboards
- Can be deployed separately or as part of the monitoring stack

### Key Namespaces

- **`openshift-monitoring`**: Core monitoring components
- **`openshift-user-workload-monitoring`**: User workload monitoring (when enabled)

## External Prometheus Setup

### Prerequisites

Before setting up external Prometheus scraping, ensure you have:

1. **Cluster Admin Access**: Required for creating service accounts and RBAC policies
2. **OCP 4.11+**: For long-lived token support
3. **External Prometheus Instance**: Running and accessible

### Step 1: Create Service Account and RBAC

The provided `setup-service-account.sh` script creates the necessary service account and permissions:

```bash
# Create service account with read-only monitoring access
oc -n openshift-monitoring create sa federator

# Grant cluster-monitoring-view role
oc adm policy add-cluster-role-to-user cluster-monitoring-view -z federator -n openshift-monitoring

# Create long-lived token (OCP 4.11+)
oc -n openshift-monitoring create token federator --duration=87600h > ocp-federate.token
```

### Step 2: Understanding the Service Account

The `federator` service account is granted the `cluster-monitoring-view` role, which provides:

- **Read access** to all monitoring resources
- **Access to metrics endpoints** across the cluster
- **No write permissions** (security best practice)

### Step 3: Prometheus Configuration

The external Prometheus needs to be configured to scrape the OCP cluster. Key configuration elements:

#### Authentication
- Use the generated token for authentication
- Store the token securely (e.g., in Prometheus secrets directory)

#### Scraping Targets
- **Thanos Querier**: Primary endpoint for federated queries
- **Individual Prometheus instances**: For direct scraping
- **Service endpoints**: For application-specific metrics

#### Configuration File Structure
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ocp-cluster'
    bearer_token_file: '/etc/prometheus/secrets/ocp-federate.token'
    static_configs:
      - targets: ['thanos-querier.openshift-monitoring.svc.cluster.local:9091']
```

## Security Considerations

### Token Management
- **Long-lived tokens**: Use for external systems (87600h = 10 years)
- **Token rotation**: Implement regular token rotation procedures
- **Secure storage**: Store tokens in secure locations with appropriate permissions

### Network Security
- **TLS/SSL**: Ensure all communications are encrypted
- **Network policies**: Implement network policies to restrict access
- **Firewall rules**: Configure appropriate firewall rules

### RBAC Best Practices
- **Principle of least privilege**: Grant only necessary permissions
- **Regular audits**: Review and audit service account permissions
- **Separation of concerns**: Use different service accounts for different purposes

## Troubleshooting Common Issues

### Authentication Failures
```bash
# Verify service account exists
oc get sa federator -n openshift-monitoring

# Check token validity
oc describe token federator -n openshift-monitoring

# Verify RBAC permissions
oc auth can-i get prometheuses --as=system:serviceaccount:openshift-monitoring:federator
```

### Network Connectivity
```bash
# Test connectivity to Thanos Querier
curl -H "Authorization: Bearer $(cat ocp-federate.token)" \
  https://thanos-querier.openshift-monitoring.svc.cluster.local:9091/api/v1/query?query=up
```

### Prometheus Configuration Validation
```bash
# Validate Prometheus configuration
promtool check config /etc/prometheus/prometheus.yaml

# Test configuration syntax
promtool check rules /path/to/alert-rules.yml
```

## Next Steps

After completing this module, you should have:

1. ✅ Understanding of OCP monitoring components
2. ✅ Service account created with appropriate permissions
3. ✅ Authentication token generated
4. ✅ Basic Prometheus configuration structure

**Proceed to [Module 2: Basic Connectivity and Sample Queries](../module2-connectivity/README.md)** to validate your setup and explore available metrics.

## References

- [OpenShift Monitoring Documentation](https://docs.openshift.com/container-platform/latest/monitoring/)
- [Prometheus Federation](https://prometheus.io/docs/prometheus/latest/federation/)
- [OpenShift Service Accounts](https://docs.openshift.com/container-platform/latest/authentication/understanding-and-creating-service-accounts.html)
