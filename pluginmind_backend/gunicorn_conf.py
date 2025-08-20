"""
Gunicorn configuration for production deployment.

Production-ready settings with environment-driven defaults for
scalability, reliability, and performance.
"""

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Restart workers gracefully
preload_app = True

# Timeout settings (env-driven)
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "300"))              # was 30
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))            # was 2
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "60"))  # was 10

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.environ.get("LOG_LEVEL", "info").lower()

# Include request ID from header injected by middleware
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" req_id=%({x-request-id}i)s'

# Process naming
proc_name = "pluginmind-backend"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Reload on code changes (only for development - should not be used in production)
reload = False