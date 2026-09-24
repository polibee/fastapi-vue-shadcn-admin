# Admin Route Boundary Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox ([ ]) syntax for tracking.

**Goal:** Move every admin frontend route under /admin/*, reserve root paths for future C-end routes, keep APIs under /api/v1/*, and reject old root admin paths without compatibility redirects.

**Architecture:** Centralize admin browser paths in a TypeScript route helper. Mount the existing Vue pages under an /admin parent route, keep FastAPI and Scalar paths unchanged, and use a catch-all not-found route for old root admin URLs. Resource Contracts will expose /admin/<resource> for UI navigation and /api/v1/<resource> for API access.

**Tech Stack:** Vue 3, Vue Router 4, TypeScript, Vite, Vitest, FastAPI, pytest, JSON locale namespaces, generated OpenAPI SDK.

**Spec:** docs/superpowers/specs/2026-09-24-admin-route-boundary-design.md

## Global Constraints

- Admin UI routes use /admin/*; C-end routes reserve /*.
- Backend API routes remain under /api/v1/*; no /admin API prefix.
- Scalar remains /docs/scalar; OpenAPI remains /openapi.json.
- Old /login, /users, /roles, /permissions, /departments, /tasks, /audit, and /settings paths must never redirect to admin pages.
- Reuse the current shadcn-vue visual system and JSON locale namespaces.
- Write a failing test before each production behavior change.
- Keep PostgreSQL and Redis as runtime services; do not introduce SQLite.
- Final verification must include backend tests, frontend tests, typecheck, build, and SDK check.

## Review Focus

- A nested admin URL must preserve the admin shell; test direct navigation to /admin/users.
- An unauthenticated admin request must use /admin/login and a safe local redirect.
- Legacy root admin paths must be rejected rather than redirected.
- Resource UI routes and API bases must remain separate.
- Nested admin routes must load correctly in development and production-style serving.

---

### Task 1: Centralize admin route paths

**Files:**
- Create: admin/src/router/paths.ts
- Create: admin/src/router/paths.test.ts
- Modify: admin/src/router/resource-routes.ts
- Modify: admin/src/core/navigation/registry.ts
- Test: admin/src/core/navigation/registry.test.ts when route assertions exist

**Interfaces:**
- ADMIN_ROUTE_PREFIX is /admin.
- adminPath(path: string): string normalizes a child path to /admin/<child>, with /admin/ for the dashboard.
- adminLoginPath(): string returns /admin/login.
- isAdminPath(path: string): boolean distinguishes /admin paths from /users and /api/v1/users.
- safeAdminRedirect(value: unknown): string accepts only local /admin/... values and falls back to /admin/.
- Every resource browser path is generated through adminPath; resource API bases remain /api/v1/<resource>.

- [ ] Write paths.test.ts first for /users, users, /, /admin, /admin/users, /users, and /api/v1/users.
- [ ] Run cd admin; pnpm vitest run src/router/paths.test.ts and confirm failure because paths.ts is absent.
- [ ] Implement the four helpers with slash normalization and no API-path behavior.
- [ ] Update resource-routes.ts and navigation/registry.ts to use adminPath for Users, Roles, and Departments.
- [ ] Run the focused path and navigation tests; expected result is PASS.
- [ ] Commit with git commit -m "refactor: centralize admin route paths".

### Task 2: Mount the Vue admin application under /admin

**Files:**
- Modify: admin/src/main.ts
- Modify: admin/src/router/resource-routes.ts
- Create or modify: admin/src/router/routes.test.ts
- Modify: admin/src/components/admin/LoginPage.vue
- Modify: admin/src/components/admin/AdminShell.vue
- Modify: admin/src/core/search/registry.ts
- Test: admin/src/core/api/auth-login.test.ts

**Interfaces:**
- Vue Router exposes /admin/ for Dashboard, /admin/login for Login, and /admin/<module> for all admin pages.
- namespaceForRoute() matches full /admin paths.
- safeAdminRedirect(value: unknown): string accepts only local /admin/... values and falls back to /admin/.

- [ ] Add failing route tests asserting /admin/, /admin/login, /admin/users, /admin/roles, and /admin/departments exist while old root paths do not.
- [ ] Add failing auth tests for safe /admin/users, https://evil.example, //evil.example, and /users redirect values.
- [ ] Run the focused tests and verify failure against the current root route table.
- [ ] Change main.ts to use an /admin parent route or centralized prefixed child routes; update namespace loading.
- [ ] Change the auth guard, LoginPage, AdminShell, and GlobalSearch to use adminLoginPath(), adminPath(), and safeAdminRedirect(). Preserve redirect query paths only when they remain inside /admin.
- [ ] Run route, auth, and path tests; expected result is PASS.
- [ ] Commit with git commit -m "feat: mount admin frontend under admin namespace".

### Task 3: Reject root admin paths explicitly

**Files:**
- Create: admin/src/components/NotFoundPage.vue
- Create: admin/src/router/legacy-routes.test.ts
- Modify: admin/src/main.ts
- Modify: admin/src/locales/zh-CN/common.json
- Modify: admin/src/locales/en/common.json

**Interfaces:**
- / explicitly redirects to /admin/ until a C-end entry route exists.
- A catch-all route renders NotFoundPage.
- The old root paths are not registered and are not aliases.
- NotFoundPage uses i18n JSON and has no hardcoded user-visible copy.

- [ ] Add failing tests for the absence of /login, /users, /roles, /permissions, /departments, /tasks, /audit, and /settings, plus the presence of / and a catch-all.
- [ ] Run cd admin; pnpm vitest run src/router/legacy-routes.test.ts and confirm failure.
- [ ] Add the root entry redirect and catch-all route; add matching common.notFound keys in both locale files.
- [ ] Keep /docs/scalar and /openapi.json outside Vue routing so Vite can proxy them to FastAPI.
- [ ] Run cd admin; pnpm vitest run src/router/legacy-routes.test.ts src/locales/locales.test.ts; expected result is PASS.
- [ ] Commit with git commit -m "feat: reject legacy root admin routes".

### Task 4: Enforce Resource Contract route separation

**Files:**
- Modify: server/app/core/resources/definitions.py
- Modify: server/app/core/resources/contract.py if validation belongs there
- Modify: server/tests/test_resources.py
- Modify: admin/src/core/resources/types.ts
- Modify: admin/src/core/resources/loader.ts
- Modify: admin/src/core/navigation/registry.ts
- Create or modify: admin/src/core/resources/routes.test.ts

**Interfaces:**
- Every manifest route starts with /admin/.
- Every manifest api_base starts with /api/v1/.
- UI route values are used only for browser navigation; api_base values are used only by SDK adapters.

- [ ] Add a backend failing assertion for Departments route /admin/departments and api_base /api/v1/departments.
- [ ] Add a frontend failing assertion for the same two distinct manifest values.
- [ ] Run the focused pytest and Vitest tests and confirm the current /departments route fails the new contract.
- [ ] Update definitions and manifest mapping without changing generated SDK URLs.
- [ ] Add validation that rejects a UI route beginning with /api/ or an API base being rendered as navigation.
- [ ] Run backend resource tests and frontend resource/navigation tests; expected result is PASS.
- [ ] Commit with git commit -m "feat: separate resource UI and API routes".

### Task 5: Verify nested serving and update project documentation

**Files:**
- Modify: admin/vite.config.ts
- Modify: admin/src/vite-config.test.ts
- Modify: docs/如何启动.md
- Modify: docs/对接开发指南.md
- Modify: docs/integration-development-guide.md
- Modify: docs/项目约束.md
- Modify: docs/阶段开发计划.md
- Modify: README.md
- Modify: README.zh-CN.md

**Interfaces:**
- Vite continues proxying /api, /docs, and /openapi.json to FastAPI.
- Opening /admin/users directly loads the SPA and root-safe assets.
- All preferred documentation links use /admin/* for admin UI and /api/v1/* for APIs.

- [ ] Add failing Vite/documentation assertions for nested admin navigation, preserved proxy targets, and absence of preferred old root admin links.
- [ ] Run cd admin; pnpm vitest run src/vite-config.test.ts and confirm failure if the current config/docs do not express the contract.
- [ ] Implement only the necessary base/fallback configuration; do not alter API or Scalar paths.
- [ ] Update Chinese and English guides, constraints, stage plan, and both READMEs with the route table. State explicitly that old root admin paths are invalid and are not redirected.
- [ ] Run the Vite test and pnpm build; expected result is PASS.
- [ ] Commit with git commit -m "docs: establish admin frontend route boundary".

### Task 6: Full verification and browser acceptance

**Files:**
- Test: server/tests
- Test: admin/src/**/*.test.ts
- Verify: admin/src/core/api/generated/client and README route links

