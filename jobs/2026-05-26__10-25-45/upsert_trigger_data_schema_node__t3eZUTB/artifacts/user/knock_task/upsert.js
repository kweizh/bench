'use strict';

const { KnockMgmt } = require('@knocklabs/mgmt');
const fs = require('fs');
const path = require('path');

const LOG_FILE = path.join(__dirname, 'output.log');

async function main() {
  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) {
    throw new Error('ZEALT_RUN_ID environment variable is required');
  }

  const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
  if (!serviceToken) {
    throw new Error('KNOCK_SERVICE_TOKEN environment variable is required');
  }

  const workflowKey = `order-confirmation-${runId}`;
  const workflowName = `Order Confirmation ${runId}`;
  const environment = 'development';

  const client = new KnockMgmt({ serviceToken });

  // Upsert the workflow with trigger_data_json_schema
  console.log(`Upserting workflow: ${workflowKey}`);
  const upsertResponse = await client.workflows.upsert(workflowKey, {
    environment,
    commit: true,
    workflow: {
      name: workflowName,
      trigger_data_json_schema: {
        type: 'object',
        properties: {
          order_id: { type: 'string' },
          total_amount: { type: 'number' },
          customer_email: { type: 'string', format: 'email' },
        },
        required: ['order_id', 'total_amount', 'customer_email'],
      },
      steps: [
        {
          type: 'channel',
          name: 'In-App Notification',
          ref: 'in-app-notification',
          channel_key: 'in-app',
          template: {
            markdown_body:
              'Your order **{{ data.order_id }}** has been confirmed. Total: **{{ data.total_amount }}**.',
            action_url: '/orders/{{ data.order_id }}',
          },
        },
      ],
    },
  });
  console.log('Upsert response:', JSON.stringify(upsertResponse, null, 2));

  // Activate the workflow in development environment
  console.log(`Activating workflow: ${workflowKey}`);
  const activateResponse = await client.workflows.activate(workflowKey, {
    environment,
    status: true,
  });
  console.log('Activate response:', JSON.stringify(activateResponse, null, 2));

  // Write results to log file
  const logLines = [
    `Workflow Key: ${workflowKey}`,
    `Workflow Active: true`,
  ];

  // Append (or create) the log file
  const existing = fs.existsSync(LOG_FILE) ? fs.readFileSync(LOG_FILE, 'utf8') : '';
  const newContent = existing
    ? existing.trimEnd() + '\n' + logLines.join('\n') + '\n'
    : logLines.join('\n') + '\n';
  fs.writeFileSync(LOG_FILE, newContent, 'utf8');

  console.log('Log written successfully.');
  console.log(`Workflow Key: ${workflowKey}`);
  console.log(`Workflow Active: true`);
}

main().catch((err) => {
  console.error('Error in upsert script:', err);
  process.exit(1);
});
