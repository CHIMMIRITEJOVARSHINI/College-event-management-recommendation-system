import streamlit as st
import requests
import json
import os
import sys
from datetime import datetime

# Add project root to sys.path for direct model imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import SessionLocal, engine, Base
from backend.models import User, Event, Registration
from backend.auth import verify_password, hash_password
from backend.recommendation import get_recommendations_for_user

# -------------------------------------------------------
# BOOT: Create all tables and seed demo data on startup.
# This runs ONCE when the Streamlit app first loads —
# critical on Streamlit Cloud where /tmp DB is empty.
# -------------------------------------------------------
@st.cache_resource(show_spinner="Setting up database...")
def _init_db():
    """Create tables and seed demo data idempotently."""
    # Import models so SQLAlchemy knows about them before create_all
    from backend.models import User, Event, Registration  # noqa: F401

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Only seed if DB is empty
        if db.query(User).count() == 0:
            admin = User(
                name="College Admin",
                email="admin@college.edu",
                password=hash_password("admin123"),
                college="National Institute of Technology",
                department="Administration",
                year="Faculty / Staff",
                interests="Seminars, Workshops, Entrepreneurship",
                role="admin"
            )
            tejo = User(
                name="Tejo",
                email="tejo@gmail.com",
                password=hash_password("student123"),
                college="National Institute of Technology",
                department="CSE",
                year="3rd Year",
                interests="AI & Machine Learning, Coding, Hackathons",
                role="student"
            )
            db.add_all([admin, tejo])
            db.commit()
            db.refresh(tejo)

            sample_events = [
                Event(
                    name="AI Innovation Hackathon",
                    description="24-hour national hackathon focused on AI agents, machine learning algorithms, and intelligent software solutions with mentorship from tech leaders.",
                    category="Hackathon", date="2026-11-20", time="10:00 AM",
                    venue="Computer Lab 3 & 4", organizer="CSE Department",
                    max_participants=100, registration_deadline="2026-11-18",
                    image="https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=700&q=80"
                ),
                Event(
                    name="Machine Learning Seminar & Hands-on Lab",
                    description="Intensive seminar covering generative AI, deep learning, computer vision and neural network optimization with live practical sessions.",
                    category="Seminars", date="2026-11-25", time="02:00 PM",
                    venue="Auditorium A", organizer="AI & Data Science Club",
                    max_participants=150, registration_deadline="2026-11-24",
                    image="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=700&q=80"
                ),
                Event(
                    name="Modern Web Development Workshop",
                    description="Hands-on full-stack development workshop covering Python backend frameworks, reactive UI design and cloud deployments.",
                    category="Workshops", date="2026-12-02", time="09:30 AM",
                    venue="Tech Seminar Hall 2", organizer="Web Development Society",
                    max_participants=80, registration_deadline="2026-12-01",
                    image="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=700&q=80"
                ),
                Event(
                    name="Inter-Department Football Tournament",
                    description="Annual college sports tournament for the Chancellor's Championship Trophy. Refreshments provided.",
                    category="Sports", date="2026-12-08", time="08:00 AM",
                    venue="College Sports Ground", organizer="Physical Education Department",
                    max_participants=160, registration_deadline="2026-12-05",
                    image="https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=700&q=80"
                ),
                Event(
                    name="Rhythm & Harmony — Cultural Music & Dance Fest",
                    description="Live band battles, classical dances, contemporary group performances, and cultural art exhibitions.",
                    category="Cultural", date="2026-12-15", time="05:30 PM",
                    venue="Open Air Amphitheatre", organizer="Fine Arts & Cultural Club",
                    max_participants=300, registration_deadline="2026-12-13",
                    image="https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=700&q=80"
                ),
                Event(
                    name="Campus Startup Pitch & Entrepreneurship Summit",
                    description="Present your pitch deck to venture capitalists and startup founders. Seed funding grants available for top 3 teams.",
                    category="Entrepreneurship", date="2026-12-20", time="11:00 AM",
                    venue="Incubation Center Hall", organizer="E-Cell",
                    max_participants=75, registration_deadline="2026-12-18",
                    image="https://images.unsplash.com/photo-1559136555-9303baea8ebd?auto=format&fit=crop&w=700&q=80"
                ),
                Event(
                    name="National Level Competitive Coding Battle",
                    description="Fast-paced algorithmic programming contest testing dynamic programming, graph algorithms and problem solving.",
                    category="Coding", date="2026-12-26", time="04:00 PM",
                    venue="Central Computing Center", organizer="Coding Club",
                    max_participants=120, registration_deadline="2026-12-25",
                    image="https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=700&q=80"
                ),
            ]
            db.add_all(sample_events)
            db.commit()

            # Pre-register Tejo for the first event
            db.refresh(tejo)
            first_event = db.query(Event).first()
            if first_event:
                db.add(Registration(user_id=tejo.id, event_id=first_event.id))
                db.commit()
    finally:
        db.close()

