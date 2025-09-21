## Overview

This is a FastAPI backend for managing invoices (`invoices`) linked to clients (`students`). It supports PDF generation via WeasyPrint and CSV import for bulk data ingestion. Built with SQLAlchemy, Alembic, and Docker for reproducible development and deployment.

1. Import csv, this will populate `fastapi_inserted_data` table
2. Add a new student, student's id will be auto-generated
3. Create a new račun, conveniently, you can find the student you wish by searching

## Env files

- To use live aiven postgres, you need .env.prod, which is not in the codebase

## Project structure

- `main.py` – FastAPI entry point
- `models/` – SQLAlchemy models
- `routers/` – API route definitions
- `alembic/` – Database migrations
- `import-csv-to-db.py` – CSV import script
- `docker-compose.dev.yml` – Development setup
- `docker-compose.prod.yml` – Production setup

## Running the app

### Without Docker

You may need to install dependencies first
.\venv\Scripts\activate
uvicorn.exe main:app --reload

### With Docker

#### Development

docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up

#### Production

docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up

## CSV import (new)

```

docker-compose up

```

and in another terminal

```

docker-compose exec fastapi python import-csv-to-db.py --env dev

```

it will generate some temporary fake student_id

## Installing dependencies

- `apt-get` – System-level packages (OS, binaries), compilers, database clients, C libs
- `pip` – Python packages for your app (FastAPI, Alembic, SQLAlchemy, etc.)
- `pip freeze > requirements.txt` – May produce too many dependencies; use carefully

### Example

```

./venv/bin/pip install weasyprint

```

## Changes in table definitions

### Create a new migration

You need to run migrations with Alembic. Make sure you're inside the virtual environment:

```

./venv/bin/alembic revision --autogenerate -m "Add new table"

```

### Apply migration

```

./venv/bin/alembic upgrade head

```

Make sure your models are imported in `alembic/env.py`.

## Testing

Not implemented.

## Deployment notes

- Production image is tagged as `fastapi-app:prod`
- Healthcheck endpoint: `/health`
- PDF generation uses WeasyPrint (requires system libraries)
- Database must support SSL (e.g. Aiven PostgreSQL)

# TODO

- Importing multiple times the same csv currently is not notifying the user
- add time

```

```
