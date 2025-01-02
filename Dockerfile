# Use a Python base image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout
ENV PYTHONUNBUFFERED: 1

# Install system dependencies needed for Pillow and other packages
RUN apt-get update \
    && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose port 5000 (for Flask app)
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
