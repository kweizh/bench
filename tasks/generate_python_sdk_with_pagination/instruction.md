# Generate Python SDK with Pagination

## Background
Speakeasy SDKs support automatic pagination. You can configure this by adding the `x-speakeasy-pagination` extension to the OpenAPI description. We have an existing OpenAPI specification for a simple API with a paginated `/items` endpoint.

## Requirements
- Modify the OpenAPI specification at `/home/user/openapi.yaml` to include the `x-speakeasy-pagination` extension for the `GET /items` operation.
- The pagination configuration must use the `offsetLimit` type.
- It must map the `page` query parameter as the page input.
- It must extract the output results from the `$.data` field of the response.
- After modifying the spec, use the Speakeasy CLI to generate a Python SDK into the `/home/user/sdk` directory.

## Implementation Guide
1. Open `/home/user/openapi.yaml`.
2. Locate the `GET /items` operation.
3. Add the `x-speakeasy-pagination` extension to the operation with the following structure:
   ```yaml
   x-speakeasy-pagination:
     type: offsetLimit
     inputs:
       - name: page
         in: parameters
         type: page
     outputs:
       results: $.data
   ```
4. Generate the Python SDK using the Speakeasy CLI:
   ```bash
   speakeasy generate sdk -s /home/user/openapi.yaml -l python -o /home/user/sdk
   ```

## Constraints
- Project path: `/home/user`
- The generated SDK must be placed in `/home/user/sdk`.
- You must use the Speakeasy CLI to generate the SDK.

## Integrations
- Speakeasy