const { KnockMgmt } = require('@knocklabs/mgmt');
const { Knock } = require('@knocklabs/node');
const fs = require('fs');
const path = require('path');

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  // Read run-id from environment variable
  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) {
    throw new Error('ZEALT_RUN_ID environment variable is required');
  }

  const knockServiceToken = process.env.KNOCK_SERVICE_TOKEN;
  if (!knockServiceToken) {
    throw new Error('KNOCK_SERVICE_TOKEN environment variable is required');
  }

  const knockApiToken = process.env.KNOCK_API_TOKEN;
  if (!knockApiToken) {
    throw new Error('KNOCK_API_TOKEN environment variable is required');
  }

  const mailtrapDomain = process.env.MAILTRAP_DOMAIN;
  if (!mailtrapDomain) {
    throw new Error('MAILTRAP_DOMAIN environment variable is required');
  }

  const gmailUserName = process.env.GMAIL_USER_NAME;
  if (!gmailUserName) {
    throw new Error('GMAIL_USER_NAME environment variable is required');
  }

  // Derived identifiers
  const workflowKey = `cancel-flow-${runId}`;
  const recipientId = `user-${runId}`;
  const cancellationKey = `cancel-${runId}`;
  const recipientEmail = `${gmailUserName}+receiver-${runId}@gmail.com`;
  const senderEmail = `sender-${runId}@${mailtrapDomain}`;

  console.log(`Run ID: ${runId}`);
  console.log(`Workflow Key: ${workflowKey}`);
  console.log(`Cancellation Key: ${cancellationKey}`);
  console.log(`Recipient Email: ${recipientEmail}`);
  console.log(`Sender Email: ${senderEmail}`);

  // Initialize the Management API client
  const mgmtClient = new KnockMgmt({
    serviceToken: knockServiceToken,
  });

  // Step 1: Upsert the workflow in the development environment (with commit)
  console.log('\nUpserting workflow...');
  const upsertResponse = await mgmtClient.workflows.upsert(workflowKey, {
    environment: 'development',
    commit: true,
    workflow: {
      name: `Cancel Flow ${runId}`,
      steps: [
        // Step 1: Delay function step (60 seconds - long enough to cancel)
        {
          ref: 'delay-step',
          type: 'delay',
          settings: {
            delay_for: {
              unit: 'seconds',
              value: 60,
            },
          },
        },
        // Step 2: Email channel step via Mailtrap
        {
          ref: 'email-step',
          type: 'channel',
          channel_key: 'mailtrap',
          channel_overrides: {
            from_address: senderEmail,
          },
          template: {
            subject: `Hello {{ recipient.name }} - Cancel Flow ${runId}`,
            html_body: `<p>Hello <strong>{{ recipient.name }}</strong>,</p><p>This is a test email from the cancel flow workflow (run: ${runId}).</p>`,
            settings: {},
          },
        },
      ],
    },
  });

  console.log(`Workflow upserted: ${upsertResponse.workflow.key}`);

  // Step 2: Activate the workflow in the development environment
  console.log('\nActivating workflow...');
  const activateResponse = await mgmtClient.workflows.activate(workflowKey, {
    environment: 'development',
    status: true,
  });

  console.log(`Workflow activated: ${activateResponse.workflow.active}`);

  // Initialize the Knock client for triggering and cancelling workflows
  const knockClient = new Knock({
    apiKey: knockApiToken,
  });

  // Step 3: Trigger the workflow with inline recipient and cancellation key
  console.log('\nTriggering workflow...');
  const triggerResponse = await knockClient.workflows.trigger(workflowKey, {
    recipients: [
      {
        id: recipientId,
        email: recipientEmail,
        name: `User ${runId}`,
      },
    ],
    cancellation_key: cancellationKey,
  });

  const workflowRunId = triggerResponse.workflow_run_id;
  console.log(`Workflow triggered. Run ID: ${workflowRunId}`);

  // Step 4: Wait at least 5 seconds before cancelling (Knock recommendation)
  console.log('\nWaiting 5 seconds before cancelling...');
  await sleep(5000);

  // Step 5: Cancel the workflow run before the delay elapses
  console.log('\nCancelling workflow...');
  await knockClient.workflows.cancel(workflowKey, {
    cancellation_key: cancellationKey,
  });

  console.log('Workflow cancelled successfully.');

  // Step 6: Write log file
  const logPath = path.join(__dirname, 'output.log');
  const logContent = [
    `Workflow Key: ${workflowKey}`,
    `Workflow Run ID: ${workflowRunId}`,
    `Cancellation Key: ${cancellationKey}`,
    `Recipient Email: ${recipientEmail}`,
  ].join('\n') + '\n';

  fs.writeFileSync(logPath, logContent, 'utf8');
  console.log(`\nLog written to: ${logPath}`);
  console.log('\nLog contents:');
  console.log(logContent);
}

main().catch((err) => {
  console.error('Error:', err);
  process.exit(1);
});
