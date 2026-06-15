# Tiered Rate Limiting with Zuplo

## Background
Zuplo is an edge-native API gateway that allows you to add authentication, rate limiting, and other policies to your APIs. In this task, you will create a Zuplo API gateway that implements tiered rate limiting based on a user's subscription plan extracted from a JWT claim.

## Requirements
- Initialize a new Zuplo project in `/home/user/myproject`.
- Create a single GET endpoint at `/api/data`.
- Secure the endpoint using JWT authentication. The JWTs will be signed using the HS256 algorithm with a symmetric secret.
- Implement a tiered rate limiting mechanism:
  - Users with the claim `"plan": "free"` in their JWT should be limited to 2 requests per minute.
  - Users with the claim `"plan": "pro"` in their JWT should be limited to 5 requests per minute.
- Return a 429 Too Many Requests status when a user exceeds their limit.
- Valid requests should return a 200 OK with a simple JSON response.

## Implementation Hints
- Use `npx -y create-zuplo-api@latest` to scaffold the project.
- You can use Zuplo's built-in JWT authentication policy and configure it to use a symmetric secret (e.g., `my-super-secret-key`).
- To implement tiered rate limiting, you might need to use Zuplo's custom policies or configure multiple rate limit policies with different conditions based on `request.user.data.plan`.
- When starting the dev server, ensure the editor port is set to 9200 (e.g., using `--editor-port 9200` or modifying `package.json`) to avoid port conflicts, while leaving the gateway on port 8787.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: npm run dev
- Port: 8787
- API Endpoints:
  - GET `/api/data`:
    - Requires a valid HS256 JWT signed with the secret `my-super-secret-key`.
    - Returns 401 Unauthorized if the JWT is missing or invalid.
    - Returns 200 OK with `{"data": "success"}` for valid requests within the rate limit.
    - Returns 429 Too Many Requests if the rate limit is exceeded.
    - Rate limits: 2 requests/minute for `"plan": "free"` and 5 requests/minute for `"plan": "pro"`.

