FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY code_search_engine.py .
COPY code_index/ ./code_index/

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/')" || exit 1

# Set environment variables
ENV FLASK_APP=code_search_engine.py
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "-c", "from code_search_engine import app, search_engine; search_engine.load_index(); app.run(host='0.0.0.0', port=5000, threaded=True)"]