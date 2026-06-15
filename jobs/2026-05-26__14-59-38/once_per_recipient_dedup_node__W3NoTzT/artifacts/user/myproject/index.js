'use strict';

const fs = require('fs');
const path = require('path');

async function main() {
  // Read environment variables
  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) throw new Error('ZEALT_RUN_ID is not set');

  const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
  if (!serviceToken) throw new Error('KNOCK_SERVICE_TOKEN is not set');

  const apiToken = process.env.KNOCK_API_TOKEN;
  if (!apiToken) throw new Error('KNOCK_API_TOKEN is not set');

  const gmailUser = process.env.GMAIL_USER_NAME;
  if (!gmailUser) throw new Error('GMAIL_USER_NAME is not set');

  const mailtrapDomain = process.env.MAILTRAP_DOMAIN;
  if (!mailtrapDomain) throw new Error('MAILTRAP_DOMAIN is not set');

  // Derived values
  const workflowKey = `dedup-test-${runId}`;
  const recipientId = `dedup-recipient-${runId}`;
  const recipientEmail = `${gmailUser}+receiver-${runId}@gmail.com`;
  const recipientName = `Recipient ${runId}`;
  const fromEmail = `dedup-${runId}@${mailtrapDomain}`;

  console.log(`Run ID: ${runId}`);
  console.log(`Workflow key: ${workflowKey}`);
  console.log(`Recipient: ${recipientId} <${recipientEmail}>`);
  console.log(`From: ${fromEmail}`);

  // Step 1: Upsert the workflow using the Management API
  const KnockMgmt = require('@knocklabs/mgmt');
  const mgmtClient = new KnockMgmt.KnockMgmt({ serviceToken });

  console.log('\nUpserting workflow via Management API...');
  const upsertResponse = await mgmtClient.workflows.upsert(workflowKey, {
    environment: 'development',
    workflow: {
      name: `Dedup Test ${runId}`,
      trigger_frequency: 'once_per_recipient',
      steps: [
        {
          ref: 'email-step-1',
          type: 'channel',
          channel_key: 'mailtrap',
          channel_type: 'email',
          template: {
            settings: {
              layout_key: null,
            },
            subject: `dedup-test-${runId}: Welcome notification`,
            html_body: `<p>Hello {{ recipient.name }},</p><p>This is a deduplication test email for run <strong>dedup-test-${runId}</strong>.</p>`,
          },
          channel_overrides: {
            from_address: fromEmail,
            from_name: `Dedup Test ${runId}`,
          },
        },
      ],
    },
    commit: true,
    commit_message: `Upsert dedup-test workflow for run ${runId}`,
  });

  console.log('Workflow upserted successfully:', upsertResponse.key || workflowKey);

  // Step 2: Activate the workflow in the development environment
  console.log('\nActivating workflow in development environment...');
  const activateResponse = await mgmtClient.workflows.activate(workflowKey, {
    environment: 'development',
    status: true,
  });
  console.log('Workflow activation response:', JSON.stringify(activateResponse));

  // Step 3: Trigger the workflow twice using the Node SDK
  const { Knock } = require('@knocklabs/node');
  const knockClient = new Knock({ apiKey: apiToken });

  const recipient = {
    id: recipientId,
    email: recipientEmail,
    name: recipientName,
  };

  const logFile = path.join(__dirname, 'output.log');
  // Clear/create the log file
  fs.writeFileSync(logFile, '');

  // First trigger
  console.log('\nTriggering workflow (first time)...');
  let firstRunId;
  try {
    const firstResult = await knockClient.workflows.trigger(workflowKey, {
      recipients: [recipient],
    });
    firstRunId = firstResult.workflow_run_id || null;
    console.log('First trigger result:', JSON.stringify(firstResult));
  } catch (err) {
    console.error('First trigger error:', err.message);
    firstRunId = null;
  }

  fs.appendFileSync(logFile, `First trigger workflow_run_id: ${firstRunId}\n`);
  console.log(`Logged: First trigger workflow_run_id: ${firstRunId}`);

  // Second trigger (should be deduplicated by Knock)
  console.log('\nTriggering workflow (second time)...');
  let secondRunId;
  try {
    const secondResult = await knockClient.workflows.trigger(workflowKey, {
      recipients: [recipient],
    });
    secondRunId = secondResult.workflow_run_id || null;
    console.log('Second trigger result:', JSON.stringify(secondResult));
  } catch (err) {
    console.error('Second trigger error:', err.message);
    secondRunId = null;
  }

  fs.appendFileSync(logFile, `Second trigger workflow_run_id: ${secondRunId}\n`);
  console.log(`Logged: Second trigger workflow_run_id: ${secondRunId}`);

  console.log('\nDone! Log file written to:', logFile);
  console.log('\nLog file contents:');
  console.log(fs.readFileSync(logFile, 'utf8'));
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
