# Basic Proxy with API Key Authentication

## Background
Zuplo is an edge-native API gateway that can add authentication, rate limiting, and other policies to your APIs. In this task, you will create a new Zuplo project that proxies requests to a public API and secures the route with an API Key Authentication policy.

## Requirements
- Initialize a new Zuplo project in the `/home/user/myproject` directory.
- Create a route at `/echo` that forwards `GET` requests to `https://echo.zuplo.io`.
- Add the `api-key-inbound` policy to the route to require a Zuplo-managed API key.

## Implementation Hints
- You can scaffold the project using `npx -y create-zuplo-api@latest myproject --git=false --install=true --no-portal --no-eslint --yes`.
- Edit `config/routes.oas.json` to define the `/echo` route and configure the `urlForwardHandler` to point to the upstream API (`https://echo.zuplo.io`).
- Add the `api-key-inbound` policy to the route's inbound policies.
- Ensure the policy is defined in `config/policies.json`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: npm run dev
- Port: 9000
- API Endpoints:
  - GET `/echo`: Returns status 401 Unauthorized when requested without an API key. (We only test the unauthorized case to verify the policy is active locally.)

