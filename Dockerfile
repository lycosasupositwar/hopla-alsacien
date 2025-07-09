FROM python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    libice6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libasound2 \
    libxkbcommon-x11-0 \
    libxcb-xinerama0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Install Python packages in order of dependency
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir opencv-python-headless==4.8.1.78
RUN pip install --no-cache-dir matplotlib==3.7.1
RUN pip install --no-cache-dir scipy==1.10.1
RUN pip install --no-cache-dir scikit-image==0.20.0
RUN pip install --no-cache-dir pandas==2.0.3
RUN pip install --no-cache-dir Pillow==10.0.0
RUN pip install --no-cache-dir openpyxl==3.1.2
RUN pip install --no-cache-dir PyQt5==5.15.9

# Copy application code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/data /app/exports

# Set environment variables
ENV PYTHONPATH=/app
ENV QT_X11_NO_MITSHM=1
ENV DISPLAY=:99

EXPOSE 8080

CMD ["python", "src/main.py"]
