# Zuplo Path Prefix Routing

## Background
Create an API Gateway using Zuplo that routes incoming requests to different upstream backend services based on the URL path prefix.

## Requirements
- Initialize a new Zuplo project in `/home/user/myproject-${run-id}`.
- Configure a route for `/api/v1/users/*` that forwards requests to `https://httpbin.org/anything/users/*`.
- Configure a route for `/api/v1/products/*` that forwards requests to `https://httpbin.org/anything/products/*`.
- Both routes must preserve the HTTP method (GET, POST, etc.) and forward the request body correctly.
- Run the local development server on port 9200.

## Implementation Hints
- Read the `ZEALT_RUN_ID` environment variable to get the `run-id`.
- Use `npx create-zuplo-api` to scaffold the project in the target directory.
- Modify `config/routes.oas.json` to define the paths with wildcard or path parameters.
- Use the appropriate built-in URL rewrite or proxy handler to forward the requests to the upstream URLs dynamically based on the path.
- Start the dev server using `zuplo dev --port 9200`.

## Acceptance Criteria
- Project path: /home/user/myproject-${run-id}
- Start command: zuplo dev --port 9200
- Port: 9200
- API Endpoints:
  - GET `/api/v1/users/{id}`: Proxies to `https://httpbin.org/anything/users/{id}`. The response should be the httpbin JSON where the `url` field matches the upstream URL.
  - POST `/api/v1/products/{id}`: Proxies to `https://httpbin.org/anything/products/{id}`. The response should be the httpbin JSON where the `url` field matches the upstream URL and the `json` field matches the request body.

