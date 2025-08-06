#!/bin/bash
set -euo pipefail

# ------------------------------------------------------------------------------
# 🔁 Load configuration from .sslchecker.env if it exists
# ------------------------------------------------------------------------------
if [ -f ".sslchecker.env" ]; then
  echo "🔁 Loading config from .sslchecker.env"
  set -a
  source .sslchecker.env
  set +a
fi

# ------------------------------------------------------------------------------
# 🌱 Default values (can be overridden by .env or CLI)
# ------------------------------------------------------------------------------
PROVIDERS="${PROVIDERS:-tf,k8s}"
OUTPUT_DIR="${OUTPUT_DIR:-./output}"
ENABLE_ALERTS="${ENABLE_ALERTS:-true}"
ENABLE_DASHBOARDS="${ENABLE_DASHBOARDS:-true}"
TASK=""

# ------------------------------------------------------------------------------
# 🧾 Parse CLI arguments
# ------------------------------------------------------------------------------
for arg in "$@"; do
  case $arg in
    ssl-check)
      TASK="ssl-check"
      shift
      ;;
    --providers=*) PROVIDERS="${arg#*=}"; shift ;;
    --output-dir=*) OUTPUT_DIR="${arg#*=}"; shift ;;
    --enable-alerts=*) ENABLE_ALERTS="${arg#*=}"; shift ;;
    --enable-dashboards=*) ENABLE_DASHBOARDS="${arg#*=}"; shift ;;
    --help|-h)
      echo "Usage: $0 ssl-check [--providers=aws,tf,k8s] [--output-dir=./output] [--enable-alerts=false] [--enable-dashboards=false]"
      exit 0
      ;;
    *) echo "❌ Unknown option: $arg"; exit 1 ;;
  esac
done

# ------------------------------------------------------------------------------
# 📦 Ensure output directory exists
# ------------------------------------------------------------------------------
mkdir -p "$OUTPUT_DIR"

# ------------------------------------------------------------------------------
# 📋 Print config
# ------------------------------------------------------------------------------
echo "Config: PROVIDERS=$PROVIDERS, OUTPUT_DIR=$OUTPUT_DIR, ENABLE_ALERTS=$ENABLE_ALERTS, ENABLE_DASHBOARDS=$ENABLE_DASHBOARDS"

# ------------------------------------------------------------------------------
# 🚀 Execute task
# ------------------------------------------------------------------------------
if [[ "$TASK" == "ssl-check" ]]; then
  if [ ! -f scripts/run_all.sh ]; then
    echo "❌ scripts/run_all.sh not found!"
    exit 1
  fi

  PROVIDERS="$PROVIDERS" \
  OUTPUT_DIR="$OUTPUT_DIR" \
  ENABLE_ALERTS="$ENABLE_ALERTS" \
  ENABLE_DASHBOARDS="$ENABLE_DASHBOARDS" \
  bash scripts/run_all.sh
else
  echo "❌ Unknown or missing task"
  exit 1
fi
