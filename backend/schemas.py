from pydantic import BaseModel, EmailStr
from typing import List, Optional

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    college: str
    department: str
    year: str
    interests: List[str]
    role: Optional[str] = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: str
    college: str
    department: str
    year: str
    interests: List[str]

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    college: str
    department: str
    year: str
    interests: List[str]
    role: str

    class Config:
        from_attributes = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Event Schemas
class EventBase(BaseModel):
    name: str
    description: str
    category: str
    date: str
    time: str
    venue: str
    organizer: str
    max_participants: int
    registration_deadline: str
    image: Optional[str] = ""
    tags: Optional[List[str]] = []

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    registered_count: int = 0
    available_seats: int = 0

    class Config:
        from_attributes = True

class RecommendedEventResponse(EventResponse):
    match_score: float
    match_percentage: int
    matching_interests: List[str]

# Registration Schemas
class RegistrationCreate(BaseModel):
    event_id: int

class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registration_date: str
    status: str
    event_name: str
    event_date: str
    event_time: str
    event_venue: str
    user_name: str
    user_email: str

    class Config:
        from_attributes = True

# Admin Dashboard Stats Schema
class DashboardStats(BaseModel):
    total_events: int
    total_students: int
    total_registrations: int
    upcoming_events: int
