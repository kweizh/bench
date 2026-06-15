import Knock from '@knocklabs/node';
import fs from 'fs';

const runId = process.env.ZEALT_RUN_ID;
if (!runId) {
  console.error('Error: ZEALT_RUN_ID environment variable is required');
  process.exit(1);
}

const apiKey = process.env.KNOCK_API_TOKEN;
if (!apiKey) {
  console.error('Error: KNOCK_API_TOKEN environment variable is required');
  process.exit(1);
}

const knock = new Knock({ apiKey });
const workflowKey = `order-confirmation-${runId}`;
const recipient = `recipient-${runId}`;

async function triggerWorkflow() {
  try {
    // Trigger with valid payload
    console.log('Triggering workflow with valid payload...');
    const validPayload = {
      order_id: `ORD-${runId}`,
      total_amount: 99.99,
      customer_email: `customer-${runId}@example.com`
    };
    
    const validResult = await knock.workflows.trigger(workflowKey, {
      recipients: [recipient],
      data: validPayload
    });
    
    console.log(`Valid trigger successful. Workflow Run ID: ${validResult.workflow_run_id}`);
    
    // Trigger with invalid payload (total_amount as string instead of number)
    console.log('Triggering workflow with invalid payload...');
    const invalidPayload = {
      order_id: `ORD-${runId}`,
      total_amount: '99.99', // Invalid: should be number, not string
      customer_email: `customer-${runId}@example.com`
    };
    
    let invalidStatus = 'unknown';
    try {
      await knock.workflows.trigger(workflowKey, {
        recipients: [recipient],
        data: invalidPayload
      });
      console.log('Invalid trigger succeeded unexpectedly');
    } catch (error) {
      invalidStatus = error.status || error.statusCode || 422;
      console.log(`Invalid trigger failed as expected. Status: ${invalidStatus}, Message: ${error.message}`);
    }
    
    // Write results to output.log
    const logLines = [
      `Valid Trigger Workflow Run ID: ${validResult.workflow_run_id}`,
      `Invalid Trigger Status: ${invalidStatus}`
    ];
    
    fs.appendFileSync('/home/user/knock_task/output.log', logLines.join('\n') + '\n');
    console.log('Results written to output.log');
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

triggerWorkflow();
