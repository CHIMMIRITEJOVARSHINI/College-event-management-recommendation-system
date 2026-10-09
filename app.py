import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

# Backend API Configuration
API_BASE_URL = "http://127.0.0.1:8000/api"

st.set_page_config(
    page_title="College Event Management & Recommendation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for College UI
st.markdown("""
<style>
    /* Main Theme colors */
    :root {
        --primary-color: #1E3A8A;
        --secondary-color: #3B82F6;
        --accent-color: #F59E0B;
        --bg-light: #F8FAFC;
    }

    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(30, 58, 138, 0.2);
    }

    .main-header h1 {
        color: white !important;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .event-card {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .event-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
    }

    .match-badge {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 0.3rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 0.5rem;
    }

    .category-badge {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .stat-card {
        background-color: #F1F5F9;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        color: #1E3A8A;
    }

    .stat-label {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ALL AVAILABLE INTERESTS
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

ALL_CATEGORIES = [
    "All",
    "Hackathon",
    "Workshops",
    "Seminars",
    "Cultural",
    "Sports",
    "Entrepreneurship",
    "Technical"
]

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# --- HELPER API CALLS ---

def api_login(email, password):
    try:
        res = requests.post(f"{API_BASE_URL}/auth/login", json={"email": email, "password": password})
        if res.status_code == 200:
            data = res.json()
            st.session_state.authenticated = True
            st.session_state.token = data["access_token"]
            st.session_state.user = data["user"]
            return True, "Login successful!"
        else:
            return False, res.json().get("detail", "Invalid login credentials.")
    except Exception as e:
        return False, f"Backend API Connection Error: {e}"

def api_register(name, email, password, college, department, year, interests, role="student"):
    try:
        payload = {
            "name": name,
            "email": email,
            "password": password,
            "college": college,
            "department": department,
            "year": year,
            "interests": interests,
            "role": role
        }
        res = requests.post(f"{API_BASE_URL}/auth/register", json=payload)
        if res.status_code == 200:
            data = res.json()
            st.session_state.authenticated = True
            st.session_state.token = data["access_token"]
            st.session_state.user = data["user"]
            return True, "Registration successful!"
        else:
            return False, res.json().get("detail", "Registration failed.")
    except Exception as e:
        return False, f"Backend API Connection Error: {e}"

def api_update_profile(name, college, department, year, interests):
    try:
        payload = {
            "name": name,
            "college": college,
            "department": department,
            "year": year,
            "interests": interests
        }
        res = requests.put(f"{API_BASE_URL}/users/profile", json=payload, headers=get_headers())
        if res.status_code == 200:
            st.session_state.user = res.json()
            return True, "Profile updated successfully!"
        else:
            return False, res.json().get("detail", "Profile update failed.")
    except Exception as e:
        return False, f"Error updating profile: {e}"

def fetch_events(search=None, category=None, department=None, venue=None):
    try:
        params = {}
        if search: params["search"] = search
        if category and category != "All": params["category"] = category
        if department and department != "All": params["department"] = department
        if venue and venue != "All": params["venue"] = venue

        res = requests.get(f"{API_BASE_URL}/events", params=params)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Failed to fetch events: {e}")
    return []

def fetch_recommendations():
    if not st.session_state.authenticated:
        return []
    try:
        res = requests.get(f"{API_BASE_URL}/recommendations", headers=get_headers())
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        pass
    return []

def register_event(event_id):
    if not st.session_state.authenticated:
        st.warning("Please login to register for events.")
        return False, "Not logged in"
    try:
        res = requests.post(f"{API_BASE_URL}/events/{event_id}/register", headers=get_headers())
        if res.status_code == 200:
            return True, "Registered successfully!"
        else:
            return False, res.json().get("detail", "Registration failed.")
    except Exception as e:
        return False, f"Error: {e}"

def cancel_event_reg(event_id):
    try:
        res = requests.post(f"{API_BASE_URL}/events/{event_id}/cancel", headers=get_headers())
        if res.status_code == 200:
            return True, "Registration cancelled successfully."
        else:
            return False, res.json().get("detail", "Failed to cancel registration.")
    except Exception as e:
        return False, f"Error: {e}"

def fetch_my_registrations():
    if not st.session_state.authenticated:
        return []
    try:
        res = requests.get(f"{API_BASE_URL}/registrations/my", headers=get_headers())
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        pass
    return []

def fetch_admin_stats():
    try:
        res = requests.get(f"{API_BASE_URL}/admin/stats", headers=get_headers())
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        pass
    return {"total_events": 0, "total_students": 0, "total_registrations": 0, "upcoming_events": 0}

def fetch_all_registrations():
    try:
        res = requests.get(f"{API_BASE_URL}/registrations/all", headers=get_headers())
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        pass
    return []

def create_new_event(event_dict):
    try:
        res = requests.post(f"{API_BASE_URL}/events", json=event_dict, headers=get_headers())
        if res.status_code == 200:
            return True, "Event created successfully!"
        else:
            return False, res.json().get("detail", "Failed to create event.")
    except Exception as e:
        return False, f"Error: {e}"

def update_existing_event(event_id, event_dict):
    try:
        res = requests.put(f"{API_BASE_URL}/events/{event_id}", json=event_dict, headers=get_headers())
        if res.status_code == 200:
            return True, "Event updated successfully!"
        else:
            return False, res.json().get("detail", "Failed to update event.")
    except Exception as e:
        return False, f"Error: {e}"

def delete_existing_event(event_id):
    try:
        res = requests.delete(f"{API_BASE_URL}/events/{event_id}", headers=get_headers())
        if res.status_code == 200:
            return True, "Event deleted successfully."
        else:
            return False, res.json().get("detail", "Failed to delete event.")
    except Exception as e:
        return False, f"Error: {e}"


# --- SIDEBAR NAVIGATION ---

st.sidebar.markdown("## 🎓 College Event Hub")

if st.session_state.authenticated:
    user = st.session_state.user
    role_badge = "👑 Admin" if user["role"] == "admin" else "🎓 Student"
    st.sidebar.success(f"Logged in as **{user['name']}**\n\nRole: **{role_badge}**")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()
else:
    st.sidebar.info("👋 Welcome Guest! Please login or register to register for events.")

st.sidebar.divider()

nav_options = ["🏠 Home & Recommendations", "🔍 Explore Events"]
if st.session_state.authenticated:
    if st.session_state.user["role"] == "student":
        nav_options.extend(["📅 My Registered Events", "👤 My Profile"])
    elif st.session_state.user["role"] == "admin":
        nav_options.extend(["📊 Admin Dashboard", "✏️ Manage Events", "👤 My Profile"])
else:
    nav_options.extend(["🔐 Login / Register"])

selected_nav = st.sidebar.radio("Navigation", nav_options)


# --- MAIN HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🎓 College Event Management & Recommendation System</h1>
    <p>Discover, Search, Register, and Get Personalized Event Recommendations Based on Your Interests!</p>
</div>
""", unsafe_allow_html=True)


# --- PAGE 1: HOME & RECOMMENDATIONS ---
if selected_nav == "🏠 Home & Recommendations":
    
    # Hero Quick Stats / Action Bar
    all_events = fetch_events()
    registered_ids = [r["event_id"] for r in fetch_my_registrations()] if st.session_state.authenticated else []

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(all_events)}</div><div class="stat-label">Total Events</div></div>', unsafe_allow_html=True)
    with col2:
        hackathons_cnt = len([e for e in all_events if e["category"] == "Hackathon"])
        st.markdown(f'<div class="stat-card"><div class="stat-number">{hackathons_cnt}</div><div class="stat-label">Hackathons</div></div>', unsafe_allow_html=True)
    with col3:
        workshops_cnt = len([e for e in all_events if e["category"] == "Workshops"])
        st.markdown(f'<div class="stat-card"><div class="stat-number">{workshops_cnt}</div><div class="stat-label">Workshops</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(registered_ids)}</div><div class="stat-label">My Registrations</div></div>', unsafe_allow_html=True)

    st.write("")
    st.write("")

    # --- SECTION 1: RECOMMENDATIONS FOR YOU ---
    if st.session_state.authenticated and st.session_state.user["role"] == "student":
        st.subheader("⭐ Recommended For You")
        st.caption("Personalized content-based event recommendations matched to your profile interests.")
        
        recs = fetch_recommendations()
        if recs:
            # Filter top matched events
            matched_recs = [r for r in recs if r.get("match_percentage", 0) > 0]
            if matched_recs:
                rec_cols = st.columns(min(3, len(matched_recs)))
                for idx, ev in enumerate(matched_recs[:3]):
                    with rec_cols[idx % 3]:
                        st.markdown(f"""
                        <div class="event-card">
                            <span class="match-badge">🔥 {ev['match_percentage']}% Match</span>
                            <h4>{ev['name']}</h4>
                            <p style="color: #64748B; font-size: 0.9rem;">🏷️ <b>Category:</b> {ev['category']}</p>
                            <p style="color: #64748B; font-size: 0.9rem;">📅 <b>Date:</b> {ev['date']} | ⏰ {ev['time']}</p>
                            <p style="color: #64748B; font-size: 0.9rem;">📍 <b>Venue:</b> {ev['venue']}</p>
                            <p style="color: #10B981; font-size: 0.85rem;"><b>Matched Interests:</b> {', '.join(ev['matching_interests'])}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        is_reg = ev["id"] in registered_ids
                        if is_reg:
                            st.success("✅ Registered")
                        else:
                            if st.button(f"Register Now", key=f"rec_reg_{ev['id']}"):
                                success, msg = register_event(ev["id"])
                                if success:
                                    st.success(f"✅ Successfully Registered for {ev['name']}!")
                                    st.rerun()
                                else:
                                    st.error(msg)
            else:
                st.info("💡 Update your profile interests to see tailored recommendations!")
        else:
            st.info("No recommendations found yet. Select your interests in Profile Settings!")
    elif not st.session_state.authenticated:
        st.info("💡 **Log in as a student** to receive personalized event recommendations matched to your interests!")

    st.divider()

    # --- SECTION 2: UPCOMING & POPULAR EVENTS ---
    st.subheader("📅 Upcoming & Popular Events")
    
    if all_events:
        cols = st.columns(3)
        for idx, ev in enumerate(all_events):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="event-card">
                    <span class="category-badge">{ev['category']}</span>
                    <h3>{ev['name']}</h3>
                    <p style="font-size: 0.9rem; color: #475569;">{ev['description'][:110]}...</p>
                    <hr style="margin: 0.5rem 0; border-top: 1px solid #E2E8F0;">
                    <p style="margin-bottom: 0.2rem;">📅 <b>Date:</b> {ev['date']} ({ev['time']})</p>
                    <p style="margin-bottom: 0.2rem;">📍 <b>Venue:</b> {ev['venue']}</p>
                    <p style="margin-bottom: 0.2rem;">🏢 <b>Organizer:</b> {ev['organizer']}</p>
                    <p style="margin-bottom: 0.5rem;">🪑 <b>Available Seats:</b> {ev['available_seats']} / {ev['max_participants']}</p>
                </div>
                """, unsafe_allow_html=True)

                is_reg = ev["id"] in registered_ids
                if is_reg:
                    st.success("✅ Registered")
                else:
                    if st.button(f"Register for {ev['name']}", key=f"home_reg_{ev['id']}"):
                        if not st.session_state.authenticated:
                            st.warning("Please log in first to register.")
                        else:
                            success, msg = register_event(ev["id"])
                            if success:
                                st.success(f"✅ Successfully Registered for {ev['name']}!")
                                st.rerun()
                            else:
                                st.error(msg)
    else:
        st.info("No upcoming events scheduled right now.")


