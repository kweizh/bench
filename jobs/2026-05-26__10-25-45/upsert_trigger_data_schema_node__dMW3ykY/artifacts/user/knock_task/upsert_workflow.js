const { KnockMgmt } = require('@knocklabs/mgmt');
const fs = require('fs');

async function main() {
  const runId = process.env.ZEALT_RUN_ID || 'default-run';
  const workflowKey = `order-confirmation-${runId}`;
  
  const knock = new KnockMgmt(process.env.KNOCK_SERVICE_TOKEN);
  
  const workflow = {
    name: `Order Confirmation ${runId}`,
    trigger_data_json_schema: {
      $schema: "http://json-schema.org/draft-07/schema#",
      type: 'object',
      properties: {
        order_id: { type: 'string' },
        total_amount: { type: 'number' },
        customer_email: { type: 'string', format: 'email' }
      },
      required: ['order_id', 'total_amount', 'customer_email'],
      additionalProperties: false
    },
    steps: [
      {
        ref: 'step-1',
        type: 'channel',
        channel_key: 'in-app',
        template: {
          settings: {},
          markdown_body: 'Order {{ data.order_id }} total: {{ data.total_amount }}',
          action_url: 'https://example.com'
        }
      }
    ]
  };

  try {
    await knock.workflows.upsert(workflowKey, {
      environment: 'development',
      commit: true,
      workflow
    });

    await knock.workflows.activate(workflowKey, {
      environment: 'development',
      status: true
    });

    fs.appendFileSync('/home/user/knock_task/output.log', `Workflow Key: ${workflowKey}\n`);
    fs.appendFileSync('/home/user/knock_task/output.log', `Workflow Active: true\n`);
  } catch (error) {
    console.error('Error upserting/activating workflow:', error.response?.data || error);
  }
}

main();
