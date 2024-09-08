FROM python:3.11.3-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
# CMD ["python", "app.py",]
CMD ["python", "visit_count.py"]