# --- PAGE 2: EXPLORE & SEARCH EVENTS ---
elif selected_nav == "🔍 Explore Events":
    st.subheader("🔍 Explore, Search & Filter Events")

    search_col, cat_col, venue_col = st.columns([2, 1, 1])
    with search_col:
        search_query = st.text_input("Search Events by Name or Keyword", placeholder="e.g. AI, Coding, Hackathon...")
    with cat_col:
        selected_cat = st.selectbox("Category Filter", ALL_CATEGORIES)
    with venue_col:
        venue_query = st.text_input("Venue Filter", placeholder="e.g. Computer Lab, Main Hall...")

    filtered_events = fetch_events(search=search_query, category=selected_cat, venue=venue_query)
    registered_ids = [r["event_id"] for r in fetch_my_registrations()] if st.session_state.authenticated else []

    st.write(f"Found **{len(filtered_events)}** matching events:")

    if filtered_events:
        for ev in filtered_events:
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {ev['name']} <span class='category-badge'>{ev['category']}</span>", unsafe_allow_html=True)
                    st.write(ev['description'])
                    st.caption(f"📅 **Date & Time:** {ev['date']} at {ev['time']} | 📍 **Venue:** {ev['venue']} | 🏢 **Organizer:** {ev['organizer']}")
                    st.caption(f"⏳ **Deadline:** {ev['registration_deadline']} | 🪑 **Seats Left:** {ev['available_seats']} / {ev['max_participants']}")
                    if ev.get("tags"):
                        st.markdown("**Tags:** " + " ".join([f"`{t}`" for t in ev["tags"]]))
                with c2:
                    st.write("")
                    st.write("")
                    is_reg = ev["id"] in registered_ids
                    if is_reg:
                        st.success("✅ Registered")
                        if st.button("Cancel Registration", key=f"exp_cancel_{ev['id']}"):
                            succ, msg = cancel_event_reg(ev["id"])
                            if succ:
                                st.success("Cancelled!")
                                st.rerun()
                            else:
                                st.error(msg)
                    else:
                        if st.button("Register Now", key=f"exp_reg_{ev['id']}", use_container_width=True):
                            if not st.session_state.authenticated:
                                st.warning("Please login to register.")
                            else:
                                succ, msg = register_event(ev["id"])
                                if succ:
                                    st.success(f"✅ Registered for {ev['name']}!")
                                    st.rerun()
                                else:
                                    st.error(msg)
            st.divider()


