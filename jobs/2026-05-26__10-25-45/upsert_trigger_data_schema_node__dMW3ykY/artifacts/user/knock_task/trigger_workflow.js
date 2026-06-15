const { Knock } = require('@knocklabs/node');
const fs = require('fs');

async function main() {
  const runId = process.env.ZEALT_RUN_ID || 'default-run';
  const workflowKey = `order-confirmation-${runId}`;
  
  const knock = new Knock({ apiKey: process.env.KNOCK_API_TOKEN });
  
  try {
    const result = await knock.workflows.trigger(workflowKey, {
      recipients: [`recipient-${runId}`],
      data: {
        order_id: '12345',
        total_amount: 100.50,
        customer_email: 'test@example.com'
      }
    });
    
    fs.appendFileSync('/home/user/knock_task/output.log', `Valid Trigger Workflow Run ID: ${result.workflow_run_id}\n`);
  } catch (error) {
    console.error('Error triggering valid:', error.response?.data || error);
  }

  try {
    await knock.workflows.trigger(workflowKey, {
      recipients: [`recipient-${runId}`],
      data: {
        order_id: '12345',
        total_amount: '100.50',
        customer_email: 'test@example.com'
      }
    });
  } catch (error) {
    const status = error.status || error.response?.status;
    fs.appendFileSync('/home/user/knock_task/output.log', `Invalid Trigger Status: ${status}\n`);
  }
}

main();
