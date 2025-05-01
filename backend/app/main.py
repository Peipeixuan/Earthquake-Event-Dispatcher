
from typing import Union
from app.db import check_mysql_connection
from app.exporter import setup_exporter

from prometheus_client import make_asgi_app


from fastapi import FastAPI


app = FastAPI()


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
