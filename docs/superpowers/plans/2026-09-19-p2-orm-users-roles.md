# P2 ORM Users and Roles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 建立不依赖手写业务 SQL 的 `users`/`roles` ORM、Repository、Service、Alembic 迁移和 PostgreSQL/MySQL 可验证的最小 CRUD API。

**Architecture:** SQLAlchemy 2.x Async ORM 作为唯一持久化边界；模型只描述数据关系，Repository 负责查询组合，Service 负责校验与事务。FastAPI 路由只调用 Service。Alembic 使用同一套元数据和双数据库交集 DDL，数据库 URL 只由环境变量切换。

**Tech Stack:** FastAPI, SQLAlchemy 2 Async ORM, Alembic, asyncpg, aiomysql, pytest, httpx.

**Spec:** `docs/项目约束.md`, `docs/阶段开发计划.md`, `docs/AI Elements与ORM集成方案.md`

## Global Constraints

- 业务代码禁止手写 Raw SQL；查询使用 SQLAlchemy ORM 或 Expression Language。
- 支持 `postgresql+asyncpg://` 和 `mysql+aiomysql://`，修改 `DATABASE_URL` 不修改业务代码。
- 迁移只使用 PostgreSQL/MySQL 共同支持的字段类型、约束和索引语义。
- 未配置数据库时 FastAPI 和 Redis 健康检查仍可启动；数据库功能返回明确配置错误。
- Repository 不负责 HTTP、权限和密码策略；Service 负责事务边界和业务校验。

## Review Focus

- 重复用户名、邮箱和角色名必须被拒绝，而不是产生未捕获的数据库异常。
- 分页必须有稳定的 `id` 次排序，避免相同时间戳导致记录抖动。
- 未配置 `DATABASE_URL` 时基础服务必须仍能启动，CRUD 必须给出明确错误。
- PostgreSQL 与 MySQL 的时间字段、布尔字段和唯一约束行为必须保持一致。
- 健康检查不得因为连接失败泄漏密码或完整连接串。

---

### Task 1: ORM 基础与模型

**Files:**
- Create: `server/app/core/database/base.py`
- Create: `server/app/modules/users/model.py`
- Create: `server/app/modules/roles/model.py`
- Create: `server/app/modules/users/__init__.py`
- Create: `server/app/modules/roles/__init__.py`
- Modify: `server/app/core/database.py`
- Test: `server/tests/test_models.py`

**Interfaces:**
- Produces `Base`, `User`, `Role`, `user_roles`, `get_session` and `SessionFactory` for later tasks without creating a global business-models directory.

- [ ] Write tests asserting table names, unique constraints, relationship names, and nullable/default behavior.
- [ ] Run `pytest server/tests/test_models.py -q` and observe the missing-module failure.
- [ ] Implement typed declarative models with integer primary keys, UTC timestamps, boolean `is_active`, and a composite primary key association table.
- [ ] Run the model test and the full `pytest -q` suite.

### Task 2: Alembic migration contract

**Files:**
- Create: `alembic.ini`
- Create: `server/migrations/env.py`
- Create: `server/migrations/script.py.mako`
- Create: `server/migrations/versions/0001_create_users_roles.py`
- Create: `server/migrations/__init__.py`
- Modify: `server/app/core/database/base.py`
- Modify: `server/app/modules/users/model.py`
- Modify: `server/app/modules/roles/model.py`
- Test: `server/tests/test_migration_contract.py`

**Interfaces:**
- Consumes `Base.metadata` from Task 1.
- Produces `alembic upgrade head` and `alembic downgrade base` workflows.

- [ ] Write a migration contract test checking revision identifiers and required table/constraint names without connecting to a database.
- [ ] Run it and observe failure because the Alembic environment is absent.
- [ ] Implement async Alembic configuration using `DATABASE_URL`, metadata import, and a deterministic initial migration.
- [ ] Run migration contract tests and `alembic check` with a configured test URL when available.

### Task 3: Repository and Service layer

**Files:**
- Create: `server/app/modules/users/repository.py`
- Create: `server/app/modules/roles/repository.py`
- Create: `server/app/modules/users/service.py`
- Create: `server/app/modules/roles/service.py`
- Test: `server/tests/test_services.py`

**Interfaces:**
- `UserRepository.list(offset: int, limit: int)`, `get_by_id(id: int)`, `get_by_username(username: str)`, `create(**values)`.
- `RoleRepository.list(offset: int, limit: int)`, `get_by_name(name: str)`, `create(**values)`.
- Services expose async `list`, `create`, and duplicate validation methods.

- [ ] Write service tests for successful creation, duplicate username/email/role rejection, and stable list ordering.
- [ ] Run tests and observe missing repository/service failures.
- [ ] Implement ORM-only queries and explicit transaction commits/rollbacks through injected `AsyncSession`.
- [ ] Run service tests and the full suite.

### Task 4: Minimal CRUD API and error contract

**Files:**
- Create: `server/app/modules/users/router.py`
- Create: `server/app/modules/roles/router.py`
- Create: `server/app/modules/users/schema.py`
- Create: `server/app/modules/roles/schema.py`
- Modify: `server/app/modules/users/module.py`
- Modify: `server/app/modules/roles/module.py`
- Test: `server/tests/test_api_contract.py`

**Interfaces:**
- `GET/POST /api/v1/users` and `GET/POST /api/v1/roles`.
- Responses contain `items`, `total`, `offset`, and `limit` for list endpoints.
- Duplicate records return HTTP 409; missing database configuration returns HTTP 503.

- [ ] Write API contract tests for OpenAPI paths, validation, duplicate conflict, and missing database configuration.
- [ ] Run tests and observe route/schema failures.
- [ ] Implement Pydantic schemas, dependency-based sessions, router registration, and safe error mapping.
- [ ] Run API tests, `python -m compileall -q server`, and `pnpm run build`.

### Task 5: Dual-database verification and documentation

**Files:**
- Create: `server/tests/integration/test_users_roles_db.py`
- Modify: `docs/如何启动.md`
- Modify: `docs/阶段开发计划.md`

- [ ] Add environment-gated integration tests that use the same CRUD cases for PostgreSQL and MySQL.
- [ ] Run them with each configured `DATABASE_URL`; skip with a clear reason when a database is unavailable.
- [ ] Record migration commands, required drivers, and current P2 gate status in the docs.
- [ ] Run the final verification: model tests, service/API tests, compileall, production build, and `/api/health`.
