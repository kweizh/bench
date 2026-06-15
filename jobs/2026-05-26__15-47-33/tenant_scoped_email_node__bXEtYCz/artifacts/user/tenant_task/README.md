# Tenant-Scoped Knock Email Workflow

This Node.js automation creates a tenant with custom properties, upserts a workflow with tenant-scoped email templates, activates the workflow, and triggers it for a Gmail-backed recipient.

## Environment Variables

The following environment variables are required:

- `KNOCK_API_TOKEN` - Knock API token for tenant operations and workflow triggers
- `KNOCK_SERVICE_TOKEN` - Knock service token for management API operations
- `ZEALT_RUN_ID` - Unique run identifier for resource isolation (defaults to timestamp if not provided)
- `GMAIL_USER_NAME` - Gmail username (without @gmail.com) for recipient email
- `MAILTRAP_DOMAIN` - Mailtrap domain for sender email (defaults to mailtrap.io)

## Installation

```bash
npm install
```

## Usage

```bash
npm start
```

## What It Does

1. **Creates a tenant** with:
   - ID: `tenant-{run-id}`
   - Name including run-id
   - Custom branding color
   - Custom property `app_name`

2. **Upserts a workflow** in development environment with:
   - Key: `tenant-welcome-{run-id}`
   - Email step bound to Mailtrap channel
   - Subject template referencing `tenant.app_name`
   - HTML body template referencing `recipient.name` and `tenant.name`
   - Custom sender email address

3. **Activates the workflow** in development environment

4. **Triggers the workflow** with:
   - Tenant scope set to the created tenant
   - Single recipient with Gmail+ alias email

5. **Logs results** to `output.log` with:
   - Tenant ID
   - Workflow Key
   - Workflow Run ID
   - Recipient Email

## Output

The log file `output.log` will contain:
```
Tenant ID: tenant-<run-id>
Workflow Key: tenant-welcome-<run-id>
Workflow Run ID: <uuid>
Recipient Email: <GMAIL_USER_NAME>+receiver-<run-id>@gmail.com
```