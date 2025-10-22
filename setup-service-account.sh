# Get the public Hostname of the Thanos Querier (route exists by default)
oc -n openshift-monitoring get route thanos-querier -o jsonpath='{.spec.host}{"\n"}'
THANOS_HOST=$(oc -n openshift-monitoring get route thanos-querier -o jsonpath='{.spec.host}{"\n"}')


# Create a service Account with Read-only monitoring acecss
#
oc -n openshift-monitoring create sa federator || true
oc adm policy add-cluster-role-to-user cluster-monitoring-view -z federator -n openshift-monitoring

# Create a long lived token (OCP 4.11+)
oc -n openshift-monitoring create token federator --duration=87600h > ocp-federate.token

# Move to ocp-federate.token to /etc/prometheus/secrets
sudo mkdir -p /etc/prometheus/secrets
sudo cp ocp-federate.token /etc/prometheus/secrets







