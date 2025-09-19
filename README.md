## Overview

This is a FastAPI backend for managing invoices (`računi`) linked to clients (`stranke`). It supports PDF generation via WeasyPrint and CSV import for bulk data ingestion. Built with SQLAlchemy, Alembic, and Docker for reproducible development and deployment.

1. Import csv, this will populate `fastapi_inserted_data` table
2. Add a new student, student's id will be auto-generated
3. Create a new račun, conveniently, you can find the student you wish by searching

## Env files

- To use local postgres, rename env.dev.example to .env.dev
- To use live aiven postgres, you need .env.prod, which is not in the codebase

## Project structure

- `main.py` – FastAPI entry point
- `models/` – SQLAlchemy models
- `routers/` – API route definitions
- `alembic/` – Database migrations
- `import-csv-to-db.py` – CSV import script
- `docker-compose.yml` – Development setup
- `docker-compose.prod.yml` – Production setup
- `docker-compose.override.yml` – Continue reading...

## Docker Compose override

By default, Docker Compose automatically loads `docker-compose.override.yml` alongside `docker-compose.yml`. This is useful for local development overrides (e.g. mounting volumes, enabling debug mode, or exposing ports).

If you're using `docker-compose.prod.yml` for production, you don't need to care about the override file.

## Running the app

### Without Docker

You may need to install dependencies first
.\venv\Scripts\activate
uvicorn.exe main:app --reload

### With Docker

#### Development

docker-compose up --build

#### Production

docker-compose -f docekr-compose.prod.yml build
docker-compose -f docekr-compose.prod.yml up

## CSV import (new)

```

docker-compose up

```

and in another terminal

```

docker-compose exec fastapi python import-csv-to-db.py --env dev

```

it will generate some temporary fake student_id

## CSV import (old)

Currently you have to import the `.csv` files manually by running:

```

import-csv-to-db.py

```

It will "link" the CSV data with `student` based on the number in the `.csv` filename.

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
