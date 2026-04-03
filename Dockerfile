## ── Stage 1: Build React frontend ──────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --ignore-scripts 2>/dev/null || npm install
COPY frontend/ ./
RUN npm run build

## ── Stage 2: Python runtime ───────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# System deps for lxml, matplotlib, pillow, LibreOffice (PDF export)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libfreetype6-dev \
    libpng-dev \
    libreoffice-writer-nogui \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt scipy httpx

# Copy all source and data
COPY src/ ./src/
COPY sozo_knowledge/ ./sozo_knowledge/
COPY data/ ./data/
COPY configs/ ./configs/
COPY templates/ ./templates/
COPY docs/ ./docs/
COPY scripts/ ./scripts/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY app.py .
COPY .streamlit/ ./.streamlit/

# Copy built React frontend
COPY --from=frontend-build /build/dist ./frontend/dist

# Create writable dirs for runtime
RUN mkdir -p outputs/documents outputs/manifests outputs/visuals \
    reviews pilot_logs data/learned data/raw/pubmed_cache \
    data/evidence_snapshots outputs/reviews \
    data/image_cache data/images

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV DATABASE_URL=sqlite+aiosqlite:///app/sozo.db

EXPOSE 8080

CMD ["uvicorn", "sozo_api.server:app", "--host", "0.0.0.0", "--port", "8080"]
