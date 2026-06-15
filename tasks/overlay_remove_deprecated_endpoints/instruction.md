# Remove Deprecated Endpoints with OpenAPI Overlays

## Background
OpenAPI Overlays provide a standard way to modify an OpenAPI specification without altering the original source file. Speakeasy CLI fully supports applying these overlays.

## Requirements
- Create an OpenAPI overlay file named `overlay.yaml` that removes the deprecated `/old-endpoint` from the provided `openapi.yaml`.
- Apply the overlay using the Speakeasy CLI and output the result to `modified.yaml`.

## Implementation Guide
1. Review the provided `openapi.yaml` in the project directory.
2. Create an `overlay.yaml` file that uses the OpenAPI Overlay specification to target and remove `$.paths['/old-endpoint']`.
3. Run the command `speakeasy overlay apply -s openapi.yaml -o overlay.yaml --out modified.yaml` to generate the new specification.

## Constraints
- Project path: /home/user/project
- The original `openapi.yaml` must not be modified.