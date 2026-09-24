# Production Acceptance Checklist

Use this checklist for human sign-off and evidence retention before deploying to a target environment. It does not replace health pages and does not modify Laragon-managed PostgreSQL, Redis, or processes.

## Configuration and security

- [ ] `ENVIRONMENT=production`, PostgreSQL, and Redis are configured.
- [ ] JWT secret is random and at least 32 characters; Trusted Hosts is enabled.
- [ ] `API_DOCS_ENABLED=false` and `VITE_DEMO_LOGIN_ENABLED=false`.
- [ ] Login, refresh, and revoke fail closed when Redis security state is unavailable.
- [ ] HTTPS responses include CSP and HSTS.

## Data and recovery

- [ ] `alembic upgrade head` succeeds on an isolated PostgreSQL database.
- [ ] `pg_dump`/`pg_restore` rehearsal verifies the Alembic revision, Users, Roles, Permissions, Audit Logs, and Tasks.
- [ ] Backup checksum, retention, recovery owner, and rollback decision owner are recorded.

## Runtime failure drills

- [ ] Redis outage makes `/api/v1/health/ready` degraded and blocks authentication/security-sensitive writes.
- [ ] Worker interruption recovers leased tasks or moves them to dead after max attempts.
- [ ] Scheduler interruption never marks a task successful; recovery republishes pending tasks.
- [ ] Only owned PIDs/service orchestration are used to stop project processes.

## Verification commands

```powershell
.venv\Scripts\python.exe -m pytest -p no:cacheprovider server/tests -q
cd admin; pnpm typecheck; pnpm test -- --run; pnpm build
scripts\production-acceptance.ps1 -SkipDatabase
```

With an isolated acceptance database, set `TEST_DATABASE_URL` and run the PostgreSQL rehearsal test. External Telemetry is out of scope for this phase.
