#!/usr/bin/env python3
"""
Demo application for ServiceMonitor demonstration.
This app exposes /, /health, and /metrics endpoints.
On startup, it sleeps for 60 seconds before becoming ready.
"""

import time
import http.server
import socketserver
import threading
from datetime import datetime
from urllib.parse import urlparse

# Global state
start_time = time.time()
is_ready = False
ready_time = None

def wait_for_ready():
    """Sleep for 60 seconds, then mark as ready."""
    global is_ready, ready_time
    print("I'm sleeping for 60 seconds...")
    time.sleep(60)
    is_ready = True
    ready_time = time.time()
    print(f"I'm ready now! (after {ready_time - start_time:.2f} seconds)")

# Start the readiness thread
readiness_thread = threading.Thread(target=wait_for_ready, daemon=True)
readiness_thread.start()

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if not is_ready:
                response = """
                <html>
                <head><title>Demo App - Not Ready</title></head>
                <body>
                    <h1>I'm not started yet</h1>
                    <p>Application is still initializing. Please wait...</p>
                    <p>Started: {}</p>
                    <p>Status: Initializing (sleeping for 60 seconds)</p>
                </body>
                </html>
                """.format(datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'))
            else:
                uptime = time.time() - ready_time
                response = """
                <html>
                <head><title>Demo App - Ready</title></head>
                <body>
                    <h1>Demo Application</h1>
                    <p>Application is ready and running!</p>
                    <p>Started: {}</p>
                    <p>Ready at: {}</p>
                    <p>Uptime: {:.2f} seconds</p>
                    <hr>
                    <h2>Endpoints:</h2>
                    <ul>
                        <li><a href="/">/</a> - This page</li>
                        <li><a href="/health">/health</a> - Health check endpoint</li>
                        <li><a href="/metrics">/metrics</a> - Prometheus metrics</li>
                    </ul>
                </body>
                </html>
                """.format(
                    datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.fromtimestamp(ready_time).strftime('%Y-%m-%d %H:%M:%S'),
                    uptime
                )
            self.wfile.write(response.encode())
            
        elif path == '/health':
            self.send_response(200 if is_ready else 503)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = "ready" if is_ready else "not_ready"
            response = f'{{"status": "{status}", "timestamp": "{datetime.now().isoformat()}"}}'
            self.wfile.write(response.encode())
            
        elif path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            uptime = time.time() - start_time
            metrics = f"""# HELP demo_app_info Application information
# TYPE demo_app_info gauge
demo_app_info{{version="1.0.0"}} 1

# HELP demo_app_uptime_seconds Application uptime in seconds
# TYPE demo_app_uptime_seconds gauge
demo_app_uptime_seconds {uptime:.2f}

# HELP demo_app_ready Application readiness status (1=ready, 0=not ready)
# TYPE demo_app_ready gauge
demo_app_ready {1 if is_ready else 0}

# HELP demo_app_http_requests_total Total number of HTTP requests
# TYPE demo_app_http_requests_total counter
demo_app_http_requests_total{{method="GET",endpoint="{path}"}} 1
"""
            self.wfile.write(metrics.encode())
            
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
    print(f"Starting demo app on port {PORT}")
    print(f"Start time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    
    with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
        print(f"Server listening on port {PORT}")
        print("Endpoints available:")
        print("  - http://localhost:8080/ (main page)")
        print("  - http://localhost:8080/health (health check)")
        print("  - http://localhost:8080/metrics (Prometheus metrics)")
        httpd.serve_forever()

