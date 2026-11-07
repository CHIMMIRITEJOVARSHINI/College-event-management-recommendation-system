# 🎓 College Event Management & Recommendation System

A full-stack web application designed for colleges and universities to enable students to discover, search, register for, and receive personalized recommendations for campus events, while providing college administrators with tools to manage events and track registrations.

---

## 🌟 Key Features

### 🎒 Student Features
- **Account Registration & Login**: Profile creation with college, department, year, and passions/interests selection.
- **Personalized Recommendation System**: Content-based matching algorithm that ranks events based on student interests and shows matching scores (`🔥 85% Match`) and matched tags.
- **Event Discovery & Filtering**: Live search by name/keywords and filters by category, venue, and organizer.
- **Event Registration**: One-click event registration with maximum capacity limits and duplicate registration prevention.
- **My Events**: Dedicated view to track registered events with quick cancellation options.

### 👑 Admin / Event Organizer Features
- **Dashboard Analytics**: Real-time metrics on total events, student count, total registrations, and upcoming events.
- **Event Management (CRUD)**: Create new events with venue, time, categories, participant limits, deadlines, and images; delete outdated events.
- **Registrations Directory**: Searchable list of all registered attendees with student contact information, department, year, and registration timestamps.

---

## 🏗️ Architecture & Technology Stack

- **Frontend**: Streamlit (Python) with custom CSS styling and responsive layouts.
- **Backend**: FastAPI RESTful API.
- **Database**: SQLite with SQLAlchemy ORM.
- **Recommendation Engine**: Content-based filtering algorithm with keyword and category token matching.

```
college-event-recommendation/
│
├── app.py                     # Streamlit Frontend Web App
│
├── backend/
│   ├── main.py                # FastAPI endpoints & seed logic
│   ├── database.py            # SQLite & SQLAlchemy engine setup
│   ├── models.py              # User, Event, and Registration DB models
│   ├── schemas.py             # Pydantic validation schemas
│   ├── auth.py                # Password hashing and authentication
│   ├── recommendation.py      # Content-based recommendation algorithm
│   └── requirements.txt       # Project dependencies
│
├── data/
│   └── events.db              # SQLite Database
│
└── README.md
```

---

## 🚀 How to Run

### 1. Start the FastAPI Backend
Open a terminal in the project directory:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

* Backend API will run at: **http://127.0.0.1:8000**
* Interactive Swagger Docs: **http://127.0.0.1:8000/docs**

### 2. Start the Streamlit Frontend
Open another terminal:

```bash
python -m streamlit run app.py --server.port 8501
```

* Frontend Web App will run at: **http://localhost:8501**

---

## 💡 Demo Credentials

- **Student Account**:
  - Email: `tejo@gmail.com`
  - Password: `student123`
- **Admin Account**:
  - Email: `admin@college.edu`
  - Password: `admin123`
