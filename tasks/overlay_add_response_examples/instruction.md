# Add Response Examples with OpenAPI Overlay

## Background
OpenAPI Overlays are a standard way to modify or extend an OpenAPI specification without changing the original source file. In this task, you will use the Speakeasy CLI to apply an overlay that adds a response example to an existing API endpoint.

## Requirements
- Create an `overlay.yaml` file conforming to the OpenAPI Overlay Specification 1.0.0.
- The overlay must target the `GET /ping` operation's `200` response in the provided `openapi.yaml`.
- It should add a `content` object for `application/json` with an `example` of `{"message": "pong"}`.
- Apply the overlay using the Speakeasy CLI and save the merged output to `openapi-modified.yaml`.

## Implementation Guide
1. Review the `openapi.yaml` file in the project directory.
2. Create an `overlay.yaml` file that uses JSONPath `$.paths['/ping'].get.responses['200']` to add the required `content` object.
3. Run the following command to apply the overlay:
   `speakeasy overlay apply -o overlay.yaml -s openapi.yaml --out openapi-modified.yaml`

## Constraints
- Project path: `/home/user/project`
- Do not modify the original `openapi.yaml` directly.
- Use the `speakeasy` CLI which is already installed.