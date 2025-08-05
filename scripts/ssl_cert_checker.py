import ssl
import socket
from datetime import datetime
import json
import sys
import argparse
import os

def get_cert_expiry(hostname, port=443, timeout=10):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as secure_socket:
                cert = secure_socket.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                return expiry_date
    except socket.timeout:
        raise Exception(f"Connection timeout to {hostname}:{port}")
    except ssl.SSLError as e:
        raise Exception(f"SSL error for {hostname}: {e}")
    except Exception as e:
        raise Exception(f"Connection error for {hostname}: {e}")

def check_cert(hostname, threshold_days=30, timeout=10):
    try:
        expiry_date = get_cert_expiry(hostname, timeout=timeout)
        days_left = (expiry_date - datetime.utcnow()).days
        return {
            'hostname': hostname,
            'expiry_date': expiry_date.isoformat(),
            'days_left': days_left,
            'status': 'FAIL' if days_left < threshold_days else 'PASS',
            'error': None
        }
    except Exception as e:
        return {
            'hostname': hostname,
            'expiry_date': None,
            'days_left': None,
            'status': 'ERROR',
            'error': str(e)
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SSL Certificate Expiration Checker')
    parser.add_argument('--hosts', nargs='+', required=True, help='List of hosts')
    parser.add_argument('--threshold', type=int, default=30, help='Days threshold')
    parser.add_argument('--timeout', type=int, default=10, help='Connection timeout in seconds')
    args = parser.parse_args()

    results = [check_cert(host, args.threshold, args.timeout) for host in args.hosts]
    for res in results:
        print(json.dumps(res))

    # Exit with error if any certificates are failing or have errors
    if any(res['status'] in ['FAIL', 'ERROR'] for res in results):
        sys.exit(1)
