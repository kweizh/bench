# Knock Workflow Cancellation Task

This project demonstrates how to trigger a Knock workflow with a cancellation key and then cancel it before the email is delivered.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Fill in the required environment variables:
   - `ZEALT_RUN_ID`: Unique identifier for this run
   - `GMAIL_USER_NAME`: Your Gmail username (before @gmail.com)
   - `MAILTRAP_DOMAIN`: Your Mailtrap domain
   - `KNOCK_SERVICE_TOKEN`: Knock service token for management API
   - `KNOCK_API_TOKEN`: Knock API token for triggering workflows

## Usage

Run the automation:
```bash
npm start
```

## What It Does

1. Creates a Knock workflow with a 30-second delay followed by a Mailtrap email step
2. Activates the workflow in the development environment
3. Triggers the workflow with a cancellation key
4. Waits 5 seconds
5. Cancels the workflow before the delay completes
6. Logs the workflow key, run ID, cancellation key, and recipient email to `output.log`

## Expected Output

The script will create `/home/user/cancel_task/output.log` with the following lines:
- `Workflow Key: cancel-flow-<run-id>`
- `Workflow Run ID: <uuid>`
- `Cancellation Key: cancel-<run-id>`
- `Recipient Email: <GMAIL_USER_NAME>+receiver-<run-id>@gmail.com`

## Verification

After running, verify that:
- The workflow exists and is active in the Knock development environment
- The workflow contains a delay step followed by a mailtrap channel step
- No email was delivered to the recipient's Gmail inbox