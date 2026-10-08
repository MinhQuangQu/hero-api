# Hero API — Lab 09

## Run

Create the PostgreSQL user/database from Part 0 if they do not exist:

```sql
CREATE USER app WITH PASSWORD 'secret';
CREATE DATABASE appdb OWNER app;
```

`secret` is the lab's local example password.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg://app:secret@localhost:5432/appdb"
alembic upgrade head
python -m app.seed
fastapi dev app/main.py
```

Open http://127.0.0.1:8000/docs. The seed adds 2 teams, 20 heroes and 2 missions. Running it again prints `Already seeded`.

For a new SQLite database, use `export DATABASE_URL="sqlite:///./app.db"` and the same commands. The app also defaults to this SQLite URL if DATABASE_URL is unset.

## Endpoints

- Heroes: POST/GET `/heroes`, GET/PATCH/DELETE `/heroes/{hero_id}`.
- Hero filters: `min_age`, `team_id`, `name`, `offset`, `limit` (1–100).
- Teams: POST/GET `/teams`, GET/PATCH/DELETE `/teams/{team_id}`, GET `/teams/{team_id}/heroes`.
- Missions: POST/GET `/missions`, GET/PATCH/DELETE `/missions/{mission_id}`.
- Assign a mission: POST `/heroes/{hero_id}/missions/{mission_id}` (repeat safely).
- List a hero's missions: GET `/heroes/{hero_id}/missions`.

Hero responses hide secret_name. A missing resource returns 404. Duplicate team names and deletion of a team that still has heroes return 409.

## Files

- `app/`: SQLModel models, database sessions, API endpoints and seed data.
- `requirements.txt`: Python dependencies.
- `alembic.ini` and `migrations/`: Alembic configuration and schema revisions.
- `migrations/versions/0001_create_initial_tables.py`: initial schema for a new database.
- `migrations/versions/0002_add_hero_power.py`: Part 9 migration.

Reports, answers, screenshots, ZIP files and the virtual environment are kept locally and excluded by `.gitignore`.

Verification uses an isolated local PostgreSQL instance on port 55432. Normal setup above uses port 5432.

If an existing database already has exactly the pre-power schema, inspect it before using `alembic stamp 0001`, then run `alembic upgrade head`. For a new empty database, simply run `alembic upgrade head` as shown above.
