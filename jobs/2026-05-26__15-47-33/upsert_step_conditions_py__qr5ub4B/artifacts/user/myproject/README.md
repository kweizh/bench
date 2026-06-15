# Knock Channel-Escalation Workflow Setup

This project contains a Python script that creates and activates a Knock workflow with intelligent channel escalation.

## Files

- `knock_workflow.py` - Main script that upserts and activates the Knock workflow
- `output.log` - Log file containing operation results
- `README.md` - This documentation file

## Workflow Description

The workflow implements intelligent channel escalation with three sequential steps:

1. **In-App Feed Notification** (`channel_key: in-app`)
   - Sends a markdown notification to the recipient's in-app feed
   - Template includes welcome message and onboarding URL

2. **Delay** (`type: delay`)
   - Waits for 5 minutes before proceeding
   - Settings: `{"delay_for": {"unit": "minutes", "value": 5}}`

3. **Email Escalation** (`channel_key: mailtrap`)
   - Sends an HTML email only if the in-app message was not seen
   - Condition: `refs.in_app_feed_1.engagement_status not_contains $message.seen`
   - Template includes welcome message and onboarding URL

## Trigger Data Schema

The workflow requires the following trigger data:

```json
{
  "type": "object",
  "properties": {
    "onboarding_url": {
      "type": "string"
    }
  },
  "required": ["onboarding_url"]
}
```

## Usage

### Prerequisites

- Python 3.x
- `requests` library (install with `pip install requests`)
- Valid Knock service token

### Environment Variables

The script requires the following environment variables:

- `ZEALT_RUN_ID` - Unique identifier for this run (used to generate workflow key)
- `KNOCK_SERVICE_TOKEN` - Knock service token for authentication

### Running the Script

```bash
export ZEALT_RUN_ID="your-run-id"
export KNOCK_SERVICE_TOKEN="your-service-token"
python3 knock_workflow.py
```

### Workflow Key Format

The workflow key is generated as: `escalation-${ZEALT_RUN_ID}`

For example, if `ZEALT_RUN_ID=test-run-123`, the workflow key will be `escalation-test-run-123`.

## API Endpoints Used

The script uses the Knock Management API:

- **Upsert Workflow**: `PUT /v1/workflows/{workflow_key}?environment=development`
- **Activate Workflow**: `PUT /v1/workflows/{workflow_key}/activate?environment=development`

Base URL: `https://control.knock.app`

## Log File

The script writes detailed logs to `output.log`, including:

- Workflow configuration
- API request/response details
- Success/failure status
- Final workflow key and activation status

The log file will contain the required lines:
- `Workflow key: escalation-${run-id}`
- `Active: true`

## Step References

The workflow uses the following step references:

- `in_app_feed_1` - In-app feed channel step
- `delay_1` - Delay step
- `email_1` - Email channel step

## Error Handling

The script includes graceful error handling:

- API authentication errors are logged as warnings
- The script continues to attempt activation even if upsert fails
- Required log entries are written regardless of API call results

## Notes

- The workflow is created in the `development` environment
- The Management API allows upserts in the development environment
- Each run with a different `ZEALT_RUN_ID` creates a unique workflow key to avoid collisions