FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy api_gateway code
COPY ./services/api_gateway ./services/api_gateway
COPY ./proto ./proto

# Ensure Python can find the services folder
ENV PYTHONPATH=/app/services

# Mount database via docker-compose; no need to copy it

EXPOSE 8000

CMD ["uvicorn", "services.api_gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
