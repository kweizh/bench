# Strip Sensitive Query Parameters

## Background
When building an API Gateway, it is often necessary to sanitize incoming requests before they reach the backend. In this task, you will configure Zuplo to remove a specific sensitive query parameter from incoming requests.

## Requirements
- Initialize a Zuplo project in `/home/user/myproject`.
- Configure a route `/echo` that proxies requests to `https://echo.zuplo.io/`.
- Implement a custom inbound policy using TypeScript that removes the `secret_token` query parameter from the request URL.
- Apply this custom policy to the `/echo` route so that the backend never receives the `secret_token`.

## Implementation Hints
- Use the `zuplo` CLI to scaffold the project (e.g., `npx -y create-zuplo-api@latest myproject --git=false --install=true --no-portal --no-eslint --yes`).
- Create a custom inbound policy module in the `./modules/` directory.
- In your policy handler, parse the `request.url` using the `URL` class, remove the `secret_token` from `searchParams`, and construct a new `ZuploRequest` with the modified URL.
- Update `config/routes.oas.json` to define the `/echo` route and bind your policy.
- Update `config/policies.json` to register your custom policy.
- Note: It may take some time to start a dev server. Please make sure the project can be built before starting the background server. The dev server should run on port 9200 since 9100 may be used by the editor.
- **MUST**: Remember to kill the background server before completing the task.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: npx zuplo dev --port 9200
- Port: 9200
- API Endpoints:
  - GET `/echo`: Proxies to the upstream backend.
    - When a request includes the `secret_token` query parameter (e.g., `?foo=bar&secret_token=supersecret`), the gateway must remove `secret_token` before forwarding.
    - Other query parameters (like `foo=bar`) must be preserved.
    - The response from the echo backend should reflect that `secret_token` is absent from the forwarded request.

