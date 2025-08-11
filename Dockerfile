FROM python:3.9

# L'image python:3.9 (non-slim) contient déjà la plupart des dépendances système
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies requested by user
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Update pip and install Python packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Environment variables
ENV PYTHONPATH=/app
ENV QT_X11_NO_MITSHM=1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "src/main.py"]
