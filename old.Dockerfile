
FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /agp

WORKDIR /agp

#RUN pip install django-bootstrap4 django-crispy-forms django-agnocomplete leaflet

COPY . /agp