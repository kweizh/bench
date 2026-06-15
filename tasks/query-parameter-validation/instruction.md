# Query Parameter Validation

## Background
Create a Zuplo API gateway that enforces query parameter validation on a specific route.

## Requirements
- Create a new Zuplo project.
- Add a route for `GET /search`.
- Implement logic (via a custom policy or handler) to require a query parameter named `q`.
- If the query parameter `q` is missing, the API must return a `400 Bad Request` status with a JSON error message.
- If `q` is provided, the API should return a `200 OK` status with a JSON response containing the value of `q`.

## Implementation Hints
- Use the Zuplo CLI (`create-zuplo-api`) to scaffold the project.
- Define the route in `config/routes.oas.json`.
- Create a custom inbound policy or a custom handler in TypeScript (e.g., in the `modules/` directory) to check for the `q` parameter in the request URL.
- Use `ZuploRequest` to parse the URL and access `searchParams`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: zuplo dev --port 9200
- Port: 9200
- API Endpoints:
  - GET `/search`: Returns status 400 if the `q` query parameter is missing.

    ```json
    // Response (Missing q)
    {
      "error": "Missing required query parameter: q"
    }
    ```

  - GET `/search?q=something`: Returns status 200 and a JSON object with the value.

    ```json
    // Response (With q)
    {
      "q": "something"
    }
    ```

