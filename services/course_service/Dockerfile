# Use a lightweight Python image

FROM python:3.11-slim

# Set working directory inside the container

WORKDIR /app

# Copy requirements first to leverage caching

COPY ./requirements.txt ./requirements.txt

#  Install dependencies

RUN pip install --no-cache-dir -r requirements.txt

#  Copy course_service and api_gateway into the container

COPY ./services/api_gateway ./services/api_gateway
COPY ./services/course_service ./services/course_service
COPY ./proto ./proto

# Set PYTHONPATH so imports can find api_gateway

ENV PYTHONPATH=/app:/app/services

# Expose gRPC port

EXPOSE 50051

# Set working directory to course_service

WORKDIR /app/services

# Run the service

CMD ["python", "-m", "course_service.service"]