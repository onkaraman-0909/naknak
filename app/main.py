from fastapi import FastAPI
from .config import settings
from .api.auth import router as auth_router

app = FastAPI(title="Nakliye Platformu API", version="0.1.0")

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": app.title,
        "version": app.version,
        "env": settings.ENV,
    }

# Routers
app.include_router(auth_router)
