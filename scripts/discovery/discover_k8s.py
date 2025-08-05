from kubernetes import client, config
import json
import sys
import os

# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import SSLConfig

def discover_k8s_domains():
    try:
        config.load_kube_config(context=SSLConfig.K8S_CONTEXT)
        v1 = client.NetworkingV1Api()
        ingresses = v1.list_ingress_for_all_namespaces()
        
        domains = []
        for ingress in ingresses.items:
            if ingress.spec.tls:
                for tls in ingress.spec.tls:
                    for host in tls.hosts:
                        domains.append({
                            "hostname": host,
                            "source": "kubernetes",
                            "namespace": ingress.metadata.namespace,
                            "ingress": ingress.metadata.name
                        })
        
        return domains
    except Exception as e:
        print(f"Error discovering Kubernetes domains: {e}", file=sys.stderr)
        return []

if __name__ == '__main__':
    domains = discover_k8s_domains()
    print(json.dumps(domains))
