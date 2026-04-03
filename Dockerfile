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
COPY data/ ./data/
COPY configs/ ./configs/
COPY templates/ ./templates/
COPY docs/ ./docs/
COPY scripts/ ./scripts/
COPY handbooks/ ./handbooks/
COPY handbooks_partners/ ./handbooks_partners/
COPY app.py .
COPY generate_all.py .
COPY create_gold_standard_templates.py .
COPY .streamlit/ ./.streamlit/
COPY legacy/ ./legacy/

# Create writable dirs for runtime
RUN mkdir -p outputs/documents outputs/manifests outputs/visuals \
    reviews pilot_logs data/learned data/raw/pubmed_cache \
    data/evidence_snapshots outputs/reviews \
    data/image_cache data/images

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

EXPOSE 8080

CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
