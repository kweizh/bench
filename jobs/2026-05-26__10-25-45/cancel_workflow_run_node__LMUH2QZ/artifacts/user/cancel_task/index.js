const { Knock } = require('@knocklabs/node');
const { KnockMgmt } = require('@knocklabs/mgmt');
const fs = require('fs');

async function main() {
  const runId = process.env.ZEALT_RUN_ID;
  const knockApiToken = process.env.KNOCK_API_TOKEN;
  const knockServiceToken = process.env.KNOCK_SERVICE_TOKEN;
  const mailtrapDomain = process.env.MAILTRAP_DOMAIN;
  const gmailUserName = process.env.GMAIL_USER_NAME;

  if (!runId || !knockApiToken || !knockServiceToken || !mailtrapDomain || !gmailUserName) {
    throw new Error('Missing required environment variables');
  }

  const knock = new Knock({ apiKey: knockApiToken });
  const knockMgmt = new KnockMgmt({ apiKey: knockServiceToken });

  const workflowKey = `cancel-flow-${runId}`;
  const cancelKey = `cancel-${runId}`;
  const recipientId = `user-${runId}`;
  const recipientEmail = `${gmailUserName}+receiver-${runId}@gmail.com`;
  const senderEmail = `sender-${runId}@${mailtrapDomain}`;

  console.log(`Upserting workflow ${workflowKey}...`);
  await knockMgmt.workflows.upsert(workflowKey, {
    environment: 'development',
    workflow: {
      name: `Cancel Flow ${runId}`,
      steps: [
        {
          type: 'delay',
          ref: 'delay_step',
          name: 'Delay Step',
          settings: {
            delay_for: {
              unit: 'seconds',
              value: 30
            }
          }
        },
        {
          type: 'channel',
          ref: 'email_step',
          name: 'Email Step',
          channel_key: 'mailtrap',
          settings: {
            from_email_address: senderEmail
          },
          template: {
            settings: {},
            subject: `Hello {{ recipient.name }} - ${runId}`,
            html_body: `<p>Hi {{ recipient.name }},</p><p>This is a test email.</p>`
          }
        }
      ]
    }
  });

  console.log(`Activating workflow ${workflowKey}...`);
  await knockMgmt.workflows.activate(workflowKey, {
    environment: 'development',
    status: true
  });

  console.log(`Triggering workflow ${workflowKey}...`);
  const triggerResponse = await knock.workflows.trigger(workflowKey, {
    recipients: [
      {
        id: recipientId,
        email: recipientEmail,
        name: `User ${runId}`
      }
    ],
    cancellation_key: cancelKey
  });

  const workflowRunId = triggerResponse.workflow_run_id;
  console.log(`Workflow triggered with run ID: ${workflowRunId}`);

  console.log('Waiting 5 seconds...');
  await new Promise(resolve => setTimeout(resolve, 5000));

  console.log(`Canceling workflow ${workflowKey} with key ${cancelKey}...`);
  await knock.workflows.cancel(workflowKey, {
    cancellation_key: cancelKey
  });
  console.log('Workflow canceled successfully.');

  const logLines = [
    `Workflow Key: ${workflowKey}`,
    `Workflow Run ID: ${workflowRunId}`,
    `Cancellation Key: ${cancelKey}`,
    `Recipient Email: ${recipientEmail}`
  ];

  fs.writeFileSync('/home/user/cancel_task/output.log', logLines.join('\n') + '\n');
  console.log('Output written to output.log');
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
