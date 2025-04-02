FROM python:3.13-slim
WORKDIR /agmp
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Accept build arguments
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG DB_USER
ARG DB_PASS
# Set environment variables from build arguments
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ENV DB_PASS=${DB_PASS}
# Install PostgreSQL client, GDAL, and other dependencies
RUN apt-get update && apt-get install -y \
postgresql-client \
netcat-openbsd \
gdal-bin \
libgdal-dev \
build-essential \
g++ \
python3-dev \
python3-gdal \
&& rm -rf /var/lib/apt/lists/*
# Find and set the correct GDAL library path
RUN find /usr -name "libgdal.so*" | head -1 > /tmp/gdal_path.txt && \
echo "export GDAL_LIBRARY_PATH=$(cat /tmp/gdal_path.txt)" >> /etc/profile.d/gdal.sh && \
find /usr -name "libgeos_c.so*" | head -1 > /tmp/geos_path.txt && \
echo "export GEOS_LIBRARY_PATH=$(cat /tmp/geos_path.txt)" >> /etc/profile.d/gdal.sh && \
chmod +x /etc/profile.d/gdal.sh && \
. /etc/profile.d/gdal.sh
# Set GDAL environment variables (will be overridden by the profile script if files are found)
ENV GDAL_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/libgeos_c.so
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy project
COPY . .
# Create a script to wait for PostgreSQL
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
until PGPASSWORD=$DB_PASS psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "\q"; do\n\
>&2 echo "PostgreSQL is unavailable - sleeping"\n\
sleep 1\n\
done\n\
\n\
>&2 echo "PostgreSQL is up - executing command"\n\
exec "$@"' > /wait-for-postgres.sh && chmod +x /wait-for-postgres.sh
# Make django user
RUN useradd -ms /bin/bash django_user
RUN chown -R django_user:django_user /agmp
USER django_user
# Wait for PostgreSQL to be available before running command
ENTRYPOINT ["/wait-for-postgres.sh"]
CMD ["gunicorn", "african_genomics_medicine_portal.wsgi:application", "-w", "2", "-b", ":8000"]
