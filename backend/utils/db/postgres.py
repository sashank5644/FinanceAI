"""PostgreSQL database connection and session management."""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)

# Global variables
engine: Optional[any] = None
SessionLocal: Optional[sessionmaker] = None
Base = declarative_base()


def get_engine():
    """Get or create the engine."""
    global engine
    
    if engine is None:
        if not settings.postgres_url:
            raise ValueError("PostgreSQL URL not configured")
        
        engine = create_engine(
            settings.postgres_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
    
    return engine


def init_postgres():
    """Initialize PostgreSQL connection."""
    global engine, SessionLocal
    
    if not settings.postgres_url:
        logger.warning("PostgreSQL URL not configured")
        return
    
    try:
        # Get or create engine
        engine = get_engine()
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        
        logger.info("PostgreSQL connection established")
        return engine
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    if SessionLocal is None:
        init_postgres()
    
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables."""
    # Import models to register them
    from models import postgres_models
    
    # Get engine
    eng = get_engine()
    
    # Create tables
    Base.metadata.create_all(bind=eng)
    logger.info("PostgreSQL tables created")