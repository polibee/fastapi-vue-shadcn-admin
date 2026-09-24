# FastAPI Vue Shadcn Admin

A reusable admin foundation for building future business applications quickly. Resource Contracts drive CRUD, permissions, menus, search, pagination, and localization without requiring a dedicated page for every ordinary resource.

Repository: [github.com/polibee/fastapi-vue-shadcn-admin](https://github.com/polibee/fastapi-vue-shadcn-admin)

Development services

Useful development infrastructure links:

- [RackNerd cloud server](https://my.racknerd.com/aff.php?aff=7572)
- [Vast.ai GPU cloud](https://cloud.vast.ai/?ref_id=91181)

## Current capabilities

- FastAPI + SQLAlchemy Async + Alembic + PostgreSQL
- Redis cache, health checks, task queue, Worker/Scheduler foundations
- JWT access/refresh tokens, revoke flow, password hardening, and login rate limiting
- RBAC, frontend Permission Guard, data scopes, and audit logging
- Vue 3 + Vite + TypeScript + Pinia + Vue Router
- shadcn-vue components and JSON i18n split by locale and module
- Resource Engine: Users, Roles, and Departments are driven by Resource Contracts for lists, forms, permissions, menus, and APIs
- OpenAPI/TypeScript SDK, schema introspection, code generator, and module registry
- Overview loads the real `/api/v1/health` endpoint and refreshes silently every 30 seconds

## Generic admin acceptance

Departments is the ordinary-resource acceptance module. It has no dedicated Vue page: a resource Contract and backend model are enough to reuse the generic resource page, CRUD API, menu, localization, search, pagination, and permission checks. Users/Roles validate extension points for more complex resources.

The project now has the core reuse value expected from a generic admin foundation. A production deployment still needs a clean PostgreSQL migration, Redis/Worker/Scheduler failure drills, backup and restore rehearsal, deployment controls, and security gates before it can be accepted as production-ready for a specific environment.

## Quick start

```powershell
# Backend
.\.venv\Scripts\python.exe -m uvicorn server.app.main:app --host 0.0.0.0 --port 8012

# Frontend
cd admin
pnpm install
pnpm dev -- --host 0.0.0.0
```

The runtime database is PostgreSQL with Redis; SQLite is not used as the application database. The development login page provides one-click demo credentials.

## URL boundaries

- Admin frontend: `http://127.0.0.1:4181/admin/`
- Future C-end frontend: `/` and other root-level routes
- Backend API: `/api/v1/*`
- Scalar API documentation: `/docs/scalar`

The old root admin paths such as `/users`, `/roles`, and `/settings` are intentionally invalid and are not redirected.

## Integration documentation

- [AI-friendly integration guide](docs/integration-development-guide.md)
- [Chinese integration guide](docs/对接开发指南.md)
- [MIT License](LICENSE)

## Project conventions

```text
server/app/modules/<module>/   # module model, repository, service, router
server/app/core/resources/     # Resource Contracts and manifests
admin/src/components/admin/    # semantic admin composition layer
admin/src/locales/<locale>/    # JSON translations split by locale/module
admin/src/core/api/            # API adapters and generated TypeScript SDK
```

## Module screenshots

| Module | 中文 | English |
| --- | --- | --- |
| Overview | ![总览](docs/screenshots/zh-CN/overview.png) | ![Overview](docs/screenshots/en/overview.png) |
| Activity | ![活动](docs/screenshots/zh-CN/activity.png) | ![Activity](docs/screenshots/en/activity.png) |
| Tasks | ![任务队列](docs/screenshots/zh-CN/tasks.png) | ![Tasks](docs/screenshots/en/tasks.png) |
| Users | ![用户](docs/screenshots/zh-CN/users.png) | ![Users](docs/screenshots/en/users.png) |
| Roles | ![角色权限](docs/screenshots/zh-CN/roles.png) | ![Roles](docs/screenshots/en/roles.png) |
| Departments | ![部门](docs/screenshots/zh-CN/departments.png) | ![Departments](docs/screenshots/en/departments.png) |
| Audit | ![审计](docs/screenshots/zh-CN/audit.png) | ![Audit](docs/screenshots/en/audit.png) |
| Introspection | ![数据库结构](docs/screenshots/zh-CN/introspection.png) | ![Introspection](docs/screenshots/en/introspection.png) |
| Generator | ![代码生成器](docs/screenshots/zh-CN/generator.png) | ![Generator](docs/screenshots/en/generator.png) |
| Modules | ![模块注册表](docs/screenshots/zh-CN/modules.png) | ![Modules](docs/screenshots/en/modules.png) |
| OpenAPI | ![接口浏览器](docs/screenshots/zh-CN/openapi.png) | ![OpenAPI](docs/screenshots/en/openapi.png) |
| Permissions | ![权限目录](docs/screenshots/zh-CN/permissions.png) | ![Permissions](docs/screenshots/en/permissions.png) |
| Settings | ![设置](docs/screenshots/zh-CN/settings.png) | ![Settings](docs/screenshots/en/settings.png) |

## Verification

```powershell
# Frontend
cd admin
pnpm typecheck
pnpm test
pnpm build

# Backend
..\.venv\Scripts\python.exe -m pytest server/tests -q
```

## License

This project uses the [MIT License](LICENSE). You may copy, modify, use commercially, and remove or replace the admin branding, while retaining the license and copyright notice.
