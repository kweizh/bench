# Zuplo Metadata-Based Routing

## Background
In multi-tenant Zuplo gateways, it is common to route requests to different backend URLs based on metadata attached to the authenticated user (typically populated by the API Key or JWT policy). In this task, you will implement a custom handler that routes requests dynamically based on `request.user.data.tenantId`.

## Requirements
- Initialize a new Zuplo project.
- Create a custom inbound policy named `mock-api-key-metadata`. This policy should read the `x-mock-tenant-id` header. If the header is present, it must set `request.user = { sub: "mock-user", data: { tenantId: <header-value> } }` and allow the request to proceed. If missing, it must return a 401 Unauthorized response.
- Create an API route for `GET /api/data` and apply the `mock-api-key-metadata` policy to it.
- Create a custom handler for the `/api/data` route. The handler must read `tenantId` from `request.user.data.tenantId`.
- The custom handler must proxy the request to `https://echo.zuplo.io/{tenantId}/data` and return the upstream response to the client.
- If `tenantId` is somehow missing in the handler, it should return a 400 Bad Request.

## Implementation Hints
- Use `npx -y create-zuplo-api@latest myproject --git=false --install=true --no-portal --no-eslint --yes` to scaffold the project.
- Create the custom policy and custom handler as TypeScript modules in the `modules/` directory.
- Update `config/policies.json` to register your custom policy.
- Update `config/routes.oas.json` to define the `/api/data` route, attach your policy, and route to your custom handler.
- Use the native `fetch` API in your handler to call the upstream URL.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: zuplo dev --port 3000
- Port: 3000
- API Endpoints:
  - GET `/api/data`:
    - When `x-mock-tenant-id` header is missing: Returns 401 Unauthorized.
    - When `x-mock-tenant-id: tenant-a` is provided: Proxies to `https://echo.zuplo.io/tenant-a/data` and returns the successful response.
    - When `x-mock-tenant-id: tenant-b` is provided: Proxies to `https://echo.zuplo.io/tenant-b/data` and returns the successful response.

