## How to run
1. Virtual environment (run from the project root)
   - Create virtual environment: `python -m venv venv`
   - Activate virtual environment: `venv\Scripts\activate `
2. Install backend dependencies (run from the project root)
   - `python -m pip install -r requirements.txt`
3. Install frontend dependencies (run from the frontend folder)
   - `npm install`
3. Start each service (run each of these in a different terminal and make sure they're on the project root with the venv activated)
   - `python -m services.users_service.service`
   -  `python -m services.course_service.service`
   -  `python -m services.enrollment_service.service`
   -  `python -m services.grades_service.service`
   -  `python -m services.auth_service.service`
4. Start the backend server (run from the project root)
   - `uvicorn backend.app.main:app --reload --port 8501`
5. Start the frontend (run from the frontend folder)
   - `npm run dev`







