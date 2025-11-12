"""Booking Service Database Models and Configuration."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Config


Base = declarative_base()


class Booking(Base):
    """Booking database model."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    hotel_id = Column(Integer, nullable=False)
    room_id = Column(Integer, nullable=False)
    check_in = Column(String, nullable=False)
    check_out = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Get database session.

    :yield: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
