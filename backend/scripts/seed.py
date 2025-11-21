r"""Seed script for populating the database with sample data.

This script creates sample users (student, faculty, admin) and a sample course.
It's designed to work when run directly (python backend\scripts\seed.py) or as
a module (python -m backend.scripts.seed).

Usage:
    # From repository root, with venv activated:
    python backend\scripts\seed.py
    
    # or using module form (preferred):
    python -m backend.scripts.seed
"""

import sys
from pathlib import Path

# Insert repository root into sys.path so relative imports work.
# This allows the script to run as:
#   python backend\scripts\seed.py
# or:
#   python -m backend.scripts.seed
# Without needing the backend package to be installed.
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def main():
    """Initialize database and populate with sample data."""
    from backend.app.database import SessionLocal, init_db
    from backend.app import crud, schemas
    
    # Initialize database tables
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Get a database session
    db = SessionLocal()
    
    try:
        # Define sample users
        sample_users = [
            schemas.UserCreate(
                username="student1",
                email="student1@example.com",
                password="pass123",  # Keep passwords short (bcrypt max 72 bytes)
                role="student"
            ),
            schemas.UserCreate(
                username="faculty1",
                email="faculty1@example.com",
                password="pass123",
                role="faculty"
            ),
            schemas.UserCreate(
                username="admin1",
                email="admin1@example.com",
                password="pass123",
                role="course_audit_admin"
            ),
        ]
        
        # Create users if they don't exist
        print("\nCreating sample users...")
        for user_create in sample_users:
            existing_user = crud.get_user_by_username(db, user_create.username)
            if existing_user:
                print(f"  ⊘ User '{user_create.username}' already exists (skipped)")
            else:
                user = crud.create_user(db, user_create)
                print(f"  ✓ Created user: {user.username} (role: {user.role})")
        
        # Create sample course
        print("\nCreating sample course...")
        from backend.app.models import Course
        
        course_data = schemas.CourseCreate(
            code="CS101",
            name="Intro to Programming",
            instructor="Dr. Smith",
            capacity=50
        )
        
        # Check if course already exists
        existing_course = db.query(Course).filter(Course.code == course_data.code).first()
        if existing_course:
            print(f"  ⊘ Course '{course_data.code}' already exists (skipped)")
        else:
            course = crud.create_course(db, course_data)
            print(f"  ✓ Created course: {course.code} - {course.name}")
        
        print("\n✓ Seeding complete!")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
