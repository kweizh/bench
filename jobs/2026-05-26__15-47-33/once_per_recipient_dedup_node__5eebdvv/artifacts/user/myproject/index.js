const { Knock } = require('@knocklabs/node');
const { Knock as KnockMgmt } = require('@knocklabs/mgmt');
const fs = require('fs');
const path = require('path');

// Read environment variables
const runId = process.env.ZEALT_RUN_ID;
const knockServiceToken = process.env.KNOCK_SERVICE_TOKEN;
const knockApiToken = process.env.KNOCK_API_TOKEN;
const gmailUserName = process.env.GMAIL_USER_NAME;
const mailtrapDomain = process.env.MAILTRAP_DOMAIN;

// Validate required environment variables
if (!runId) {
  throw new Error('ZEALT_RUN_ID environment variable is required');
}
if (!knockServiceToken) {
  throw new Error('KNOCK_SERVICE_TOKEN environment variable is required');
}
if (!knockApiToken) {
  throw new Error('KNOCK_API_TOKEN environment variable is required');
}
if (!gmailUserName) {
  throw new Error('GMAIL_USER_NAME environment variable is required');
}
if (!mailtrapDomain) {
  throw new Error('MAILTRAP_DOMAIN environment variable is required');
}

// Initialize Knock clients
const knockClient = new Knock(knockApiToken);
const knockMgmtClient = new KnockMgmt(knockServiceToken);

// Log file path
const logFilePath = '/home/user/myproject/output.log';

async function main() {
  console.log(`Starting deduplication test with run-id: ${runId}`);

  // Workflow configuration
  const workflowKey = `dedup-test-${runId}`;
  const recipientId = `dedup-recipient-${runId}`;
  const recipientEmail = `${gmailUserName}+receiver-${runId}@gmail.com`;
  const recipientName = `Recipient ${runId}`;
  const senderEmail = `dedup-${runId}@${mailtrapDomain}`;

  console.log(`Workflow key: ${workflowKey}`);
  console.log(`Recipient: ${recipientEmail}`);

  // Step 1: Upsert workflow using Management API
  console.log('Upserting workflow...');
  const workflow = await knockMgmtClient.workflows.upsert(workflowKey, {
    name: `Dedup Test Workflow ${runId}`,
    trigger_frequency: 'once_per_recipient',
    steps: [
      {
        channel_key: 'mailtrap',
        email: {
          subject: `Dedup Test ${runId} - Welcome!`,
          from: senderEmail,
        },
      },
    ],
  });

  console.log(`Workflow upserted: ${workflow.id}`);

  // Step 2: Activate the workflow in development environment
  console.log('Activating workflow in development environment...');
  await knockMgmtClient.workflows.activate(workflowKey, 'development');
  console.log('Workflow activated');

  // Step 3: Trigger the workflow twice for the same recipient
  console.log('Triggering workflow (first time)...');
  const firstTrigger = await knockClient.workflows.trigger(workflowKey, {
    recipients: [
      {
        id: recipientId,
        email: recipientEmail,
        name: recipientName,
      },
    ],
    data: {},
  });

  const firstWorkflowRunId = firstTrigger.workflow_run_id || null;
  console.log(`First trigger workflow_run_id: ${firstWorkflowRunId}`);

  console.log('Triggering workflow (second time)...');
  const secondTrigger = await knockClient.workflows.trigger(workflowKey, {
    recipients: [
      {
        id: recipientId,
        email: recipientEmail,
        name: recipientName,
      },
    ],
    data: {},
  });

  const secondWorkflowRunId = secondTrigger.workflow_run_id || null;
  console.log(`Second trigger workflow_run_id: ${secondWorkflowRunId}`);

  // Step 4: Write to log file
  const logContent = `First trigger workflow_run_id: ${firstWorkflowRunId}\nSecond trigger workflow_run_id: ${secondWorkflowRunId}\n`;
  fs.writeFileSync(logFilePath, logContent, 'utf-8');

  console.log(`Log written to ${logFilePath}`);
  console.log('Test completed successfully!');
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});