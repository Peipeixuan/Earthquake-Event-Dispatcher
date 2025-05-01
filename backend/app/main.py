from typing import Union
from app.db import check_mysql_connection

from fastapi import FastAPI
from app.routers import earthquake, settings

app = FastAPI()

app.include_router(earthquake.router)
app.include_router(settings.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    db_ok = check_mysql_connection()
    return {"mysql_connected": db_ok}