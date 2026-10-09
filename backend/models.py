from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    college = Column(String, default="Engineering College")
    department = Column(String, nullable=False)
    year = Column(String, nullable=False)
    interests = Column(Text, default="")  # Comma-separated list of interests
    role = Column(String, default="student")  # "student" or "admin"

    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False)  # YYYY-MM-DD
    time = Column(String, nullable=False)  # e.g., 10:00 AM
    venue = Column(String, nullable=False)
    organizer = Column(String, nullable=False)
    max_participants = Column(Integer, default=100)
    registration_deadline = Column(String, nullable=False)
    image = Column(Text, default="")
    tags = Column(Text, default="")  # Additional tags for recommendation matching

    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    registration_date = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    status = Column(String, default="Registered")  # "Registered" or "Cancelled"

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
