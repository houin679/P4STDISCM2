
## To install dependencies, using pnpm is recommended, but npm will work too

### Using pnpm
pnpm install

### Using npm
npm install

## Starting the development server

### Using pnpm 
pnpm dev

### Using npm
npm run dev

Then open the displayed loalhost or network URL to view the website.

## Backend
run this on a separate console from the frontend
1. Virtual environment
   - Create virtual environment: `python -m venv venv`
   - Activate virtual environment: `venv\Scripts\Activate.ps1 `
2. Install dependencies (run from the project root)
   - `python -m pip install -r requirements.txt`
3. Start each service (run each of these in a different terminal from the project root)
   - `python -m services.users_service.service`
   -  `python -m services.course_service.service`
   -  `python -m services.enrollment_service.service`
   -  `python -m services.grades_service.service`
   -  `python -m services.auth_service.service`
4. Start the backend server
   - `uvicorn backend.app.main:app --reload --port 8501`
5. Start the frontend (run from the frontend folder)
   - `npm run dev`






