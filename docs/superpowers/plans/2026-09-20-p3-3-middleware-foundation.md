# P3.3 Middleware Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 FastAPI Admin 建立可配置、可测试、与业务模块解耦的生产级请求管线。

**Architecture:** 使用 Starlette/FastAPI 原生 Middleware 承载 Request ID、Context、CORS、Trusted Host、安全响应头、Timing 和 Access Log；认证、RBAC、Data Scope 继续使用 FastAPI Dependency/Policy。配置统一进入现有 Settings，日志和 Context 只保存基础设施信息，不访问业务数据库。

**Tech Stack:** FastAPI、Starlette Middleware、Pydantic Settings、Python logging、pytest、httpx ASGITransport。

**Spec:** `docs/P3.3-中间件基础设施设计.md`

## Global Constraints

- Middleware 只依赖 Core、配置、上下文、日志和基础设施，不依赖 `server.app.modules.*` 的 Service、Repository 或 Model。
- 不实现全局 Auth Middleware、RBAC Middleware 或 Data Scope Middleware。
- 不记录 Authorization、JWT、密码、数据库 URL、Redis URL 和敏感请求体字段。
- 认证继续使用 `Depends(get_current_user)`，授权继续使用 `Depends(require_permission(...))`。
- 所有响应必须保留 `X-Request-ID`；正常响应与异常响应均适用。
- Development、Test、Production 必须使用明确的 CORS、Trusted Host 和安全头配置。

## Review Focus

- Starlette Middleware 注册顺序与实际执行顺序不一致：由完整请求集成测试覆盖。
- 异常响应提前返回导致 Request ID、安全头或 Access Log 丢失：由 4xx/5xx 测试覆盖。
- 用户伪造过长或包含换行的 `X-Request-ID`：由输入校验测试覆盖。
- CORS Credentials 与通配符 Origin 组合产生错误配置：由 Settings 校验测试覆盖。
- Access Log 泄露 Authorization、密码或连接字符串：由日志捕获测试覆盖。

---

### Task 1: 配置契约与 Request Context

**Files:**
- Modify: `server/app/core/config.py`
- Create: `server/app/core/context.py`
- Create: `server/app/core/middleware/__init__.py`
- Create: `server/app/core/middleware/request_id.py`
- Create: `server/app/core/middleware/request_context.py`
- Test: `server/tests/test_middleware_context.py`

**Interfaces:**
- Produces `RequestContext`、`get_request_context(request)`、`ensure_request_id(request)` 和 `RequestIdMiddleware`。
- Context 字段：`request_id`、`trace_id`、`user_id`、`ip`、`user_agent`、`method`、`path`、`started_at`。

- [ ] Write tests for generated/forwarded Request ID, newline rejection, context fields, and default security configuration.
- [ ] Run `pytest server/tests/test_middleware_context.py -v` and verify the new tests fail because the middleware/context interfaces do not exist.
- [ ] Add validated configuration fields for CORS, trusted hosts, security headers, slow request threshold, and access log mode.
- [ ] Implement typed request context and safe Request ID normalization; preserve the existing `ensure_request_id` behavior used by audit.
- [ ] Run the focused tests and verify they pass.
- [ ] Run the existing audit and health tests to confirm Request ID compatibility.

### Task 2: Timing、Access Log 与敏感信息脱敏

**Files:**
- Create: `server/app/core/logging.py`
- Create: `server/app/core/middleware/timing.py`
- Create: `server/app/core/middleware/access_log.py`
- Test: `server/tests/test_middleware_logging.py`

**Interfaces:**
- Produces `sanitize_headers(headers)`、`sanitize_payload(payload)`、`log_access(request, response, duration_ms)` and middleware wrappers.
- Log record fields: `request_id`、`method`、`path`、`status_code`、`duration_ms`、`user_id`、`client_ip`。

- [ ] Write tests for normal response logging, exception response logging, slow request warning, and redaction of Authorization/password/database URL/Redis URL.
- [ ] Run the focused test file and verify expected failures.
- [ ] Implement monotonic timing and structured JSON-compatible log records without logging request bodies by default.
- [ ] Ensure exceptions are re-raised after logging so FastAPI exception handlers remain authoritative.
- [ ] Run focused logging tests and then the full backend suite.

### Task 3: CORS、Trusted Host 与 Security Headers

**Files:**
- Create: `server/app/core/middleware/cors.py`
- Create: `server/app/core/middleware/trusted_host.py`
- Create: `server/app/core/middleware/security_headers.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_middleware_http.py`

**Interfaces:**
- Produces `build_cors_middleware(app, settings)`、`build_trusted_host_middleware(app, settings)` and `SecurityHeadersMiddleware`。
- Security headers：`X-Content-Type-Options`、`X-Frame-Options`、`Referrer-Policy`、`Permissions-Policy`。

- [ ] Write ASGI integration tests for allowed/denied Origin, preflight, trusted/untrusted Host, and security headers on 200/404/500 responses.
- [ ] Run the focused tests and verify failures before implementation.
- [ ] Register middleware through a dedicated `configure_middlewares(app, settings)` function instead of expanding unrelated router code in `main.py`.
- [ ] Reject production wildcard Host/CORS configurations where credentials are enabled.
- [ ] Run focused tests and full API contract tests.

### Task 4: Middleware Registration and Runtime Compatibility

**Files:**
- Modify: `server/app/main.py`
- Modify: `server/app/core/audit.py`
- Test: `server/tests/test_middleware_pipeline.py`

**Interfaces:**
- Produces a single application bootstrap path that registers all P3.3 middleware and preserves existing exception handlers, OpenAPI, Scalar, health, auth, audit, tasks, and Resource routes.

- [ ] Write an integration test that calls health, login, protected API, validation error, and unknown route through the complete middleware stack.
- [ ] Verify failure cases demonstrate missing headers, missing context, or missing access-log events before implementation.
- [ ] Register middleware with explicit comments documenting Starlette execution order.
- [ ] Keep `X-Request-ID` generation compatible with `record_audit` and existing audit assertions.
- [ ] Run the full backend test suite and verify no regression.

### Task 5: Documentation, Configuration Examples and Quality Gates

**Files:**
- Modify: `docs/P3.3-中间件基础设施设计.md`
- Modify: `docs/阶段开发计划.md`
- Modify: `.env.example` or the repository’s existing environment template
- Test: `server/tests/test_middleware_config.py`

- [ ] Add configuration examples for local development and production.
- [ ] Add tests for invalid CORS/Trusted Host combinations and default environment behavior.
- [ ] Run backend tests, SDK consistency check, frontend tests, typecheck, and production build.
- [ ] Verify `/api/v1/health` and `/openapi.json` from the Windows browser-facing ports.
- [ ] Mark P3.3 complete only after all documented gates pass.

## Completion Checklist

- [ ] Request ID and Request Context implemented and tested.
- [ ] Timing and structured Access Log implemented and tested.
- [ ] CORS, Trusted Host, and Security Headers implemented and tested.
- [ ] Middleware does not import business Modules.
- [ ] Existing auth/RBAC/Data Scope/Audit/Task behavior has no regression.
- [ ] Backend, frontend, typecheck, build, and SDK gates pass.
- [ ] Browser preview confirms the service remains reachable.