_init_db()   # Always call at module level so it runs before any page renders

# Set Page Config
st.set_page_config(
    page_title="Campus Events Recommendation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE = "http://127.0.0.1:8000/api"

# Available interest options
ALL_INTERESTS = [
    "Coding",
    "AI & Machine Learning",
    "Web Development",
    "Sports",
    "Cultural",
    "Music",
    "Dance",
    "Technical",
    "Workshops",
    "Seminars",
    "Hackathons",
    "Entrepreneurship"
]

CATEGORIES = [
    "All",
    "Hackathon",
    "Technical",
    "Coding",
    "Workshops",
    "Seminars",
    "Sports",
    "Cultural",
    "Entrepreneurship"
]

# Custom CSS for modern styling
st.markdown("""
<style>
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.2rem 2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 1.2rem;
    }
    
    .stat-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        color: #2563eb;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .event-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        background: #eff6ff;
        color: #1d4ed8;
        margin-right: 0.5rem;
    }
    
    .match-badge {
        display: inline-block;
        padding: 0.28rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    
    .match-badge-high {
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Home"
if "filter_category" not in st.session_state:
    st.session_state.filter_category = "All"
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# -------------------------------------------------------------
# Resilient Service Layer (FastAPI REST API with Direct DB Fallback)
# -------------------------------------------------------------
def api_request(method, endpoint, data=None, params=None):
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    try:
        if method == "GET":
            resp = requests.get(url, params=params, timeout=2)
        elif method == "POST":
            resp = requests.post(url, json=data, timeout=2)
        elif method == "PUT":
            resp = requests.put(url, json=data, timeout=2)
        elif method == "DELETE":
            resp = requests.delete(url, params=params, timeout=2)
        return resp
    except Exception:
        return None

def login_user_service(email, password):
    # Try FastAPI endpoint first
    res = api_request("POST", "/auth/login", data={"email": email, "password": password})
    if res and res.status_code == 200:
        return True, res.json()["user"], "Login successful"
    elif res and res.status_code == 401:
        # Fallback check against DB
        pass

    # Direct database fallback
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.strip().lower()).first()
        if user and verify_password(password, user.password):
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "college": user.college,
                "department": user.department,
                "year": user.year,
                "interests": user.interests,
                "role": user.role
            }
            return True, user_dict, "Login successful"
        return False, None, "Invalid email or password."
    finally:
        db.close()

def register_user_service(payload):
    res = api_request("POST", "/auth/register", data=payload)
    if res and res.status_code == 201:
        return True, "Registration successful! You can now log in."
    
    # Direct database fallback
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == payload["email"].strip().lower()).first()
        if existing:
            return False, "An account with this email already exists."
        
        interests_str = ", ".join(payload.get("interests", [])) if payload.get("interests") else ""
        new_user = User(
            name=payload["name"].strip(),
            email=payload["email"].strip().lower(),
            password=hash_password(payload["password"]),
            college=payload.get("college", ""),
            department=payload.get("department", ""),
            year=payload.get("year", ""),
            interests=interests_str,
            role=payload.get("role", "student")
        )
        db.add(new_user)
        db.commit()
        return True, "Registration successful! You can now log in."
    except Exception as e:
        return False, f"Registration error: {str(e)}"
    finally:
        db.close()

def fetch_events(search=None, category=None, department=None, venue=None):
    res = api_request("GET", "/events", params={
        "search": search or None,
        "category": category if category != "All" else None,
        "department": department if department != "All" else None,
        "venue": venue if venue != "All" else None
    })
    if res and res.status_code == 200:
        return res.json()

    # Direct database fallback
    db = SessionLocal()
    try:
        q = db.query(Event)
        if search:
            pat = f"%{search.strip()}%"
            q = q.filter((Event.name.ilike(pat)) | (Event.description.ilike(pat)) | (Event.category.ilike(pat)))
        if category and category != "All":
            q = q.filter(Event.category == category)
        if venue and venue != "All":
            q = q.filter(Event.venue.ilike(f"%{venue}%"))
        
        events = q.order_by(Event.id.desc()).all()
        result = []
        for ev in events:
            reg_cnt = db.query(Registration).filter(Registration.event_id == ev.id).count()
            result.append({
                "id": ev.id,
                "name": ev.name,
                "description": ev.description or "",
                "category": ev.category,
                "date": ev.date,
                "time": ev.time,
                "venue": ev.venue,
                "organizer": ev.organizer,
                "max_participants": ev.max_participants,
                "registration_deadline": ev.registration_deadline or "",
                "image": ev.image or "",
                "registered_count": reg_cnt
            })
        return result
    finally:
        db.close()

def fetch_recommendations(user_id):
    res = api_request("GET", "/recommendations", params={"user_id": user_id})
    if res and res.status_code == 200:
        return res.json()

    # Direct DB fallback
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        user_interests = [i.strip() for i in (user.interests or "").split(",") if i.strip()]
        events = db.query(Event).all()
        ranked = get_recommendations_for_user(user_interests, events)
        results = []
        for item in ranked:
            ev = item["event"]
            reg_cnt = db.query(Registration).filter(Registration.event_id == ev.id).count()
            results.append({
                "event": {
                    "id": ev.id,
                    "name": ev.name,
                    "description": ev.description or "",
                    "category": ev.category,
                    "date": ev.date,
                    "time": ev.time,
                    "venue": ev.venue,
                    "organizer": ev.organizer,
                    "max_participants": ev.max_participants,
                    "registration_deadline": ev.registration_deadline or "",
                    "image": ev.image or "",
                    "registered_count": reg_cnt
                },
                "match_score": item["match_score"],
                "match_percentage": item["match_percentage"],
                "matching_interests": item["matching_interests"]
            })
        return results
    finally:
        db.close()

def fetch_my_events(user_id):
    res = api_request("GET", "/registrations/my-events", params={"user_id": user_id})
    if res and res.status_code == 200:
        return res.json()

    db = SessionLocal()
    try:
        regs = db.query(Registration).filter(Registration.user_id == user_id).order_by(Registration.id.desc()).all()
        out = []
        for r in regs:
            if r.event:
                out.append({
                    "registration_id": r.id,
                    "event_id": r.event.id,
                    "name": r.event.name,
                    "category": r.event.category,
                    "date": r.event.date,
                    "time": r.event.time,
                    "venue": r.event.venue,
                    "organizer": r.event.organizer,
                    "description": r.event.description,
                    "registration_date": r.registration_date.strftime("%d %b %Y, %I:%M %p") if r.registration_date else "",
                    "status": "Registered"
                })
        return out
    finally:
        db.close()

def register_for_event_service(user_id, event_id):
    res = api_request("POST", "/registrations", data={"user_id": user_id, "event_id": event_id})
    if res and res.status_code == 200:
        return True, "Registered successfully!"
    
    # Direct DB fallback
    db = SessionLocal()
    try:
        existing = db.query(Registration).filter(Registration.user_id == user_id, Registration.event_id == event_id).first()
        if existing:
            return False, "You are already registered for this event."
        
        ev = db.query(Event).filter(Event.id == event_id).first()
        if not ev:
            return False, "Event not found."
            
        cnt = db.query(Registration).filter(Registration.event_id == event_id).count()
        if ev.max_participants and cnt >= ev.max_participants:
            return False, "Event is full!"

        db.add(Registration(user_id=user_id, event_id=event_id))
        db.commit()
        return True, "Registered successfully!"
    finally:
        db.close()

def cancel_event_service(user_id, event_id):
    res = api_request("DELETE", f"/registrations/{event_id}", params={"user_id": user_id})
    if res and res.status_code == 200:
        return True, "Registration cancelled."

    db = SessionLocal()
    try:
        reg = db.query(Registration).filter(Registration.user_id == user_id, Registration.event_id == event_id).first()
        if reg:
            db.delete(reg)
            db.commit()
            return True, "Registration cancelled."
        return False, "Registration not found."
    finally:
        db.close()

def fetch_admin_stats():
    res = api_request("GET", "/admin/stats")
    if res and res.status_code == 200:
        return res.json()
    db = SessionLocal()
    try:
        return {
            "total_events": db.query(Event).count(),
            "total_students": db.query(User).filter(User.role == "student").count(),
            "total_registrations": db.query(Registration).count(),
            "upcoming_events": db.query(Event).count()
        }
    finally:
        db.close()

def fetch_admin_registrations():
    res = api_request("GET", "/admin/registrations")
    if res and res.status_code == 200:
        return res.json()
    db = SessionLocal()
    try:
        regs = db.query(Registration).order_by(Registration.id.desc()).all()
        return [{
            "registration_id": r.id,
            "student_name": r.user.name if r.user else "Unknown",
            "student_email": r.user.email if r.user else "Unknown",
            "department": r.user.department if r.user else "N/A",
            "year": r.user.year if r.user else "N/A",
            "event_name": r.event.name if r.event else "Deleted",
            "category": r.event.category if r.event else "N/A",
            "event_date": r.event.date if r.event else "N/A",
            "registration_date": r.registration_date.strftime("%d %b %Y, %I:%M %p") if r.registration_date else ""
        } for r in regs]
    finally:
        db.close()


# -------------------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 Campus Events Recommendation System")
    
    if st.session_state.user:
        user = st.session_state.user
        role_badge = "👑 Admin" if user.get("role") == "admin" else "🎒 Student"
        st.success(f"**{user.get('name')}** ({role_badge})")
        st.caption(f"📧 {user.get('email')} | 🏛️ {user.get('department')}")
        
        if user.get("interests"):
            st.caption(f"🎯 **Interests:** {user.get('interests')}")
            
        if st.button("🚪 Logout", width="stretch"):
            st.session_state.user = None
            st.session_state.active_page = "🏠 Home"
            st.rerun()
    else:
        st.info("👋 Welcome! Log in to register and see personalized recommendations.")

    st.markdown("---")
    
    nav_options = ["🏠 Home", "🔍 Explore Events"]
    
    if st.session_state.user:
        if st.session_state.user.get("role") == "student":
            nav_options.extend(["⭐ Recommended For You", "📝 My Events"])
        elif st.session_state.user.get("role") == "admin":
            nav_options.extend(["📊 Admin Dashboard", "⭐ Recommended Preview"])
    else:
        nav_options.extend(["🔑 Login", "📝 Register"])

    selected_page = st.radio("Navigation", nav_options, index=nav_options.index(st.session_state.active_page) if st.session_state.active_page in nav_options else 0)
    st.session_state.active_page = selected_page

    st.markdown("---")
    # Quick Login Buttons for Demo Convenience
    if not st.session_state.user:
        st.markdown("##### ⚡ Quick 1-Click Logins")
        col_demo1, col_demo2 = st.columns(2)
        with col_demo1:
            if st.button("👑 Admin Officer", key="demo_admin", width="stretch"):
                ok, u_data, msg = login_user_service("admin@college.edu", "admin123")
                if ok:
                    st.session_state.user = u_data
                    st.session_state.active_page = "📊 Admin Dashboard"
                    st.rerun()
                else:
                    st.error(msg)
        with col_demo2:
            if st.button("🎒 Student Tejo", key="demo_student", width="stretch"):
                ok, u_data, msg = login_user_service("tejo@gmail.com", "student123")
                if ok:
                    st.session_state.user = u_data
                    st.session_state.active_page = "🏠 Home"
                    st.rerun()
                else:
                    st.error(msg)


# -------------------------------------------------------------
# Event Card Renderer Component
# -------------------------------------------------------------
def render_event_card(ev, registered_event_ids=None, match_info=None):
    registered_event_ids = registered_event_ids or []
    ev_id = ev.get("id")
    is_registered = ev_id in registered_event_ids
    
    with st.container():
        st.markdown(f"### 🎯 {ev.get('name')}")
        
        # Badges
        col_badges, col_score = st.columns([3, 1])
        with col_badges:
            st.markdown(f"<span class='event-badge'>🏷️ {ev.get('category')}</span>"
                        f"<span class='event-badge'>📍 {ev.get('venue')}</span>"
                        f"<span class='event-badge'>👥 {ev.get('registered_count', 0)} / {ev.get('max_participants', 100)} slots</span>", 
                        unsafe_allow_html=True)
        with col_score:
            if match_info:
                pct = match_info.get("match_percentage", 0)
                badge_class = "match-badge-high" if pct >= 60 else "match-badge"
                st.markdown(f"<div style='text-align:right;'><span class='match-badge {badge_class}'>🔥 {pct}% Match</span></div>", unsafe_allow_html=True)

        col_img, col_details = st.columns([1, 2])
        with col_img:
            img_url = ev.get("image") or "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=600&q=80"
            st.image(img_url, width="stretch")
            
        with col_details:
            st.markdown(f"**📅 Date:** {ev.get('date')} &nbsp;&nbsp;|&nbsp;&nbsp; **⏰ Time:** {ev.get('time')}")
            st.markdown(f"**🏛️ Organizer:** {ev.get('organizer')}")
            if ev.get("registration_deadline"):
                st.markdown(f"**⏳ Deadline:** {ev.get('registration_deadline')}")
            
            st.write(ev.get("description", "No description provided."))

            if match_info and match_info.get("matching_interests"):
                st.info(f"💡 **Matching Interests:** {', '.join(match_info.get('matching_interests'))}")

            # Action Buttons
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.session_state.user:
                    user_id = st.session_state.user["id"]
                    if is_registered:
                        st.success("✅ Registered")
                    else:
                        if st.button(f"Register Now", key=f"reg_btn_{ev_id}_{match_info is not None}"):
                            ok, msg = register_for_event_service(user_id, ev_id)
                            if ok:
                                st.toast("Successfully registered for event!", icon="🎉")
                                st.rerun()
                            else:
                                st.error(msg)
                else:
                    if st.button(f"Login to Register", key=f"login_reg_{ev_id}"):
                        st.session_state.active_page = "🔑 Login"
                        st.rerun()
            with col_b2:
                if st.session_state.user and is_registered:
                    if st.button("Cancel Registration", key=f"cancel_btn_{ev_id}", type="secondary"):
                        ok, msg = cancel_event_service(st.session_state.user["id"], ev_id)
                        if ok:
                            st.toast("Registration cancelled.", icon="ℹ️")
                            st.rerun()
                        else:
                            st.error(msg)
        st.markdown("---")


# =============================================================
# PAGE: HOME
# =============================================================
if st.session_state.active_page == "🏠 Home":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🎓 Campus Events Recommendation System</div>
        <div class="hero-subtitle">Discover exciting technical hackathons, cultural festivals, workshops, sports, and receive personalized event recommendations matched to your passions!</div>
    </div>
    """, unsafe_allow_html=True)

    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        if st.button("🔍 Explore All Events", width="stretch", type="primary"):
            st.session_state.active_page = "🔍 Explore Events"
            st.rerun()
    with cta2:
        if not st.session_state.user:
            if st.button("🔑 Login to Account", width="stretch"):
                st.session_state.active_page = "🔑 Login"
                st.rerun()
        else:
            if st.button("⭐ View Recommendations", width="stretch"):
                st.session_state.active_page = "⭐ Recommended For You"
                st.rerun()
    with cta3:
        if not st.session_state.user:
            if st.button("📝 Register as Student", width="stretch"):
                st.session_state.active_page = "📝 Register"
                st.rerun()
        else:
            if st.button("📋 View My Events", width="stretch"):
                st.session_state.active_page = "📝 My Events"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🏷️ Browse by Categories")
    cat_cols = st.columns(len(CATEGORIES[1:]))
    for i, cat in enumerate(CATEGORIES[1:]):
        with cat_cols[i]:
            if st.button(cat, key=f"cat_pill_{cat}", width="stretch"):
                st.session_state.filter_category = cat
                st.session_state.active_page = "🔍 Explore Events"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    user_reg_ids = []
    if st.session_state.user:
        my_evs = fetch_my_events(st.session_state.user["id"])
        user_reg_ids = [m["event_id"] for m in my_evs]

    if st.session_state.user and st.session_state.user.get("role") == "student":
        st.markdown("### ⭐ Recommended For You")
        recs = fetch_recommendations(st.session_state.user["id"])
        if recs:
            for rec_item in recs[:2]:
                render_event_card(
                    ev=rec_item["event"],
                    registered_event_ids=user_reg_ids,
                    match_info={
                        "match_percentage": rec_item["match_percentage"],
                        "matching_interests": rec_item["matching_interests"]
                    }
                )
            if len(recs) > 2:
                if st.button("See All Recommended Events →", key="see_all_recs"):
                    st.session_state.active_page = "⭐ Recommended For You"
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📅 Upcoming College Events")
    all_events = fetch_events()
    if all_events:
        for ev in all_events[:3]:
            render_event_card(ev, registered_event_ids=user_reg_ids)
    else:
        st.info("No events found. Start by adding events in the Admin Dashboard.")


# =============================================================
# PAGE: EXPLORE EVENTS & SEARCH
# =============================================================
elif st.session_state.active_page == "🔍 Explore Events":
    st.title("🔍 Explore College Events")
    st.caption("Search, filter, and register for workshops, competitions, hackathons, and cultural fests.")

    search_col, cat_col, venue_col = st.columns([2, 1, 1])
    with search_col:
        search_input = st.text_input("Search Events by Name or Keywords", value=st.session_state.search_query, placeholder="e.g. AI, Hackathon, Coding, Football...")
    with cat_col:
        selected_cat = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(st.session_state.filter_category) if st.session_state.filter_category in CATEGORIES else 0)
    with venue_col:
        selected_venue = st.selectbox("Venue Filter", ["All", "Computer Lab", "Auditorium", "Sports Ground", "Amphitheatre", "Incubation Center"])

    events = fetch_events(
        search=search_input,
        category=selected_cat,
        venue=selected_venue
    )

    user_reg_ids = []
    if st.session_state.user:
        my_evs = fetch_my_events(st.session_state.user["id"])
        user_reg_ids = [m["event_id"] for m in my_evs]

    st.markdown(f"**Found {len(events)} events**")
    st.markdown("---")

    if events:
        for ev in events:
            render_event_card(ev, registered_event_ids=user_reg_ids)
    else:
        st.warning("No events found matching your search and filter criteria.")


