# Prometheus Configuration for OCP Cluster Scraping

This directory contains the Prometheus configuration file for scraping metrics from your OpenShift Container Platform cluster.

## Quick Setup

1. **Copy the configuration file** to your Prometheus configuration directory:
   ```bash
   sudo cp prometheus.yaml /etc/prometheus/prometheus.yaml
   ```

2. **Create the secrets directory** and copy your token:
   ```bash
   sudo mkdir -p /etc/prometheus/secrets
   sudo cp ../ocp-federate.token /etc/prometheus/secrets/
   sudo chown prometheus:prometheus /etc/prometheus/secrets/ocp-federate.token
   sudo chmod 600 /etc/prometheus/secrets/ocp-federate.token
   ```

3. **Restart Prometheus** to load the new configuration:
   ```bash
   sudo systemctl restart prometheus
   ```

## Configuration Overview

The `prometheus.yaml` file includes:

- **Global settings**: Scrape intervals and external labels
- **Alerting configuration**: AlertManager targets
- **Rule files**: Path to custom alert rules
- **Scrape configurations**: Multiple jobs for different metric types:
  - `ocp-cluster-federation`: Federated metrics from Thanos Querier
  - `ocp-cluster-direct`: Direct queries to Thanos Querier
  - `ocp-cluster-core`: Core cluster metrics
  - `ocp-cluster-apps`: Application-specific metrics

## Customization

### Update Cluster Endpoint
Replace the Thanos Querier endpoint with your cluster's actual endpoint:
```bash
# Get your cluster's Thanos Querier endpoint
oc -n openshift-monitoring get route thanos-querier -o jsonpath='{.spec.host}'
```

### Add Custom Alert Rules
Uncomment and configure the `rule_files` section:
```yaml
rule_files:
  - "/etc/prometheus/rules/*.yml"
```

### Modify Scrape Intervals
Adjust the `scrape_interval` and `evaluation_interval` based on your needs:
```yaml
global:
  scrape_interval: 15s  # How often to scrape targets
  evaluation_interval: 15s  # How often to evaluate alert rules
```

## Troubleshooting

### Check Configuration
```bash
# Validate Prometheus configuration
promtool check config /etc/prometheus/prometheus.yaml
```

### Check Targets
1. Open Prometheus web UI (e.g., `http://192.168.1.234:9999`)
2. Navigate to **Status > Targets**
3. Verify OCP targets show as **UP**

### Check Logs
```bash
# View Prometheus logs
sudo journalctl -u prometheus -f
```

## Security Notes

- The token file should be readable only by the Prometheus user
- Use TLS/SSL for production deployments
- Regularly rotate the service account token
- Implement network policies to restrict access

## Next Steps

After configuring Prometheus:
1. Follow **Module 2** to validate connectivity and explore metrics
2. Follow **Module 3** to create custom alert rules and ServiceMonitors
3. Configure AlertManager for alert routing and notifications

