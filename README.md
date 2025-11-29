
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
2. Install dependencies
   - `python -m pip install -r backend\requirements.txt`
3. Seed the database with sample data
   - `python backend\scripts\seed.py`
4. Start the backend server
   - `uvicorn backend.app.main:app --reload --port 8501`





