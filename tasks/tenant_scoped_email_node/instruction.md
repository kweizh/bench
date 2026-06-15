# Tenant-Scoped Knock Email Workflow (Node.js)

## Background
Knock (https://knock.app) is a notification infrastructure platform. Its workflow engine supports multi-tenancy: when a workflow is triggered with a `tenant` field, the engine exposes the full tenant object inside the workflow run scope (available in templates as `{{ tenant.* }}`), tags every produced message with the tenant id, and applies any tenant-level branding overrides.

The Knock workspace used for this task already has two channels configured:
- An in-app feed channel with channel key `in-app`.
- A Mailtrap email channel with channel key `mailtrap`.

You will build a Node.js automation that explicitly creates a tenant with custom properties using the Knock Node SDK, upserts a workflow whose email template uses tenant data, activates the workflow, and triggers it for a Gmail-backed recipient scoped to that tenant.

## Requirements
- Implement the automation as a Node.js project located at `/home/user/tenant_task` that runs end-to-end with `npm start`.
- Use `@knocklabs/node` (authenticated with `KNOCK_API_TOKEN`) to **set a tenant** in Knock with custom properties:
  - The tenant `name` must include the run id.
  - The tenant `settings.branding.primary_color` must be set to a non-empty hex color string.
  - The tenant must carry a custom top-level property `app_name` with a non-empty string value.
- Use `@knocklabs/mgmt` (authenticated with `KNOCK_SERVICE_TOKEN`) to **upsert** a workflow in the `development` environment whose body contains a single channel step bound to the `mailtrap` channel.
  - The email step's subject template MUST reference `{{ tenant.app_name }}` so the rendered subject contains the tenant's `app_name` value.
  - The email step's HTML body template MUST reference `{{ recipient.name }}` and `{{ tenant.name }}` so the rendered body contains both values.
  - The email step's `settings.from_email_address` MUST be `sender-${run-id}@${MAILTRAP_DOMAIN}`.
- **Activate** the workflow in the `development` environment via the Management API after upserting it.
- Use `@knocklabs/node` to **trigger** the workflow exactly once with:
  - The `tenant` field set to the tenant id created above.
  - A single inline recipient whose `email` is the Gmail `+receiver-${run-id}` address described in the Acceptance Criteria.
- Persist the workflow key, tenant id, workflow run id, and recipient email to a log file in the format described in the Acceptance Criteria.
- All resource identifiers that are externally visible must be suffixed with the current `run-id` so concurrent runs do not collide.

## Implementation Hints
- Read the current `run-id` from the `ZEALT_RUN_ID` environment variable and append it to the tenant id, workflow key, recipient id, and email subject so concurrent runs do not collide.
- The Knock Node client exposes `client.tenants.set(id, { name, settings, ...customProps })`. Custom properties (such as `app_name`) sit alongside `name` and `settings` at the top level of the request body.
- The Knock Management API only writes to the `development` environment; pass `environment: "development"` to both `workflows.upsert` and the activation call.
- Inside Liquid templates the tenant payload is available under the `tenant` namespace (for example, `{{ tenant.name }}` and `{{ tenant.app_name }}`).
- When triggering the workflow, set the top-level `tenant` field to the tenant id you created; Knock will associate every message produced for the run with that tenant.
- After triggering, append the workflow key, tenant id, run id, and recipient email to the log file using the exact prefixes shown in Acceptance Criteria.

## Acceptance Criteria
- Project path: `/home/user/tenant_task`
- Ensure the real Knock tenant set, workflow upsert, activation, and trigger actions are executed against the live Knock environment (no mocks).
- Log file: `/home/user/tenant_task/output.log`
- Read `run-id` from the `ZEALT_RUN_ID` environment variable.
- A tenant whose `id` equals `tenant-${run-id}` MUST exist in Knock with:
  - A `name` that contains the `run-id` (Knock may return this under `properties.name`).
  - `settings.branding.primary_color` set to a non-empty hex color string.
  - A custom property `app_name` whose value is a non-empty string (Knock may return this under `properties.app_name`).
- A workflow whose `key` equals `tenant-welcome-${run-id}` MUST exist in the `development` environment and MUST be `active`.
- The workflow MUST contain at least one `channel` step whose `channel_key` is `mailtrap`, whose subject template references `tenant.app_name`, and whose HTML body template references both `recipient.name` and `tenant.name`.
- The workflow MUST be triggered exactly once with `tenant` set to `tenant-${run-id}` and a single inline recipient whose:
  - `id` is `user-${run-id}`.
  - `email` is `${GMAIL_USER_NAME}+receiver-${run-id}@gmail.com`.
  - `name` includes the `run-id`.
- A Knock message that was produced from workflow `tenant-welcome-${run-id}` for user `user-${run-id}` MUST be tagged with `tenant = tenant-${run-id}`.
- The log file MUST contain the following four lines (one per line, in any order):
  - `Tenant ID: tenant-<run-id>`
  - `Workflow Key: tenant-welcome-<run-id>`
  - `Workflow Run ID: <uuid>` where `<uuid>` is the `workflow_run_id` returned by the trigger call.
  - `Recipient Email: <GMAIL_USER_NAME>+receiver-<run-id>@gmail.com`
- An email matching the rendered subject (containing the tenant `app_name` value) MUST arrive in the Gmail inbox of `${GMAIL_USER_NAME}+receiver-${run-id}@gmail.com`.

