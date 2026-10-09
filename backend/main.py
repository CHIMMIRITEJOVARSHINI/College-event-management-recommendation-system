from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database import engine, get_db, Base, SessionLocal
from backend.models import User, Event, Registration
from backend.schemas import (
    UserCreate, UserLogin, UserUpdate, UserResponse, Token,
    EventCreate, EventUpdate, EventResponse, RecommendedEventResponse,
    RegistrationCreate, RegistrationResponse, DashboardStats
)
from backend.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_user, require_admin
)
from backend.recommendation import recommend_events

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="College Event Management & Recommendation System API",
    description="Backend API for discovering, registering, managing and recommending college events.",
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


def seed_initial_data(db: Session):
    """Seeds sample users and events if the database is empty."""
    # Seed Admin
    admin_user = db.query(User).filter(User.email == "admin@college.edu").first()
    if not admin_user:
        admin_user = User(
            name="College Event Admin",
            email="admin@college.edu",
            password=hash_password("admin123"),
            college="State Institute of Technology",
            department="Event Operations",
            year="Faculty / Admin",
            interests="Technical,Hackathons,Workshops,Seminars,Cultural",
            role="admin"
        )
        db.add(admin_user)

    # Seed Sample Student
    student_user = db.query(User).filter(User.email == "tejo@gmail.com").first()
    if not student_user:
        student_user = User(
            name="Tejo",
            email="tejo@gmail.com",
            password=hash_password("student123"),
            college="State Institute of Technology",
            department="CSE",
            year="3rd Year",
            interests="AI & Machine Learning,Coding,Hackathons,Web Development",
            role="student"
        )
        db.add(student_user)

    db.commit()

    # Seed Events if empty
    if db.query(Event).count() == 0:
        sample_events = [
            Event(
                name="AI Innovation Hackathon",
                description="24-hour hackathon to build intelligent solutions using Generative AI, Computer Vision, and ML models. Win cash prizes and internship opportunities!",
                category="Hackathon",
                date="2026-10-20",
                time="10:00 AM",
                venue="Computer Lab 3 & Auditorium",
                organizer="CSE Department",
                max_participants=100,
                registration_deadline="2026-10-18",
                image="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&auto=format&fit=crop",
                tags="AI & Machine Learning,Coding,Hackathons,Python"
            ),
            Event(
                name="Machine Learning & Deep Learning Seminar",
                description="Industry leaders from top AI labs discuss recent breakthroughs in Neural Networks, Transformers, and scalable ML infrastructure.",
                category="Seminars",
                date="2026-10-25",
                time="02:00 PM",
                venue="Main Seminar Hall B",
                organizer="AI Student Club",
                max_participants=150,
                registration_deadline="2026-10-24",
                image="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop",
                tags="AI & Machine Learning,Seminars,Technical,Data Science"
            ),
            Event(
                name="Full Stack Web Development Workshop",
                description="Hands-on workshop covering React, FastAPI, Docker, and Cloud Deployment. Build and deploy a complete web application in one day.",
                category="Workshops",
                date="2026-11-02",
                time="09:30 AM",
                venue="Web Tech Lab 102",
                organizer="WebDev Society",
                max_participants=60,
                registration_deadline="2026-11-01",
                image="https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=800&auto=format&fit=crop",
                tags="Web Development,Coding,Workshops,Technical,React,FastAPI"
            ),
            Event(
                name="Annual Inter-College Cultural Fest - Rhythm 2026",
                description="Grand annual cultural event showcasing live music concerts, group dance battles, fashion shows, and dramatic plays.",
                category="Cultural",
                date="2026-11-15",
                time="05:00 PM",
                venue="Open Air Theatre",
                organizer="Cultural Committee",
                max_participants=500,
                registration_deadline="2026-11-12",
                image="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop",
                tags="Cultural,Music,Dance,Talent"
            ),
            Event(
                name="College Premier League Football Tournament",
                description="Inter-department 7-a-side football championship. Form your team and compete for the prestigious College Champions Trophy.",
                category="Sports",
                date="2026-11-08",
                time="08:00 AM",
                venue="Main Sports Complex Field",
                organizer="Department of Physical Education",
                max_participants=120,
                registration_deadline="2026-11-05",
                image="https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800&auto=format&fit=crop",
                tags="Sports,Football,Tournament,Fitness"
            ),
            Event(
                name="Entrepreneurship & Startup Pitch Fest",
                description="Pitch your innovative startup ideas to angel investors and venture capitalists. Win seed funding up to $10,000!",
                category="Entrepreneurship",
                date="2026-11-20",
                time="11:00 AM",
                venue="Incubation Center Conference Room",
                organizer="E-Cell (Entrepreneurship Cell)",
                max_participants=80,
                registration_deadline="2026-11-18",
                image="https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&auto=format&fit=crop",
                tags="Entrepreneurship,Startup,Pitch,Business,Seminars"
            )
        ]
        db.add_all(sample_events)
        db.commit()


