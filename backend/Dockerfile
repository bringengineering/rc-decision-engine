FROM python:3.12-slim

WORKDIR /app

# System dependencies for PostGIS and WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    libgdal-dev \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Add engine to Python path
ENV PYTHONPATH="/app:/app/engine"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
