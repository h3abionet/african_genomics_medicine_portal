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
# Database settings
DB_NAME=database-name
DB_USER=db-user
DB_PASS=pdb-pass
DB_PORT=port_number
SECRET_KEY=django-secret-key
# CSRF settings
CSRF_TRUSTED_ORIGINS=https://domain-name.org
# Host settings
ALLOWED_HOSTS=domain-name.org
SITE_DOMAINS=domain-name.org
```

## Running with Docker

### Development Environment

Development mode features hot-reloading and runs on port 8000.
```bash
# Start services
docker compose -f docker-compose-dev.yml up -d

# Run migrations
docker exec agmp_django_dev python manage.py migrate

# Create superuser (optional)
docker exec -it agmp_django_dev python manage.py createsuperuser

# Load data
docker exec agmp_django_dev python manage.py load_data

# Seed ontology configuration (see Ontology Mapping section below)
docker exec agmp_django_dev python manage.py seed_ontology_config

# Quality control check
docker exec agmp_django_dev python manage.py quality_control
```

**Access the app:** http://localhost:8000

**View logs:**
```bash
docker logs -f agmp_django_dev
```

**Stop services:**
```bash
docker compose -f docker-compose-dev.yml down
```

### Production Environment

Production mode uses Gunicorn with Nginx. Migrations run automatically on container start.
```bash
# Start services
docker compose -f docker-compose-prod.yml up -d

# Load data
docker exec agmp_django python manage.py load_data

# Seed ontology configuration
docker exec agmp_django python manage.py seed_ontology_config

# Quality control check
docker exec agmp_django python manage.py quality_control
```

**Access the app:** https://your-domain.com (configured in Nginx)

**Stop services:**
```bash
docker compose -f docker-compose-prod.yml down
```

### Running Both Environments Simultaneously

Dev and prod can run together on the same machine using different ports and container names:

| Environment | URL | Containers |
|-------------|-----|------------|
| Development | http://localhost:8000 | `agmp_*_dev` |
| Production | http://localhost:8080 (or domain) | `agmp_*` |
```bash
# Start both
docker compose -f docker-compose-dev.yml up -d
docker compose -f docker-compose-prod.yml up -d

# Stop both
docker compose -f docker-compose-dev.yml down
docker compose -f docker-compose-prod.yml down
```

---

## Ontology Mapping

The portal uses ontology mapping to enhance search for **phenotypes/diseases** and **drugs**. When a user searches for a common term like "heart attack", the system automatically resolves it to the canonical medical term ("myocardial infarction"), its synonyms, and its subtypes — returning all relevant results from the database.

This feature is powered by the [EMBL-EBI OLS4 API](https://www.ebi.ac.uk/ols4/) (Ontology Lookup Service), a free public API that provides access to over 270 biomedical ontologies. No API key is required.

### How It Works

```
User searches: "heart attack"
         │
         ▼
┌─────────────────────────────────────────────────┐
│  OLS4 API resolves to:                          │
│                                                 │
│  Canonical:  Myocardial infarction              │
│  Synonyms:   heart attack, cardiac infarction,  │
│              MI                                 │
│  Children:   ↳ Acute myocardial infarction      │
│              ↳ ST-elevation MI (STEMI)           │
│              ↳ Non-ST-elevation MI (NSTEMI)      │
└─────────────────────────────────────────────────┘
         │
         ▼
  Database query matches ALL of these names
  against the phenotypeagmp__name field
