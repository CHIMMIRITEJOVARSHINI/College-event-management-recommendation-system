import os
import json
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import engine, Base, get_db
from .models import User, Event, Registration
from .schemas import (
    UserRegister, UserLogin, UserResponse,
    EventCreate, EventUpdate, EventResponse,
    RegistrationCreate, RegistrationResponse,
    RecommendedEvent, AdminStats
)
from .auth import hash_password, verify_password
from .recommendation import get_recommendations_for_user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="College Event Management & Recommendation System API",
    description="REST API for campus events, student registrations, and content-based recommendations",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Database Seeder (Demo Data)
# ==========================================
def seed_initial_data(db: Session):
    """Seed sample users and events if database is newly initialized."""
    if db.query(User).count() == 0:
        # Create default Admin
        admin_user = User(
            name="College Admin",
            email="admin@college.edu",
            password=hash_password("admin123"),
            college="National Institute of Technology",
            department="Administration",
            year="Faculty / Staff",
            interests="Seminars, Workshops, Entrepreneurship",
            role="admin"
        )
        db.add(admin_user)

        # Create demo Student Tejo
        student_user = User(
            name="Tejo",
            email="tejo@gmail.com",
            password=hash_password("student123"),
            college="National Institute of Technology",
            department="CSE",
            year="3rd Year",
            interests="AI & Machine Learning, Coding, Hackathons",
            role="student"
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)

        # Sample college events
        sample_events = [
            Event(
                name="AI Innovation Hackathon",
                description="Join the 24-hour hackathon where student teams develop cutting-edge artificial intelligence, machine learning agents, and deep learning apps with mentorship from tech leaders.",
                category="Hackathon",
                date="2026-10-20",
                time="10:00 AM",
                venue="Computer Lab 3 & 4",
                organizer="CSE Department",
                max_participants=100,
                registration_deadline="2026-10-18",
                image="https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=700&q=80"
            ),
            Event(
                name="Machine Learning Seminar & Hands-on Lab",
                description="An intensive seminar covering generative AI architectures, neural networks, and model fine-tuning with live practical demos in Google Colab.",
                category="Seminars",
                date="2026-10-25",
                time="02:00 PM",
                venue="Auditorium A",
                organizer="AI & Data Science Club",
                max_participants=150,
                registration_deadline="2026-10-24",
                image="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=700&q=80"
            ),
            Event(
                name="Modern Web Development Workshop",
                description="Hands-on full-stack development workshop covering modern Python backend frameworks, reactive components, responsive UI design, and cloud deployments.",
                category="Workshops",
                date="2026-11-02",
                time="09:30 AM",
                venue="Tech Seminar Hall 2",
                organizer="Web Development Society",
                max_participants=80,
                registration_deadline="2026-11-01",
                image="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=700&q=80"
            ),
            Event(
                name="Inter-Department Football Tournament",
                description="Annual college sports tournament. Gather your department teams to compete for the Chancellor's Championship Trophy. Refreshments provided.",
                category="Sports",
                date="2026-11-08",
                time="08:00 AM",
                venue="College Sports Ground",
                organizer="Physical Education Department",
                max_participants=160,
                registration_deadline="2026-11-05",
                image="https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=700&q=80"
            ),
            Event(
                name="Rhythm & Harmony - Cultural Music & Dance Fest",
                description="Experience an evening of energetic live band battles, classical dances, contemporary group performances, and cultural art exhibitions.",
                category="Cultural",
                date="2026-11-15",
                time="05:30 PM",
                venue="Open Air Amphitheatre",
                organizer="Fine Arts & Cultural Club",
                max_participants=300,
                registration_deadline="2026-11-13",
                image="https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=700&q=80"
            ),
            Event(
                name="Campus Startup Pitch & Entrepreneurship Summit",
                description="Have an innovative idea? Present your pitch deck to venture capitalists and startup founders. Seed funding grants available for top 3 teams.",
                category="Entrepreneurship",
                date="2026-11-20",
                time="11:00 AM",
                venue="Incubation Center Hall",
                organizer="E-Cell (Entrepreneurship Cell)",
                max_participants=75,
                registration_deadline="2026-11-18",
                image="https://images.unsplash.com/photo-1559136555-9303baea8ebd?auto=format&fit=crop&w=700&q=80"
            ),
            Event(
                name="National Level Coding Battle 2026",
                description="Fast-paced algorithmic coding competition on data structures, algorithmic puzzles, dynamic programming, and speed debugging.",
                category="Coding",
                date="2026-11-26",
                time="04:00 PM",
                venue="Central Computing Center",
                organizer="Coding Club & ACM Chapter",
                max_participants=120,
                registration_deadline="2026-11-25",
                image="https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=700&q=80"
            )
        ]

        db.add_all(sample_events)
        db.commit()

        # Seed registration for demo student
        first_event = db.query(Event).filter(Event.name.like("%AI Innovation%")).first()
        if first_event and student_user:
            reg = Registration(user_id=student_user.id, event_id=first_event.id)
            db.add(reg)
            db.commit()