# --- PAGE 3: MY REGISTERED EVENTS (STUDENT) ---
elif selected_nav == "📅 My Registered Events":
    st.subheader("📅 My Registered Events")
    
    my_regs = fetch_my_registrations()
    if my_regs:
        for r in my_regs:
            with st.expander(f"🎯 {r['event_name']} — {r['event_date']}", expanded=True):
                col_info, col_act = st.columns([3, 1])
                with col_info:
                    st.write(f"📅 **Date:** {r['event_date']}")
                    st.write(f"⏰ **Time:** {r['event_time']}")
                    st.write(f"📍 **Venue:** {r['event_venue']}")
                    st.write(f"🕒 **Registered On:** {r['registration_date']}")
                    st.markdown(f"**Status:** <span style='color: green; font-weight: bold;'>{r['status']}</span>", unsafe_allow_html=True)
                with col_act:
                    if st.button(f"Cancel Registration", key=f"my_cancel_{r['event_id']}"):
                        succ, msg = cancel_event_reg(r['event_id'])
                        if succ:
                            st.success("Registration cancelled!")
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        st.info("You haven't registered for any events yet. Explore events to get started!")


# --- PAGE 4: LOGIN / REGISTER ---
elif selected_nav == "🔐 Login / Register":
    tab1, tab2 = st.tabs(["🔐 Student / Admin Login", "📝 Student Registration"])

    with tab1:
        st.subheader("Account Login")
        login_email = st.text_input("Email Address", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_pass")

        col_l1, col_l2 = st.columns([1, 2])
        with col_l1:
            if st.button("Login", use_container_width=True):
                if login_email and login_password:
                    succ, msg = api_login(login_email, login_password)
                    if succ:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in both email and password.")

        st.caption("💡 Quick Demo Login Credentials:")
        st.caption("Student: `tejo@gmail.com` | Password: `student123`")
        st.caption("Admin: `admin@college.edu` | Password: `admin123`")

    with tab2:
        st.subheader("Create Student Account")
        with st.form("reg_form"):
            reg_name = st.text_input("Full Name", value="Tejo")
            reg_email = st.text_input("Email Address", value="newstudent@college.edu")
            reg_pass = st.text_input("Password", type="password", value="student123")
            
            c_col, d_col, y_col = st.columns(3)
            with c_col:
                reg_college = st.text_input("College Name", value="State Institute of Technology")
            with d_col:
                reg_dept = st.text_input("Department", value="CSE")
            with y_col:
                reg_year = st.selectbox("Year of Study", ["1st Year", "2nd Year", "3rd Year", "4th Year"])

            st.write("#### Select Your Interests (used for personalized event recommendations):")
            selected_interests = []
            int_cols = st.columns(3)
            for idx, interest in enumerate(ALL_INTERESTS):
                with int_cols[idx % 3]:
                    # Default check first 3 for demo convenience
                    checked = st.checkbox(interest, value=(idx < 3), key=f"reg_int_{interest}")
                    if checked:
                        selected_interests.append(interest)

            submitted = st.form_submit_button("Register Account")
            if submitted:
                if reg_name and reg_email and reg_pass:
                    succ, msg = api_register(
                        name=reg_name,
                        email=reg_email,
                        password=reg_pass,
                        college=reg_college,
                        department=reg_dept,
                        year=reg_year,
                        interests=selected_interests
                    )
                    if succ:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in all required fields.")


# --- PAGE 5: MY PROFILE ---
elif selected_nav == "👤 My Profile":
    st.subheader("👤 Student Profile Settings")
    user = st.session_state.user

    with st.form("profile_form"):
        p_name = st.text_input("Full Name", value=user["name"])
        p_email = st.text_input("Email", value=user["email"], disabled=True)
        p_college = st.text_input("College Name", value=user["college"])
        p_dept = st.text_input("Department", value=user["department"])
        p_year = st.selectbox("Year of Study", ["1st Year", "2nd Year", "3rd Year", "4th Year"], 
                               index=["1st Year", "2nd Year", "3rd Year", "4th Year"].index(user["year"]) if user["year"] in ["1st Year", "2nd Year", "3rd Year", "4th Year"] else 2)

        st.write("#### Update Your Interests:")
        curr_interests = user.get("interests", [])
        updated_interests = []
        p_cols = st.columns(3)
        for idx, interest in enumerate(ALL_INTERESTS):
            with p_cols[idx % 3]:
                is_selected = interest in curr_interests
                chk = st.checkbox(interest, value=is_selected, key=f"prof_int_{interest}")
                if chk:
                    updated_interests.append(interest)

        save_profile = st.form_submit_button("Save Profile Updates")
        if save_profile:
            succ, msg = api_update_profile(p_name, p_college, p_dept, p_year, updated_interests)
            if succ:
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error(msg)


# --- PAGE 6: ADMIN DASHBOARD ---
elif selected_nav == "📊 Admin Dashboard":
    st.subheader("📊 Event Administrator Overview")

    stats = fetch_admin_stats()
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_events"]}</div><div class="stat-label">Total Events</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_students"]}</div><div class="stat-label">Registered Students</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_registrations"]}</div><div class="stat-label">Total Registrations</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["upcoming_events"]}</div><div class="stat-label">Upcoming Events</div></div>', unsafe_allow_html=True)

    st.write("")
    st.divider()
    st.subheader("📋 Registered Students List")
    
    regs_all = fetch_all_registrations()
    if regs_all:
        df_regs = pd.DataFrame(regs_all)
        st.dataframe(df_regs[["id", "event_name", "user_name", "user_email", "registration_date", "status"]], use_container_width=True)
    else:
        st.info("No student registrations found.")


