# config.py
"""Application configuration using Pydantic."""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables or defaults."""
    
    # FastAPI application settings
    app_name: str = "Financial Research Agent"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost", "http://localhost:3000", "https://finance-ai-frontend-sigma.vercel.app"]
    debug: bool = True
    
    # Database settings
    postgres_url: str = "postgresql://postgres:password@localhost:5432/financial_db"
    redis_url: str = "redis://localhost:6379"
    neo4j_uri: Optional[str] = None
    neo4j_user: Optional[str] = None
    neo4j_password: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: Optional[str] = "financial-research-index"
    
    # API keys
    google_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    
    # MCP server settings
    mcp_servers: List[str] = [
        "ws://0.0.0.0:8081",
        "ws://0.0.0.0:8082",
        "ws://0.0.0.0:8083",
        "ws://0.0.0.0:8084"
    ]
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8080
    
    # Environment settings
    environment: str = "development"
    secret_key: str = "your-secret-key"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()