# =============================================================
# PAGE: RECOMMENDATION SYSTEM
# =============================================================
elif st.session_state.active_page in ["⭐ Recommended For You", "⭐ Recommended Preview"]:
    st.title("⭐ Personalized Event Recommendations")
    
    if not st.session_state.user:
        st.warning("Please log in to receive personalized recommendations based on your interests.")
        if st.button("🔑 Go to Login"):
            st.session_state.active_page = "🔑 Login"
            st.rerun()
    else:
        user = st.session_state.user
        st.markdown(f"""
        <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem;">
            <strong>🎯 Your Selected Interests:</strong> {user.get('interests') or 'None selected'}<br>
            <span style="font-size:0.85rem; color:#64748b;">
                <strong>Algorithm:</strong> Content-based recommendation compares your interests against event tags, titles, and descriptions, computing a personalized match score.
            </span>
        </div>
        """, unsafe_allow_html=True)

        user_reg_ids = []
        my_evs = fetch_my_events(user["id"])
        user_reg_ids = [m["event_id"] for m in my_evs]

        recs = fetch_recommendations(user["id"])
        if recs:
            for item in recs:
                render_event_card(
                    ev=item["event"],
                    registered_event_ids=user_reg_ids,
                    match_info={
                        "match_percentage": item["match_percentage"],
                        "matching_interests": item["matching_interests"]
                    }
                )
        else:
            st.info("No recommendations found at the moment.")


