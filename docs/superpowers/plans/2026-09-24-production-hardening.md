# Production Hardening Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

Goal: Establish a production-safe configuration, authentication-failure policy, health contract, browser security baseline, and operational rehearsal package without adding external Telemetry.

Architecture: Keep development defaults usable, but add explicit production validation at startup. Treat Redis as mandatory for authentication security state while allowing narrowly scoped read-only degradation. Separate public liveness/readiness probes from authenticated operational detail.

Tech Stack: FastAPI, Pydantic Settings, SQLAlchemy Async, Alembic, Redis, ARQ, Vue 3, Vite, TypeScript, Vitest, pytest.

Spec: docs/superpowers/specs/2026-09-24-production-hardening-design.md

## Global Constraints

- External Telemetry exporters and hosted alerting remain out of scope.
- PostgreSQL and Redis remain runtime services; SQLite is not an application fallback.
- Production UI routes remain under /admin/* and API routes under /api/v1/*.
- Production errors expose stable codes without secrets or raw connection errors.
- Tests are written and observed failing before production implementation changes.
- Demo credentials and demo seed behavior are development-only.

## Review Focus

- Missing/default production secrets fail before serving requests: Task 1 test.
- Redis outage cannot silently bypass authentication security: Task 3 tests.
- Public health probes do not reveal task counters: Task 4 tests.
- CSP permits the bundled SPA without unsafe-eval: Task 5 tests.
- Restore and rollback commands are reproducible against clean PostgreSQL: Tasks 6-7 checks.

---

### Task 1: Production configuration guard

Files:
- Create: server/app/core/production_guard.py
- Modify: server/app/core/config.py, server/app/main.py, server/app/cli.py
- Test: server/tests/test_production_guard.py

Interfaces: validate_production_settings(settings: Settings) -> None raises ProductionConfigurationError(code, fields) without secret values. The lifespan invokes it before module boot in production. doctor reports the same non-secret result.

- [ ] Write tests for default JWT secret, missing database/Redis, disabled Trusted Hosts, empty hosts, enabled API docs, and one valid production configuration.
- [ ] Run .venv\Scripts\python.exe -m pytest -p no:cacheprovider server/tests/test_production_guard.py -q; verify expected failure because the guard is absent.
- [ ] Implement production-only checks while preserving development defaults; use stable codes and no URL/secret output.
- [ ] Run the focused test plus server/tests/test_settings.py.
- [ ] Commit with git add server/app/core/production_guard.py server/app/core/config.py server/app/main.py server/app/cli.py server/tests/test_production_guard.py and git commit -m "feat: enforce production configuration safety".

### Task 2: Production-safe seed and demo login

Files:
- Modify: server/scripts/seed_demo_admin.py, server/app/cli.py, admin/src/core/api/auth.ts, admin/src/components/admin/LoginPage.vue
- Test: server/tests/test_seed_protection.py, admin/src/core/api/auth-login.test.ts

Interfaces: seed_demo_admin() rejects production before opening a session. Demo login UI is enabled only by explicit VITE_DEMO_LOGIN_ENABLED.

- [ ] Write tests proving production seed rejection and disabled demo UI behavior.
- [ ] Run the focused server and frontend tests; verify current behavior fails the new contract.
- [ ] Add the environment guard before database access and make the demo panel conditional; do not reset known passwords in production.
- [ ] Run .venv\Scripts\python.exe -m pytest -p no:cacheprovider server/tests/test_seed_protection.py -q and cd admin; npm run test -- --run src/core/api/auth-login.test.ts.
- [ ] Commit with git commit -m "feat: block demo seed in production".

### Task 3: Redis security failure policy

Files:
- Modify: server/app/core/rate_limit.py, server/app/core/auth_tokens.py, server/app/modules/auth/router.py, server/app/core/permissions.py
- Test: server/tests/test_rate_limit.py, server/tests/test_auth_lifecycle.py

Interfaces: api_rate_limit(resource: str, *, fail_closed: bool = False) supports explicit policy. Token-store operations raise RedisSecurityStateUnavailable when revocation state cannot be verified. Authentication, permission-changing, and destructive paths fail closed; ordinary read-only listings may degrade.

- [ ] Write outage tests for Redis incr, exists, and setex; assert login/refresh/revoke do not silently succeed.
- [ ] Run focused tests and observe current fail-open behavior.
- [ ] Implement the exception and explicit policy, preserving localized stable errors.
- [ ] Run rate-limit, auth lifecycle, and permission API tests.
- [ ] Commit with git commit -m "feat: fail closed for authentication security state".

### Task 4: Layered health endpoints

Files:
- Modify: server/app/core/health.py, server/app/core/permissions.py, server/app/main.py, admin/src/core/api/health.ts, admin/src/components/admin/DashboardPage.vue
- Test: server/tests/test_health.py, admin/src/core/api/health.test.ts

Interfaces: /api/v1/health/live returns only status; /api/v1/health/ready returns readiness without task counters; /api/v1/health/detail requires health.detail and returns detailed counters; /api/v1/health remains a readiness alias.

- [ ] Write tests for public liveness/readiness, protected detail, and alias behavior.
- [ ] Run focused health tests and observe current single-endpoint behavior.
- [ ] Extract response builders, add the permission catalog entry, and update the dashboard adapter to use detail.
- [ ] Run backend health tests and cd admin; npm run test -- --run src/core/api/health.test.ts.
- [ ] Commit with git commit -m "feat: split liveness readiness and detail health".

### Task 5: CSP and Token security baseline

Files:
- Modify: server/app/core/middleware/security_headers.py, server/app/core/config.py, admin/src/core/api/auth.ts, admin/src/main.ts
- Test: server/tests/test_middleware_http.py, admin/src/core/api/auth-login.test.ts
- Docs: docs/如何启动.md, docs/integration-development-guide.md, docs/对接开发指南.md

- [ ] Write tests for production CSP, HTTPS-only HSTS behavior, and token clearing after refresh failure.
- [ ] Run focused tests and observe the missing CSP contract.
- [ ] Add configuration-driven CSP without unsafe-eval; document same-origin secure-cookie deployment mode without claiming it is implemented where it is not.
- [ ] Run frontend typecheck and focused tests.
- [ ] Commit with git commit -m "feat: add production browser security baseline".

### Task 6: Deployment, backup, restore, and rollback runbook

Files:
- Create: docs/生产部署与回滚.md, docs/production-deployment-and-rollback.md, scripts/production-acceptance.ps1
- Modify: README.md, README.zh-CN.md
- Test: server/tests/test_production_docs.py

- [ ] Write checks requiring production variables, process topology, reverse proxy TLS, Alembic order, pg_dump/pg_restore, Redis behavior, worker drain, and rollback criteria.
- [ ] Run the checks and observe failure because the files do not exist.
- [ ] Add runbooks with environment-variable references only and a read-only-by-default acceptance script; destructive commands require an explicit target.
- [ ] Parse the PowerShell script and run static checks.
- [ ] Commit with git commit -m "docs: add production deployment recovery runbook".

### Task 7: PostgreSQL migration and restore rehearsal

Files:
- Create: server/tests/test_production_rehearsal.py
- Modify: docs/生产部署与回滚.md, docs/production-deployment-and-rollback.md

- [ ] Write an integration test using explicit TEST_DATABASE_URL; it must skip clearly when absent and never fall back to SQLite.
- [ ] Run without TEST_DATABASE_URL and verify a safe skip.
- [ ] With an explicit user-provided PostgreSQL test URL, apply migrations, verify the head revision/core tables, and execute the documented restore rehearsal without changing Laragon service configuration.
- [ ] Commit with git commit -m "test: add postgres migration rehearsal".

### Task 8: Redis, Worker, and Scheduler failure drills

Files:
- Create: server/tests/test_operational_failure_drills.py
- Modify: server/app/core/health.py, server/worker/tasks_worker.py only when a test proves a missing boundary
- Docs: docs/生产部署与回滚.md, docs/production-deployment-and-rollback.md

- [ ] Write tests for Redis outage/recovery, task publication failure, stale lease recovery, Scheduler recovery invocation, and no-database worker behavior.
- [ ] Run the focused tests and observe expected failures.
- [ ] Implement only missing recovery behavior by reusing existing adapters/services; never create a second Redis client or kill arbitrary processes.
- [ ] Run the drills plus existing task recovery, task event, and rate-limit tests.
- [ ] Commit with git commit -m "test: add redis and worker failure drills".

### Task 9: Production acceptance gate

Files:
- Create: docs/生产验收清单.md, docs/production-acceptance-checklist.md
- Modify: scripts/production-acceptance.ps1

- [ ] Write checklist/script contract tests covering configuration, migration, health, auth, authorization, audit, CSP, backup/restore, Redis outage, Worker/Scheduler recovery, build, and rollback.
- [ ] Run them and verify missing gates fail.
- [ ] Connect only stable commands/endpoints; mark external Telemetry explicitly out of scope.
- [ ] Run:
  cd admin; npm run typecheck; npm run test -- --run; npm run build
  and
  .venv\Scripts\python.exe -m pytest -p no:cacheprovider server/tests -q --basetemp .pytest-tmp.
- [ ] Run the acceptance script against configured local services, record environment-only limitations, run git diff --check, and commit with git commit -m "test: add production acceptance gate".
