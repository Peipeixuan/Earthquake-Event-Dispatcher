from app.db import check_mysql_connection
from app.exporter import setup_exporter
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.report_service import auto_close_unprocessed_events

from prometheus_client import make_asgi_app

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.routers import earthquake, settings, report

api_router = APIRouter(prefix="/api")

app = FastAPI()
app.include_router(api_router)
app.include_router(earthquake.router)
app.include_router(settings.router)
app.include_router(report.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = BackgroundScheduler()
scheduler.add_job(auto_close_unprocessed_events, 'interval', minutes=1)
scheduler.start()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health",
    description="沒有綁到 nginx，要從 8000 Port 才能看")
def health_check():
    db_ok = check_mysql_connection()
    return {"mysql_connected": db_ok}

setup_exporter()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
