from fastapi import FastAPI
from app.database.base import create_db_tables
from app.api.auth_routes import router as auth_router
from app.api.protected_routes import router as protected_router
from app.api.product_routes import router as product_router
from app.api.user_routes import router as user_router
from app.api.inventory_routes import router as inventory_router
from app.api.file_routes import router as file_router
from app.api.ai_routes import router as ai_router
from app.api.health_routes import router as health_router
from app.core.exceptions import global_exception_handler



app = FastAPI(
    title="WarehouseAI Backend",
    description="Smart Inventory Management System API",
    version="1.0.0"
)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(auth_router)

app.include_router(protected_router, prefix="/user")
app.include_router(user_router)
app.include_router(product_router)
app.include_router(inventory_router)
app.include_router(file_router)
app.include_router(ai_router)
app.include_router(health_router)

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