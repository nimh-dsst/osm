from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import metrics

app = FastAPI(title="OpenSciMetrics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router, prefix="/api")