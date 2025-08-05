import boto3
import json
import sys
import os

# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import SSLConfig

def discover_tf_domains():
    try:
        if not SSLConfig.TF_STATE_BUCKET:
            print("TF_STATE_BUCKET not configured", file=sys.stderr)
            return []
        
        s3 = boto3.client('s3', region_name=SSLConfig.AWS_REGION)
        state_file = s3.get_object(Bucket=SSLConfig.TF_STATE_BUCKET, Key=SSLConfig.TF_STATE_KEY)['Body'].read()
        state_json = json.loads(state_file)
        
        domains = []
        for resource in state_json.get('resources', []):
            if resource['type'] == 'aws_acm_certificate':
                for instance in resource['instances']:
                    attributes = instance.get('attributes', {})
                    domain_name = attributes.get('domain_name')
                    if domain_name:
                        domains.append({
                            "hostname": domain_name,
                            "source": "terraform",
                            "resource_type": resource['type'],
                            "resource_name": resource['name']
                        })
        
        return domains
    except Exception as e:
        print(f"Error retrieving Terraform state: {e}", file=sys.stderr)
        return []

if __name__ == '__main__':
    domains = discover_tf_domains()
    print(json.dumps(domains))