# =============================================================
# PAGE: MY REGISTERED EVENTS
# =============================================================
elif st.session_state.active_page == "📝 My Events":
    st.title("📝 My Registered Events")
    
    if not st.session_state.user:
        st.warning("Please log in to view your registered events.")
    else:
        user_id = st.session_state.user["id"]
        my_events = fetch_my_events(user_id)
        
        if my_events:
            st.success(f"You are currently registered for **{len(my_events)}** event(s).")
            
            for ev in my_events:
                with st.container():
                    st.markdown(f"### 🎯 {ev['name']}")
                    st.markdown(f"<span class='event-badge'>🏷️ {ev['category']}</span>"
                                f"<span class='event-badge'>📍 {ev['venue']}</span>"
                                f"<span class='event-badge' style='background:#ecfdf5; color:#059669;'>✅ {ev['status']}</span>", 
                                unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**📅 Date:** {ev['date']} &nbsp;|&nbsp; **⏰ Time:** {ev['time']} &nbsp;|&nbsp; **🏛️ Organizer:** {ev['organizer']}")
                        st.caption(f"Registered on: {ev['registration_date']}")
                        if ev.get("description"):
                            st.write(ev["description"])
                    with c2:
                        if st.button("Cancel Registration", key=f"my_ev_cancel_{ev['event_id']}", type="secondary"):
                            ok, msg = cancel_event_service(user_id, ev["event_id"])
                            if ok:
                                st.toast("Registration cancelled successfully.", icon="ℹ️")
                                st.rerun()
                            else:
                                st.error(msg)
                    st.markdown("---")
        else:
            st.info("You haven't registered for any events yet.")
            if st.button("🔍 Explore Events to Register"):
                st.session_state.active_page = "🔍 Explore Events"
                st.rerun()


# =============================================================
# PAGE: ADMIN DASHBOARD
# =============================================================
elif st.session_state.active_page == "📊 Admin Dashboard":
    st.title("📊 Event Organizer & Admin Dashboard")
    
    if not st.session_state.user or st.session_state.user.get("role") != "admin":
        st.error("Access Restricted. Please log in with an Administrator account.")
        if st.button("👑 Connect as Admin Instantly"):
            ok, u_data, msg = login_user_service("admin@college.edu", "admin123")
            if ok:
                st.session_state.user = u_data
                st.rerun()
    else:
        stats = fetch_admin_stats()
        
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('total_events', 0)}</div>
                <div class="stat-label">Total Events</div>
            </div>
            """, unsafe_allow_html=True)
        with sc2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('total_students', 0)}</div>
                <div class="stat-label">Total Students</div>
            </div>
            """, unsafe_allow_html=True)
        with sc3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('total_registrations', 0)}</div>
                <div class="stat-label">Registrations</div>
            </div>
            """, unsafe_allow_html=True)
        with sc4:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('upcoming_events', 0)}</div>
                <div class="stat-label">Upcoming Events</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["📋 Manage Events", "➕ Create Event", "👥 View Registrations"])

        with admin_tab1:
            st.subheader("Existing Events")
            all_events = fetch_events()
            for ev in all_events:
                with st.expander(f"🎯 {ev['name']} ({ev['category']} - {ev['date']})"):
                    st.write(f"**Venue:** {ev['venue']} | **Time:** {ev['time']} | **Organizer:** {ev['organizer']}")
                    st.write(f"**Registered:** {ev.get('registered_count', 0)} / {ev.get('max_participants', 100)}")
                    st.write(f"**Description:** {ev.get('description')}")
                    
                    del_col1, del_col2 = st.columns([1, 4])
                    with del_col1:
                        if st.button("🗑️ Delete Event", key=f"del_ev_{ev['id']}", type="secondary"):
                            db = SessionLocal()
                            try:
                                ev_obj = db.query(Event).filter(Event.id == ev['id']).first()
                                if ev_obj:
                                    db.delete(ev_obj)
                                    db.commit()
                                    st.toast("Event deleted successfully", icon="🗑️")
                                    st.rerun()
                            finally:
                                db.close()

        with admin_tab2:
            st.subheader("Add New College Event")
            with st.form("create_event_form"):
                f_name = st.text_input("Event Name", placeholder="e.g. AI Innovation Hackathon")
                f_desc = st.text_area("Description", placeholder="Provide details about schedule, rules, and topics...")
                
                c_form1, c_form2 = st.columns(2)
                with c_form1:
                    f_cat = st.selectbox("Category", CATEGORIES[1:])
                    f_date = st.text_input("Date", placeholder="e.g. 2026-11-20 or 20 Nov 2026")
                    f_time = st.text_input("Time", placeholder="e.g. 10:00 AM")
                    f_venue = st.text_input("Venue", placeholder="e.g. Computer Lab 3")
                with c_form2:
                    f_organizer = st.text_input("Organizer", placeholder="e.g. CSE Department")
                    f_max = st.number_input("Maximum Participants", min_value=10, max_value=2000, value=100)
                    f_deadline = st.text_input("Registration Deadline", placeholder="e.g. 2026-11-18")
                    f_image = st.text_input("Event Image URL (Optional)", placeholder="https://...")

                submit_event = st.form_submit_button("➕ Create Event", type="primary")
                if submit_event:
                    if not f_name or not f_cat or not f_date or not f_venue or not f_organizer:
                        st.error("Please fill in all required fields.")
                    else:
                        db = SessionLocal()
                        try:
                            new_event = Event(
                                name=f_name,
                                description=f_desc,
                                category=f_cat,
                                date=f_date,
                                time=f_time,
                                venue=f_venue,
                                organizer=f_organizer,
                                max_participants=int(f_max),
                                registration_deadline=f_deadline,
                                image=f_image or "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=700&q=80"
                            )
                            db.add(new_event)
                            db.commit()
                            st.success(f"Event '{f_name}' created successfully!")
                            st.rerun()
                        finally:
                            db.close()

        with admin_tab3:
            st.subheader("Student Registrations List")
            registrations_data = fetch_admin_registrations()
            if registrations_data:
                st.dataframe(
                    registrations_data,
                    column_config={
                        "registration_id": "Reg ID",
                        "student_name": "Student Name",
                        "student_email": "Email",
                        "department": "Department",
                        "year": "Year",
                        "event_name": "Event",
                        "category": "Category",
                        "event_date": "Date",
                        "registration_date": "Registered On"
                    },
                    hide_index=True,
                    width="stretch"
                )
            else:
                st.info("No student registrations yet.")


# =============================================================
# PAGE: LOGIN
# =============================================================
elif st.session_state.active_page == "🔑 Login":
    st.title("🔑 Student & Admin Login")
    
    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        with st.form("login_form"):
            l_email = st.text_input("Email", placeholder="admin@college.edu or tejo@gmail.com")
            l_pass = st.text_input("Password", type="password")
            btn_login = st.form_submit_button("Login", type="primary", width="stretch")
            
            if btn_login:
                if not l_email or not l_pass:
                    st.error("Please provide both email and password.")
                else:
                    ok, u_data, msg = login_user_service(l_email, l_pass)
                    if ok:
                        st.session_state.user = u_data
                        st.success(f"Welcome back, {st.session_state.user['name']}!")
                        if st.session_state.user.get("role") == "admin":
                            st.session_state.active_page = "📊 Admin Dashboard"
                        else:
                            st.session_state.active_page = "🏠 Home"
                        st.rerun()
                    else:
                        st.error(msg)
                        
        st.markdown("Don't have an account?")
        if st.button("Create an account (Register)"):
            st.session_state.active_page = "📝 Register"
            st.rerun()

    with col_l2:
        st.markdown("""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1.5rem; margin-top:1.5rem;">
            <h4>💡 Verified Working Credentials</h4>
            <p><strong>👑 Admin Account:</strong><br>
            Email: <code>admin@college.edu</code><br>
            Password: <code>admin123</code></p>
            <p><strong>🎒 Student Account:</strong><br>
            Email: <code>tejo@gmail.com</code><br>
            Password: <code>student123</code></p>
            <hr>
            <p style="font-size:0.9rem; color:#64748b;">
                Tip: You can also use the <strong>⚡ Quick 1-Click Logins</strong> in the left sidebar to sign in instantly without typing!
            </p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================
