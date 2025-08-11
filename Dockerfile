# ---- Builder Stage ----
# This stage installs build-time dependencies and compiles the Python packages.
FROM python:3.9-alpine as builder

# Install build-time system dependencies for the Python packages
# This includes compilers and development headers.
RUN apk add --no-cache \
    build-base \
    cmake \
    linux-headers \
    lapack-dev \
    freetype-dev \
    pkgconfig \
    jpeg-dev \
    zlib-dev \
    qt5-qtbase-dev

# Create a virtual environment for clean dependency management
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python packages into the virtual environment
COPY requirements.txt .
# We specify the build options for PyQt5 to ensure it finds Qt.
RUN pip install --no-cache-dir -r requirements.txt

# ---- Final Stage ----
# This stage creates the final, lightweight image.
FROM python:3.9-alpine

# Install only the run-time system dependencies
RUN apk add --no-cache \
    lapack \
    freetype \
    libjpeg-turbo \
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
