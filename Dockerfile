# ── Stage 1: Build React Frontend ─────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /frontend

# Copy React package files and install dependencies
COPY smartagri-react/package*.json ./
RUN npm install

# Copy React source code and compile production assets
COPY smartagri-react/ ./
RUN npm run build

# ── Stage 2: Python Backend with TensorFlow ───────────────
FROM python:3.12-slim
WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python ML dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application and models
COPY . .

# Copy compiled React frontend into the Flask static distribution path
COPY --from=frontend-builder /frontend/dist ./smartagri-react/dist

# Render port configuration
ENV PORT=10000
ENV PYTHONUNBUFFERED=1
EXPOSE 10000

# Start production Gunicorn server dynamically bound to $PORT
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 2 --timeout 180 app:app"]