
import logging
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)


engine = create_engine(
    str(settings.DATABASE_URL),
    echo=False,  
    poolclass=QueuePool,
    pool_size=10, 
    max_overflow=20,  
    pool_pre_ping=True, 
    pool_recycle=3600,  
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)



# DATABASE LIFECYCLE EVENTS


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    SQLite-specific pragma settings.
    Only applies if using SQLite (development).
    """
    if "sqlite" in str(settings.DATABASE_URL):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    SQLite-specific pragma settings.
    Only applies if using SQLite (development).
    """
    if "sqlite" in str(settings.DATABASE_URL):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides database session.
    
    Usage:
        @app.get("/")
        async def get_something(db: Session = Depends(get_db)):
            # Use db session
            result = db.query(...).all()
            return result
    
    Yields:
        SQLAlchemy Session object
    """
    db = SessionLocal()
    try:
        logger.debug("📖 Creating new database session")
        yield db
    except Exception as e:
        logger.error(f"❌ Database session error: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("📖 Database session closed")


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """
    Initialize database - create all tables.
    
    Should be called on application startup.
    
    Usage:
        from app.core.database import init_db
        from app.models.history import Base
        
        # Import all models to register them with Base
        from app.models import history
        
        init_db()
    """
    try:
        logger.info("🔧 Initializing database...")
        # Import models here to ensure they're registered
        from app.models.history import Base
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
        raise


def close_db():
    """
    Close database connection.
    
    Should be called on application shutdown.
    """
    try:
        logger.info("🔌 Closing database engine...")
        engine.dispose()
        logger.info("✅ Database engine closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}", exc_info=True)
        raise
