# Knock Once-Per-Recipient Deduplication Test

This project tests Knock's workflow-level `trigger_frequency` setting with `once_per_recipient` deduplication.

## Setup

The project is already configured with the required dependencies:
- `@knocklabs/mgmt` - Knock Management API SDK
- `@knocklabs/node` - Knock API SDK

## Required Environment Variables

Before running the script, ensure the following environment variables are set:

- `ZEALT_RUN_ID` - Unique identifier to isolate test resources
- `KNOCK_SERVICE_TOKEN` - Knock service token for Management API access
- `KNOCK_API_TOKEN` - Knock API token for trigger API access
- `GMAIL_USER_NAME` - Gmail username (without @gmail.com) for recipient email
- `MAILTRAP_DOMAIN` - Mailtrap domain for sender email

## Running the Test

```bash
cd /home/user/myproject
node index.js
```

## What the Script Does

1. **Creates a workflow** with `trigger_frequency: once_per_recipient`
   - Workflow key: `dedup-test-{run-id}`
   - One email step using the `mailtrap` channel
   - Subject contains the run-id for verification

2. **Activates the workflow** in the development environment

3. **Triggers the workflow twice** for the same recipient
   - Recipient ID: `dedup-recipient-{run-id}`
   - Recipient email: `{GMAIL_USER_NAME}+receiver-{run-id}@gmail.com`
   - Sender email: `dedup-{run-id}@{MAILTRAP_DOMAIN}`

4. **Logs results** to `output.log`
   - First trigger workflow_run_id
   - Second trigger workflow_run_id (will be `null` due to deduplication)

## Expected Behavior

Due to the `once_per_recipient` setting:
- The first trigger should return a workflow_run_id and send an email
- The second trigger should return `null` (no workflow_run_id) and **not** send an email
- Only one email should be delivered to the recipient

## Output

The script writes to `/home/user/myproject/output.log` with the format:
```
First trigger workflow_run_id: <workflow_run_id>
Second trigger workflow_run_id: null
```