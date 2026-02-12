from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from app.config import get_settings

settings = get_settings()

# Configure connection based on database type
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,  # Verify connections before using
}

if settings.database_url.startswith("sqlite"):
    # SQLite needs special connect_args for multi-threading
    connect_args = {"check_same_thread": False}
    engine_kwargs["poolclass"] = NullPool  # SQLite doesn't support connection pooling
elif settings.database_url.startswith("postgresql"):
    # PostgreSQL production settings with connection pooling
    engine_kwargs["poolclass"] = QueuePool
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
