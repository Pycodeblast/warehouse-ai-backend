from fastapi import FastAPI

app = FastAPI(
    title="WarehouseAI Backend",
    description="Smart Inventory Management System API",
    version="1.0.0"
)


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