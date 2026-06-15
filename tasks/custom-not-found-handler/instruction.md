# Custom 404 Not Found Handler in Zuplo

## Background
Create a custom handler for 404 Not Found responses in a Zuplo API gateway. By default, Zuplo returns a standard 404 response for unmatched routes. You need to implement a catch-all route with a custom handler that returns a specific JSON payload.

## Requirements
- Scaffold a new Zuplo project named `myproject`.
- Implement a custom handler module that returns a 404 HTTP status code and a JSON body `{"error": "Not Found", "message": "Custom 404 handler"}`.
- Configure a catch-all route (e.g., `/{path:.*}`) in the OpenAPI routes file to use this custom handler.
- Ensure the local development server starts properly.

## Implementation Hints
- Use `npx -y create-zuplo-api@latest myproject --git=false --install=true --no-portal --no-eslint --yes` to create the project.
- Create a TypeScript module (e.g., `modules/not-found.ts`) that exports a default function taking `ZuploRequest` and `ZuploContext`. The function should return a `new Response` with the required JSON, a 404 status, and `content-type: application/json` header.
- Update `config/routes.oas.json` to include a path like `/{path:.*}` with a `GET` operation that uses the custom handler. Ensure this route is placed such that it acts as a fallback.
- Start the dev server using `npx zuplo dev --editor-port 9200` to avoid port conflicts with port 9100.
- **Important**: You must kill the background server before completing the task.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: `npx zuplo dev --editor-port 9200`
- Port: 9000
- API Endpoints:
  - GET `/some-random-non-existent-route`: Returns status 404 and a JSON response with the custom error message.

    ```json
    // Response
    {
      "error": "Not Found",
      "message": "Custom 404 handler"
    }
    ```

