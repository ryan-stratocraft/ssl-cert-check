from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import json
import sys

PUSHGATEWAY_URL = "http://your-pushgateway:9091"

registry = CollectorRegistry()
g = Gauge('ssl_cert_days_remaining', 'Days remaining SSL cert', ['host'], registry=registry)

with open(sys.argv[1]) as f:
    results = [json.loads(line) for line in f if line.strip()]

for cert in results:
    g.labels(host=cert['hostname']).set(cert['days_left'])

push_to_gateway(PUSHGATEWAY_URL, job='ssl_cert_checker', registry=registry)
