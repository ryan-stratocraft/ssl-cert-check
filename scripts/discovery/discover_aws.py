import boto3
import json
import os

region = os.getenv('AWS_REGION', 'us-east-1')
client = boto3.client('acm', region_name=region)

def get_cert_domains():
    certs = []
    paginator = client.get_paginator('list_certificates')
    for page in paginator.paginate(CertificateStatuses=['ISSUED']):
        for cert in page['CertificateSummaryList']:
            details = client.describe_certificate(CertificateArn=cert['CertificateArn'])
            domain = details['Certificate']['DomainName']
            expiry = details['Certificate']['NotAfter'].isoformat()
            certs.append({"hostname": domain, "expires_at": expiry})
    return certs

if __name__ == '__main__':
    print(json.dumps(get_cert_domains()))
