#!/usr/bin/env python3
"""
Setup and trigger a Knock workflow with per-recipient data.
"""

import os
import json
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/myproject/output.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_run_id():
    """Get the run ID from environment variable."""
    run_id = os.environ.get('ZEALT_RUN_ID')
    if not run_id:
        raise ValueError("ZEALT_RUN_ID environment variable is required")
    logger.info(f"Using run-id: {run_id}")
    return run_id


def get_knock_tokens():
    """Get Knock tokens from environment variables."""
    service_token = os.environ.get('KNOCK_SERVICE_TOKEN')
    api_token = os.environ.get('KNOCK_API_TOKEN')
    gmail_user = os.environ.get('GMAIL_USER_NAME')
    
    if not service_token:
        raise ValueError("KNOCK_SERVICE_TOKEN environment variable is required")
    if not api_token:
        raise ValueError("KNOCK_API_TOKEN environment variable is required")
    if not gmail_user:
        raise ValueError("GMAIL_USER_NAME environment variable is required")
    
    return service_token, api_token, gmail_user


def create_workflow(run_id, service_token):
    """
    Create or update a Knock workflow using the Management API.
    
    Args:
        run_id: The run ID for namespacing
        service_token: The Knock service token for authentication
    
    Returns:
        The workflow key
    """
    workflow_key = f"per-recipient-alert-{run_id}"
    
    # Build the workflow definition
    workflow_definition = {
        "key": workflow_key,
        "name": f"Per-Recipient Alert {run_id}",
        "description": "Workflow that sends personalized emails to multiple recipients",
        "active": True,
        "steps": [
            {
                "key": "email_step",
                "type": "channel",
                "channel_key": "mailtrap",
                "templates": {
                    "subject": "Alert: {{ data.alert_type }} - {{ data.role }}",
                    "body": "Hello {{ recipient.name }},\n\n"
                           "You are receiving this alert because you are a {{ data.role }}.\n\n"
                           "Alert Type: {{ data.alert_type }}\n"
                           "Role: {{ data.role }}\n\n"
                           "Please check your dashboard for more details:\n"
                           "{{ data.dashboard_url }}\n\n"
                           "Best regards,\n"
                           "Jurassic Park Team"
                }
            }
        ]
    }
    
    logger.info(f"Upserting workflow: {workflow_key}")
    
    # Use Management API to upsert the workflow
    management_url = f"https://api.knock.app/v1/workflows/{workflow_key}"
    headers = {
        "Authorization": f"Bearer {service_token}",
        "Content-Type": "application/json",
        "X-Knock-Environment": "development"
    }
    
    response = requests.put(
        management_url,
        headers=headers,
        json=workflow_definition
    )
    
    if response.status_code not in [200, 201]:
        logger.error(f"Failed to create workflow: {response.status_code} - {response.text}")
        response.raise_for_status()
    
    logger.info(f"Workflow created/updated successfully: {workflow_key}")
    
    # Activate the workflow
    activate_url = f"https://api.knock.app/v1/workflows/{workflow_key}/activate"
    activate_response = requests.post(
        activate_url,
        headers=headers
    )
    
    if activate_response.status_code not in [200, 201]:
        logger.warning(f"Failed to activate workflow: {activate_response.status_code} - {activate_response.text}")
        # Don't fail if activation fails, it might already be active
    else:
        logger.info(f"Workflow activated successfully")
    
    return workflow_key


def trigger_workflow(run_id, api_token, gmail_user, workflow_key):
    """
    Trigger the workflow with inline recipients using the Knock backend SDK.
    
    Args:
        run_id: The run ID for namespacing
        api_token: The Knock API token for authentication
        gmail_user: The Gmail username for email addresses
        workflow_key: The key of the workflow to trigger
    
    Returns:
        The workflow run ID
    """
    # Import the Knock SDK
    import knockapi
    from knockapi.rest import ApiException
    
    # Configure the Knock client
    configuration = knockapi.Configuration(
        host="https://api.knock.app"
    )
    configuration.api_key['ApiKey'] = api_token
    
    # Create the API client
    client = knockapi.KnockApi(configuration)
    
    # Prepare the trigger data
    trigger_data = {
        "data": {
            "alert_type": "security_breach"
        },
        "recipients": [
            {
                "id": f"owner-{run_id}",
                "name": "John Hammond",
                "email": f"{gmail_user}+r1-{run_id}@gmail.com",
                "$trigger_data": {
                    "role": "Park Owner",
                    "dashboard_url": f"https://jurassicpark.com/dashboard/owner-{run_id}"
                }
            },
            {
                "id": f"paleo-{run_id}",
                "name": "Ellie Sattler",
                "email": f"{gmail_user}+r2-{run_id}@gmail.com",
                "$trigger_data": {
                    "role": "Paleobotanist",
                    "dashboard_url": f"https://jurassicpark.com/dashboard/paleo-{run_id}"
                }
            }
        ]
    }
    
    logger.info(f"Triggering workflow: {workflow_key}")
    logger.info(f"Recipients: {[r['id'] for r in trigger_data['recipients']]}")
    
    # Trigger the workflow
    workflow_trigger_request = knockapi.WorkflowTriggerRequest(**trigger_data)
    
    try:
        response = client.workflows.trigger(workflow_key, workflow_trigger_request)
        workflow_run_id = response.workflow_run_id
        logger.info(f"Workflow triggered successfully")
        logger.info(f"Workflow run ID: {workflow_run_id}")
        return workflow_run_id
    except ApiException as e:
        logger.error(f"Failed to trigger workflow: {e}")
        raise


def main():
    """Main function to orchestrate the setup and trigger process."""
    try:
        # Get environment variables
        run_id = get_run_id()
        service_token, api_token, gmail_user = get_knock_tokens()
        
        # Create and activate the workflow
        workflow_key = create_workflow(run_id, service_token)
        
        # Trigger the workflow with inline recipients
        workflow_run_id = trigger_workflow(run_id, api_token, gmail_user, workflow_key)
        
        # Log the results
        logger.info(f"Workflow key: {workflow_key}")
        logger.info(f"Workflow run ID: {workflow_run_id}")
        
        print(f"\n✓ Workflow successfully created and triggered!")
        print(f"  Workflow key: {workflow_key}")
        print(f"  Workflow run ID: {workflow_run_id}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())