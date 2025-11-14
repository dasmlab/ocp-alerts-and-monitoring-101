# Get the public Hostname of the Thanos Querier (route exists by default)
oc -n openshift-monitoring get route thanos-querier -o jsonpath='{.spec.host}{"\n"}'
THANOS_HOST=$(oc -n openshift-monitoring get route thanos-querier -o jsonpath='{.spec.host}{"\n"}')


# Create a service Account with Read-only monitoring acecss
#
#

#4.19+
#oc -n openshift-monitoring create sa federator || true
#oc adm policy add-cluster-role-to-user cluster-monitoring-view -z federator -n openshift-monitoring

# Create a long lived token (OCP 4.19+)
#oc -n openshift-monitoring create token federator --duration=87600h > ocp-federate.token
#
#

# 4.18-
oc -n openshift-monitoring create serviceaccount federator 2>/dev/null || true
oc adm policy add-cluster-role-to-user cluster-monitoring-view -n openshift-monitoring -z federator


# Mint a Token
cat <<'EOF' | oc -n openshift-monitoring apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: federator-token
  annotations:
    kubernetes.io/service-account.name: federator
type: kubernetes.io/service-account-token
EOF

# Sleep for 5 seconds for generation
echo "Sleeping for 5 seconds"
sleep 5

# Extract Token
# confirm the controller has populated the Secret
oc -n openshift-monitoring get secret federator-token -o jsonpath='{.data.token}' >/dev/null

# write the token to a file
oc -n openshift-monitoring get secret federator-token \
  -o jsonpath='{.data.token}' | base64 -d > ocp-federate.token

# show fields present (token, ca.crt should exist)
oc -n openshift-monitoring get secret federator-token -o jsonpath='{.data}'

# Sanity Check peek JWT header/payload (padding-safe)
python3 - <<'PY'
import base64, json, sys
tok=open("ocp-federate.token").read().strip().split('.')
pad=lambda s: s+'='*(-len(s)%4)
print(json.dumps(json.loads(base64.urlsafe_b64decode(pad(tok[0]))), indent=2))
print(json.dumps(json.loads(base64.urlsafe_b64decode(pad(tok[1]))), indent=2))
PY



# Move to ocp-federate.token to /etc/prometheus/secrets
sudo mkdir -p /etc/prometheus/secrets
sudo cp ocp-federate.token /etc/prometheus/secrets/ocp-federate.token.SNO-2







