#!/bin/sh

set -e
#pause this job as there is no need for db container

python manage.py collectstatic --noinput
python manage.py migrate


uwsgi --socket :9000 --workers 4 --master --enable-threads --module african_genomics_medicine_portal.wsgi