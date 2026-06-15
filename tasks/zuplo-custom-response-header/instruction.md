# Zuplo Custom Response Header Policy

## Background
Zuplo allows developers to build custom policies in TypeScript. In this task, you will create a custom outbound policy that reads the response body and adds an `X-Signature` header based on its contents.

## Requirements
- Create a new Zuplo project at `/home/user/myproject`.
- Add a custom route handler for `GET /hello` that returns the JSON response `{"message": "Hello World"}`.
- Create a custom outbound policy that reads the response body as text.
- The policy must append an `X-Signature` header to the response. The value of this header must be the base64 encoded string of the response body text.
- Apply this custom outbound policy to the `GET /hello` route.

## Implementation Hints
- You will need to clone the response (e.g., `response.clone()`) to safely read the body text without causing a "body used" exception when returning the response.
- You can use the standard Web API `btoa()` function to base64 encode the text.
- Make sure the policy is correctly defined in `config/policies.json` and applied to the route in `config/routes.oas.json`.
- A new `Response` object might need to be constructed if the original response headers are immutable.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: npm run dev
- Port: 8787
- API Endpoints:
  - GET `/hello`: Returns status 200 and the JSON `{"message": "Hello World"}`. The response must include an `X-Signature` header containing the base64 encoded string of the exact response body.
