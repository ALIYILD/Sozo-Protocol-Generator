FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY src/ ./src/
COPY sozo_knowledge/ ./sozo_knowledge/
COPY configs/ ./configs/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY data/ ./data/
COPY templates/ ./templates/

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "sozo_api.server:app", "--host", "0.0.0.0", "--port", "8000"]
