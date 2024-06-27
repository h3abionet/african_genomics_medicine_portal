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

### Running the application in development

* clone from Github `git clone https://github.com/h3abionet/african_genomics_medicine_portal.git`
* `python manage.py makemigrations agmp_app`
* `python manage.py migrate`
* `python manage.py runserver`


### Running the application in docker production

* clone from Github 'git clone  https://github.com/h3abionet/african_genomics_medicine_portal.git'
* `vim config.py #change debug from true to false on the host machine`
* `mkdir static_cdn # inside the project directory on the host machine`
* `docker-compose build or docker-compose build`
* `docker-compose up -d or docker-compose up -d`

### Import script notes
1. The import script exist in /scripts/load_data.py.
2. To run the import script # python3 manage.py runscript load_data
3. The script imports
                <br>1.<b>first_import_job_run.csv <b> file 
               <br> 2. the second script imports a <b>second_import_job_run.xlsx</b> file
4. The import script selects the column name instead of the column number.

### Other project files
1. Other project files not limitted to ERD's, data wrangling scripts, csv files are located <a href="https://drive.google.com/drive/u/0/folders/17vzyy3QGL466uH5uxAXDXiCySe3rZD36" target="_blank">here</a>

<!-- # Screen shots of tabular presentation of PharmaGKb data -->
<!-- ![](images/drug.png?raw=true)
![](images/snp.png?raw=true)
![](images/snp_ethnic.png?raw=true) -->

### Generating and ERD Diagram

* Generates ERD for the specified agmp_app only: <br> `python3 manage.py graph_models agmp_app -g -o agmp_app_erd.png` 
* Generates ERD for all apps in the project, including the authentication model:<br> `python3 manage.py graph_models -a -g -o project_erd.png` 

### Fix the issue with git large files
* run the below within the terminal of your repository for a csv large file: <br> git lfs migrate import --include="*.csv"

<hr>      
Learning Resources for Beginers
<hr> 

1. Freely available resources
- CoreyMS. Python Tutorial for Beginners . Retrieved August 31, 2022, from [ https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7/](https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7)

- CoreyMS. Python Django Tutorial: Full-Featured Web App . Retrieved August 31, 2022, from [ https://www.youtube.com/watch?v=UmljXZIypDc&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p/](https://www.youtube.com/watch?v=UmljXZIypDc&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p)

- Chaudhary, A. (2018, October 31). Django Orm if you already know SQL. Django ORM if you already know SQL . Retrieved August 31, 2022, from [ https://amitness.com/2018/10/django-orm-for-sql-users/](https://amitness.com/2018/10/django-orm-for-sql-users/)

2. Udemy & other online resources i.e if available
- William Vincent - William Vincent. (2022). Retrieved 27 August 2022, from [https://wsvincent.com/](https://wsvincent.com/)
- Docker and Kubernetes: The Complete Guide. (2022). Retrieved 27 August 2022, from [UDEMY](https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/?LSNPUBID=JVFxdTr9V80&ranEAID=JVFxdTr9V80&ranMID=39197&ranSiteID=JVFxdTr9V80-FPVFIipzqssQR0YfZDpoHA&utm_medium=udemyads&utm_source=aff-campaign)