```

### Term Types

| Type | Description | Example |
|------|-------------|---------|
| **Canonical match** | The official standardised name in the ontology | "Myocardial infarction" |
| **Synonym** | Alternative names for the same concept | "heart attack", "cardiac infarction", "MI" |
| **Child term** | A more specific subtype in the ontology hierarchy | "Acute myocardial infarction", "STEMI" |

### Ontology Sources

The system queries these ontologies depending on what the user is searching for:

**Phenotype / Disease searches:**

| OLS ID | Name | What it covers |
|--------|------|----------------|
| `mondo` | MONDO Disease Ontology | Unified disease ontology integrating multiple sources |
| `doid` | Disease Ontology | Standardised disease classifications and subtypes |
| `hp` | Human Phenotype Ontology | Observable signs, symptoms, and measurable traits |
| `efo` | Experimental Factor Ontology | Experimental variables used in GWAS Catalog |

**Drug searches:**

| OLS ID | Name | What it covers |
|--------|------|----------------|
| `chebi` | ChEBI Chemical Entities | Chemical compounds, drug synonyms, IUPAC names |

### Where Ontology is Used

| Feature | Variant | Gene | Drug | Phenotype |
|---------|---------|------|------|-----------|
| Search page | No | No | **Yes** | **Yes** |
| Batch query | No | No | **Yes** | **Yes** |

Variant and gene searches use direct database lookups only (no ontology resolution).

### Setup

#### 1. Migrations

The ontology feature requires three new database tables.

**Development** (migrations run manually):
```bash
docker exec agmp_django_dev python manage.py makemigrations agmp_app
docker exec agmp_django_dev python manage.py migrate
```

**Production** (migrations run automatically on container start via the `command` in `docker-compose-prod.yml`, so no manual step is needed unless you've added new model changes after the container is already running):
```bash
# Only if needed after the container is already up
docker exec agmp_django python manage.py migrate
```

#### 2. Seed Configuration Data

The management command populates the ontology sources and field mappings. This must be run **after** migrations, and is safe to run multiple times (`get_or_create`).

**Development:**
```bash
# Seed ontology config
docker exec agmp_django_dev python manage.py seed_ontology_config

# Preview what would be created (no changes)
docker exec agmp_django_dev python manage.py seed_ontology_config --dry-run

# Reset and re-seed (deletes existing config first)
docker exec agmp_django_dev python manage.py seed_ontology_config --reset
```

**Production:**
```bash
# Seed ontology config
docker exec agmp_django python manage.py seed_ontology_config

# Preview what would be created (no changes)
docker exec agmp_django python manage.py seed_ontology_config --dry-run

# Reset and re-seed (deletes existing config first)
docker exec agmp_django python manage.py seed_ontology_config --reset
```

> **Note:** The seed command is intentionally not part of the automatic container startup. Ontology config rarely changes, and running it automatically on every restart would add unnecessary overhead. Run it once after initial deployment and again only when updating ontology sources.

#### 3. Verify

```bash
# Development
docker exec agmp_django_dev python manage.py shell -c "
from agmp_app.models import OntologyConfig, SearchFieldMapping
print(f'OntologyConfig: {OntologyConfig.objects.count()} rows')
print(f'SearchFieldMapping: {SearchFieldMapping.objects.count()} rows')
"

# Production
docker exec agmp_django python manage.py shell -c "
from agmp_app.models import OntologyConfig, SearchFieldMapping
print(f'OntologyConfig: {OntologyConfig.objects.count()} rows')
print(f'SearchFieldMapping: {SearchFieldMapping.objects.count()} rows')
"
```

Expected output: `OntologyConfig: 5, SearchFieldMapping: 4`.

### Admin Configuration

All ontology behaviour is configurable through the Django admin at `/admin/` without code changes:

**Ontology Sources** (`/admin/agmp_app/ontologyconfig/`):

| Setting | Description | Default |
|---------|-------------|---------|
| `enabled` | Toggle this ontology on/off | `True` |
| `priority` | Lower number = searched first | `1-4` |
| `expand_children` | Include child terms (subtypes) in results | `True` for phenotype, `False` for drug |
| `child_depth` | How many hierarchy levels to walk (1 = direct children, 2 = grandchildren) | `1` |
| `max_search_hits` | Max OLS4 results to process per query | `5` |
| `max_children` | Max child terms to fetch per hit | `30` |
| `cache_duration` | How long to cache OLS4 responses in seconds | `86400` (24h) |

**Field Mappings** (`/admin/agmp_app/searchfieldmapping/`):

| Setting | Description |
|---------|-------------|
| `lookup_field` | Django ORM field path (e.g. `phenotypeagmp__name`) |
| `lookup_type` | Django lookup: `iexact`, `icontains`, `exact` |
| `is_fallback` | If checked, matches raw user input loosely when ontology finds nothing |

**Adding a new ontology**: click "Add" in the OntologyConfig admin, enter the OLS4 ontology ID (e.g. `ordo` for Orphanet Rare Disease Ontology), set the category, and save.

**Disabling child term expansion**: uncheck `expand_children` for any ontology, or set `child_depth` to `0`.

**Disabling ontology entirely for a category**: uncheck `enabled` on all ontologies in that category. The search falls back to plain `icontains` matching.

### Architecture

```
agmp_app/
├── ontology_resolver.py          # OLS4 API client and Q builder
├── models.py                     # OntologyConfig, SearchFieldMapping, OxOMapping
├── admin.py                      # Admin registration for config models
├── views.py                      # search_view and batch query use resolver
└── management/
    └── commands/
        └── seed_ontology_config.py   # Seed script
