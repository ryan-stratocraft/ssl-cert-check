import boto3
import json
import sys

cloudwatch = boto3.client('cloudwatch')

with open(sys.argv[1]) as f:
    results = [json.loads(line) for line in f if line.strip()]

for cert in results:
    cloudwatch.put_metric_data(
        Namespace='SSLChecker',
        MetricData=[{
            'MetricName': 'DaysToExpiry',
            'Dimensions': [{'Name': 'Host', 'Value': cert['hostname']}],
            'Value': cert['days_left'],
            'Unit': 'Count'
        }]
    )
