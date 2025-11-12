"""Hotel Service Database Models and Configuration."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from config import Config


Base = declarative_base()


class Hotel(Base):
    """Hotel database model."""

    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String)
    amenities = Column(String)
    rating = Column(Float, default=0.0)

    rooms = relationship("Room", back_populates="hotel")


class Room(Base):
    """Room database model."""

    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_type = Column(String, nullable=False)
    price_per_night = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    available_count = Column(Integer, nullable=False)

    hotel = relationship("Hotel", back_populates="rooms")


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