@app.on_event("startup")
def startup_db():
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()


# --- AUTH ENDPOINTS ---

@app.post("/api/auth/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    interests_str = ",".join(user_data.interests) if user_data.interests else ""
    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        college=user_data.college,
        department=user_data.department,
        year=user_data.year,
        interests=interests_str,
        role=user_data.role or "student"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "role": user.role})
    
    user_resp = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        college=user.college,
        department=user.department,
        year=user.year,
        interests=[i.strip() for i in user.interests.split(",") if i.strip()],
        role=user.role
    )
    return Token(access_token=token, token_type="bearer", user=user_resp)


@app.post("/api/auth/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token({"sub": user.email, "role": user.role})
    
    user_resp = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        college=user.college,
        department=user.department,
        year=user.year,
        interests=[i.strip() for i in user.interests.split(",") if i.strip()] if user.interests else [],
        role=user.role
    )
    return Token(access_token=token, token_type="bearer", user=user_resp)


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(user: User = Depends(require_user)):
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        college=user.college,
        department=user.department,
        year=user.year,
        interests=[i.strip() for i in user.interests.split(",") if i.strip()] if user.interests else [],
        role=user.role
    )


@app.put("/api/users/profile", response_model=UserResponse)
def update_profile(profile_data: UserUpdate, user: User = Depends(require_user), db: Session = Depends(get_db)):
    user.name = profile_data.name
    user.college = profile_data.college
    user.department = profile_data.department
    user.year = profile_data.year
    user.interests = ",".join(profile_data.interests) if profile_data.interests else ""
    
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        college=user.college,
        department=user.department,
        year=user.year,
        interests=[i.strip() for i in user.interests.split(",") if i.strip()] if user.interests else [],
        role=user.role
    )


# --- EVENT ENDPOINTS ---

