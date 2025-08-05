import ssl
import socket
from datetime import datetime
import json
import sys
import argparse

def get_cert_expiry(hostname, port=443):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_socket:
            cert = secure_socket.getpeercert()
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            return expiry_date

def check_cert(hostname, threshold_days=10):
    expiry_date = get_cert_expiry(hostname)
    days_left = (expiry_date - datetime.utcnow()).days
    return {
        'hostname': hostname,
        'expiry_date': expiry_date.isoformat(),
        'days_left': days_left,
        'status': 'FAIL' if days_left < threshold_days else 'PASS'
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SSL Certificate Expiration Checker')
    parser.add_argument('--hosts', nargs='+', required=True, help='List of hosts')
    parser.add_argument('--threshold', type=int, default=10, help='Days threshold')
    args = parser.parse_args()

    results = [check_cert(host, args.threshold) for host in args.hosts]
    for res in results:
        print(json.dumps(res))

    if any(res['status'] == 'FAIL' for res in results):
        sys.exit(1)
