import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# On Streamlit Cloud the project root is read-only; /tmp is always writable.
# Locally we prefer data/ inside the project root so the DB persists.
def _resolve_db_path() -> str:
    """Return a writable path for the SQLite database."""
    # Try project-local data/ directory first (works locally)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_data_dir = os.path.join(base_dir, "data")
    try:
        os.makedirs(local_data_dir, exist_ok=True)
        test_file = os.path.join(local_data_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return os.path.join(local_data_dir, "events.db")
    except (OSError, PermissionError):
        # Fallback: use /tmp (writable on Streamlit Cloud)
        tmp_dir = "/tmp/campus_events"
        os.makedirs(tmp_dir, exist_ok=True)
        return os.path.join(tmp_dir, "events.db")

DB_PATH = _resolve_db_path()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False required for SQLite in multithreaded environments
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
