#!/usr/bin/env python3
import os
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from logger import setup_logger

logger = setup_logger(__name__)

HEALTH_PORT = int(os.getenv("HEALTH_PORT", 8080))
if not HEALTH_PORT:
    logger.error("Set HEALTH_PORT to a valid port")
    sys.exit(1)
else:
    logger.info(f"Using HEALTH_PORT: {HEALTH_PORT}")

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": "axelar-wallet-monitor-health",
                "wallet": os.getenv("AXELAR_WALLET", "not-configured"),
                "version": "1.0.0"
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Health check service is running. Use /health endpoint.")
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": "Not found", "path": self.path}
            self.wfile.write(json.dumps(error_response).encode())
    
    def log_message(self, format, *args):
        # Override to use our logger instead of stderr
        logger.info(f"Health check: {format % args}")

def start_health_check_service():
    # Prefer Cloud Run's PORT, fallback to HEALTH_PORT, default 8080
    server = HTTPServer(('0.0.0.0', HEALTH_PORT), HealthHandler)
    logger.info(f"Health check service starting on port {HEALTH_PORT}")
    logger.info(f"Monitoring wallet: {os.getenv('AXELAR_WALLET', 'not-configured')}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Health check service shutting down...")
        server.shutdown()
