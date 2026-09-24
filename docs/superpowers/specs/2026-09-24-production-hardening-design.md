# Production Hardening Design

## Goal

Raise the FastAPI/Vue admin foundation from local-development readiness to a production-deployable baseline without adding external Telemetry or alerting in this phase.

The implementation must preserve the existing PostgreSQL/Redis architecture, `/admin/*` frontend boundary, `/api/v1/*` API boundary, JSON module localization, and Resource Contract model.

## Scope and release gate

The release gate covers:

1. Production configuration validation.
2. Production-safe seed behavior.
3. Redis failure policy for rate limiting and token revocation.
4. Layered liveness, readiness, and protected detail health checks.
5. Browser token and Content Security Policy hardening.
6. Deployment, backup, restore, migration, and rollback documentation.
7. PostgreSQL clean-database migration and restore rehearsal.
8. Redis, Worker, and Scheduler failure drills.
9. Repeatable production acceptance tests.

External Telemetry exporters, hosted alerting, and vendor integrations are explicitly out of scope. The existing in-process metrics and CLI snapshot remain available.

## Design

### 1. Production configuration guard

Add a single startup validation boundary driven by `ENVIRONMENT`:

- production requires a non-default, sufficiently strong `JWT_SECRET`;
- production requires `DATABASE_URL` and `REDIS_URL`;
- production requires `TRUSTED_HOSTS_ENABLED=true` and at least one explicit host;
- production disables Scalar/OpenAPI unless an explicit override is provided;
- production disables demo login and demo seed behavior;
- invalid production configuration fails startup with a stable, non-secret error.

The existing `admin doctor` command will report the same checks without exposing connection strings or secrets.

### 2. Seed protection

The development seed command must refuse to run when `ENVIRONMENT=production`. Development credentials will not be compiled into a production login experience. If an explicit bootstrap workflow is needed later, it must accept a password from a protected operator input rather than a source-controlled default.

### 3. Redis failure policy

Redis is an operational dependency for security state:

- login and refresh-token security operations fail closed when Redis is unavailable;
- refresh-token revocation and validation must not silently treat Redis failure as “not revoked”;
- ordinary read-only API rate limiting may use the existing degraded behavior, but write, authentication, permission, and destructive operations must not bypass the security gate;
- failure responses remain stable and localized without exposing Redis details.

Add tests for both Redis outage and recovery paths.

### 4. Health contract

Split health responsibilities:

- `/api/v1/health/live`: process liveness only;
- `/api/v1/health/ready`: database and Redis readiness, suitable for deployment probes;
- `/api/v1/health/detail`: existing dependency and task counters, protected by an operational permission.

The admin Overview page consumes the detail endpoint. Public probes do not expose task counts or dependency topology.

### 5. Browser security

- Add a production Content Security Policy with explicit script, style, connect, image, font, and frame sources appropriate for the bundled SPA.
- Keep bearer access tokens short-lived and prevent refresh-token fallback when its secure storage policy is unavailable.
- Document the current SPA storage trade-off and provide a secure-cookie deployment mode for refresh tokens where the deployment uses a same-origin backend.
- Preserve logout revocation and token rotation tests.

### 6. Operational documentation and drills

Add operator documentation for:

- production environment variables;
- process topology and reverse proxy boundaries;
- Alembic clean-database migration;
- PostgreSQL backup, restore, and rollback;
- Redis outage behavior;
- Worker/Scheduler startup, recovery, and shutdown;
- release acceptance and rollback criteria.

Add deterministic tests or scripts that exercise migration, service degradation, task recovery, and readiness behavior without modifying user-managed Laragon service configuration.

## Error handling and compatibility

- Existing development defaults remain usable for local development.
- Production-only failures use stable error codes and never return secrets or raw connection errors.
- `/api/v1/health` remains available during the transition as a compatibility alias for readiness, but new deployment documentation uses the explicit liveness/readiness endpoints.
- No external Telemetry dependency is introduced.

## Verification

The implementation is complete only when:

- production guard tests cover missing/default secrets, missing dependencies, unsafe hosts, and docs/demo settings;
- seed protection tests reject production execution;
- Redis outage tests prove fail-closed authentication security and documented read-only degradation;
- health endpoint tests prove public/private information boundaries;
- CSP and token behavior are verified through API and frontend tests;
- clean PostgreSQL migration and restore rehearsal commands are documented and reproducible;
- frontend typecheck, tests, and production build pass;
- backend tests pass, with any environment-only test infrastructure issue explicitly recorded.
