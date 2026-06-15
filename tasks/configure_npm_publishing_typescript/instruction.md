# Configure npm Publishing for a Speakeasy TypeScript SDK

## Background
Speakeasy generates TypeScript SDKs from OpenAPI specifications. Before such an SDK can be published to npm, the `gen.yaml` configuration file must declare the npm package name (and ideally the author) under the `typescript` section. A project has been bootstrapped at `/home/user/project` with an existing `gen.yaml` that still uses the default `packageName` (`openapi`). You must update the configuration so the SDK is publishable as a scoped npm package.

## Requirements
- Update `/home/user/project/gen.yaml` so that the npm package name for the TypeScript target is set to `@example/my-sdk`.
- Also set the package `author` for the TypeScript target to `Example Team`.
- Keep the rest of the file valid YAML (do not corrupt existing keys such as `configVersion`, `generation`, or the TypeScript `version` field).

## Implementation Hints
- Speakeasy TypeScript publishing fields live directly under the top-level `typescript` key in `gen.yaml` (not under a `targets` block). Refer to the [TypeScript configuration reference](https://www.speakeasy.com/docs/speakeasy-reference/generation/ts-config) for the exact field names.
- You can edit `gen.yaml` directly with a text editor, or use a YAML-aware tool such as `yq` to set the fields.
- The Speakeasy CLI (`speakeasy`) and `yq` are installed in the environment if you want to use them for inspection.

## Acceptance Criteria
- Project path: /home/user/project
- The file `/home/user/project/gen.yaml` exists and is valid YAML.
- In `gen.yaml`, the value at `.typescript.packageName` equals `@example/my-sdk`.
- In `gen.yaml`, the value at `.typescript.author` equals `Example Team`.
- The TypeScript `version` field (`.typescript.version`) and the top-level `configVersion` field remain present and unchanged.

