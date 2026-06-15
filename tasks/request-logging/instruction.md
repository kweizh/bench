# Zuplo Request Logging Policy

## Background
Zuplo is a programmable API gateway. You can write custom policies in TypeScript to intercept and modify requests. In this task, you will create a custom inbound policy that logs a specific request header to the console.

## Requirements
- Scaffold a new Zuplo project in `/home/user/myproject`.
- Create a custom inbound policy in TypeScript that reads the `x-custom-id` header from the incoming request.
- If the header is present, log exactly `Custom ID: <value>` using `context.log.info()`.
- Apply this policy to a new `GET /hello` route.
- The route should return a 200 OK with the text `Hello World`.

## Implementation Hints
- Use `npx -y create-zuplo-api@latest myproject --git=false --install=true --no-portal --no-eslint --yes` to scaffold the project.
- Create a custom policy module in `modules/` (e.g., `modules/log-header.ts`) that exports a default function taking `request: ZuploRequest` and `context: ZuploContext`.
- Read the header using `request.headers.get('x-custom-id')`.
- Register the policy in `config/policies.json`.
- Define the `GET /hello` route in `config/routes.oas.json` and apply the policy in the `inbound` array of `x-zuplo-route.policies`.
- The handler for `/hello` can be a simple inline handler or a custom module that returns `new Response("Hello World")`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: `npx zuplo dev --editor-port 9200 --port 3000`
- Port: 3000
- API Endpoints:
  - GET `/hello`: Returns status 200 and response body `Hello World`.
- Logging behavior:
  - When a request is made to `/hello` with the header `x-custom-id: <value>`, the server must log `Custom ID: <value>` to stdout.

