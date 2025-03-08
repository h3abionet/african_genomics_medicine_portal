# syntax=docker/dockerfile:1
FROM python:3

# Prevents Python from writing .pyc files and ensures output is flushed
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    libgdal-dev \
    gdal-bin \
    build-essential \
    vim \
    nano \
    cmake \
    g++

# Set environment variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Upgrade pip
RUN python -m pip install -U pip

# Create project directory and set permissions
RUN mkdir -p /agmp
WORKDIR /agmp

# Copy requirements file first to leverage Docker caching
COPY requirements.txt /agmp

# Create a dedicated user for running Django
RUN useradd --no-log-init --uid 9999 --create-home --shell /bin/bash django_user

# Change ownership of the project directory
RUN chown -R django_user:django_user /agmp

# Switch to the Django user
USER django_user
ENV PATH="/home/django_user/.local/bin:${PATH}"

# Install Python dependencies
RUN python -m pip install -r requirements.txt

# Copy project files with correct ownership
COPY --chown=django_user:django_user . /agmp

# Ensure database directory and migrations folder are writable
RUN mkdir -p /agmp/db && chmod -R 775 /agmp/db
RUN mkdir -p /agmp/migrations && chmod -R 775 /agmp/migrations

# Ensure db.sqlite3 exists and is writable
RUN touch /agmp/db.sqlite3 && chmod 664 /agmp/db.sqlite3 && chown django_user:django_user /agmp/db.sqlite3

# Run migrations and collect static files
RUN python manage.py migrate
RUN python manage.py collectstatic --no-input

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
