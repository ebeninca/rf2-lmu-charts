import multiprocessing

# Bind to all interfaces on port 7860
bind = '0.0.0.0:7860'

# Workers
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = 'sync'
worker_connections = 100
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5

# Limites de request
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Security
forwarded_allow_ips = '*'
proxy_protocol = False
proxy_allow_ips = '*'

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'warning'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
