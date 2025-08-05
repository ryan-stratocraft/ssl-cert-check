import boto3
import json
import sys

STATE_BUCKET = "your-terraform-state-bucket"
STATE_KEY = "path/to/terraform.tfstate"

s3 = boto3.client('s3')

try:
    state_file = s3.get_object(Bucket=STATE_BUCKET, Key=STATE_KEY)['Body'].read()
    state_json = json.loads(state_file)
    cert_domains = []

    for resource in state_json.get('resources', []):
        if resource['type'] == 'aws_acm_certificate':
            for instance in resource['instances']:
                attributes = instance.get('attributes', {})
                cert_domains.append(attributes.get('domain_name'))

    print(json.dumps(cert_domains))
except Exception as e:
    print(f"Error retrieving Terraform state: {e}")
    sys.exit(1)
