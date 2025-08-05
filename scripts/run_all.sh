#!/bin/bash
set -e

PROVIDERS=${PROVIDERS:-"tf,k8s"}

> all_domains.json

for provider in $(echo $PROVIDERS | tr ',' '\n'); do
  case "$provider" in
    tf)
      echo "Running Terraform discovery..."
      python scripts/discovery/discover_tf.py > tf.json || true
      cat tf.json >> all_domains.json
      ;;
    k8s)
      echo "Running K8s discovery..."
      python scripts/discovery/discover_k8s.py > k8s.json || true
      cat k8s.json >> all_domains.json
      ;;
    aws)
      echo "Running AWS discovery..."
      python scripts/discovery/discover_aws.py > aws.json || true
      cat aws.json >> all_domains.json
      ;;
    azure)
      echo "Running Azure discovery..."
      python scripts/discovery/discover_azure.py > azure.json || true
      cat azure.json >> all_domains.json
      ;;
    gcp)
      echo "Running GCP discovery..."
      python scripts/discovery/discover_gcp.py > gcp.json || true
      cat gcp.json >> all_domains.json
      ;;
    *)
      echo "Unknown provider: $provider"
      ;;
  esac
done

echo "Deduplicating domains..."
jq -s 'add | unique_by(.hostname)' all_domains.json > unique_domains.json

echo "Running SSL cert check..."
python scripts/ssl_cert_checker.py --hosts $(jq -r '.[].hostname' unique_domains.json) > cert-results.json

echo "Pushing to dashboards..."
python scripts/dashboards/prometheus.py cert-results.json || true
python scripts/dashboards/cloudwatch.py cert-results.json || true

echo "Sending alerts..."
python scripts/alerting/slack_alert.py cert-results.json || true
python scripts/alerting/jira_alert.py cert-results.json || true
