"""Database engine and session factory configuration."""

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from app.config.env_config import DATABASE_PATH

DATABASE_URL = URL.create(
    drivername="sqlite",
    database=str(DATABASE_PATH),
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
