# ---- Builder Stage ----
# This stage installs build-time dependencies and compiles the Python packages.
FROM python:3.9-alpine as builder

# Enable the community repository for more packages
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

# Install build-time system dependencies for the Python packages
# This includes compilers, headers, and development libraries.
RUN apk add --no-cache \
    build-base \
    cmake \
    linux-headers \
    gfortran \
    openblas-dev \
    freetype-dev \
    pkgconfig \
    jpeg-dev \
    zlib-dev \
    tiff-dev \
    libpng-dev \
    qt5-qtbase-dev

# Create a virtual environment for clean dependency management
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python packages into the virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Final Stage ----
# This stage creates the final, lightweight image.
FROM python:3.9-alpine

# Enable the community repository for runtime packages
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

# Install only the run-time system dependencies
RUN apk add --no-cache \
    openblas \
    freetype \
    libjpeg-turbo \
    tiff \
    libpng \
    qt5-qtbase

# Set the working directory
WORKDIR /app

# Copy the virtual environment (with compiled packages) from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY src/ ./src/

# Set environment variables for the application to run
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app
# This is often needed for running Qt apps in Docker
ENV QT_QPA_PLATFORM=offscreen

# Run the application
CMD ["python", "src/main.py"]
