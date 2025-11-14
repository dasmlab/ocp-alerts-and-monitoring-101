docker stop prometheus-instance
docker rm prometheus-instance
docker run -d --name=prometheus-instance \
	--restart=always \
	-p 9999:9090 \
	-v /etc/prometheus:/etc/prometheus \
	--add-host prometheus-k8s-federate-openshift-monitoring.apps.ocp-ai-sno.rh.dasmlab.org:192.168.1.130 \
	--add-host federate-openshift-user-workload-monitoring.apps.ocp-ai-sno.rh.dasmlab.org:192.168.1.130 \
	prom/prometheus:latest \
	--config.file=/etc/prometheus/prometheus.yaml
