# Request Body Transformation (JSON to XML)

## Background
In enterprise API gateways, it's common to integrate modern JSON-based clients with legacy backend systems that only accept XML. You need to implement a custom policy in Zuplo that transforms an incoming JSON payload into an XML format before the request reaches the backend.

## Requirements
- Create a new Zuplo project.
- Define a route for `POST /api/submit`.
- Implement a custom inbound policy that intercepts the request, reads the JSON body, converts it to XML, and forwards the transformed request.
- The JSON payload will look like: `{"user": {"name": "Alice", "role": "admin"}}`.
- The transformed XML payload should look like: `<user><name>Alice</name><role>admin</role></user>`.
- Set the `Content-Type` header of the forwarded request to `application/xml`.
- Route the transformed request to a custom handler that simply echoes back the request body as text, so the transformation can be verified.

## Implementation Hints
- Use `zuplo` CLI to create a new project.
- Write a custom inbound policy in TypeScript (e.g., `./modules/json-to-xml.ts`).
- Since Zuplo runs on the edge, you can use standard Web APIs. You can manually construct the XML string or use a lightweight library that is edge-compatible.
- Remember to clone or recreate the `Request` object in your policy because the request body cannot be read twice or modified directly in place. Return a new `Request` object with the new XML body and updated headers.
- For the backend handler, create another module (e.g., `./modules/echo.ts`) that reads `request.text()` and returns it in a `Response`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Start command: zuplo dev --port 3000
- Port: 3000
- API Endpoints:
  - POST `/api/submit`: Accepts a JSON payload and returns the transformed XML payload as text.

    ```json
    // Request
    {
      "user": {
        "name": string,
        "role": string
      }
    }
    ```
    ```xml
    // Response (Echoed from the custom handler)
    <user><name>string</name><role>string</role></user>
    ```

