import os
from typing import List

# ------------------------------------------------------------------------------
# 🔁 Load env vars from .sslchecker.env first, fallback to .env
# ------------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv('.sslchecker.env', override=True)
    load_dotenv('.env', override=False)
except ImportError:
    pass

# ------------------------------------------------------------------------------
# ⚙️ Central Configuration Class
# ------------------------------------------------------------------------------
class SSLConfig:
    """Centralized configuration for SSL certificate checker"""

    # Provider Configuration
    PROVIDERS = os.getenv('SSL_PROVIDERS', 'k8s,tf').split(',')

    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')

    # Azure Configuration
    AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
    AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')

    # GCP Configuration
    GCP_PROJECT = os.getenv('GCP_PROJECT')
    GCP_REGION = os.getenv('GCP_REGION', 'us-central1')

    # Terraform Configuration
    TF_STATE_BUCKET = os.getenv('TF_STATE_BUCKET')
    TF_STATE_KEY = os.getenv('TF_STATE_KEY', 'terraform.tfstate')

    # Kubernetes Configuration
    K8S_CONTEXT = os.getenv('K8S_CONTEXT', 'default')

    # SSL Check Configuration
    SSL_THRESHOLD_DAYS = int(os.getenv('SSL_THRESHOLD_DAYS', '30'))
    SSL_CHECK_TIMEOUT = int(os.getenv('SSL_CHECK_TIMEOUT', '10'))

    # Monitoring Configuration
    PROMETHEUS_PUSHGATEWAY = os.getenv('PROMETHEUS_PUSHGATEWAY')
    CLOUDWATCH_NAMESPACE = os.getenv('CLOUDWATCH_NAMESPACE', 'SSLChecker')

    # Alerting Configuration
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_AUTH_BASIC = os.getenv('JIRA_AUTH_BASIC')
    JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY', 'CERT')

    # Pipeline Configuration
    PIPELINE_MODE = os.getenv('PIPELINE_MODE', 'scheduled')
    FAIL_ON_EXPIRY = os.getenv('FAIL_ON_EXPIRY', 'true').lower() == 'true'

    @classmethod
    def validate(cls) -> List[str]:
        """Validate required configuration and return list of missing variables"""
        missing = []
        for provider in cls.PROVIDERS:
            p = provider.strip().lower()
            if p == 'aws':
                if not cls.AWS_ACCOUNT_ID:
                    missing.append('AWS_ACCOUNT_ID')
                if not os.getenv('AWS_ACCESS_KEY_ID'):
                    missing.append('AWS_ACCESS_KEY_ID')
                if not os.getenv('AWS_SECRET_ACCESS_KEY'):
                    missing.append('AWS_SECRET_ACCESS_KEY')
            elif p == 'azure':
                if not cls.AZURE_SUBSCRIPTION_ID:
                    missing.append('AZURE_SUBSCRIPTION_ID')
                if not cls.AZURE_TENANT_ID:
                    missing.append('AZURE_TENANT_ID')
            elif p == 'gcp':
                if not cls.GCP_PROJECT:
                    missing.append('GCP_PROJECT')
                if not cls.GCP_REGION:
                    missing.append('GCP_REGION')
                if not os.getenv('GCP_CREDENTIALS_JSON'):
                    missing.append('GCP_CREDENTIALS_JSON')
            elif p == 'tf':
                if not cls.TF_STATE_BUCKET:
                    missing.append('TF_STATE_BUCKET')
            elif p == 'k8s':
                if not cls.K8S_CONTEXT:
                    missing.append('K8S_CONTEXT')

        if cls.PIPELINE_MODE == 'scheduled':
            if not cls.SLACK_WEBHOOK_URL:
                missing.append('SLACK_WEBHOOK_URL')
            if not cls.JIRA_AUTH_BASIC:
                missing.append('JIRA_AUTH_BASIC')

        return missing

    @classmethod
    def get_provider_config(cls, provider: str) -> dict:
        return {
            'aws': {
                'region': cls.AWS_REGION,
                'account_id': cls.AWS_ACCOUNT_ID
            },
            'azure': {
                'subscription_id': cls.AZURE_SUBSCRIPTION_ID,
                'tenant_id': cls.AZURE_TENANT_ID
            },
            'gcp': {
                'project': cls.GCP_PROJECT,
                'region': cls.GCP_REGION
            },
            'tf': {
                'state_bucket': cls.TF_STATE_BUCKET,
                'state_key': cls.TF_STATE_KEY
            },
            'k8s': {
                'context': cls.K8S_CONTEXT
            }
        }.get(provider, {})

    @classmethod
    def describe(cls) -> None:
        print("Selected Providers:", cls.PROVIDERS)
        print("Missing config:", cls.validate())
        for provider in cls.PROVIDERS:
            print(f"{provider} config:", cls.get_provider_config(provider))
