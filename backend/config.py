import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "MCP Key Server"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mcp_key_db")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # NPM settings
    NPM_REGISTRY: str = os.getenv("NPM_REGISTRY", "https://registry.npmjs.org")
    NPM_CACHE_DIR: str = os.getenv("NPM_CACHE_DIR", "./npm-cache")
    
    # MCP settings
    MCP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"


settings = Settings()
