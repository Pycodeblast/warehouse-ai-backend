from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from app.api.dashboard_routes import router as dashboard_router

from app.api.dashboard_routes import router as dashboard_router


app = FastAPI(
    title="WarehouseAI Backend",
    description="Smart Inventory Management System API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"
    ,"http://localhost:5174",
     "http://warehouse-ai-frontend.s3-website.ap-south-1.amazonaws.com",
       "http://warehouse-ai-frontend-staging.s3-website.ap-south-1.amazonaws.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(Exception, global_exception_handler)


app.include_router(auth_router)
app.include_router(dashboard_router)
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



