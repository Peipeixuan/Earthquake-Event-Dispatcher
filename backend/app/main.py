
from typing import Union
from app.db import check_mysql_connection
from app.exporter import setup_exporter

from prometheus_client import make_asgi_app


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import earthquake, settings


app = FastAPI()

app.include_router(earthquake.router)
app.include_router(settings.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    db_ok = check_mysql_connection()
    return {"mysql_connected": db_ok}


setup_exporter()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
