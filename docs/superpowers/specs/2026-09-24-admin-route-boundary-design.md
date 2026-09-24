# Admin Route Boundary Design

**Status:** Design proposal for review  
**Date:** 2026-09-24  
**Scope:** Separate the reusable admin panel frontend from future C-end frontend routes.

## 1. Goal

Make the admin panel use the `/admin/` URL namespace while reserving the root namespace for future C-end pages. Keep backend APIs independently addressable under `/api/v1/`, so frontend route ownership is not confused with backend resource ownership.

The target URL model is:

```text
Admin frontend:  /admin/*
C-end frontend:  /*
Backend API:     /api/v1/*
API docs:        /docs/scalar and /openapi.json
```

## 2. Current Problem

The current Vue application mounts the admin dashboard at `/` and admin modules at root paths such as `/users`, `/roles`, `/tasks`, and `/settings`. The login route is `/login`. This prevents a future C-end application from owning the root namespace without route collisions and makes route intent ambiguous in shared links, redirects, tests, and documentation.

## 3. Decisions

### 3.1 Admin frontend namespace

All admin UI routes will be children of `/admin`:

```text
/admin/
/admin/login
/admin/activity
/admin/tasks
/admin/users
/admin/roles
/admin/permissions
/admin/departments
/admin/audit
/admin/settings
/admin/introspection
/admin/generator
/admin/modules
/admin/openapi-browser
```

The admin shell, admin authentication guard, admin permission guard, admin resource registry, and admin locale route loading will operate inside this namespace.

### 3.2 C-end namespace

The root namespace remains available for future C-end routes. The current repository does not implement C-end pages as part of this change. The root route must not silently render the admin dashboard after the migration.

Until a C-end application is introduced, `/` will explicitly redirect to `/admin/` as a temporary entry behavior. It is not an admin route alias and will be replaced by the C-end entry route when that application is added.

### 3.3 Backend API namespace

Backend API routes remain under `/api/v1/`:

```text
/api/v1/auth/*
/api/v1/users/*
/api/v1/roles/*
/api/v1/departments/*
```

No `/admin` prefix will be added to API routes. Backend authorization continues to be enforced by authentication dependencies, RBAC, data scope, and service-layer checks. URL prefixes are not authorization controls.

### 3.4 Public backend tooling routes

The following remain independent public/tooling endpoints:

```text
/docs/scalar
/openapi.json
/api/v1/health
```

They are not frontend admin routes and must not be moved beneath `/admin`.

## 4. Legacy route policy

There will be no compatibility redirects for old root-level admin routes. After migration, these paths are not valid admin URLs and must not be registered as aliases:

```text
/login
/users
/roles
/permissions
/departments
/tasks
/audit
/settings
```

They must resolve to the frontend's normal not-found behavior (or the deployment's standard 404 response), never to an admin page. New navigation, generated resource routes, auth redirects, documentation, screenshots, and tests must use `/admin/...`. This deliberate break prevents stale links from preserving the route collision that this migration is intended to remove.

## 5. Frontend architecture

Vue Router will use an `/admin` parent route. Admin child routes will keep their existing route names and components where possible, but their paths will be generated from one admin route prefix instead of repeating string literals.

The following helpers/contracts are expected:

```ts
const ADMIN_ROUTE_PREFIX = '/admin'
function adminPath(path: string): string
function adminRedirectTarget(path: string): string
```

`ResourceDefinition.route` is a frontend admin route and must resolve to `/admin/<resource>`. `ResourceDefinition.api_base` remains an API path such as `/api/v1/departments`.

All of these must be migrated together:

- sidebar navigation;
- global search results;
- login success and auth-failure redirects;
- sign-out redirect;
- user-center settings link;
- resource route registry;
- locale namespace selection based on route;
- browser links to Scalar and OpenAPI explorer where relevant;
- frontend route tests.

The admin shell must only be reachable through `/admin/*`. A future C-end shell must be a separate root-level route tree, not another mode inside `AdminShell.vue`.

## 6. Backend and development-server behavior

The FastAPI backend keeps serving APIs and Scalar directly. Vite continues to proxy `/api`, `/docs`, and `/openapi.json` to FastAPI during development.

The frontend development and production server configuration must support history fallback for direct visits to `/admin/*`, including refreshes at `/admin/users` and `/admin/settings`. Static asset URLs must remain valid when the browser is at a nested admin path.

## 7. Authentication and authorization behavior

The admin route guard will:

1. Load the correct admin locale namespaces.
2. Redirect unauthenticated `/admin/*` navigation to `/admin/login?redirect=<encoded-admin-path>`.
3. Preserve the originally requested admin path after successful login.
4. Clear the token and redirect to `/admin/login` when the current-user request fails.
5. Apply the existing permission guard to admin resources.

The redirect query must never be allowed to escape the intended local frontend route boundary. External URLs and protocol-relative URLs must be rejected or normalized to a safe admin route.

## 8. API, SDK, and Resource Contract boundaries

The generated TypeScript SDK remains unchanged for API URLs because API paths stay under `/api/v1/`. Only frontend route metadata and navigation paths change.

For every ordinary resource:

```text
ResourceDefinition.route    = /admin/<resource>
ResourceDefinition.api_base = /api/v1/<resource>
```

Tests must assert that these two namespaces remain distinct. A resource route must never be used as an API URL, and an API base must never be rendered as a browser navigation target.

## 9. Documentation and examples

Update both integration guides, project constraints where needed, startup documentation, and stage plan to state:

- admin UI starts at `/admin/`;
- C-end routes own `/`;
- APIs stay under `/api/v1/`;
- Scalar remains `/docs/scalar`;
- new Resource Contracts use `/admin/<resource>` for UI routes and `/api/v1/<resource>` for API routes.

Examples and screenshots must use the new admin URLs. Legacy root admin paths must be documented as invalid after migration, not as migration aliases.

## 10. Testing requirements

The implementation must add or update tests for:

- every admin route resolving under `/admin`;
- `/admin/login` being public;
- unauthenticated `/admin/users` redirecting to `/admin/login` with a safe encoded redirect;
- successful login returning to the requested `/admin/...` route;
- permission denial staying inside the admin route tree;
- old root admin links being rejected instead of redirected;
- root namespace not being mistaken for an admin child route;
- Resource Contract UI route/API base separation;
- direct navigation and refresh behavior for nested admin paths;
- Scalar and `/openapi.json` remaining available.

Existing API tests, generated SDK checks, type checks, frontend tests, and frontend build must remain part of the final verification gate.

## 11. Non-goals

- No C-end business pages are implemented in this migration.
- No backend API prefix migration from `/api/v1` to `/admin/api`.
- No authentication mechanism replacement.
- No unrelated visual redesign.
- No second frontend UI framework.
- No reintroduction of root-level admin aliases for compatibility.

## 12. Acceptance criteria

The design is implemented when:

1. All admin UI navigation uses `/admin/...`.
2. Root-level routes are reserved for explicit C-end behavior or a documented entry redirect.
3. Backend APIs remain under `/api/v1/...` and generated SDK output remains valid.
4. Unauthenticated and unauthorized flows stay inside the admin route boundary.
5. Direct browser navigation to nested admin routes works in development and production-style static serving.
6. Old root admin links are deterministically rejected and never redirected.
7. Documentation and tests describe and enforce the same route model.
