from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from app.config import get_settings

settings = get_settings()

# Configure connection based on database type
connect_args = {}
poolclass = QueuePool

if settings.database_url.startswith("sqlite"):
    # SQLite needs special connect_args for multi-threading
    connect_args = {"check_same_thread": False}
    poolclass = NullPool  # SQLite doesn't support connection pooling well
elif settings.database_url.startswith("postgresql"):
    # PostgreSQL production settings
    # Use connection pooling for better performance
    poolclass = QueuePool

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    poolclass=poolclass,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5 if not settings.database_url.startswith("sqlite") else 0,
    max_overflow=10 if not settings.database_url.startswith("sqlite") else 0,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
