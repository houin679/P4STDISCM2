from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

# For a simple scaffold we use SQLAlchemy synchronous engine.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Create database tables from models if they don't exist.

    For development this will create tables automatically using the models defined
    in `backend.app.models`. In production you should use Alembic migrations.
    """
    # Import models so they are registered with Base.metadata before creating tables
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
