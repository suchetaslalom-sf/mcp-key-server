import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, engine
import models
from routers import auth, keys, npm
from config import settings

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MCP Key Server",
    description="A service for storing API keys and providing npm installations",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(keys.router, prefix="/api/keys", tags=["API Keys"])
app.include_router(npm.router, prefix="/api/npm", tags=["NPM Packages"])


@app.get("/")
def read_root():
    return {"message": "Welcome to MCP Key Server"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