@app.on_event("startup")
def on_startup():
    db = next(get_db())
    try:
        seed_initial_data(db)
    finally:
        db.close()


# ==========================================
# Authentication Endpoints
# ==========================================
@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    interests_str = ", ".join(user_in.interests) if user_in.interests else ""
    user = User(
        name=user_in.name.strip(),
        email=user_in.email.strip().lower(),
        password=hash_password(user_in.password),
        college=user_in.college.strip() if user_in.college else "",
        department=user_in.department.strip() if user_in.department else "",
        year=user_in.year.strip() if user_in.year else "",
        interests=interests_str,
        role=user_in.role if user_in.role in ["student", "admin"] else "student"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/auth/login")
def login_user(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email.strip().lower()).first()
    if not user or not verify_password(creds.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "college": user.college,
            "department": user.department,
            "year": user.year,
            "interests": user.interests,
            "role": user.role
        }
    }


# ==========================================
# Event Endpoints
# ==========================================
def format_event_response(ev: Event, db: Session) -> EventResponse:
    reg_count = db.query(Registration).filter(Registration.event_id == ev.id).count()
    return EventResponse(
        id=ev.id,
        name=ev.name,
        description=ev.description or "",
        category=ev.category,
        date=ev.date,
        time=ev.time,
        venue=ev.venue,
        organizer=ev.organizer,
        max_participants=ev.max_participants,
        registration_deadline=ev.registration_deadline or "",
        image=ev.image or "",
        registered_count=reg_count
    )

@app.get("/api/events", response_model=List[EventResponse])
def get_events(
    search: Optional[str] = None,
    category: Optional[str] = None,
    department: Optional[str] = None,
    venue: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Event)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Event.name.ilike(search_pattern)) |
            (Event.description.ilike(search_pattern)) |
            (Event.category.ilike(search_pattern)) |
            (Event.organizer.ilike(search_pattern))
        )
    if category and category != "All":
        query = query.filter(Event.category == category)
    if department and department != "All":
        query = query.filter(Event.organizer.ilike(f"%{department}%"))
    if venue and venue != "All":
        query = query.filter(Event.venue.ilike(f"%{venue}%"))

    events = query.order_by(Event.id.desc()).all()
    return [format_event_response(ev, db) for ev in events]


