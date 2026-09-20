# FastAPI Vue Shadcn Admin

通用后台管理面板底座，目标是让后续业务项目通过 Resource Contract 快速生成可复用的 CRUD、权限、菜单、搜索、分页和多语言能力。

仓库地址：[github.com/polibee/fastapi-vue-shadcn-admin](https://github.com/polibee/fastapi-vue-shadcn-admin)

## 当前能力

- FastAPI + SQLAlchemy Async + Alembic + PostgreSQL
- Redis 缓存、健康检查、任务队列、Worker/Scheduler 基础设施
- JWT Access/Refresh、Revoke、密码安全和登录限流
- RBAC、Permission Guard、Data Scope、审计日志
- Vue 3 + Vite + TypeScript + Pinia + Vue Router
- shadcn-vue 组件体系与按语言/模块拆分的 JSON i18n
- Resource Engine：Users、Roles、Departments 通过 Resource Contract 驱动列表、表单、权限、菜单和 API
- OpenAPI/TypeScript SDK、数据库结构检查、代码生成器和模块注册表
- Overview 通过真实 `/api/v1/health` 首次加载并每 30 秒同步一次

## 通用化验收结论

Departments 是普通业务资源的验收样例：它没有专用 Vue 页面，只定义资源 Contract 和后端模型，即可复用通用资源页面、CRUD API、菜单、多语言、搜索、分页和权限。Users/Roles 则验证了复杂资源的扩展能力。

当前项目已经具备通用后台底座的核心复用能力，但仍应在目标项目中完成 PostgreSQL 干净库迁移、Redis/Worker/Scheduler 故障演练、备份恢复、部署和安全门禁后，才能宣称某个具体部署达到生产验收标准。

## 快速启动

```powershell
# 后端
.\.venv\Scripts\python.exe -m uvicorn server.app.main:app --host 0.0.0.0 --port 8012

# 前端
cd admin
pnpm install
pnpm dev -- --host 0.0.0.0
```

使用项目配置的 PostgreSQL 和 Redis，不使用 SQLite 作为运行数据库。开发环境演示账号可在登录页一键填充。

## 目录约定

```text
server/app/modules/<module>/   # 模块模型、仓储、服务、路由
server/app/core/resources/     # Resource Contract 与 Manifest
admin/src/components/admin/    # 管理后台语义组合层
admin/src/locales/<locale>/    # 按语言、按模块拆分的 JSON 翻译
admin/src/core/api/            # API Adapter 与生成的 TypeScript SDK
```

## 功能模块截图

| 模块 | 中文 | English |
| --- | --- | --- |
| Overview / 总览 | ![总览](docs/screenshots/zh-CN/overview.png) | ![Overview](docs/screenshots/en/overview.png) |
| Activity / 活动 | ![活动](docs/screenshots/zh-CN/activity.png) | ![Activity](docs/screenshots/en/activity.png) |
| Tasks / 任务队列 | ![任务队列](docs/screenshots/zh-CN/tasks.png) | ![Tasks](docs/screenshots/en/tasks.png) |
| Users / 用户 | ![用户](docs/screenshots/zh-CN/users.png) | ![Users](docs/screenshots/en/users.png) |
| Roles / 角色权限 | ![角色权限](docs/screenshots/zh-CN/roles.png) | ![Roles](docs/screenshots/en/roles.png) |
| Departments / 部门 | ![部门](docs/screenshots/zh-CN/departments.png) | ![Departments](docs/screenshots/en/departments.png) |
| Audit / 审计 | ![审计](docs/screenshots/zh-CN/audit.png) | ![Audit](docs/screenshots/en/audit.png) |
| Introspection / 数据库结构 | ![数据库结构](docs/screenshots/zh-CN/introspection.png) | ![Introspection](docs/screenshots/en/introspection.png) |
| Generator / 代码生成器 | ![代码生成器](docs/screenshots/zh-CN/generator.png) | ![Generator](docs/screenshots/en/generator.png) |
| Modules / 模块注册表 | ![模块注册表](docs/screenshots/zh-CN/modules.png) | ![Modules](docs/screenshots/en/modules.png) |
| OpenAPI / 接口浏览器 | ![接口浏览器](docs/screenshots/zh-CN/openapi.png) | ![OpenAPI](docs/screenshots/en/openapi.png) |
| Permissions / 权限目录 | ![权限目录](docs/screenshots/zh-CN/permissions.png) | ![Permissions](docs/screenshots/en/permissions.png) |
| Settings / 设置 | ![设置](docs/screenshots/zh-CN/settings.png) | ![Settings](docs/screenshots/en/settings.png) |

## 验证命令

```powershell
# 前端
cd admin
pnpm typecheck
pnpm test
pnpm build

# 后端
..\.venv\Scripts\python.exe -m pytest server/tests -q
```

## License

项目许可证和贡献规则将在正式发布前补充。