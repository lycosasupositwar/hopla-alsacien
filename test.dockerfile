# test.dockerfile
FROM python:3.9-slim

# Install basic system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Test installation one by one
RUN pip install numpy
RUN pip install opencv-python-headless
RUN pip install matplotlib

# Simple test
CMD ["python", "-c", "import numpy, cv2, matplotlib; print('Basic packages OK')"]
