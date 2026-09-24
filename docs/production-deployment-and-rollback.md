# Production Deployment, Backup, and Rollback

This runbook is for production rehearsal. PostgreSQL and Redis are mandatory runtime services; SQLite must not be used as an application fallback.

## Environment

```env
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<database>
REDIS_URL=redis://:<password>@<host>:6379/0
JWT_SECRET=<random value of at least 32 characters>
TRUSTED_HOSTS_ENABLED=true
TRUSTED_HOSTS=["admin.example.com"]
API_DOCS_ENABLED=false
VITE_DEMO_LOGIN_ENABLED=false
```

Startup rejects the default JWT secret, missing PostgreSQL/Redis, disabled Trusted Hosts, or public production API docs. Store connection strings in a protected secret manager; never place them in logs, screenshots, or Git.

## Process topology

The reverse proxy owns TLS, domain routing, and frontend static files. FastAPI listens on an internal interface. Worker and Scheduler use the same release, environment, and `background` Redis queue. Release order: build frontend, drain old Worker, run `alembic upgrade head`, start API, wait for `/api/v1/health/ready`, start Worker/Scheduler, then run the acceptance script.

## Database migration

```powershell
.venv\Scripts\python.exe -m server.app migrate --dry-run
.venv\Scripts\python.exe -m alembic upgrade head
```

Do not run manual `CREATE TABLE` or `ALTER TABLE`. If migration fails, stop the release and preserve the old application/database state; do not attempt an unverified downgrade.

## PostgreSQL backup and restore rehearsal

```powershell
pg_dump --format=custom --no-owner --file=backup.dump "$env:PRODUCTION_DATABASE_URL"
createdb fastapi_admin_restore
pg_restore --clean --if-exists --no-owner --dbname="$env:RESTORE_DATABASE_URL" backup.dump
.venv\Scripts\python.exe -m alembic upgrade head
```

Use an isolated restore database. Verify Users, Roles, Permissions, Audit Logs, Tasks, and the Alembic revision, then call `/api/v1/health/ready` and authorized `/api/v1/health/detail`. Do not automatically restart or reconfigure Laragon-managed services.

## Redis, Worker, and Scheduler

When Redis is unavailable, readiness becomes degraded. Production login, Refresh/Revoke, writes, and destructive operations fail closed. After Redis recovery, verify login, rate limiting, task publication, and task recovery.

```powershell
.venv\Scripts\python.exe -m server.app worker
.venv\Scripts\python.exe -m server.app scheduler
```

Drain Worker before stopping a release, then stop Scheduler and verify that running tasks recover according to their lease. Never kill unrelated processes by executable name.

## Rollback

Roll code back only to a verified release artifact. Database downgrade is allowed only for a revision that passed restore rehearsal. Prefer backward-compatible migrations. For an irreversible migration, restore PostgreSQL into an isolated database and switch configuration rather than experimenting on the production database.

## Acceptance

Run `scripts/production-acceptance.ps1` and record configuration, health, authentication, authorization, audit, CSP, migration, backup/restore, Redis outage, and Worker/Scheduler recovery evidence. External Telemetry is explicitly out of scope for this phase.
