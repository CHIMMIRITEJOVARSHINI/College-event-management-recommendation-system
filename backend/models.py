from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    college = Column(String(150), nullable=True)
    department = Column(String(100), nullable=True)
    year = Column(String(50), nullable=True)
    interests = Column(Text, nullable=True)  # Comma-separated or JSON string
    role = Column(String(20), default="student")  # 'student' or 'admin'

    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    date = Column(String(50), nullable=False)  # e.g., '2026-10-20' or '20 Oct 2026'
    time = Column(String(50), nullable=False)  # e.g., '10:00 AM'
    venue = Column(String(150), nullable=False)
    organizer = Column(String(150), nullable=False)
    max_participants = Column(Integer, default=100)
    registration_deadline = Column(String(50), nullable=True)
    image = Column(String(500), nullable=True)

    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_registration"),
    )

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
