import KnockMgmt from '@knocklabs/mgmt';
import fs from 'fs';

const runId = process.env.ZEALT_RUN_ID;
if (!runId) {
  console.error('Error: ZEALT_RUN_ID environment variable is required');
  process.exit(1);
}

const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
if (!serviceToken) {
  console.error('Error: KNOCK_SERVICE_TOKEN environment variable is required');
  process.exit(1);
}

const knock = new KnockMgmt(serviceToken);
const workflowKey = `order-confirmation-${runId}`;
const environment = 'development';

// Define the workflow with trigger data JSON schema
const workflow = {
  name: `Order Confirmation ${runId}`,
  trigger_data_json_schema: {
    type: 'object',
    required: ['order_id', 'total_amount', 'customer_email'],
    properties: {
      order_id: {
        type: 'string'
      },
      total_amount: {
        type: 'number'
      },
      customer_email: {
        type: 'string',
        format: 'email'
      }
    }
  },
  steps: [
    {
      ref: 'in-app-notification',
      type: 'channel',
      channel_key: 'in-app',
      template: {
        markdown_body: `Your order **{{ data.order_id }}** has been confirmed.

Total amount: **{{ data.total_amount }}**

Thank you for your purchase!`,
        action_url: 'https://example.com/orders'
      }
    }
  ]
};

async function upsertAndActivateWorkflow() {
  try {
    console.log(`Upserting workflow with key: ${workflowKey}`);
    
    // Upsert the workflow with commit=true
    await knock.workflows.upsert(workflowKey, {
      environment,
      workflow,
      commit: true,
      commit_message: 'Upsert order confirmation workflow'
    });
    
    console.log(`Workflow upserted and committed successfully`);
    
    // Activate the workflow
    await knock.workflows.activate(workflowKey, {
      environment,
      status: true
    });
    
    console.log(`Workflow activated successfully`);
    
    // Write results to output.log
    const logLines = [
      `Workflow Key: ${workflowKey}`,
      `Workflow Active: true`
    ];
    
    fs.appendFileSync('/home/user/knock_task/output.log', logLines.join('\n') + '\n');
    console.log('Results written to output.log');
    
  } catch (error) {
    console.error('Error:', error.message);
    if (error.error && error.error.errors) {
      console.error('Detailed errors:', JSON.stringify(error.error.errors, null, 2));
    }
    process.exit(1);
  }
}

upsertAndActivateWorkflow();
