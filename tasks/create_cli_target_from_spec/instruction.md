# Configure a Speakeasy CLI Target

## Background
You have an `openapi.yaml` file for a simple API. Use Speakeasy to configure a project that generates a CLI application from this specification.

## Requirements
- Initialize a Speakeasy workflow configuration in `.speakeasy/workflow.yaml` with a target named `my-target` of type `cli`.
- The workflow should reference a source named `my-source` pointing to `./openapi.yaml`.
- Create a valid `gen.yaml` in `.speakeasy/gen.yaml` for the `cli` target.
- The `gen.yaml` must define the `cli` target with `version: 1.0.0` and the generation config must have `sdkClassName: TestAPI`.

## Implementation Guide
1. Create the `.speakeasy` directory.
2. Create `.speakeasy/workflow.yaml` with the source and target configuration.
3. Create `.speakeasy/gen.yaml` with the `cli` target configuration.
4. Run `speakeasy lint config` to ensure your configuration is valid.

## Constraints
- Project path: /home/user/myproject
- Do not attempt to use commands that require authentication (like `speakeasy generate` or `speakeasy configure`). You must create the configuration files manually based on Speakeasy documentation.