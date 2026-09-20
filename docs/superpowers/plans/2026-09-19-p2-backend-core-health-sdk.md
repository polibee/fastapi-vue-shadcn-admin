# P2 Backend Core, Health, ORM and SDK Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 建立 FastAPI 后端核心、真实 `/api/v1/health`、Users/Roles SQLAlchemy ORM 与 Alembic 迁移，并从 OpenAPI 生成 TypeScript SDK 接入 Dashboard。

**Architecture:** 后端采用 `server/app/core` 基础设施和 `server/app/modules/{users,roles}` 垂直模块。健康检查只通过 Infrastructure Adapter 探测数据库与 Redis，业务路由遵循 `Router → Service → Repository → SQLAlchemy`。前端 API 访问统一收敛到生成 SDK，不再手写业务 Client。

**Tech Stack:** Python 3.13+, FastAPI, Pydantic v2, SQLAlchemy 2.x async, Alembic, asyncpg, aiomysql, redis, pytest, httpx, openapi-typescript, TypeScript.

**Spec:** `docs/项目约束.md`, `docs/阶段开发计划.md`

## Global Constraints

- 业务代码禁止 Raw SQL；查询使用 SQLAlchemy ORM 或 Expression Language。
- `DATABASE_URL` 支持 `postgresql+asyncpg://` 和 `mysql+aiomysql://`，业务代码不随数据库切换而变化。
- 未配置数据库或 Redis 时，应用仍可启动；健康检查明确返回 `unavailable`，不泄漏连接串。
- ORM、Schema、Repository、Service、Router 必须位于对应 Vertical Module 内。
- 前端只使用生成 SDK 访问后端，不重复声明 API 类型和 URL。
- 所有用户可见文本继续使用现有中英文 locale。

## Review Focus

- 数据库和 Redis 任一不可用时，`/api/v1/health` 返回可解释状态且响应不泄密。
- 数据库未配置时，基础 FastAPI/OpenAPI 能启动，Users/Roles 操作返回稳定 503。
- 用户名、邮箱和角色名重复时返回稳定 409，而不是数据库异常。
- OpenAPI 生成 SDK 后，Dashboard 仍能在浏览器中显示真实健康状态。
- Alembic 初始迁移升级、降级、再升级可重复执行。

### Task 1: FastAPI application and infrastructure

**Files:**
- Create: `server/pyproject.toml`, `server/app/main.py`, `server/app/core/config.py`, `server/app/core/database/session.py`, `server/app/core/cache/redis.py`, `server/app/core/health.py`
- Create: `server/tests/test_health.py`, `server/tests/conftest.py`

- [ ] Write failing tests for app startup, `/api/v1/health`, unavailable database/Redis, and secret-safe response.
- [ ] Run the focused tests and observe missing-module failures.
- [ ] Implement settings, optional async SQLAlchemy engine/session, optional Redis adapter, lifespan, and health router.
- [ ] Run focused health tests and the full server test suite.

### Task 2: Users/Roles ORM and Alembic

**Files:**
- Create: `server/app/core/database/base.py`, `server/app/modules/users/{__init__,module,model,schema,repository,service,router}.py`
- Create: `server/app/modules/roles/{__init__,module,model,schema,repository,service,router}.py`
- Create: `server/migrations/env.py`, `server/migrations/script.py.mako`, `server/migrations/versions/0001_create_users_roles.py`, `alembic.ini`
- Create: `server/tests/test_models.py`, `server/tests/test_migration_contract.py`

- [ ] Write failing model and migration contract tests for table names, relationships, constraints, timestamps, and reversible revision.
- [ ] Run them and observe absent model/migration failures.
- [ ] Implement typed SQLAlchemy models, association table, Pydantic schemas, and deterministic Alembic metadata.
- [ ] Run model and migration contract tests.

### Task 3: Repository, Service and CRUD API

**Files:**
- Modify: `server/app/main.py`
- Create: `server/tests/test_services.py`, `server/tests/test_api_contract.py`

- [ ] Write failing tests for create/list, stable id ordering, duplicate conflicts, validation, and missing database 503.
- [ ] Run tests and observe missing repository/service/router failures.
- [ ] Implement ORM-only repositories, service transaction boundaries, router dependencies, and stable error codes.
- [ ] Run API tests and compile the entire server.

### Task 4: OpenAPI to TypeScript SDK

**Files:**
- Create: `scripts/generate-sdk.ps1`, `admin/src/core/api/generated/README.md`
- Modify: `admin/package.json`, `admin/src/core/api/health.ts`, `admin/src/components/admin/DashboardPage.vue`
- Create: `admin/src/core/api/generated/` output and `admin/src/core/api/health.test.ts` updates

- [ ] Write a failing adapter test proving Dashboard health access is routed through generated SDK.
- [ ] Generate the SDK from the running FastAPI OpenAPI schema with an explicit repeatable command.
- [ ] Replace the handwritten health fetch implementation with the generated client wrapper.
- [ ] Run frontend typecheck, tests, and production build.

### Task 5: Runtime verification and documentation

**Files:**
- Modify: `docs/如何启动.md`, `docs/阶段开发计划.md`
- Create: `server/tests/integration/test_runtime.py`

- [ ] Add environment-gated PostgreSQL/MySQL integration tests and clear skips when services are absent.
- [ ] Run `alembic upgrade head`, `alembic downgrade base`, and `alembic upgrade head` against configured databases when available.
- [ ] Start backend and frontend in the background, verify `/api/v1/health`, `/openapi.json`, Scalar, and Dashboard through the browser.
- [ ] Run final server tests, frontend tests, typecheck, build, and compileall.
