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

    `virtualenv -p python3 env_pm`
* activate the new virtual environment 

    `source env_pm/bin/activate`
* Install the required packages (if you have not done so already):

    `python -m pip install -r requirements.txt`

### Running the application

* clone from Github
* `python manage.py makemigrations agmp_app`
* `python manage.py migrate`
* `python manage.py runserver`

Project will now be running on the server.


### Generate PDF ERD of models
`python manage.py graph_models agmp_app -g -o erd.pdf`

### Ingest test data
`./ingest.sh`