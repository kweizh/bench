import KnockMgmt from '@knocklabs/mgmt';
import Knock from '@knocklabs/node';
import fs from 'fs';
import path from 'path';

// Read environment variables
const KNOCK_SERVICE_TOKEN = process.env.KNOCK_SERVICE_TOKEN;
const KNOCK_API_TOKEN = process.env.KNOCK_API_TOKEN;
const MAILTRAP_DOMAIN = process.env.MAILTRAP_DOMAIN;
const GMAIL_USER_NAME = process.env.GMAIL_USER_NAME;
const ZEALT_RUN_ID = process.env.ZEALT_RUN_ID;

// Validate required environment variables
if (!KNOCK_SERVICE_TOKEN || !KNOCK_API_TOKEN || !GMAIL_USER_NAME || !ZEALT_RUN_ID) {
  console.error('Missing required environment variables');
  process.exit(1);
}

// Generate workflow key with run ID suffix
const workflowKey = `top-level-conditions-${ZEALT_RUN_ID}`;

// Initialize clients
const mgmtClient = new KnockMgmt({
  serviceToken: KNOCK_SERVICE_TOKEN,
});

const apiClient = new Knock({
  apiKey: KNOCK_API_TOKEN,
});

async function main() {
  try {
    console.log('Creating workflow with top-level conditions...');

    // Upsert workflow with top-level conditions
    const upsertResponse = await mgmtClient.workflows.upsert(workflowKey, {
      environment: 'development',
      workflow: {
        name: `Admin-only security alert - ${ZEALT_RUN_ID}`,
        description: 'Admin-only security alert notification',
        conditions: {
          all: [
            {
              variable: 'recipient.role',
              operator: 'equal_to',
              argument: 'admin',
            },
          ],
        },
        steps: [
          {
            ref: 'mailtrap_email',
            type: 'channel',
            channel_key: 'mailtrap',
            template: {
              subject: `Admin alert ${ZEALT_RUN_ID}`,
              html_body: `<p>Hello {{ recipient.name }},</p><p>This is an admin-only security alert.</p>`,
            },
          },
        ],
        trigger_frequency: 'every_trigger',
      },
    });

    console.log('Workflow upserted successfully:', upsertResponse.workflow.key);

    // Activate the workflow in development environment
    console.log('Activating workflow...');
    const activateResponse = await mgmtClient.workflows.activate(workflowKey, {
      environment: 'development',
      status: true,
    });

    console.log('Workflow activated successfully:', activateResponse.workflow.active);

    // Prepare recipients with inline identification
    const adminRecipientId = `admin-${ZEALT_RUN_ID}`;
    const viewerRecipientId = `viewer-${ZEALT_RUN_ID}`;

    const recipients = [
      {
        id: adminRecipientId,
        name: 'Admin User',
        email: `${GMAIL_USER_NAME}+${adminRecipientId}@gmail.com`,
        role: 'admin',
      },
      {
        id: viewerRecipientId,
        name: 'Viewer User',
        email: `${GMAIL_USER_NAME}+${viewerRecipientId}@gmail.com`,
        role: 'viewer',
      },
    ];

    // Trigger the workflow with two recipients
    console.log('Triggering workflow with recipients...');
    const triggerResponse = await apiClient.workflows.trigger(workflowKey, {
      recipients: recipients,
      data: {
        alert_type: 'security',
        message: 'Admin-only security alert',
      },
      tenant: 'default',
    });

    console.log('Workflow triggered successfully');
    console.log('Workflow run ID:', triggerResponse.workflow_run_id);

    // Write workflow run ID to output.log
    const logPath = path.join('/home/user/myproject', 'output.log');
    fs.writeFileSync(logPath, `Workflow run ID: ${triggerResponse.workflow_run_id}\n`);
    console.log(`Workflow run ID written to ${logPath}`);

  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();