from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import metrics

app = FastAPI(title="OpenSciMetrics API")

# Regex for localhost, IPv4 loopback, and Docker CIDR block (e.g., 192.168.0.0/16)
allowed_origin_regex = r"^(http://)?(localhost|js_dashboard_backend|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}):\d+$"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router, prefix="/api")
