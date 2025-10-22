oc -n openshift-user-workload-monitoring create route reencrypt user-workload-federate \
  --service=prometheus-user-workload \
  --port=web \
  --path=/federate

