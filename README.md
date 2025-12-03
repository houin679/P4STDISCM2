## How to run
1. Install Docker for Desktop
2. Start the backend
   - From the project root, run `docker-compose up --build`
3. Add sample data
   - From the project root, run `docker-compose exec api_gateway python -m services.api_gateway.scripts.seed`
4. Start the frontend (run from the frontend folder)
   - Install dependencies (only needed once) `npm install`
   - Run the frontend `npm run dev`








