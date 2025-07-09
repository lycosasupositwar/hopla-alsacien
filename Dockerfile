FROM python:3.8-slim

# Install system dependencies including Qt dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Update pip and install wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

ENV PYTHONPATH=/app
ENV QT_X11_NO_MITSHM=1

EXPOSE 8080
CMD ["python", "src/main.py"]
