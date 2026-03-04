FROM python:3.11-slim
WORKDIR /app

# Copy from the 'backend' folder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy from the 'frontend' folder (at the root)
COPY frontend ./frontend

# Copy the 'app' folder from inside 'backend'
COPY backend/app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
