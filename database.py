"""
Database configuration and session management for Pet Adoption & Management System.
Provides SQLAlchemy engine, declarative Base, SessionLocal factory,
and FastAPI dependency get_db.
Author: Sagar / Neal (S2_Neal)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pets.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency yielding database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables if they do not exist and perform idempotent schema migrations."""
    Base.metadata.create_all(bind=engine)

    if DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            # Check pets table columns
            pet_cols_info = conn.exec_driver_sql("PRAGMA table_info(pets)").fetchall()
            pet_cols = [r[1] for r in pet_cols_info]

            if "gender" not in pet_cols:
                conn.exec_driver_sql("ALTER TABLE pets ADD COLUMN gender VARCHAR(20) DEFAULT 'Unknown'")
            if "size" not in pet_cols:
                conn.exec_driver_sql("ALTER TABLE pets ADD COLUMN size VARCHAR(20) DEFAULT 'Medium'")
            if "age_category" not in pet_cols:
                conn.exec_driver_sql("ALTER TABLE pets ADD COLUMN age_category VARCHAR(20) DEFAULT 'Adult'")

            # Check adoption_requests table columns
            req_cols_info = conn.exec_driver_sql("PRAGMA table_info(adoption_requests)").fetchall()
            req_cols = [r[1] for r in req_cols_info]

            if "user_id" not in req_cols:
                conn.exec_driver_sql("ALTER TABLE adoption_requests ADD COLUMN user_id INTEGER")

            conn.commit()

            if os.getenv("TESTING") != "1":
                pet_count = conn.exec_driver_sql("SELECT COUNT(*) FROM pets").scalar()
                if pet_count == 0:
                    try:
                        from seed_data import seed_database
                        seed_database()
                    except Exception:
                        pass
