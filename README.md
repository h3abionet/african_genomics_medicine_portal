# African Genomics Precision Medicine Portal

This is the African Genomics Medicine Portal that provides information about African genomics and variation with regards to pharmocology and disease.

## How to run:

One prerequisite is to have Python installed and have valid understanding on the language.

* create virtual environment
* `virtualenv -p python3 env_p`
* `activate the new virtual environment (source env_pm/bin/activate)`

* clone from Github
* `python manage.py makemigrations agmp_app`
* `python manage.py migrate`
* `python manage.py runserver`

Project will now be running on the server.
