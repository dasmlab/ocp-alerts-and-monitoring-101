# Tutorial Modules Overview

This directory contains the three main modules of the OCP Prometheus Alerting Tutorial. Each module is designed to build upon the previous one, taking you from basic setup to advanced custom alerting.

## 📚 Module Structure

### [Module 1: OCP Monitoring Components and Prometheus Setup](./module1-setup/README.md)
**Prerequisites**: OCP cluster access, cluster admin privileges

**What you'll learn:**
- Understanding OCP's built-in monitoring stack
- Key components: Prometheus, Thanos, AlertManager, Grafana
- Service accounts and RBAC for monitoring access
- Basic Prometheus configuration for OCP scraping
- Security considerations and best practices

**Key topics covered:**
- OCP monitoring architecture overview
- Service account creation and token generation
- Prometheus configuration structure
- Network security and authentication
- Troubleshooting connectivity issues

**Time to complete**: ~30-45 minutes

---

### [Module 2: Basic Connectivity and Sample Queries](./module2-connectivity/README.md)
**Prerequisites**: Completed Module 1

**What you'll learn:**
- Validating Prometheus connectivity to OCP
- Exploring available metrics and their namespaces
- Writing PromQL queries for common use cases
- Understanding metric labels and structure
- Using both Prometheus web UI and API

**Key topics covered:**
- Connectivity validation techniques
- Metric namespace understanding (kube_*, container_*, node_*, etc.)
- Sample queries for cluster health, resource utilization, and applications
- PromQL query language basics
- Troubleshooting query issues

**Files included:**
- `sample-queries.yml` - 50+ ready-to-use PromQL queries organized by category

**Time to complete**: ~45-60 minutes

---

### [Module 3: Custom Alert Writing and Service Monitor](./module3-alerts/README.md)
**Prerequisites**: Completed Modules 1 and 2

**What you'll learn:**
- Writing effective Prometheus alert rules
- Creating ServiceMonitor resources for application monitoring
- Alert routing and notification configuration
- Best practices for alert design and management
- Advanced monitoring scenarios

**Key topics covered:**
- Alert rule structure and components
- Alert states and lifecycle management
- ServiceMonitor configuration and best practices
- AlertManager setup and routing
- Custom application monitoring
- Alert fatigue prevention

**Files included:**
- `example-alert-rules.yml` - 20+ production-ready alert rules
- `example-servicemonitors.yml` - 10+ ServiceMonitor configurations for different scenarios

**Time to complete**: ~60-90 minutes

---

## 🎯 Learning Path

### For Beginners
Start with **Module 1** to understand the fundamentals, then progress through each module sequentially. Each module builds essential knowledge for the next.

### For Experienced Users
- **Module 1**: Quick review of OCP monitoring components
- **Module 2**: Jump to sample queries for immediate validation
- **Module 3**: Focus on custom alert rules and ServiceMonitor examples

### For Specific Use Cases
- **Infrastructure Monitoring**: Modules 1-2 + cluster health alerts from Module 3
- **Application Monitoring**: Modules 1-2 + ServiceMonitor examples from Module 3
- **Custom Alerting**: All modules, with focus on alert rules in Module 3

## 📋 Module Completion Checklist

### Module 1 ✅
- [ ] Understand OCP monitoring components
- [ ] Service account created with appropriate permissions
- [ ] Authentication token generated and secured
- [ ] Prometheus configuration structure understood
- [ ] Basic troubleshooting knowledge acquired

### Module 2 ✅
- [ ] Prometheus connectivity validated
- [ ] Sample queries executed successfully
- [ ] Metric namespaces and labels understood
- [ ] Both web UI and API usage demonstrated
- [ ] Query troubleshooting skills developed

### Module 3 ✅
- [ ] Custom alert rules written and tested
- [ ] ServiceMonitor resources created
- [ ] Alert routing configured
- [ ] Best practices implemented
- [ ] Advanced monitoring scenarios covered

## 🔧 Quick Reference

### Common Commands
```bash
# Module 1: Setup
./setup-service-account.sh
oc -n openshift-monitoring get route thanos-querier -o jsonpath='{.spec.host}'

# Module 2: Validation
curl -G 'http://192.168.1.234:9999/api/v1/query' --data-urlencode 'query=up'
curl -G 'http://192.168.1.234:9999/api/v1/query' --data-urlencode 'query=kube_node_status_condition{condition="Ready",status="true"}'

# Module 3: Alert Testing
promtool check rules /path/to/alert-rules.yml
curl http://192.168.1.234:9999/api/v1/alerts
```

### Key Files
- `../prometheus/prometheus.yaml` - Main Prometheus configuration
- `../prometheus/README.md` - Prometheus setup guide
- `module2-connectivity/sample-queries.yml` - Ready-to-use queries
- `module3-alerts/example-alert-rules.yml` - Production alert rules
- `module3-alerts/example-servicemonitors.yml` - ServiceMonitor examples

## 🆘 Getting Help

### Module-Specific Issues
- **Module 1**: Check service account permissions and network connectivity
- **Module 2**: Validate PromQL syntax and metric availability
- **Module 3**: Verify alert rule syntax and ServiceMonitor selectors

### General Troubleshooting
1. Check Prometheus logs: `sudo journalctl -u prometheus -f`
2. Validate configuration: `promtool check config /etc/prometheus/prometheus.yaml`
3. Test connectivity: Use sample queries from Module 2
4. Review target status: Prometheus web UI > Status > Targets

### Additional Resources
- [OpenShift Monitoring Documentation](https://docs.openshift.com/container-platform/latest/monitoring/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [ServiceMonitor API Reference](https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/api.md#servicemonitor)

## 🎓 Next Steps

After completing all modules, you'll have:
- ✅ Comprehensive understanding of OCP monitoring
- ✅ Working Prometheus setup with custom alerting
- ✅ Production-ready alert rules and ServiceMonitors
- ✅ Knowledge to monitor custom applications
- ✅ Best practices for alert management

**Ready to implement monitoring for your applications!** 🚀
