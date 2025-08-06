#!/bin/bash
set -euo pipefail

PROVIDERS=${1:-${PROVIDERS:-"tf,k8s"}}
OUTPUT_DIR=${OUTPUT_DIR:-"./output"}
ENABLE_ALERTS=${ENABLE_ALERTS:-true}
ENABLE_DASHBOARDS=${ENABLE_DASHBOARDS:-true}

mkdir -p "$OUTPUT_DIR"
ALL_DOMAINS="$OUTPUT_DIR/all_domains.json"
UNIQUE_DOMAINS="$OUTPUT_DIR/unique_domains.json"
CERT_RESULTS="$OUTPUT_DIR/cert-results.json"

> "$ALL_DOMAINS"

for provider in $(echo "$PROVIDERS" | tr ',' '\n'); do
  case "$provider" in
    tf|k8s|aws|azure|gcp)
      echo "Running $provider discovery..."
      python "scripts/discovery/discover_${provider}.py" > "$OUTPUT_DIR/${provider}.json" || true
      cat "$OUTPUT_DIR/${provider}.json" >> "$ALL_DOMAINS"
      ;;
    *)
      echo "⚠️ Unknown provider: $provider"
      ;;
  esac
done

echo "Deduplicating domains..."
jq -s 'add | unique_by(.hostname)' "$ALL_DOMAINS" > "$UNIQUE_DOMAINS"

echo "Running SSL cert check..."
python scripts/ssl_cert_checker.py --hosts "$(jq -r '.[].hostname' "$UNIQUE_DOMAINS")" > "$CERT_RESULTS"

if [ "$ENABLE_DASHBOARDS" = "true" ]; then
  echo "Pushing to dashboards..."
  python scripts/dashboards/prometheus.py "$CERT_RESULTS" || true
  python scripts/dashboards/cloudwatch.py "$CERT_RESULTS" || true
fi

if [ "$ENABLE_ALERTS" = "true" ]; then
  echo "Sending alerts..."
  python scripts/alerting/slack_alert.py "$CERT_RESULTS" || true
  python scripts/alerting/jira_alert.py "$CERT_RESULTS" || true
fi