**Interfaces:**
- README quick-start links point to /admin/ and /admin/departments.
- No README or integration guide presents a root admin path as preferred.
- Verification evidence is recorded in the final delivery report.

- [ ] Run .venv/Scripts/python.exe -m pytest server/tests -q and record the exact result.
- [ ] Run cd admin; pnpm typecheck; pnpm test; pnpm generate:sdk:check; pnpm build.
- [ ] Search admin/src, docs, README.md, and README.zh-CN.md for preferred root admin links; allow only /api/v1 backend paths and explicit legacy-path rejection tests.
- [ ] Verify in the browser: /admin/, /admin/login, /admin/users, /admin/departments, /users, and /docs/scalar. Expected: admin pages render, /users is not redirected, and Scalar remains available.
- [ ] Commit any final README or screenshot updates with git commit -m "docs: update admin route examples".

## Final Delivery Checklist

- [ ] /admin/ is the only preferred admin dashboard URL.
- [ ] /admin/login is the only preferred admin login URL.
- [ ] All resource UI routes use /admin/<resource>.
- [ ] All resource API bases use /api/v1/<resource>.
- [ ] Root legacy admin paths are rejected, not redirected.
- [ ] Root / has explicit temporary entry behavior until a C-end shell exists.
- [ ] Scalar and OpenAPI URLs remain unchanged.
- [ ] Backend tests, frontend tests, typecheck, SDK check, and build are green.
