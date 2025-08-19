# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for WeasyPrint
# WeasyPrint needs Pango, Cairo, and GDK-PixBuf for rendering
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8050

# Define environment variables
ENV MODULE_NAME="app.main"
ENV VARIABLE_NAME="app"
ENV GUNICORN_CMD_ARGS="--workers 4 --bind 0.0.0.0:8050"

# Run app.main:app when the container launches
CMD exec gunicorn "$MODULE_NAME:$VARIABLE_NAME" $GUNICORN_CMD_ARGS
