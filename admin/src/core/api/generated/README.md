# Generated API SDK

This directory is generated from the running FastAPI OpenAPI document. Do not edit files under `client/` by hand.

Regenerate from the project backend with:

```powershell
pnpm run generate:sdk

# CI/local gate: fail when generated files are stale
pnpm run generate:sdk:check
```

The generated client is configured at runtime to use the current browser origin, so Vite can proxy `/api` to the local FastAPI service.
