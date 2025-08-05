from google.cloud import compute_v1
import os
import json

project = os.getenv("GCP_PROJECT")
client = compute_v1.SslCertificatesClient()

certs = []
for cert in client.list(project=project):
    certs.append({
        "hostname": cert.name,
        "expires_at": cert.expire_time  # RFC3339 format
    })

print(json.dumps(certs))
