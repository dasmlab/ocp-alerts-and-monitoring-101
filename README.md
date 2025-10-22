# OCP Prometheus Alerting Tutorial

A comprehensive guide to setting up custom alarms and alerting via Prometheus and Service Monitor in OpenShift Container Platform (OCP).

## Overview

This tutorial provides a step-by-step approach to implementing custom monitoring and alerting for your OCP cluster using Prometheus. You'll learn how to configure Prometheus to scrape metrics from your OCP cluster and create custom alert rules to monitor your applications and infrastructure.

## Prerequisites

- Access to an OCP cluster (4.11+)
- Cluster admin privileges for initial setup
- Basic understanding of Kubernetes and Prometheus concepts
- A Prometheus instance (we'll use one running on 192.168.1.234:9999 as an example)

## Tutorial Modules

### [Module 1: OCP Monitoring Components and Prometheus Setup](./modules/module1-setup/README.md)
- Understanding OCP's built-in monitoring stack
- Key components: Prometheus, Thanos, AlertManager
- Service accounts and RBAC for monitoring
- Basic Prometheus configuration for OCP scraping

### [Module 2: Basic Connectivity and Sample Queries](./modules/module2-connectivity/README.md)
- Validating Prometheus connectivity to OCP
- Exploring available metrics
- Sample queries for common use cases
- Understanding metric namespaces and labels

### [Module 3: Custom Alert Writing and Service Monitor](./modules/module3-alerts/README.md)
- Writing custom Prometheus alert rules
- Creating ServiceMonitor resources
- Alert routing and notification configuration
- Best practices for alert design

## Quick Start

1. **Setup Service Account**: Run the setup script to create the necessary service account and token
   ```bash
   ./setup-service-account.sh
   ```

2. **Configure Prometheus**: Copy the provided `prometheus.yaml` to your Prometheus configuration directory

3. **Validate Setup**: Use the sample queries in Module 2 to verify connectivity

4. **Create Custom Alerts**: Follow Module 3 to implement your custom alerting rules

## Project Structure

```
ocp-alerts-and-metrics/
├── README.md                           # This file
├── setup-service-account.sh           # Service account creation script
├── delete-service-account.sh          # Cleanup script
├── ocp-federate.token                 # Generated service account token
├── prometheus/
│   └── prometheus.yaml                # Prometheus configuration
└── modules/
    ├── module1-setup/                 # OCP monitoring setup
    ├── module2-connectivity/          # Basic queries and validation
    └── module3-alerts/                # Custom alerting
```

## References

- [OpenShift Monitoring Documentation](https://docs.openshift.com/container-platform/latest/monitoring/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)

## Contributing

This tutorial is designed to be a living document. Feel free to contribute improvements, additional examples, or corrections.

## License

This tutorial is provided as-is for educational purposes.
