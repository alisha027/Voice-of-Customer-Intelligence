FROM python:3.13-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend and dataset
COPY backend /app/backend
COPY data /app/data

# Set Python import path
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]