# PAGE: REGISTER
# =============================================================
elif st.session_state.active_page == "📝 Register":
    st.title("📝 Student Registration")
    st.caption("Sign up to participate in campus events and receive tailored recommendations.")
    
    with st.form("registration_form"):
        r_name = st.text_input("Full Name *", placeholder="e.g. Tejo")
        r_email = st.text_input("Email Address *", placeholder="e.g. tejo@gmail.com")
        r_pass = st.text_input("Password *", type="password")
        
        reg_c1, reg_c2, reg_c3 = st.columns(3)
        with reg_c1:
            r_college = st.text_input("College Name", value="National Institute of Technology")
        with reg_c2:
            r_dept = st.selectbox("Department", ["CSE", "ECE", "EEE", "Mechanical", "Civil", "IT", "AI & DS", "MBA", "MCA"])
        with reg_c3:
            r_year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Postgraduate"])

        st.markdown("#### Select Your Interests")
        st.caption("Choose topics you are passionate about to receive smart recommendations:")
        
        selected_interests = []
        cols = st.columns(3)
        for idx, interest in enumerate(ALL_INTERESTS):
            col_target = cols[idx % 3]
            with col_target:
                checked = st.checkbox(interest, key=f"interest_{interest}")
                if checked:
                    selected_interests.append(interest)

        r_role = st.selectbox("Role", ["student", "admin"], index=0)

        submit_reg = st.form_submit_button("Register Now", type="primary")
        if submit_reg:
            if not r_name or not r_email or not r_pass:
                st.error("Please fill in all required fields (Name, Email, Password).")
            else:
                user_payload = {
                    "name": r_name,
                    "email": r_email,
                    "password": r_pass,
                    "college": r_college,
                    "department": r_dept,
                    "year": r_year,
                    "interests": selected_interests,
                    "role": r_role
                }
                ok, msg = register_user_service(user_payload)
                if ok:
                    st.success(msg)
                    st.session_state.active_page = "🔑 Login"
                    st.rerun()
                else:
                    st.error(msg)