# --- PAGE 7: MANAGE EVENTS (ADMIN) ---
elif selected_nav == "✏️ Manage Events":
    st.subheader("✏️ Manage Events (Create, Edit, Delete)")

    admin_tabs = st.tabs(["➕ Create New Event", "📝 Existing Events List"])

    with admin_tabs[0]:
        st.write("#### Add a New College Event")
        with st.form("create_event_form"):
            ev_name = st.text_input("Event Name*", value="AI Robotics Workshop")
            ev_desc = st.text_area("Description*", value="Hands-on robotics and micro-controller programming with AI vision module integration.")
            
            c1, c2 = st.columns(2)
            with c1:
                ev_cat = st.selectbox("Category*", ALL_CATEGORIES[1:])
                ev_date = st.date_input("Event Date*").strftime("%Y-%m-%d")
                ev_time = st.text_input("Time*", value="10:00 AM")
                ev_venue = st.text_input("Venue*", value="Robotics Lab 404")
            with c2:
                ev_organizer = st.text_input("Organizer*", value="ECE & CSE Department")
                ev_max = st.number_input("Max Participants*", min_value=1, value=80)
                ev_deadline = st.date_input("Registration Deadline*").strftime("%Y-%m-%d")
                ev_image = st.text_input("Image URL", value="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop")

            st.write("Select Event Tags for Recommendation Matching:")
            ev_tags_selected = []
            t_cols = st.columns(3)
            for idx, tag_opt in enumerate(ALL_INTERESTS):
                with t_cols[idx % 3]:
                    if st.checkbox(tag_opt, key=f"create_tag_{tag_opt}"):
                        ev_tags_selected.append(tag_opt)

            submit_create = st.form_submit_button("Create Event")
            if submit_create:
                if ev_name and ev_desc and ev_venue and ev_organizer:
                    new_ev_payload = {
                        "name": ev_name,
                        "description": ev_desc,
                        "category": ev_cat,
                        "date": ev_date,
                        "time": ev_time,
                        "venue": ev_venue,
                        "organizer": ev_organizer,
                        "max_participants": int(ev_max),
                        "registration_deadline": ev_deadline,
                        "image": ev_image,
                        "tags": ev_tags_selected
                    }
                    succ, msg = create_new_event(new_ev_payload)
                    if succ:
                        st.success("✅ Event created successfully!")
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please complete all required fields marked with *.")

    with admin_tabs[1]:
        st.write("#### Existing Events & Management")
        all_evs = fetch_events()
        if all_evs:
            for ev in all_evs:
                with st.expander(f"🎯 {ev['name']} ({ev['category']}) - {ev['date']}"):
                    st.write(f"**Description:** {ev['description']}")
                    st.write(f"📍 **Venue:** {ev['venue']} | ⏰ **Time:** {ev['time']} | 🏢 **Organizer:** {ev['organizer']}")
                    st.write(f"🪑 **Seats:** Registered {ev['registered_count']} / {ev['max_participants']} (Available: {ev['available_seats']})")
                    
                    c_del, c_edit = st.columns(2)
                    with c_del:
                        if st.button("❌ Delete Event", key=f"del_ev_{ev['id']}"):
                            succ, msg = delete_existing_event(ev['id'])
                            if succ:
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("No events found.")
