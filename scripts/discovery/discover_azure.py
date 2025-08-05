from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient
import os
import json

subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
credential = DefaultAzureCredential()
client = WebSiteManagementClient(credential, subscription_id)

certs = []

for cert in client.certificates.list():
    certs.append({
        "hostname": cert.host_names[0] if cert.host_names else "unknown",
        "expires_at": cert.expiration_date.isoformat()
    })

print(json.dumps(certs))
