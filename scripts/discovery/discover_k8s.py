from kubernetes import client, config
import json

config.load_kube_config()
v1 = client.NetworkingV1Api()
ingresses = v1.list_ingress_for_all_namespaces()

domains = []
for ingress in ingresses.items:
    if ingress.spec.tls:
        for tls in ingress.spec.tls:
            domains.extend(tls.hosts)

print(json.dumps(domains))
