# brave-service

## Requirements

- Python 3.10 or newer
- `uv`
- Docker Desktop

## Install

```bash
git clone <repository-url>
cd brave-service
uv sync
cp .env.example .env
```

## Run the database

```bash
# Spin up database
docker compose up -d
# Apply migrations
uv run alembic upgrade head
```
To create a new migration

```bash
uv run alembic revision --autogenerate -m "Example"
# To undo a migration (latest)
uv run alembic downgrade -1
```

Other useful commands
```bash
uv run alembic history
uv run alembic current
```


To stop the database:

```bash
docker compose down
```

The local database connection is configured through `DATABASE_URL` in `.env`.


To run the backend daemon:

```bash
uv run fastapi dev src/brave_service/main.py
```

To create an administrator account, run the private provisioning command from
a trusted machine with access to the configured database:

```bash
uv run create-admin
```

The command prompts for the email and password without displaying the password.
It stores only the password hash and does not create a public registration
endpoint.

To install the dev dependencies:

```bash
uv sync --dev
```
