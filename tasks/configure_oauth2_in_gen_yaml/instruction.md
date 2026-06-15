# Enable OAuth 2.0 Client Credentials in Speakeasy gen.yaml

## Background
Speakeasy generates idiomatic SDKs from OpenAPI specifications. The `gen.yaml` file is the primary configuration file for SDK generation targets, and the `generation.auth` section controls authentication-related code generation. To support APIs that authenticate via the OAuth 2.0 client-credentials flow, Speakeasy exposes the `oAuth2ClientCredentialsEnabled` flag under `generation.auth`. When set to `true`, Speakeasy generates the code required to handle OAuth 2.0 client credentials in the generated SDK.

A partial Speakeasy project has been initialized at `/home/user/project`. The existing `gen.yaml` configures a TypeScript SDK target but currently has `oAuth2ClientCredentialsEnabled: false`. Your job is to flip this single flag on so the next generation run will produce SDK code that supports the OAuth 2.0 client-credentials flow.

## Requirements
- Edit `/home/user/project/gen.yaml` so that `generation.auth.oAuth2ClientCredentialsEnabled` is set to `true`.
- Do **not** rename, remove, or restructure any other fields in `gen.yaml`. All existing keys (configuration version, SDK class name, language target, etc.) must remain valid and unchanged in meaning.
- The resulting `gen.yaml` must still be valid YAML that Speakeasy can read.

## Implementation Hints
- This is a configuration-only change inside `gen.yaml`. No CLI command is required to be executed against Speakeasy's servers.
- You can edit the file directly with any text editor, or use a tool such as `yq` to update the specific key in place.
- Refer to the Speakeasy `gen.yaml` reference if you need to confirm the exact location of the flag inside the `generation.auth` block.

## Acceptance Criteria
- Project path: /home/user/project
- The file `/home/user/project/gen.yaml` exists and is valid YAML.
- In `/home/user/project/gen.yaml`, the value at path `.generation.auth.oAuth2ClientCredentialsEnabled` is the boolean `true` (verified by `yq` evaluating to the string `"true"`).
- The top-level keys `configVersion` and `generation` are still present, and `generation.auth` still exists as a mapping.
- The TypeScript target section (top-level key `typescript`) is still present in `gen.yaml`.

