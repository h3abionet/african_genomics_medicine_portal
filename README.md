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

Required environment variables:
```env
DB_NAME=agmp
DB_USER=postgres
DB_PASS=your_password
SECRET_KEY=your_secret_key
DEBUG=False
```

## Running with Docker

### Development Environment

Development mode features hot-reloading and runs on port 8080.
```bash
# Start services
docker compose -f docker-compose.dev.yml up -d

# Run migrations
docker exec agmp_django_dev python manage.py migrate

# Create superuser (optional)
docker exec -it agmp_django_dev python manage.py createsuperuser

# Load data
docker exec agmp_django_dev python manage.py load_data

# Quality control check
docker exec agmp_django_dev python manage.py quality_control
```

**Access the app:** http://localhost:8080

**View logs:**
```bash
docker logs -f agmp_django_dev
```

**Stop services:**
```bash
docker compose -f docker-compose.dev.yml down
```

### Production Environment

Production mode uses Gunicorn with Caddy for HTTPS.
```bash
# Start services
docker compose -f docker-compose.prod.yml up -d

# Run migrations (if needed)
docker exec agmp_django python manage.py migrate

# Load data
docker exec agmp_django python manage.py load_data

# Quality control check
docker exec agmp_django python manage.py quality_control
```

**Access the app:** https://your-domain.com (configured in `Caddyfile.prod`)

**Stop services:**
```bash
docker compose -f docker-compose.prod.yml down
```

### Running Both Environments Simultaneously

Dev and prod can run together on the same machine using different ports and container names:

| Environment | URL | Containers |
|-------------|-----|------------|
| Development | http://localhost:8080 | `agmp_*_dev` |
| Production | http://localhost (or domain) | `agmp_*` |
```bash
# Start both
docker compose -f docker-compose-dev.yml up -d
docker compose -f docker-compose-prod.yml up -d

# Stop both
docker compose -f docker-compose-dev.yml down
docker compose -f docker-compose-prod.yml down
```

## Running without Docker (Local Development)

### Creating a Virtual Environment

#### Using conda
```bash
conda create --name env_pm python=3.12
conda activate env_pm
pip install -r requirements.txt
```

#### Using virtualenv
```bash
virtualenv -p python3 env_pm
source env_pm/bin/activate
pip install -r requirements.txt
```

### Running the Application
```bash
python manage.py makemigrations agmp_app
python manage.py migrate
python manage.py runserver
```

## Common Commands

### Database Operations
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

### Data Management
```bash
# Development
docker exec agmp_django_dev python manage.py load_data
docker exec agmp_django_dev python manage.py quality_control

# Production
docker exec agmp_django python manage.py load_data
docker exec agmp_django python manage.py quality_control
```

### Generate ERD Diagram
```bash
# Development
docker exec agmp_django_dev python manage.py graph_models agmp_app -g -o agmp_app_erd.png

# Production
docker exec agmp_django python manage.py graph_models agmp_app -g -o agmp_app_erd.png
```

## Project Structure
```
├── docker-compose-dev.yml    # Development Docker configuration
├── docker-compose-prod.yml   # Production Docker configuration
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

1. The import script exists in `agmp_app/management/commands/load_data.py`
2. The script imports:
   - `first_import_job_run.csv`
   - `second_import_job_run.xlsx`
3. The import script selects the column name instead of the column number

## Other Project Files

1. ERDs, data wrangling scripts, csv files: [Google Drive](https://drive.google.com/drive/u/0/folders/17vzyy3QGL466uH5uxAXDXiCySe3rZD36)
2. Recent csv files: [Google Drive](https://drive.google.com/drive/folders/1QO1YDZQV2mj7_mwrUWxg9HZ3xKahNzqL)

## Troubleshooting

### Fix Git Large Files Issue
```bash
git lfs migrate import --include="*.csv"
```

### View Container Logs
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

### Restart Services
```bash
# Development
docker compose -f docker-compose-dev.yml restart

# Production
docker compose -f docker-compose-prod.yml restart
```

## Learning Resources

### Free Resources

- [Python Tutorial for Beginners - CoreyMS](https://www.youtube.com/watch?v=YYXdXT2l-Gg&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7)
- [Python Django Tutorial: Full-Featured Web App - CoreyMS](https://www.youtube.com/watch?v=UmljXZIypDc&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p)
- [Django ORM if you already know SQL](https://amitness.com/2018/10/django-orm-for-sql-users/)

### Paid Resources

- [William Vincent](https://wsvincent.com/)
- [Docker and Kubernetes: The Complete Guide - Udemy](https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/)