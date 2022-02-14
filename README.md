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


### Data import for genes
* python3 manage.py import_from_drug_csv /Users/perceval/que/dummy_data/drugs.csv --verbosity=3

### Data import for drugs
* python3 manage.py import_from_drug_csv /Users/perceval/que/dummy_data/drugs.csv --verbosity=3

### Data import for snps