FROM python:3.12-slim
WORKDIR /agmp

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Accept build arguments without defaults for sensitive information
ARG DB_HOST=localhost
ARG DB_PORT=5432
ARG DB_NAME
ARG DB_USER
ARG DB_PASS

# Set environment variables from build arguments
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ENV DB_PASS=${DB_PASS}

# Install basic dependencies first
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg \
    ca-certificates \
    curl \
    && apt-get clean

# Install core system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    python3-dev \
    && apt-get clean

# Install application-specific packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    graphviz \
    postgresql-client \
    netcat-openbsd \
    vim \
    && apt-get clean

# Install GDAL packages separately (often problematic)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Find and explicitly verify GDAL library paths
RUN ldconfig && \
    GDAL_PATH=$(ldconfig -p | grep libgdal | awk '{print $4}' | head -1) && \
    if [ -z "$GDAL_PATH" ]; then \
        GDAL_PATH=$(find /usr -name "libgdal.so*" | head -1); \
    fi && \
    echo "GDAL Path: $GDAL_PATH" && \
    GEOS_PATH=$(ldconfig -p | grep libgeos_c | awk '{print $4}' | head -1) && \
    if [ -z "$GEOS_PATH" ]; then \
        GEOS_PATH=$(find /usr -name "libgeos_c.so*" | head -1); \
    fi && \
    echo "GEOS Path: $GEOS_PATH" && \
    echo "export GDAL_LIBRARY_PATH=$GDAL_PATH" > /etc/profile.d/gdal.sh && \
    echo "export GEOS_LIBRARY_PATH=$GEOS_PATH" >> /etc/profile.d/gdal.sh && \
    chmod +x /etc/profile.d/gdal.sh && \
    . /etc/profile.d/gdal.sh

# Create symbolic links to ensure libraries are found - using architecture-independent path
RUN mkdir -p /usr/lib/ && \
    GDAL_PATH=$(ldconfig -p | grep libgdal | awk '{print $4}' | head -1) && \
    if [ -n "$GDAL_PATH" ]; then \
        ln -sf $GDAL_PATH /usr/lib/libgdal.so; \
    fi && \
    GEOS_PATH=$(ldconfig -p | grep libgeos_c | awk '{print $4}' | head -1) && \
    if [ -n "$GEOS_PATH" ]; then \
        ln -sf $GEOS_PATH /usr/lib/libgeos_c.so; \
    fi

# Set GDAL environment variables with architecture-independent paths
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install GDAL Python bindings via pip for better compatibility
RUN pip install GDAL==$(gdal-config --version) --no-cache-dir

# Copy project
COPY . .

# Create a script to wait for PostgreSQL
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
until PGPASSWORD=$DB_PASS psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "\\q"; do\n\
    >&2 echo "PostgreSQL is unavailable - sleeping"\n\
    sleep 1\n\
done\n\
\n\
>&2 echo "PostgreSQL is up - executing command"\n\
exec "$@"' > /wait-for-postgres.sh && chmod +x /wait-for-postgres.sh

# Make django user
RUN useradd -ms /bin/bash django_user

# Create static directory with proper permissions
RUN mkdir -p /agmp/static_cdn && chown -R django_user:django_user /agmp/static_cdn
RUN chown -R django_user:django_user /agmp

USER django_user

# Wait for PostgreSQL to be available before running command
ENTRYPOINT ["/wait-for-postgres.sh"]
CMD ["gunicorn", "african_genomics_medicine_portal.wsgi:application", "-w", "2", "-b", ":8000"]