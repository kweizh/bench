# Zuplo URL Rewrite Policy

## Background
Zuplo is an edge-native API gateway. A common requirement is to rewrite the URL path of an incoming request before it is forwarded to the upstream backend. In this task, you will implement a custom inbound policy that rewrites the URL path for a specific route.

## Requirements
- Initialize a Zuplo project.
- Create a route for `GET /api/v1/users`.
- The route should forward requests to the backend `https://echo.zuplo.io`.
- Implement a custom inbound policy in TypeScript that rewrites the URL path from `/api/v1/users` to `/users` before the request is forwarded.
- Apply this policy to the route.

## Implementation Hints
- Use `npx -y create-zuplo-api@latest myproject --git=false --install=true --no-portal --no-eslint --yes` to scaffold the project.
- Define the route in `config/routes.oas.json` using the URL rewrite policy you will create.
- A custom inbound policy should export a default function that takes `(request: ZuploRequest, context: ZuploContext)`.
- To rewrite the URL, construct a new URL object from `request.url`, modify its `pathname`, and return a new `ZuploRequest` using `new ZuploRequest(newUrl.toString(), request)`.
- Configure the policy in `config/policies.json` and attach it to the route's `inbound` policies.
- Use the built-in URL Rewrite policy or a custom TypeScript policy.
- Ensure the dev server runs on port 9200.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: npm run dev -- --port 9200
- Port: 9200
- API Endpoints:
  - GET `/api/v1/users`: Forwards the request to `https://echo.zuplo.io/users`.
    The response from `echo.zuplo.io` must indicate that the path received by the backend was `/users`.
