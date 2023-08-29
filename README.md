# African Genomic Precision Medicine Portal

This is the African Genomic Medicine Portal that provides information about African genomics and variation with regards to pharmocology and disease.

## How to run:

One prerequisite is to have Python installed and have valid understanding on the language.

### Creating a virtual environment 

#### Working with conda 

Create an isolated working environment with conda.

```shell
conda create --name env_pm django-bootstrap4=1.0.1 django-crispy-forms=1.7.0 django-leaflet=0.24.0 django-agnocomplete python=3.6
```
Important: Make sure you install the aforementioned versions for the dependencies because of the compatibility reasons. 

Then activate the environment 

```
conda activate env_pm
```

#### Working with `virtualenv`
* create virtual environment
* `virtualenv -p python3 env_pm`
* `activate the new virtual environment (source env_pm/bin/activate)`
Install the following packages (if you have not done so already):
`django-bootstrap4 django-crispy-forms django-leaflet django-agnocomplete`

### Running the application

* clone from Github
* `python manage.py makemigrations agmp_app`
* `python manage.py migrate`
* `python manage.py runserver`

Project will now be running on the server.


# Screen shots of tabular presentation of PharmaGKb data

![](images/drug.png?raw=true)
![](images/snp.png?raw=true)
![](images/snp_ethnic.png?raw=true)



# Data injest from csv

* python3 manage.py runscript load_data


# Docker commands in dev 

$ docker-compose build

1. Makemigrations: 
$ docker-compose run --rm african_genomics_medicine_portal sh -c "python manage.py makemigrations"

2. Migrate: 
$ docker-compose run --rm african_genomics_medicine_portal sh -c "python manage.py migrate"

3. Create superuser: 
$ docker-compose run --rm african_genomics_medicine_portal sh -c "python manage.py createsuperuser"

4. Data injest: 
$ docker-compose run --rm african_genomics_medicine_portal sh -c "python3 manage.py runscript load_data"

$ docker-compose up


# Django operations in Docker Production environment

1. Create superuser: 
$ docker-compose -f docker-compose-deploy.yml run --rm african_genomics_medicine_portal sh -c "python manage.py createsuperuser"

2. Makemigrations: 
$ docker-compose -f docker-compose-deploy.yml run --rm african_genomics_medicine_portal sh -c "python manage.py makemigrations"

3. Migrate: 
$ docker-compose -f docker-compose-deploy.yml run --rm african_genomics_medicine_portal sh -c "python manage.py migrate"


** the /scripts directory is added to the git ignore file so all scripts will have to be manually added to the server. (load_data.py)

$ docker-compose -f docker-compose-deploy.yml run --rm african_genomics_medicine_portal sh -c "python3 manage.py runscript load_data"


# Docker in dev



# Docker in prod

$ docker-compose -f docker-compose-deploy.yml build

$ docker-compose -f docker-compose-deploy.yml up -d


# Docker containers

1. agmp_nginx_proxy_container
    - proxy
2. agmp_djangocode_container
    - this is a container with the code base
3. agmp_postgres_container
    - this is a db container


### Docker bash on container

1. $ docker exec -it container_id sh 

### Docker bash as root on a container

1.  docker exec -u 0 -it container_id sh | where 0 represents user with root priviledges

   