from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# Create engine with pool_pre_ping to check connection viability
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# Set up local session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Standard SQLAlchemy 2.0 Base class
class Base(DeclarativeBase):
    pass

# DB dependency for FastAPI routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
