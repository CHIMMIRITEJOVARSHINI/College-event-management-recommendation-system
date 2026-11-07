from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    college: Optional[str] = "College of Engineering"
    department: Optional[str] = "Computer Science"
    year: Optional[str] = "3rd Year"
    interests: Optional[List[str]] = []
    role: Optional[str] = "student"

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    college: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    interests: Optional[str] = None
    role: str

    class Config:
        from_attributes = True

# --- Event Schemas ---
class EventBase(BaseModel):
    name: str
    description: Optional[str] = ""
    category: str
    date: str
    time: str
    venue: str
    organizer: str
    max_participants: Optional[int] = 100
    registration_deadline: Optional[str] = ""
    image: Optional[str] = ""

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    venue: Optional[str] = None
    organizer: Optional[str] = None
    max_participants: Optional[int] = None
    registration_deadline: Optional[str] = None
    image: Optional[str] = None

class EventResponse(EventBase):
    id: int
    registered_count: Optional[int] = 0

    class Config:
        from_attributes = True

# --- Registration Schemas ---
class RegistrationCreate(BaseModel):
    user_id: int
    event_id: int

class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registration_date: datetime
    event_name: Optional[str] = None
    event_date: Optional[str] = None
    event_venue: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True

# --- Recommendation Schemas ---
class RecommendedEvent(BaseModel):
    event: EventResponse
    match_score: float
    matching_interests: List[str]
    match_percentage: int

# --- Admin Schemas ---
class AdminStats(BaseModel):
    total_events: int
    total_students: int
    total_registrations: int
    upcoming_events: int
