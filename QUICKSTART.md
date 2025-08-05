# Quick Start Guide

Get SSL certificate checking running in your enterprise pipeline in 5 minutes.

## 🚀 Quick Setup

### 1. Add to Your GitLab CI Pipeline

Add this to your `.gitlab-ci.yml`:

```yaml
include:
  - project: 'your-org/ssl-cert-check'
    file: '/pipelines/enterprise-ssl-check.yml'

variables:
  # Required - choose your providers
  SSL_PROVIDERS: "k8s,tf"
  
  # Optional - customize thresholds
  SSL_THRESHOLD_DAYS: "30"
  FAIL_ON_EXPIRY: "true"
  
  # Add your specific configuration below
  AWS_REGION: "eu-west-1"
  TF_STATE_BUCKET: "my-terraform-state"
```

### 2. Set Required Variables

In your GitLab project settings → CI/CD → Variables, add:

#### For Kubernetes:
```
K8S_CONTEXT: "default"
```

#### For Terraform:
```
TF_STATE_BUCKET: "your-terraform-state-bucket"
TF_STATE_KEY: "terraform.tfstate"
```

#### For AWS:
```
AWS_REGION: "eu-west-1"
AWS_ACCESS_KEY_ID: "your-access-key"
AWS_SECRET_ACCESS_KEY: "your-secret-key"
```

### 3. Test It

Push a commit to any branch - the SSL check will run automatically!

## 📋 Minimal Configuration Examples

### Kubernetes Only
```yaml
variables:
  SSL_PROVIDERS: "k8s"
  SSL_THRESHOLD_DAYS: "30"
```

### Terraform + AWS
```yaml
variables:
  SSL_PROVIDERS: "tf,aws"
  AWS_REGION: "us-east-1"
  TF_STATE_BUCKET: "my-terraform-state"
```

### All Providers
```yaml
variables:
  SSL_PROVIDERS: "k8s,tf,aws,azure,gcp"
  SSL_THRESHOLD_DAYS: "30"
  AWS_REGION: "eu-west-1"
  AZURE_SUBSCRIPTION_ID: "your-sub-id"
  GCP_PROJECT: "your-project"
```

## 🔧 Pipeline Stages

The pipeline automatically creates these stages:

- **Pre-deployment**: Runs on feature branches, fails if certs expiring
- **Scheduled**: Runs weekly, sends alerts only
- **Production**: Runs on main branch, strict validation
- **Manual**: For testing via web interface

## 🎯 What Happens

1. **Discovery**: Finds all SSL certificates in your infrastructure
2. **Checking**: Validates expiration dates
3. **Reporting**: Shows results in pipeline
4. **Alerting**: Sends notifications if needed
5. **Metrics**: Exports to monitoring systems

## ✅ Success Criteria

Your setup is working if you see:
- ✅ SSL check stage in your pipeline
- 📊 Certificate count in the output
- 🟢 Pipeline passes (or fails appropriately)

## 🆘 Need Help?

- Check the [main README](README.md) for detailed configuration
- Review the [troubleshooting section](README.md#troubleshooting)
- Ensure your cloud provider credentials are correct