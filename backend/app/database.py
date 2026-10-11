import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Default: a SQLite file inside the backend folder (used on your laptop).
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_URL = f"sqlite:///{BASE_DIR / 'smart_health_card.db'}"

# In the cloud we set DATABASE_URL to point at a Postgres database instead.
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_URL)

# Cloud providers often give "postgres://..." or "postgresql://...".
# Tell SQLAlchemy to use the psycopg driver for those.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# This setting is only needed for SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# The engine is the actual connection to the database.
# pool_pre_ping checks a connection is alive before using it (cloud databases can drop idle ones).
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

# A session is a short "conversation" with the database (read, add, save).
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All our database table classes inherit from this."""
    pass


def get_db():
    """Give each API request its own session, and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()