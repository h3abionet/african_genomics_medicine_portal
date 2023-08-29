# reference a linux image to avoid associated dependancies issues with pip

FROM --platform=linux/amd64 python:3.9.13-alpine3.15


LABEL maintainer="mtrper001@myuct.ac.za"


ENV PYTHONUNBUFFERED=1
   

COPY ./requirements.txt /requirements.txt
COPY ./african_genomics_medicine_portal /african_genomics_medicine_portal
COPY ./scripts /scripts

WORKDIR /african_genomics_medicine_portal
EXPOSE 8000
RUN apk add vim
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base musl-dev linux-headers && \
    /py/bin/pip install -r /requirements.txt && \
    apk del .tmp-deps && \
    adduser --disabled-password --no-create-home -D african_genomics_medicine_portal && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R african_genomics_medicine_portal:african_genomics_medicine_portal /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts



ENV PATH="/scripts:/py/bin:$PATH"

ENV PATH="/py/bin:$PATH"

USER african_genomics_medicine_portal

CMD ["run.sh"]