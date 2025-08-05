#!/usr/bin/env python3
"""
Unified SSL Certificate Checker Runner
Handles discovery, checking, monitoring, and alerting in a single script
"""

import json
import sys
import os
import subprocess
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import SSLConfig

class SSLCheckRunner:
    def __init__(self):
        self.results_file = "cert-results.json"
        self.domains_file = "unique_domains.json"
        
    def validate_config(self) -> bool:
        """Validate configuration and exit if missing required variables"""
        missing = SSLConfig.validate()
        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            print("Please set the required variables for your providers.")
            return False
        return True
    
    def run_discovery(self) -> List[Dict[str, Any]]:
        """Run domain discovery for configured providers"""
        print(f"🔍 Running discovery for providers: {', '.join(SSLConfig.PROVIDERS)}")
        
        all_domains = []
        discovery_scripts = {
            'k8s': 'scripts/discovery/discover_k8s.py',
            'tf': 'scripts/discovery/discover_tf.py',
            'aws': 'scripts/discovery/discover_aws.py',
            'azure': 'scripts/discovery/discover_azure.py',
            'gcp': 'scripts/discovery/discover_gcp.py'
        }
        
        for provider in SSLConfig.PROVIDERS:
            if provider not in discovery_scripts:
                print(f"⚠️  Unknown provider: {provider}")
                continue
                
            script_path = discovery_scripts[provider]
            if not os.path.exists(script_path):
                print(f"⚠️  Discovery script not found: {script_path}")
                continue
            
            try:
                print(f"  Running {provider} discovery...")
                result = subprocess.run([sys.executable, script_path], 
                                      capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0 and result.stdout.strip():
                    domains = json.loads(result.stdout)
                    if isinstance(domains, list):
                        all_domains.extend(domains)
                        print(f"    Found {len(domains)} domains")
                    else:
                        print(f"    Invalid output format from {provider}")
                else:
                    print(f"    No domains found or error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"    ⏰ Timeout running {provider} discovery")
            except Exception as e:
                print(f"    ❌ Error running {provider} discovery: {e}")
        
        return all_domains
    
    def deduplicate_domains(self, domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate domains based on hostname"""
        print("🔄 Deduplicating domains...")
        
        seen = set()
        unique_domains = []
        
        for domain in domains:
            hostname = domain.get('hostname', '')
            if hostname and hostname not in seen:
                seen.add(hostname)
                unique_domains.append(domain)
        
        print(f"  Found {len(unique_domains)} unique domains")
        return unique_domains
    
    def run_ssl_checks(self, domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run SSL certificate checks on discovered domains"""
        if not domains:
            print("⚠️  No domains to check")
            return []
        
        print(f"🔒 Running SSL certificate checks on {len(domains)} domains...")
        
        hostnames = [d['hostname'] for d in domains]
        
        try:
            result = subprocess.run([
                sys.executable, 'scripts/ssl_cert_checker.py',
                '--hosts'] + hostnames + [
                '--threshold', str(SSLConfig.SSL_THRESHOLD_DAYS)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse JSON lines format
                results = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        results.append(json.loads(line))
                return results
            else:
                print(f"❌ SSL check failed: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print("⏰ SSL check timeout")
            return []
        except Exception as e:
            print(f"❌ Error running SSL checks: {e}")
            return []
    
    def send_to_monitoring(self, results: List[Dict[str, Any]]) -> None:
        """Send results to monitoring systems"""
        if not results:
            return
            
        print("📊 Sending to monitoring systems...")
        
        # Save results to file for monitoring scripts
        with open(self.results_file, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')
        
        monitoring_scripts = [
            ('Prometheus', 'scripts/dashboards/prometheus.py'),
            ('CloudWatch', 'scripts/dashboards/cloudwatch.py')
        ]
        
        for name, script_path in monitoring_scripts:
            if os.path.exists(script_path):
                try:
                    subprocess.run([sys.executable, script_path, self.results_file], 
                                  timeout=30, check=False)
                    print(f"  ✅ Sent to {name}")
                except Exception as e:
                    print(f"  ❌ Failed to send to {name}: {e}")
    
    def send_alerts(self, results: List[Dict[str, Any]]) -> None:
        """Send alerts for failing certificates"""
        failing = [r for r in results if r.get('status') == 'FAIL']
        
        if not failing:
            print("✅ No failing certificates to alert on")
            return
        
        print(f"🚨 Sending alerts for {len(failing)} failing certificates...")
        
        alert_scripts = [
            ('Slack', 'scripts/alerting/slack_alert.py'),
            ('Jira', 'scripts/alerting/jira_alert.py')
        ]
        
        for name, script_path in alert_scripts:
            if os.path.exists(script_path):
                try:
                    subprocess.run([sys.executable, script_path, self.results_file], 
                                  timeout=30, check=False)
                    print(f"  ✅ Alert sent to {name}")
                except Exception as e:
                    print(f"  ❌ Failed to send alert to {name}: {e}")
    
    def generate_report(self, results: List[Dict[str, Any]]) -> None:
        """Generate a summary report"""
        if not results:
            return
            
        total = len(results)
        failing = len([r for r in results if r.get('status') == 'FAIL'])
        passing = total - failing
        
        print("\n" + "="*50)
        print("📋 SSL Certificate Check Report")
        print("="*50)
        print(f"Total certificates checked: {total}")
        print(f"Passing: {passing}")
        print(f"Failing: {failing}")
        print(f"Threshold: {SSLConfig.SSL_THRESHOLD_DAYS} days")
        
        if failing > 0:
            print("\n🚨 Failing Certificates:")
            for result in results:
                if result.get('status') == 'FAIL':
                    print(f"  • {result['hostname']}: {result['days_left']} days remaining")
        
        print("="*50)
    
    def run(self) -> int:
        """Main execution method"""
        print(f"🚀 Starting SSL Certificate Check ({SSLConfig.PIPELINE_MODE} mode)")
        print(f"Providers: {', '.join(SSLConfig.PROVIDERS)}")
        print(f"Threshold: {SSLConfig.SSL_THRESHOLD_DAYS} days")
        
        # Validate configuration
        if not self.validate_config():
            return 1
        
        # Run discovery
        domains = self.run_discovery()
        if not domains:
            print("⚠️  No domains discovered")
            return 0
        
        # Deduplicate
        unique_domains = self.deduplicate_domains(domains)
        
        # Run SSL checks
        results = self.run_ssl_checks(unique_domains)
        if not results:
            print("❌ No SSL check results")
            return 1
        
        # Send to monitoring
        self.send_to_monitoring(results)
        
        # Send alerts
        self.send_alerts(results)
        
        # Generate report
        self.generate_report(results)
        
        # Determine exit code
        failing = len([r for r in results if r.get('status') == 'FAIL'])
        if failing > 0 and SSLConfig.FAIL_ON_EXPIRY:
            print(f"❌ {failing} certificates are expiring soon")
            return 1
        
        print("✅ SSL certificate check completed successfully")
        return 0

if __name__ == '__main__':
    runner = SSLCheckRunner()
    sys.exit(runner.run())