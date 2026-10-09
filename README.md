# 🎓 College Event Management & Recommendation System

A modern, full-stack web application that helps college students **discover, search, register for, and receive personalized content-based recommendations for college events**, while empowering event organizers and administrators to **manage events, track registrations, and view analytics**.

---

## 🌟 Key Features

### 🎓 Student Portal
- **User Authentication:** Registration & Secure Login with role management.
- **Personalized Recommendations:** Content-based recommendation algorithm matching student interests (e.g. AI & ML, Coding, Hackathons, Web Dev, Cultural) with event categories & tags, displaying match percentages (e.g., `🔥 85% Match`).
- **Event Discovery & Search:** Search by name/keyword and filter by category, venue, date, and organizer.
- **Event Registration:** Instant one-click event registration with capacity checking and duplicate registration prevention.
- **My Registered Events:** Manage active registrations and cancel registrations if plans change.

### 👑 Admin & Event Organizer Dashboard
- **Admin Authentication:** Protected admin panel access.
- **Event Management:** Full CRUD (Create, Read, Update, Delete) capability for college events with tags, image URLs, capacity limits, and deadlines.
- **Registration Tracking:** View and filter student registration logs across all events.
- **Analytics Dashboard:** Real-time metrics for total events, total registered students, total registrations, and upcoming events.

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit (Python), Custom CSS3
- **Backend API:** FastAPI (Python), Uvicorn
- **Database:** SQLite & SQLAlchemy ORM
- **Recommendation Engine:** Content-Based Filtering with NLP Keyword Token Matching
- **Auth & Security:** SHA-256 Hashing & JWT (JSON Web Tokens)

---

## 📁 Project Structure

```text
college-event-recommendation/
│
├── app.py                  # Streamlit Frontend Application
│
├── backend/
│   ├── main.py             # FastAPI App & Endpoints + Startup Auto-Seeding
│   ├── database.py         # SQLAlchemy Engine & Session Configuration
│   ├── models.py           # SQLite Database Models (User, Event, Registration)
│   ├── schemas.py          # Pydantic Schemas for Requests & Responses
│   ├── auth.py             # Password Hashing & JWT Authentication
│   ├── recommendation.py   # Content-Based Recommendation Algorithm
│   └── requirements.txt    # Python Dependencies
│
├── data/
│   └── events.db           # SQLite Database
│
└── README.md               # Documentation
```

---

## 🚀 Quick Start Guide

### 1. Setup Virtual Environment & Install Dependencies

```bash
# Navigate into project directory
cd C:\Users\tejuv\.gemini\antigravity\scratch\college-event-recommendation

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r backend/requirements.txt
```

### 2. Start the FastAPI Backend API

Run the FastAPI backend server on `http://127.0.0.1:8000`:

```bash
uvicorn backend.main:app --reload --port 8000
```

*(Note: The database tables and initial sample data for admin, student, and events will be created automatically on initial startup!)*

### 3. Start the Streamlit Frontend UI

In a new terminal window (with virtual environment activated):

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🔑 Demo Login Credentials

- **Student Login:**
  - **Email:** `tejo@gmail.com`
  - **Password:** `student123`

- **Admin / Organizer Login:**
  - **Email:** `admin@college.edu`
  - **Password:** `admin123`

---

## 🧠 Recommendation Algorithm Explanation

The recommendation system implements a **Content-Based Filtering** algorithm:
1. **User Profile Mapping:** Student interest selections (e.g. `["AI & Machine Learning", "Coding", "Hackathons"]`) are converted into normalized keyword tokens.
2. **Event Attribute Processing:** Event attributes (Category, Tags, Name, Description) are extracted into feature sets.
3. **Similarity Calculation:** The system calculates keyword overlap, category match weight, and tag alignment ratio relative to student interests.
4. **Scoring & Ranking:** Computes a normalized match score between 0.0 and 1.0, formatted as a match percentage (e.g. `🔥 85% Match`), and ranks events from highest to lowest score.
