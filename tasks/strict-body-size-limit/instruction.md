# Enforce Strict Body Size Limit

## Background
To protect backend services from excessively large payloads, we need to enforce a strict request body size limit at the API gateway layer using Zuplo.

## Requirements
- Initialize a new Zuplo project.
- Create a custom inbound policy that restricts the request body size to a maximum of 1024 bytes.
- Create a POST route at `/upload` that returns a 200 OK with the text `Upload successful`.
- Apply the custom policy to the `/upload` route.
- If a request is missing the `content-length` header or its value exceeds 1024, the policy must reject the request with a `413 Payload Too Large` status code and the text `Payload Too Large`.

## Implementation Hints
- Use `npx -y create-zuplo-api@latest myproject --git=false --install=true --no-portal --no-eslint --yes` to scaffold the project.
- Create a custom policy module (e.g., `modules/body-limit.ts`) that inspects the `content-length` header of the incoming `ZuploRequest`.
- Register the policy in `config/policies.json`.
- Define the `/upload` POST route in `config/routes.oas.json` and attach the policy and a simple handler.
- Remember to kill the background dev server before completing the task.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: zuplo dev --port 9200
- Port: 9200
- API Endpoints:
  - POST `/upload`:
    - Rejects requests without a `content-length` header with status 413 and text `Payload Too Large`.
    - Rejects requests where `content-length` > 1024 with status 413 and text `Payload Too Large`.
    - Accepts requests where `content-length` <= 1024, returning status 200 and text `Upload successful`.
