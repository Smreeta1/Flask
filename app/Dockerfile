# Use the official Python image from the Docker Hub
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8008

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV SECRET_KEY=SECRET_KEYY
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