```

Key files:

- **`ontology_resolver.py`** — The `OntologyResolver` class reads config from the database, queries OLS4, walks child hierarchies, and builds Django `Q()` objects. All behaviour is driven by the `OntologyConfig` and `SearchFieldMapping` tables.
- **`views.py`** — `search_view`, `query_drug_data`, and `query_phenotype_data` instantiate the resolver. If it fails or is unavailable, they fall back silently to direct database lookups.
- **`seed_ontology_config.py`** — Management command that populates the config tables. Safe to run multiple times (uses `get_or_create`). Supports `--dry-run` to preview changes and `--reset` to wipe and re-seed.

### Troubleshooting

**Ontology not working (no expansion shown):**
```bash
# Check config is seeded
docker exec agmp_django_dev python manage.py shell -c "
from agmp_app.models import OntologyConfig, SearchFieldMapping
print(f'OntologyConfig: {OntologyConfig.objects.count()}')
print(f'SearchFieldMapping: {SearchFieldMapping.objects.count()}')
"
# If 0 rows, run: python manage.py seed_ontology_config
```

**Container can't reach OLS4 API:**
```bash
docker exec agmp_django_dev python -c "
import requests
r = requests.get('https://www.ebi.ac.uk/ols4/api/search', params={'q':'diabetes','ontology':'doid','rows':1}, timeout=10)
print(f'Status: {r.status_code}')
"
# If blocked, check container network/firewall settings
```

**Search is slow for phenotype queries:**
- Reduce `max_search_hits` (fewer OLS4 results to process)
- Set `expand_children` to `False` (skip hierarchy walking)
- Increase `cache_duration` (results cached longer between identical searches)
- All configurable via Django admin, no restart needed

**Too many irrelevant results:**
- Set `child_depth` to `0` (disable hierarchy expansion, keep synonyms)
- Disable HP ontology if trait-level results are unwanted (uncheck `enabled`)
- Lower `priority` for noisy ontologies so they contribute fewer results

---

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
python manage.py seed_ontology_config
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
docker exec agmp_django_dev python manage.py seed_ontology_config
docker exec agmp_django_dev python manage.py quality_control

# Production
docker exec agmp_django python manage.py load_data
docker exec agmp_django python manage.py seed_ontology_config
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
├── docker-compose-dev.yml        # Development Docker configuration
├── docker-compose-prod.yml       # Production Docker configuration
├── nginx.conf                    # Nginx configuration
├── Dockerfile                    # Django application Dockerfile
├── .env                          # Environment variables
└── agmp_app/                     # Main application
    ├── ontology_resolver.py      # OLS4 API client for synonym resolution
    ├── models.py                 # Django models (incl. OntologyConfig)
    ├── admin.py                  # Admin config (incl. ontology admin)
    ├── views.py                  # Views with ontology-enhanced search
    ├── templates/
    │   ├── search_list_template.html   # Search page with ontology panel
    │   └── batch_query.html            # Batch query with ontology hints
    └── management/
        └── commands/
            ├── load_data.py              # Data import script
            └── seed_ontology_config.py   # Ontology config seeder
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
docker logs -f agmp_nginx_dev

# Production
docker logs -f agmp_django
docker logs -f agmp_postgres
docker logs -f agmp_nginx
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
- [EMBL-EBI OLS4 API Documentation](https://www.ebi.ac.uk/ols4/docs/api)

### Paid Resources

- [William Vincent](https://wsvincent.com/)
- [Docker and Kubernetes: The Complete Guide - Udemy](https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/)