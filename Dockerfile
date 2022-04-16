# syntax=docker/dockerfile:1
FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /agp

WORKDIR /agp
COPY requirements.txt /agp
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    libgdal-dev \
    gdal-bin \
    g++

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN python -m pip install -r requirements.txt

COPY . /agp

RUN python manage.py migrate
