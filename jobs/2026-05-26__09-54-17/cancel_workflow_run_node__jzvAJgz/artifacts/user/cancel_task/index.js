const { KnockMgmt: KnockManagement } = require('@knocklabs/mgmt');
const { Knock } = require('@knocklabs/node');
const fs = require('fs');
const path = require('path');

async function run() {
  const runId = process.env.ZEALT_RUN_ID;
  const knockServiceToken = process.env.KNOCK_SERVICE_TOKEN;
  const knockApiToken = process.env.KNOCK_API_TOKEN;
  const mailtrapDomain = process.env.MAILTRAP_DOMAIN;
  const gmailUserName = process.env.GMAIL_USER_NAME;

  if (!runId || !knockServiceToken || !knockApiToken || !mailtrapDomain || !gmailUserName) {
    console.error('Missing required environment variables');
    process.exit(1);
  }

  const workflowKey = `cancel-flow-${runId}`;
  const cancellationKey = `cancel-${runId}`;
  const recipientId = `user-${runId}`;
  const recipientEmail = `${gmailUserName}+receiver-${runId}@gmail.com`;
  const senderEmail = `sender-${runId}@${mailtrapDomain}`;

  const mgmtClient = new KnockManagement({ bearerToken: knockServiceToken });
  const nodeClient = new Knock({ apiKey: knockApiToken });

  console.log(`Upserting workflow: ${workflowKey}`);

  // 1. Upsert the workflow
  await mgmtClient.workflows.upsert(workflowKey, {
    workflow: {
      name: `Cancel Flow ${runId}`,
      steps: [
        {
          type: 'delay',
          ref: 'delay_1',
          settings: {
            delay_for: {
              unit: 'seconds',
              value: 30,
            },
          },
        },
        {
          type: 'channel',
          ref: 'email_1',
          channel_key: 'mailtrap',
          settings: {
            from_email_address: senderEmail,
          },
          template: {
            settings: {
              layout_key: 'default',
            },
            subject: `Hello {{ recipient.name }} - ${runId}`,
            html_body: `<p>Hi {{ recipient.name }}, this is a test email for run ${runId}.</p>`,
          },
        },
      ],
    },
    environment: 'development',
  });

  console.log(`Activating workflow: ${workflowKey}`);

  // 2. Activate the workflow
  await mgmtClient.workflows.activate(workflowKey, {
    environment: 'development',
  });

  console.log(`Triggering workflow: ${workflowKey}`);

  // 3. Trigger the workflow
  const triggerResponse = await nodeClient.workflows.trigger(workflowKey, {
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
  console.log(`Workflow Triggered. Run ID: ${workflowRunId}`);

  // 4. Wait at least 5 seconds
  console.log('Waiting 7 seconds before cancellation...');
  await new Promise((resolve) => setTimeout(resolve, 7000));

  console.log(`Cancelling workflow run with cancellation key: ${cancellationKey}`);

  // 5. Cancel the workflow
  await nodeClient.workflows.cancel(workflowKey, {
    cancellation_key: cancellationKey,
  });

  console.log('Workflow cancellation request sent.');

  // 6. Log to output.log
  const logContent = [
    `Workflow Key: ${workflowKey}`,
    `Workflow Run ID: ${workflowRunId}`,
    `Cancellation Key: ${cancellationKey}`,
    `Recipient Email: ${recipientEmail}`,
  ].join('\n') + '\n';

  fs.writeFileSync(path.join(__dirname, 'output.log'), logContent);
  console.log('Results logged to output.log');
}

  run().catch((err) => {
  console.error('Error:', err);
  if (err.error && err.error.errors) {
    console.error('Validation Errors:', JSON.stringify(err.error.errors, null, 2));
  }
  process.exit(1);
});
