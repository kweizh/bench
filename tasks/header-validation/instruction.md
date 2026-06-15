# Zuplo Header Validation

## Background
Create a programmable API gateway using Zuplo that enforces a custom header check before allowing access to a route.

## Requirements
- Scaffold a new Zuplo project.
- Create a route at `GET /protected`.
- Implement a custom inbound policy (or use a built-in one if applicable) to check for the presence and value of a custom header: `x-custom-auth`.
- The header value must be exactly `my-secret-token`.
- If the header is missing or incorrect, the gateway should return a `401 Unauthorized` status code with a JSON response: `{"error": "Unauthorized"}`.
- If the header is correct, the gateway should return a `200 OK` status code with a JSON response: `{"message": "success"}`.

## Implementation Hints
- Use `npx create-zuplo-api@latest` to scaffold the project.
- You can write a custom policy in TypeScript within the `modules/` directory to inspect the `request.headers`.
- Bind the policy to the `/protected` route in `config/routes.oas.json` and register the policy in `config/policies.json`.
- Ensure the dev server runs on port 9200 to avoid port conflicts.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: npm run dev -- --port 9200 (or zuplo dev --port 9200)
- Port: 9200
- API Endpoints:
  - GET `/protected`: 
    - Without header or wrong header: Returns status 401 and JSON `{"error": "Unauthorized"}`.
    - With header `x-custom-auth: my-secret-token`: Returns status 200 and JSON `{"message": "success"}`.

