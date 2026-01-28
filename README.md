# African Genomic Precision Medicine Portal

This is the African Genomic Medicine Portal that provides information about African genomics and variation with regards to pharmacology and disease.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Clone the Repository
```bash
git clone https://github.com/h3abionet/african_genomics_medicine_portal.git
cd african_genomics_medicine_portal
git checkout deployed_v2_1
```

### Environment Setup

Create a `.env` file with your database credentials:
```bash
cp .env.example .env
# Edit .env with your credentials
```

<details>
<summary>Required environment variables</summary>
```env
DB_NAME=agmp
DB_USER=postgres
DB_PASS=your_password
SECRET_KEY=your_secret_key
DEBUG=False
```

</details>

## Running with Docker

### Development Environment

Development mode features hot-reloading and runs on port 8080.
```bash
# Start services
docker compose -f docker-compose.dev.yml up -d
```

**Access the app:** http://localhost:8080

<details>
<summary>Additional setup commands</summary>
```bash
# Run migrations
docker exec agmp_django_dev python manage.py migrate

# Collect static files
docker exec agmp_django_dev python manage.py collectstatic --noinput

# Create superuser (optional)
docker exec -it agmp_django_dev python manage.py createsuperuser

# Load data
docker exec agmp_django_dev python manage.py load_data

# Quality control check
docker exec agmp_django_dev python manage.py quality_control
```

</details>

<details>
<summary>View logs and stop services</summary>
```bash
# View logs
docker logs -f agmp_django_dev

# Stop services
docker compose -f docker-compose.dev.yml down
```

</details>

### Production Environment

Production mode uses Gunicorn with Caddy for HTTPS.
```bash
# Start services
docker compose -f docker-compose.prod.yml up -d
```

**Access the app:** https://your-domain.com (configured in `Caddyfile.prod`)

<details>
<summary>Additional setup commands</summary>
```bash
# Run migrations (if needed)
docker exec agmp_django python manage.py migrate

# Load data
docker exec agmp_django python manage.py load_data

# Quality control check
docker exec agmp_django python manage.py quality_control
```

</details>

<details>
<summary>Stop services</summary>
```bash
docker compose -f docker-compose.prod.yml down
```

</details>

### Running Both Environments Simultaneously

Dev and prod can run together on the same machine using different ports and container names:

| Environment | URL                          | Containers    |
| ----------- | ---------------------------- | ------------- |
| Development | http://localhost:8080        | `agmp_*_dev`  |
| Production  | http://localhost (or domain) | `agmp_*`      |

<details>
<summary>Commands</summary>
```bash
# Start both
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.prod.yml up -d

# Stop both
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.prod.yml down
```

</details>

## Running without Docker (Local Development)

<details>
<summary>Using conda</summary>
```bash
conda create --name env_pm python=3.12
conda activate env_pm
pip install -r requirements.txt
```

</details>

<details>
<summary>Using virtualenv</summary>
```bash
virtualenv -p python3 env_pm
source env_pm/bin/activate
pip install -r requirements.txt
```

</details>

<details>
<summary>Running the application</summary>
```bash
python manage.py makemigrations agmp_app
python manage.py migrate
python manage.py runserver
```

</details>

## Common Commands

<details>
<summary>Database Operations</summary>
```bash
# Development
docker exec agmp_django_dev python manage.py makemigrations
docker exec agmp_django_dev python manage.py migrate
docker exec -it agmp_django_dev python manage.py createsuperuser

# Production
docker exec agmp_django python manage.py makemigrations
docker exec agmp_django python manage.py migrate
docker exec -it agmp_django python manage.py createsuperuser
```

</details>

<details>
<summary>Data Management</summary>
```bash
# Development
docker exec agmp_django_dev python manage.py load_data
docker exec agmp_django_dev python manage.py quality_control

# Production
docker exec agmp_django python manage.py load_data
docker exec agmp_django python manage.py quality_control
```

</details>

<details>
<summary>Generate ERD Diagram</summary>
```bash
# Development
docker exec agmp_django_dev python manage.py graph_models agmp_app -g -o agmp_app_erd.png

# Production
docker exec agmp_django python manage.py graph_models agmp_app -g -o agmp_app_erd.png
```

</details>

## Project Structure
```
├── docker-compose.dev.yml    # Development Docker configuration
├── docker-compose.prod.yml   # Production Docker configuration
├── Caddyfile.local           # Caddy config for local development
├── Caddyfile.prod            # Caddy config for production
├── Dockerfile                # Django application Dockerfile
├── .env                      # Environment variables
└── agmp_app/                 # Main application
    └── management/
        └── commands/
            └── load_data.py  # Data import script
```

## Import Script Notes

<details>
<summary>Details</summary>

1. The import script exists in `agmp_app/management/commands/load_data.py`
2. The script imports:
   - `first_import_job_run.csv`
   - `second_import_job_run.xlsx`
3. The import script selects the column name instead of the column number

</details>

## Other Project Files

- ERDs, data wrangling scripts, csv files: [Google Drive](https://drive.google.com/drive/u/0/folders/17vzyy3QGL466uH5uxAXDXiCySe3rZD36)
- Recent csv files: [Google Drive](https://drive.google.com/drive/folders/1QO1YDZQV2mj7_mwrUWxg9HZ3xKahNzqL)

## Troubleshooting

<details>
<summary>Fix Git Large Files Issue</summary>
```bash
git lfs migrate import --include="*.csv"
```

</details>

<details>
<summary>View Container Logs</summary>
```bash
# Development
docker logs -f agmp_django_dev
docker logs -f agmp_postgres_dev
docker logs -f agmp_caddy_dev

# Production
docker logs -f agmp_django
docker logs -f agmp_postgres
docker logs -f agmp_caddy
```

</details>

<details>
<summary>Restart Services</summary>
```bash
# Development
docker compose -f docker-compose.dev.yml restart

# Production
docker compose -f docker-compose.prod.yml restart
```

</details>

## Learning Resources

<details>
<summary>Free Resources</summary>

- [Python Tutorial for Beginners - CoreyMS](https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7)
- [Python Django Tutorial: Full-Featured Web App - CoreyMS](https://www.youtube.com/watch?v=UmljXZIypDc&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p)
- [Django ORM if you already know SQL](https://amitness.com/2018/10/django-orm-for-sql-users/)

</details>

<details>
<summary>Paid Resources</summary>

- [William Vincent](https://wsvincent.com/)
- [Docker and Kubernetes: The Complete Guide - Udemy](https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/)

</details>