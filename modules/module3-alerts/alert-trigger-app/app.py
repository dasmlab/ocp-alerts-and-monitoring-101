#!/usr/bin/env python3
"""
Alert Trigger Demo App
This app can be used to trigger various alerts for demonstration purposes.
It exposes metrics that can be used to trigger alerts defined in PrometheusRules.
"""

import time
import http.server
import socketserver
import threading
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Global state for triggering alerts
cpu_usage = 50.0  # Default CPU usage percentage
memory_usage = 50.0  # Default memory usage percentage
error_rate = 0.0  # Default error rate (0-100%)
request_count = 0
error_count = 0
high_cpu_mode = False
high_memory_mode = False
high_error_mode = False

def generate_metrics():
    """Generate Prometheus metrics based on current state."""
    global request_count, error_count, cpu_usage, memory_usage, error_rate
    
    # Simulate some variation
    if high_cpu_mode:
        cpu_usage = min(100.0, cpu_usage + random.uniform(0, 2))
    else:
        cpu_usage = max(0, cpu_usage - random.uniform(0, 1))
        if cpu_usage < 50:
            cpu_usage = 50
    
    if high_memory_mode:
        memory_usage = min(100.0, memory_usage + random.uniform(0, 2))
    else:
        memory_usage = max(0, memory_usage - random.uniform(0, 1))
        if memory_usage < 50:
            memory_usage = 50
    
    if high_error_mode:
        error_rate = min(100.0, error_rate + random.uniform(0, 5))
    else:
        error_rate = max(0, error_rate - random.uniform(0, 2))
    
    # Calculate request rates
    total_requests = request_count
    error_requests = error_count
    
    metrics = f"""# HELP alert_demo_cpu_usage_percent CPU usage percentage (0-100)
# TYPE alert_demo_cpu_usage_percent gauge
alert_demo_cpu_usage_percent {cpu_usage:.2f}

# HELP alert_demo_memory_usage_percent Memory usage percentage (0-100)
# TYPE alert_demo_memory_usage_percent gauge
alert_demo_memory_usage_percent {memory_usage:.2f}

# HELP alert_demo_http_requests_total Total number of HTTP requests
# TYPE alert_demo_http_requests_total counter
alert_demo_http_requests_total {total_requests}

# HELP alert_demo_http_errors_total Total number of HTTP errors (5xx)
# TYPE alert_demo_http_errors_total counter
alert_demo_http_errors_total {error_requests}

# HELP alert_demo_error_rate_percent Error rate percentage (0-100)
# TYPE alert_demo_error_rate_percent gauge
alert_demo_error_rate_percent {error_rate:.2f}

# HELP alert_demo_info Application information
# TYPE alert_demo_info gauge
alert_demo_info{{version="1.0.0",app="alert-trigger"}} 1
"""
    return metrics

class AlertTriggerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global cpu_usage, memory_usage, error_rate, request_count, error_count
        global high_cpu_mode, high_memory_mode, high_error_mode
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = f"""
            <html>
            <head><title>Alert Trigger Demo App</title></head>
            <body>
                <h1>Alert Trigger Demo Application</h1>
                <p>Use this app to trigger alerts for demonstration purposes.</p>
                
                <h2>Current Metrics</h2>
                <ul>
                    <li>CPU Usage: {cpu_usage:.2f}%</li>
                    <li>Memory Usage: {memory_usage:.2f}%</li>
                    <li>Error Rate: {error_rate:.2f}%</li>
                    <li>Total Requests: {request_count}</li>
                    <li>Error Requests: {error_count}</li>
                </ul>
                
                <h2>Trigger Actions</h2>
                <p>Click the buttons below to trigger different alert conditions:</p>
                <ul>
                    <li><a href="/trigger?action=high_cpu">Trigger High CPU Alert (CPU > 80%)</a></li>
                    <li><a href="/trigger?action=high_memory">Trigger High Memory Alert (Memory > 90%)</a></li>
                    <li><a href="/trigger?action=high_errors">Trigger High Error Rate (Errors > 5%)</a></li>
                    <li><a href="/trigger?action=reset">Reset All Metrics</a></li>
                </ul>
                
                <h2>Endpoints</h2>
                <ul>
                    <li><a href="/">/</a> - This page</li>
                    <li><a href="/metrics">/metrics</a> - Prometheus metrics</li>
                    <li><a href="/health">/health</a> - Health check</li>
                    <li><a href="/trigger?action=high_cpu">/trigger?action=high_cpu</a> - Trigger high CPU</li>
                    <li><a href="/trigger?action=high_memory">/trigger?action=high_memory</a> - Trigger high memory</li>
                    <li><a href="/trigger?action=high_errors">/trigger?action=high_errors</a> - Trigger high errors</li>
                    <li><a href="/trigger?action=reset">/trigger?action=reset</a> - Reset metrics</li>
                </ul>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
            request_count += 1
            
        elif path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(generate_metrics().encode())
            request_count += 1
            
        elif path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = f'{{"status": "healthy", "timestamp": "{datetime.now().isoformat()}"}}'
            self.wfile.write(response.encode())
            request_count += 1
            
        elif path == '/trigger':
            action = query_params.get('action', [''])[0]
            
            if action == 'high_cpu':
                high_cpu_mode = True
                cpu_usage = 85.0
                message = "High CPU mode activated! CPU usage set to 85%"
            elif action == 'high_memory':
                high_memory_mode = True
                memory_usage = 95.0
                message = "High Memory mode activated! Memory usage set to 95%"
            elif action == 'high_errors':
                high_error_mode = True
                error_rate = 10.0
                error_count += 100
                message = "High Error Rate mode activated! Error rate set to 10%"
            elif action == 'reset':
                high_cpu_mode = False
                high_memory_mode = False
                high_error_mode = False
                cpu_usage = 50.0
                memory_usage = 50.0
                error_rate = 0.0
                message = "All metrics reset to normal values"
            else:
                message = f"Unknown action: {action}"
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = f"""
            <html>
            <head><title>Trigger Result</title></head>
            <body>
                <h1>{message}</h1>
                <p><a href="/">Back to main page</a></p>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
            request_count += 1
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    
    def log_message(self, format, *args):
        """Override to add timestamp to logs."""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

if __name__ == '__main__':
    PORT = 8080
    print(f"Starting Alert Trigger Demo App on port {PORT}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with socketserver.TCPServer(("", PORT), AlertTriggerHandler) as httpd:
        print(f"Server listening on port {PORT}")
        print("Endpoints available:")
        print("  - http://localhost:8080/ (main page)")
        print("  - http://localhost:8080/metrics (Prometheus metrics)")
        print("  - http://localhost:8080/health (health check)")
        print("  - http://localhost:8080/trigger?action=high_cpu (trigger high CPU)")
        print("  - http://localhost:8080/trigger?action=high_memory (trigger high memory)")
        print("  - http://localhost:8080/trigger?action=high_errors (trigger high errors)")
        print("  - http://localhost:8080/trigger?action=reset (reset metrics)")
        httpd.serve_forever()

