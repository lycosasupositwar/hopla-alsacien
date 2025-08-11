# ---- Builder Stage ----
# This stage installs dependencies into a virtual environment.
FROM python:3.9 as builder

# Set the working directory
WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install them into the venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Final Stage ----
# This stage copies the application and the venv from the builder.
FROM python:3.9-slim-bullseye

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY src/ ./src/

# Set the path to use the venv's python
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV QT_X11_NO_MITSHM=1

# Run the application
CMD ["python", "src/main.py"]
