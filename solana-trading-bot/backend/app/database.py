from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def get_session():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session
