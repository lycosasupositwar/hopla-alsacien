FROM python:3.9

# Set the working directory
WORKDIR /app

# Install a comprehensive set of system dependencies to ensure pip install succeeds
# This will result in a larger image, but is more robust.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For general compilation
    build-essential \
    cmake \
    pkg-config \
    # For numpy/scipy
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    # For Pillow/OpenCV image formats
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    # For OpenCV video formats and general utilities
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    # For PyQt5 GUI
    libgl1-mesa-glx \
    libegl1-mesa \
    libxkbcommon-x11-0 \
    libxcb1-dev \
    libxcb-xinerama0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-render0 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-icccm4 \
    libxcb-render-util0 \
    libxcb-xfixes0 \
    libdbus-1-3 \
    # User-requested
    libpq-dev \
    # Clean up apt cache to save space
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

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
CMD ["python", "-m", "src.main"]
