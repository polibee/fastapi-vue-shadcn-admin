# FastAPI Vue Shadcn Admin Integration Guide (AI-Friendly)

This is the implementation guide for integrating a new business project with the admin foundation. Before changing code, an AI agent should read this guide, `docs/项目约束.md`, and `docs/阶段开发计划.md`, then inspect the closest existing module. The default rule is to reuse the Resource Engine and define a Contract instead of writing a dedicated Vue page for ordinary resources.

## 1. Positioning

The project provides reusable administration infrastructure: authentication, JWT, RBAC, data scopes, audit logs, health checks, task queues, module registration, OpenAPI/TypeScript SDK, JSON localization, and generic resource pages.

Recommended stack:

- Backend: FastAPI, SQLAlchemy Async, Alembic, PostgreSQL, Redis
- Frontend: Vue 3, Vite, TypeScript, Vue Router, Pinia, shadcn-vue
- Data flow: Router → Service → Repository → SQLAlchemy → Database
- Ordinary resources: Resource Contract → Manifest → generic list/form/permission/menu

Do not replace the agreed PostgreSQL runtime database with SQLite.

## 2. Pre-flight checklist for AI agents

```text
1. Read docs/项目约束.md
2. Read docs/阶段开发计划.md
3. Inspect existing modules under server/app/modules
4. Inspect server/app/core/resources/definitions.py
5. Inspect the relevant admin/src/locales/<locale> namespaces
6. Write a failing test before production code
7. Run backend/frontend tests, typecheck, and build
```

Do not invent a global models/services/repositories layout. New business modules use vertical module boundaries; create a dedicated frontend page only when the resource is genuinely complex.

## 3. Short path for a normal resource

For example, `Departments`:

### 3.1 Backend model and migration

```text
server/app/modules/departments/
├── model.py
├── repository.py
├── schemas.py
├── service.py
└── router.py
```

Requirements:

- Use PostgreSQL-compatible SQLAlchemy types.
- Every new table has an Alembic migration.
- List endpoints support pagination, search, sorting, and permission-aware filtering.
- Deletes and bulk writes require authorization and audit logging.

### 3.2 Register the Resource Contract

Define the resource in `server/app/core/resources/definitions.py`:

```python
ResourceDefinition(
    name="departments",
    label="departments.label",
    label_plural="departments.labelPlural",
    api_base="/api/v1/departments",
    route="/departments",
    permissions={
        "view": "departments.view",
        "create": "departments.create",
        "update": "departments.update",
        "delete": "departments.delete",
    },
    fields=(...),
)
```

Also connect:

- `RESOURCE_DEFINITIONS`;
- backend router registration;
- permission catalog and default administrator permissions;
- Module Provider when lifecycle hooks are needed;
- menu permission checks.

### 3.3 Frontend localization

Every resource provides:

```text
admin/src/locales/zh-CN/departments.json
admin/src/locales/en/departments.json
```

The English file must contain the same keys as the Chinese file. Never hardcode user-visible text in Vue templates and never render unresolved keys such as `users.labelPlural`.

### 3.4 Frontend page

Use `GenericResourcePage` and resource routes for ordinary resources. Create a dedicated page only for complex relation editors, multi-step workflows, non-CRUD operations, or interactions that cannot be expressed by the Contract.

## 4. Permissions and data scopes

Use `<resource>.<action>` permission names, for example:

```text
departments.view
departments.create
departments.update
departments.delete
```

The frontend Permission Guard is for UX only. The backend must authorize again. Data scopes belong in Service/Repository query logic, not only in hidden frontend buttons.

## 5. API and SDK

OpenAPI is the API source of truth:

```text
http://127.0.0.1:8012/openapi.json
```

Generate the SDK:

```powershell
cd admin
pnpm generate:sdk
pnpm generate:sdk:check
```

Application code calls SDK methods through API Adapters rather than scattering `fetch` calls. Adapters standardize tokens, errors, pagination, and response shapes.

## 6. Localization and namespace loading

Use `admin/src/locales/<locale>/<namespace>.json`. Put shared copy in `common.json` and module copy in module namespaces. Resource routes must load their module namespace; shell labels for Users, Roles, Departments, and Auth are preloaded through the shared namespace baseline.

When adding a locale:

1. Add the locale directory;
2. Add JSON for every module;
3. Update `SupportedLocale`;
4. Add key-parity tests;
5. Manually check login, menus, tables, sign-out, and error messages.

## 7. Local development

```powershell
# API
.\.venv\Scripts\python.exe -m uvicorn server.app.main:app --host 0.0.0.0 --port 8012

# Frontend
cd admin
pnpm dev -- --host 0.0.0.0
```

PostgreSQL and Redis are required. Health endpoint:

```text
http://127.0.0.1:8012/api/v1/health
```

## 8. Acceptance checklist

```text
[ ] PostgreSQL migration runs on a clean database
[ ] List/detail/create/update/delete honor permissions
[ ] Frontend list supports search, pagination, sorting, and status filters
[ ] Internal id is hidden unless explicitly required by the business
[ ] Chinese and English JSON keys match
[ ] Menus never display raw i18n keys
[ ] Settings and sign-out work from the user menu
[ ] Mutating operations are audited
[ ] SDK is regenerated and passes check
[ ] pnpm typecheck passes
[ ] pnpm test passes
[ ] pnpm build passes
[ ] server/tests passes
```

## 9. Required AI delivery format

After implementing a module, an AI agent must report:

1. Changed files;
2. New APIs, permissions, and migrations;
3. Whether the Resource Contract was reused;
4. Localization namespaces;
5. Test and build results;
6. Unimplemented items or decisions requiring a human.

Do not report only “done”; provide reproducible commands and results.