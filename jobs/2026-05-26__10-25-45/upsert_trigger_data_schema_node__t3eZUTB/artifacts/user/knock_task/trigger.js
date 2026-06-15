'use strict';

const Knock = require('@knocklabs/node');
const fs = require('fs');
const path = require('path');

const LOG_FILE = path.join(__dirname, 'output.log');

async function main() {
  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) {
    throw new Error('ZEALT_RUN_ID environment variable is required');
  }

  const apiKey = process.env.KNOCK_API_TOKEN;
  if (!apiKey) {
    throw new Error('KNOCK_API_TOKEN environment variable is required');
  }

  const workflowKey = `order-confirmation-${runId}`;
  const recipient = `recipient-${runId}`;

  // Support both default export and named export
  const KnockClient = Knock.default || Knock.Knock || Knock;
  const client = new KnockClient({ apiKey });

  const logLines = [];

  // 1. Trigger with a VALID payload
  console.log('Triggering workflow with valid payload...');
  let workflowRunId;
  try {
    const validResponse = await client.workflows.trigger(workflowKey, {
      recipients: [recipient],
      data: {
        order_id: 'ORD-12345',
        total_amount: 99.99,
        customer_email: 'customer@example.com',
      },
    });
    workflowRunId = validResponse.workflow_run_id;
    console.log(`Valid trigger succeeded. workflow_run_id: ${workflowRunId}`);
    logLines.push(`Valid Trigger Workflow Run ID: ${workflowRunId}`);
  } catch (err) {
    console.error('Unexpected error on valid trigger:', err);
    throw err;
  }

  // 2. Trigger with an INVALID payload (total_amount as string instead of number)
  console.log('Triggering workflow with invalid payload...');
  try {
    await client.workflows.trigger(workflowKey, {
      recipients: [recipient],
      data: {
        order_id: 'ORD-99999',
        total_amount: 'not-a-number', // invalid: should be a number
        customer_email: 'customer@example.com',
      },
    });
    // If we get here, the API did not reject the invalid payload
    console.warn('Warning: invalid trigger was NOT rejected by the API.');
    logLines.push('Invalid Trigger Status: not-rejected');
  } catch (err) {
    const status = err.status || err.statusCode || (err.response && err.response.status);
    console.log(`Invalid trigger rejected with status: ${status}`);
    console.log(`Error message: ${err.message}`);
    logLines.push(`Invalid Trigger Status: ${status}`);
  }

  // Append results to log file
  const existing = fs.existsSync(LOG_FILE) ? fs.readFileSync(LOG_FILE, 'utf8') : '';
  const newContent = existing
    ? existing.trimEnd() + '\n' + logLines.join('\n') + '\n'
    : logLines.join('\n') + '\n';
  fs.writeFileSync(LOG_FILE, newContent, 'utf8');

  console.log('Trigger log written successfully.');
}

main().catch((err) => {
  console.error('Error in trigger script:', err);
  process.exit(1);
});