def format_event_response(event: Event, db: Session) -> EventResponse:
    reg_count = db.query(Registration).filter(
        Registration.event_id == event.id, Registration.status == "Registered"
    ).count()
    available_seats = max(0, event.max_participants - reg_count)
    tags_list = [t.strip() for t in event.tags.split(",") if t.strip()] if event.tags else []

    return EventResponse(
        id=event.id,
        name=event.name,
        description=event.description,
        category=event.category,
        date=event.date,
        time=event.time,
        venue=event.venue,
        organizer=event.organizer,
        max_participants=event.max_participants,
        registration_deadline=event.registration_deadline,
        image=event.image or "",
        tags=tags_list,
        registered_count=reg_count,
        available_seats=available_seats
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
        search_term = f"%{search}%"
        query = query.filter(
            (Event.name.ilike(search_term)) |
            (Event.description.ilike(search_term)) |
            (Event.tags.ilike(search_term)) |
            (Event.category.ilike(search_term))
        )
    if category and category != "All":
        query = query.filter(Event.category == category)
    if department and department != "All":
        query = query.filter(Event.organizer.ilike(f"%{department}%"))
    if venue and venue != "All":
        query = query.filter(Event.venue.ilike(f"%{venue}%"))

    events = query.order_by(Event.date.asc()).all()
    return [format_event_response(ev, db) for ev in events]


@app.get("/api/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return format_event_response(event, db)


@app.post("/api/events", response_model=EventResponse)
def create_event(event_data: EventCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    tags_str = ",".join(event_data.tags) if event_data.tags else ""
    event = Event(
        name=event_data.name,
        description=event_data.description,
        category=event_data.category,
        date=event_data.date,
        time=event_data.time,
        venue=event_data.venue,
        organizer=event_data.organizer,
        max_participants=event_data.max_participants,
        registration_deadline=event_data.registration_deadline,
        image=event_data.image or "",
        tags=tags_str
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return format_event_response(event, db)


@app.put("/api/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_data: EventUpdate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    event.name = event_data.name
    event.description = event_data.description
    event.category = event_data.category
    event.date = event_data.date
    event.time = event_data.time
    event.venue = event_data.venue
    event.organizer = event_data.organizer
    event.max_participants = event_data.max_participants
    event.registration_deadline = event_data.registration_deadline
    event.image = event_data.image or ""
    event.tags = ",".join(event_data.tags) if event_data.tags else ""

    db.commit()
    db.refresh(event)
    return format_event_response(event, db)


@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully."}


# --- REGISTRATION ENDPOINTS ---

@app.post("/api/events/{event_id}/register", response_model=RegistrationResponse)
def register_for_event(event_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    # Check capacity
    active_regs = db.query(Registration).filter(
        Registration.event_id == event_id, Registration.status == "Registered"
    ).count()
    if active_regs >= event.max_participants:
        raise HTTPException(status_code=400, detail="Event is already full.")

    # Check existing active registration
    existing = db.query(Registration).filter(
        Registration.user_id == user.id,
        Registration.event_id == event_id,
        Registration.status == "Registered"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You are already registered for this event.")

    reg = Registration(
        user_id=user.id,
        event_id=event_id,
        registration_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status="Registered"
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)

    return RegistrationResponse(
        id=reg.id,
        user_id=reg.user_id,
        event_id=reg.event_id,
        registration_date=reg.registration_date,
        status=reg.status,
        event_name=event.name,
        event_date=event.date,
        event_time=event.time,
        event_venue=event.venue,
        user_name=user.name,
        user_email=user.email
    )


@app.post("/api/events/{event_id}/cancel")
def cancel_registration(event_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    reg = db.query(Registration).filter(
        Registration.user_id == user.id,
        Registration.event_id == event_id,
        Registration.status == "Registered"
    ).first()
    if not reg:
        raise HTTPException(status_code=404, detail="No active registration found for this event.")

    reg.status = "Cancelled"
    db.commit()
    return {"message": "Registration cancelled successfully."}


@app.get("/api/registrations/my", response_model=List[RegistrationResponse])
def get_my_registrations(user: User = Depends(require_user), db: Session = Depends(get_db)):
    regs = db.query(Registration).filter(
        Registration.user_id == user.id,
        Registration.status == "Registered"
    ).order_by(Registration.id.desc()).all()

    response = []
    for r in regs:
        ev = r.event
        response.append(
            RegistrationResponse(
                id=r.id,
                user_id=r.user_id,
                event_id=r.event_id,
                registration_date=r.registration_date,
                status=r.status,
                event_name=ev.name if ev else "Unknown Event",
                event_date=ev.date if ev else "",
                event_time=ev.time if ev else "",
                event_venue=ev.venue if ev else "",
                user_name=user.name,
                user_email=user.email
            )
        )
    return response


@app.get("/api/registrations/all", response_model=List[RegistrationResponse])
def get_all_registrations(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    regs = db.query(Registration).order_by(Registration.id.desc()).all()
    response = []
    for r in regs:
        ev = r.event
        u = r.user
        response.append(
            RegistrationResponse(
                id=r.id,
                user_id=r.user_id,
                event_id=r.event_id,
                registration_date=r.registration_date,
                status=r.status,
                event_name=ev.name if ev else "Unknown Event",
                event_date=ev.date if ev else "",
                event_time=ev.time if ev else "",
                event_venue=ev.venue if ev else "",
                user_name=u.name if u else "Unknown User",
                user_email=u.email if u else ""
            )
        )
    return response


# --- RECOMMENDATIONS ENDPOINT ---

@app.get("/api/recommendations", response_model=List[RecommendedEventResponse])
def get_recommendations(user: User = Depends(require_user), db: Session = Depends(get_db)):
    student_interests = [i.strip() for i in user.interests.split(",") if i.strip()] if user.interests else []
    all_events = db.query(Event).all()

    ranked = recommend_events(student_interests, all_events)
    
    response = []
    for item in ranked:
        ev = item["event"]
        ev_resp = format_event_response(ev, db)
        response.append(
            RecommendedEventResponse(
                **ev_resp.dict(),
                match_score=item["match_score"],
                match_percentage=item["match_percentage"],
                matching_interests=item["matching_interests"]
            )
        )

    return response


# --- ADMIN STATS ENDPOINT ---

@app.get("/api/admin/stats", response_model=DashboardStats)
def get_admin_stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_events = db.query(Event).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_registrations = db.query(Registration).filter(Registration.status == "Registered").count()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    upcoming_events = db.query(Event).filter(Event.date >= today_str).count()

    return DashboardStats(
        total_events=total_events,
        total_students=total_students,
        total_registrations=total_registrations,
        upcoming_events=upcoming_events
    )
