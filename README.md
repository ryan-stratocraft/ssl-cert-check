# SSL Certificate Checker

An enterprise-grade automated SSL certificate monitoring and alerting system designed for hybrid cloud environments. This tool automatically discovers SSL certificates across multiple cloud providers and infrastructure platforms, checks their expiration dates, and provides monitoring and alerting capabilities.

## 🚀 Features

- **Multi-Provider Discovery**: Automatically discovers SSL certificates from:
  - Kubernetes (Ingress resources with TLS)
  - Terraform (state files)
  - AWS (ACM, Load Balancers, API Gateway)
  - Azure (Application Gateways, Front Door)
  - GCP (Load Balancers, Cloud Armor)

- **Flexible Deployment**: 
  - Pre-deployment checks (fail pipeline on expiring certs)
  - Scheduled monitoring (weekly checks)
  - Manual testing capabilities

- **Enterprise Integration**:
  - GitLab CI/CD pipeline integration
  - Prometheus metrics export
  - CloudWatch metrics
  - Slack notifications
  - Jira ticket creation

- **Configuration-Driven**: Set variables once, use across all environments

## 📋 Prerequisites

- Python 3.11+
- Access to cloud provider APIs
- GitLab CI/CD (for pipeline integration)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ssl-cert-check
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (see Configuration section)

## ⚙️ Configuration

### Required Variables

Set these environment variables based on your providers:

#### For All Providers:
```bash
SSL_PROVIDERS="k8s,tf,aws"        # Comma-separated list
SSL_THRESHOLD_DAYS="30"           # Days before expiry to alert
PIPELINE_MODE="deployment"        # "scheduled" or "deployment"
FAIL_ON_EXPIRY="true"             # Whether to fail pipeline
```

#### AWS Configuration:
```bash
AWS_REGION="eu-west-1"
AWS_ACCOUNT_ID="123456789012"
AWS_ACCESS_KEY_ID="your-access-key"
AWS_SECRET_ACCESS_KEY="your-secret-key"
```

#### Azure Configuration:
```bash
AZURE_SUBSCRIPTION_ID="your-subscription-id"
AZURE_TENANT_ID="your-tenant-id"
AZURE_CLIENT_ID="your-client-id"
AZURE_CLIENT_SECRET="your-client-secret"
```

#### GCP Configuration:
```bash
GCP_PROJECT="your-project-id"
GCP_REGION="us-central1"
GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

#### Terraform Configuration:
```bash
TF_STATE_BUCKET="your-terraform-state-bucket"
TF_STATE_KEY="path/to/terraform.tfstate"
```

#### Kubernetes Configuration:
```bash
K8S_CONTEXT="default"
KUBECONFIG="path/to/kubeconfig"
```

#### Monitoring Configuration:
```bash
PROMETHEUS_PUSHGATEWAY="http://prometheus-pushgateway:9091"
CLOUDWATCH_NAMESPACE="SSLChecker"
```

#### Alerting Configuration:
```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
JIRA_URL="https://your-jira.atlassian.net"
JIRA_AUTH_BASIC="base64-encoded-user:token"
JIRA_PROJECT_KEY="CERT"
```

## 🚀 Usage

### Local Execution

Run the SSL checker locally:

```bash
python scripts/ssl_check_runner.py
```

### GitLab CI Integration

Include the pipeline template in your `.gitlab-ci.yml`:

```yaml
include:
  - project: 'your-org/ssl-cert-check'
    file: '/pipelines/enterprise-ssl-check.yml'
```

Or copy the template and customize as needed.

### Pipeline Stages

The pipeline provides different stages for different use cases:

1. **Pre-deployment Check** (`ssl-check-pre-deployment`):
   - Runs before feature branch deployments
   - Fails pipeline if certificates are expiring soon
   - Triggers on push to feature branches and merge requests

2. **Scheduled Check** (`ssl-check-scheduled`):
   - Runs weekly via scheduled pipelines
   - Sends alerts but doesn't fail pipeline
   - Good for monitoring and early warning

3. **Production Check** (`ssl-check-production`):
   - Runs before main branch deployments
   - Stricter validation for production deployments
   - Fails pipeline on any certificate issues

4. **Manual Check** (`ssl-check-manual`):
   - For testing and manual validation
   - Triggered via web interface

## 📊 Output

The tool generates:

- **Console Report**: Summary of all certificate checks
- **JSON Results**: Detailed results in `cert-results.json`
- **Prometheus Metrics**: For monitoring dashboards
- **CloudWatch Metrics**: For AWS monitoring
- **Slack Alerts**: For immediate notifications
- **Jira Tickets**: For tracking certificate renewals

## 🔧 Customization

### Adding New Providers

1. Create a discovery script in `scripts/discovery/`
2. Add provider configuration to `config.py`
3. Update the runner script to include the new provider

### Custom Alerting

Modify the alerting scripts in `scripts/alerting/` to integrate with your notification systems.

### Custom Monitoring

Extend the dashboard scripts in `scripts/dashboards/` to send metrics to your monitoring systems.

## 🐛 Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Use the validation in `config.py` to check required variables
2. **Permission Issues**: Ensure proper IAM roles and permissions for cloud providers
3. **Network Issues**: Check firewall rules and network connectivity
4. **Timeout Issues**: Adjust `SSL_CHECK_TIMEOUT` for slow networks

### Debug Mode

Set `DEBUG=true` to enable verbose logging:

```bash
export DEBUG=true
python scripts/ssl_check_runner.py
```

## 🏗️ How to Use in Your Own Repo (Peripheral Integration)

### 1. Create a `.sslchecker.env` file in your repo:

```
# .sslchecker.env
SSL_PROVIDERS=aws,tf
AWS_REGION=eu-west-1
TF_STATE_BUCKET=mybucket
ENABLE_ALERTS=true
ENABLE_DASHBOARDS=true
```

You can also use a `.env` file as a fallback for local development.

### 2. Add the SSL checker as a submodule or reference in your pipeline

- **GitHub Actions**: Use `run.sh` as your job step
- **GitLab CI**: Use `run.sh` in your job script
- **Azure DevOps**: Use a bash step to call `./run.sh ssl-check`

### 3. Example pipeline step

**GitHub Actions**
```yaml
- name: Run SSL Cert Check
  run: |
    chmod +x ./run.sh
    ./run.sh ssl-check
```

**GitLab CI**
```yaml
ssl-check:
  stage: test
  script:
    - chmod +x ./run.sh
    - ./run.sh ssl-check
```

**Azure DevOps**
```yaml
- script: |
    chmod +x ./run.sh
    ./run.sh ssl-check
  displayName: 'Run SSL Cert Check'
```

### 4. Debugging

- The script will echo the final config it uses for debugging.
- If you want to override any variable, set it in `.sslchecker.env`, `.env`, or as a CLI argument.

### 5. Output

- Results and logs will be placed in the directory specified by `OUTPUT_DIR` (default: `./output`).

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration examples
