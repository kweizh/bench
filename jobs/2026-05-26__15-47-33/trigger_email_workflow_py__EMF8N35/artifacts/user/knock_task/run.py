#!/usr/bin/env python3
"""
Knock Email Workflow Automation Script

This script creates and triggers a Knock workflow that sends a welcome email
to a specified user using the mailtrap email channel.
"""

import os
import sys
import json
import requests

# Required environment variables
REQUIRED_ENV_VARS = [
    'ZEALT_RUN_ID',
    'KNOCK_SERVICE_TOKEN',
    'KNOCK_API_TOKEN',
    'MAILTRAP_DOMAIN',
    'GMAIL_USER_NAME'
]


def validate_environment():
    """Validate that all required environment variables are set."""
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)


def get_env_vars():
    """Get all required environment variables."""
    return {
        'run_id': os.environ['ZEALT_RUN_ID'],
        'service_token': os.environ['KNOCK_SERVICE_TOKEN'],
        'api_token': os.environ['KNOCK_API_TOKEN'],
        'mailtrap_domain': os.environ['MAILTRAP_DOMAIN'],
        'gmail_user_name': os.environ['GMAIL_USER_NAME']
    }


def create_workflow(env_vars):
    """
    Create (upsert) a Knock workflow in the development environment.
    
    Returns the workflow key.
    """
    workflow_key = f"welcome-email-{env_vars['run_id']}"
    workflow_name = f"Welcome Email {env_vars['run_id']}"
    
    url = f"https://control.knock.app/v1/workflows/{workflow_key}?environment=development"
    
    headers = {
        'Authorization': f"Bearer {env_vars['service_token']}",
        'Content-Type': 'application/json'
    }
    
    workflow_data = {
        "workflow": {
            "key": workflow_key,
            "name": workflow_name,
            "description": f"Welcome email workflow for run {env_vars['run_id']}",
            "status": "active",
            "trigger_data_json_schema": {
                "type": "object",
                "properties": {
                    "dashboard_url": {
                        "type": "string"
                    }
                },
                "required": ["dashboard_url"]
            },
            "steps": [
                {
                    "ref": "welcome_email",
                    "type": "channel",
                    "channel_key": "mailtrap",
                    "template": {
                        "key": f"welcome-template-{env_vars['run_id']}",
                        "subject": "Welcome to Knock, {{ recipient.name }}!",
                        "html_body": "<html><body><p>Welcome {{ recipient.name }}!</p><p>Access your dashboard at: <a href=\"{{ data.dashboard_url }}\">{{ data.dashboard_url }}</a></p></body></html>",
                        "settings": {}
                    },
                    "settings": {
                        "from_email_address": f"sender-{env_vars['run_id']}@{env_vars['mailtrap_domain']}"
                    }
                }
            ]
        }
    }
    
    print(f"Creating/upserting workflow: {workflow_key}")
    response = requests.put(url, json=workflow_data, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"Error creating workflow: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    
    print(f"Workflow created successfully: {workflow_key}")
    return workflow_key


def activate_workflow(env_vars, workflow_key):
    """
    Activate the workflow in the development environment.
    """
    url = f"https://control.knock.app/v1/workflows/{workflow_key}/commit?environment=development"
    
    headers = {
        'Authorization': f"Bearer {env_vars['service_token']}",
        'Content-Type': 'application/json'
    }
    
    print(f"Committing workflow: {workflow_key}")
    response = requests.post(url, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"Error committing workflow: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    
    print(f"Workflow committed successfully: {workflow_key}")
    
    if response.status_code not in [200, 201]:
        print(f"Error activating workflow: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    
    print(f"Workflow activated successfully: {workflow_key}")


def identify_user(env_vars, knock_client):
    """
    Identify a user in Knock.
    
    Returns the user ID.
    """
    user_id = f"user-{env_vars['run_id']}"
    user_name = f"Knock User {env_vars['run_id']}"
    user_email = f"{env_vars['gmail_user_name']}+receiver-{env_vars['run_id']}@gmail.com"
    
    print(f"Identifying user: {user_id}")
    
    try:
        knock_client.users.update(
            user_id=user_id,
            name=user_name,
            email=user_email
        )
    except Exception as e:
        print(f"Error identifying user: {e}")
        sys.exit(1)
    
    print(f"User identified successfully: {user_id}")
    
    return {
        'id': user_id,
        'name': user_name,
        'email': user_email
    }


def trigger_workflow(env_vars, knock_client, workflow_key, user):
    """
    Trigger the workflow for the specified user.
    
    Returns the workflow run ID.
    """
    dashboard_url = f"https://app.example.com/dashboard/{env_vars['run_id']}"
    
    print(f"Triggering workflow: {workflow_key} for user: {user['id']}")
    
    try:
        result = knock_client.workflows.trigger(
            key=workflow_key,
            recipients=[user['id']],
            data={
                'dashboard_url': dashboard_url
            }
        )
    except Exception as e:
        print(f"Error triggering workflow: {e}")
        sys.exit(1)
    
    # Extract the workflow run ID from the response
    workflow_run_id = result.get('workflow_run_id') or result.get('workflowRunId')
    
    if not workflow_run_id:
        print(f"Error: Could not extract workflow_run_id from response: {result}")
        sys.exit(1)
    
    print(f"Workflow triggered successfully. Run ID: {workflow_run_id}")
    
    return workflow_run_id


def write_log_file(env_vars, workflow_key, workflow_run_id, user):
    """
    Write the output log file with the required information.
    """
    log_path = "/home/user/knock_task/output.log"
    
    print(f"Writing log file: {log_path}")
    
    with open(log_path, 'w') as f:
        f.write(f"Workflow key: {workflow_key}\n")
        f.write(f"Workflow run id: {workflow_run_id}\n")
        f.write(f"Recipient id: {user['id']}\n")
        f.write(f"Recipient email: {user['email']}\n")
    
    print(f"Log file written successfully")


def main():
    """Main execution function."""
    print("Starting Knock email workflow automation...")
    
    # Validate environment
    validate_environment()
    
    # Get environment variables
    env_vars = get_env_vars()
    
    # Create workflow
    workflow_key = create_workflow(env_vars)
    
    # Activate workflow
    activate_workflow(env_vars, workflow_key)
    
    # Import knockapi after validating environment
    try:
        import knockapi
        from knockapi import Knock
    except ImportError:
        print("Error: knockapi package not installed. Please install it with: pip install knockapi")
        sys.exit(1)
    
    # Initialize Knock client
    knock_client = Knock(api_key=env_vars['api_token'])
    
    # Identify user
    user = identify_user(env_vars, knock_client)
    
    # Trigger workflow
    workflow_run_id = trigger_workflow(env_vars, knock_client, workflow_key, user)
    
    # Write log file
    write_log_file(env_vars, workflow_key, workflow_run_id, user)
    
    print("Knock email workflow automation completed successfully!")


if __name__ == '__main__':
    main()