@app.get("/api/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return format_event_response(event, db)


@app.post("/api/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    event = Event(
        name=event_in.name,
        description=event_in.description,
        category=event_in.category,
        date=event_in.date,
        time=event_in.time,
        venue=event_in.venue,
        organizer=event_in.organizer,
        max_participants=event_in.max_participants or 100,
        registration_deadline=event_in.registration_deadline or "",
        image=event_in.image or "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=700&q=80"
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return format_event_response(event, db)


@app.put("/api/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_in: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(event, field, val)

    db.commit()
    db.refresh(event)
    return format_event_response(event, db)


@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": f"Event '{event.name}' successfully deleted"}


# ==========================================
# Recommendation Endpoint
# ==========================================
@app.get("/api/recommendations", response_model=List[RecommendedEvent])
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_interests = [i.strip() for i in (user.interests or "").split(",") if i.strip()]
    events = db.query(Event).all()

    ranked = get_recommendations_for_user(user_interests, events)

    results = []
    for item in ranked:
        formatted_event = format_event_response(item["event"], db)
        results.append(RecommendedEvent(
            event=formatted_event,
            match_score=item["match_score"],
            matching_interests=item["matching_interests"],
            match_percentage=item["match_percentage"]
        ))
    return results


# ==========================================
# Registration Endpoints
# ==========================================
@app.post("/api/registrations", response_model=RegistrationResponse)
def register_for_event(reg_in: RegistrationCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == reg_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    event = db.query(Event).filter(Event.id == reg_in.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Prevent duplicate registrations
    existing = db.query(Registration).filter(
        Registration.user_id == reg_in.user_id,
        Registration.event_id == reg_in.event_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You are already registered for this event.")

    # Check maximum participants limit
    current_count = db.query(Registration).filter(Registration.event_id == reg_in.event_id).count()
    if event.max_participants and current_count >= event.max_participants:
        raise HTTPException(status_code=400, detail="Event is already full! Maximum capacity reached.")

    reg = Registration(user_id=reg_in.user_id, event_id=reg_in.event_id)
    db.add(reg)
    db.commit()
    db.refresh(reg)

    return RegistrationResponse(
        id=reg.id,
        user_id=reg.user_id,
        event_id=reg.event_id,
        registration_date=reg.registration_date,
        event_name=event.name,
        event_date=event.date,
        event_venue=event.venue,
        user_name=user.name,
        user_email=user.email
    )


@app.delete("/api/registrations/{event_id}")
def cancel_registration(event_id: int, user_id: int, db: Session = Depends(get_db)):
    reg = db.query(Registration).filter(
        Registration.user_id == user_id,
        Registration.event_id == event_id
    ).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration record not found.")

    db.delete(reg)
    db.commit()
    return {"message": "Registration cancelled successfully."}


@app.get("/api/registrations/my-events", response_model=List[dict])
def get_my_registered_events(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    registrations = db.query(Registration).filter(Registration.user_id == user_id).order_by(Registration.registration_date.desc()).all()

    my_events = []
    for r in registrations:
        ev = r.event
        if ev:
            my_events.append({
                "registration_id": r.id,
                "event_id": ev.id,
                "name": ev.name,
                "category": ev.category,
                "date": ev.date,
                "time": ev.time,
                "venue": ev.venue,
                "organizer": ev.organizer,
                "description": ev.description,
                "registration_date": r.registration_date.strftime("%d %b %Y, %I:%M %p"),
                "status": "Registered"
            })
    return my_events


# ==========================================
# Admin Endpoints
# ==========================================
@app.get("/api/admin/stats", response_model=AdminStats)
def get_admin_stats(db: Session = Depends(get_db)):
    total_events = db.query(Event).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_registrations = db.query(Registration).count()
    
    # Upcoming events count
    upcoming_events = total_events

    return AdminStats(
        total_events=total_events,
        total_students=total_students,
        total_registrations=total_registrations,
        upcoming_events=upcoming_events
    )


@app.get("/api/admin/registrations", response_model=List[dict])
def get_all_registrations_admin(db: Session = Depends(get_db)):
    registrations = db.query(Registration).order_by(Registration.id.desc()).all()
    results = []
    for r in registrations:
        results.append({
            "registration_id": r.id,
            "student_name": r.user.name if r.user else "Unknown",
            "student_email": r.user.email if r.user else "Unknown",
            "department": r.user.department if r.user else "N/A",
            "year": r.user.year if r.user else "N/A",
            "event_id": r.event_id,
            "event_name": r.event.name if r.event else "Deleted Event",
            "category": r.event.category if r.event else "N/A",
            "event_date": r.event.date if r.event else "N/A",
            "registration_date": r.registration_date.strftime("%d %b %Y, %I:%M %p")
        })
    return results
