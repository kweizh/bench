# Knock Branch Workflow Project

This project demonstrates how to use the Knock Management SDK to upsert a workflow with a branch step and trigger it using the Knock Node SDK.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set the required environment variables:
```bash
export ZEALT_RUN_ID="your-run-id"
export GMAIL_USER_NAME="your-gmail-username"
export KNOCK_API_KEY="your-knock-api-key"
export KNOCK_SERVICE_TOKEN="your-knock-service-token"
```

## Usage

Run the project:
```bash
npm start
```

## What it does

1. **Upserts a workflow** in the `development` environment with:
   - A top-level `branch` step that routes based on `data.channel_preference`
   - Two branches:
     - Email branch: runs when `channel_preference == "email"`, sends via `mailtrap` channel
     - Default branch: runs otherwise, sends via `in-app` channel
   - JSON schema requiring `channel_preference` as a string

2. **Activates the workflow** in the development environment

3. **Triggers the workflow twice**:
   - First with `channel_preference = "email"` (exercises email branch)
   - Second with `channel_preference = "in-app"` (exercises default branch)

4. **Logs results** to `output.log`:
   - Workflow key
   - Email branch run ID
   - In-app branch run ID

## Output

The script creates an `output.log` file with the following format:
```
Workflow Key: branch-flow-<run-id>
Email Run ID: <uuid>
InApp Run ID: <uuid>
```

## Requirements

- Node.js 20 LTS or later
- Valid Knock API credentials
- Knock workspace with `in-app` and `mailtrap` channels configured