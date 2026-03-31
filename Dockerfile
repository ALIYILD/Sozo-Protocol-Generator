FROM python:3.11-slim

WORKDIR /app

# System deps for lxml, matplotlib, pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/
COPY data/ ./data/
COPY configs/ ./configs/
COPY app.py .
COPY .streamlit/ ./.streamlit/
COPY pyproject.toml .

# Install the package itself
RUN pip install --no-cache-dir -e . --no-deps

ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SHARING_MODE=1

EXPOSE 8080

CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
