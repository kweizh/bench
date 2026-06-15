# Upsert a Knock Workflow With Trigger Data Validation (Node.js)

## Background
Knock supports JSON-Schema validation of the `data` payload sent to a workflow trigger via the `trigger_data_json_schema` field on a workflow. When this field is set, the Knock trigger endpoint will reject any payload that does not match the schema with a `422 Unprocessable Entity` response. Your job is to programmatically create such a validated workflow using the Knock Node.js Management SDK, activate it, and then exercise it by triggering it with both a valid and an invalid payload using the Knock Node.js SDK.

## Requirements
- Build a Node.js script that uses the `@knocklabs/mgmt` SDK to upsert a workflow in the `development` environment of your Knock account.
  - Workflow key: `order-confirmation-${run-id}` (where `${run-id}` is the value of the `ZEALT_RUN_ID` environment variable).
  - Workflow `name`: `Order Confirmation ${run-id}`.
  - The workflow must declare a `trigger_data_json_schema` requiring all three properties below as `required`, with the following exact JSON Schema types:
    - `order_id`: string
    - `total_amount`: number
    - `customer_email`: string with `format` set to `email`
  - The workflow must contain exactly one channel step targeting the `in-app` channel (channel key `in-app`) with a Markdown template body that includes the Liquid placeholders `{{ data.order_id }}` and `{{ data.total_amount }}`.
- After upsert, activate the workflow in the `development` environment so it can be triggered.
- Build a second Node.js script that uses the `@knocklabs/node` SDK to:
  1. Trigger the workflow once with a valid payload and capture the returned `workflow_run_id`.
  2. Trigger the workflow a second time with an invalid payload (a payload that the schema rejects, e.g., `total_amount` sent as a string) and capture the error.
- Both scripts must write structured results to a single shared log file so the verifier can inspect them.

## Implementation Hints
- Read `run-id` from the `ZEALT_RUN_ID` environment variable and append it to the workflow key and workflow name to keep concurrent runs isolated.
- `@knocklabs/mgmt` provides `client.workflows.upsert(workflowKey, { environment, workflow })` and `client.workflows.activate(workflowKey, { environment, status })` — use the management service token (`KNOCK_SERVICE_TOKEN`) for these calls. Service tokens authenticate management API calls; the trigger API requires the environment-scoped secret API key (`KNOCK_API_TOKEN`).
- `@knocklabs/node`'s `knock.workflows.trigger(key, { recipients, data })` returns `{ workflow_run_id }` on success and throws on validation errors. Catch the validation error from the invalid trigger and serialize its HTTP status code and message into the log.
- Use any non-empty recipient identifier for trigger calls (e.g., `recipient-${run-id}`); inline recipients are fine.

## Acceptance Criteria
- Project path: /home/user/knock_task
- Ensure both scripts are executed and produce the artifacts listed below.
- Log file: /home/user/knock_task/output.log
- The workflow created by the upsert script must be named `order-confirmation-${run-id}` in the `development` environment, must be active, and must carry a `trigger_data_json_schema` requiring `order_id`, `total_amount`, and `customer_email`.
- The log file must contain the following lines (in any order, one per line) where `${run-id}` is read from the `ZEALT_RUN_ID` environment variable:
  - `Workflow Key: order-confirmation-${run-id}`
  - `Workflow Active: true`
  - `Valid Trigger Workflow Run ID: <uuid>` where `<uuid>` is the `workflow_run_id` returned by the valid trigger call.
  - `Invalid Trigger Status: 422`

