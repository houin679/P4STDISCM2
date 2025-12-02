from backend.app.database import SessionLocal
from backend.app import crud, schemas

def main():
    db = SessionLocal()

    student = schemas.UserCreate(
        username="teststudent",
        email="student@example.com",
        password="password123",
        role="student"
    )

    faculty = schemas.UserCreate(
        username="testfaculty",
        email="testfaculty@example.com",
        password="password123",
        role="faculty"
    )


    # crud.create_user(db, student)
    crud.create_user(db, faculty)

    db.close()

if __name__ == "__main__":
    main()

