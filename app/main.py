from fastapi import FastAPI
from app.database.base import create_db_tables
from app.api.auth_routes import router as auth_router
from app.api.protected_routes import router as protected_router




app = FastAPI(
    title="WarehouseAI Backend",
    description="Smart Inventory Management System API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(protected_router, prefix="/user")

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