from fastapi import FastAPI
from app.database.base import create_db_tables

app = FastAPI(
    title="WarehouseAI Backend",
    description="Smart Inventory Management System API",
    version="1.0.0"
)

@app.on_event("startup")
def startup():
    create_db_tables()


@app.get("/")
def root():
    return {
        "message": "Welcome to WarehouseAI Backend"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }