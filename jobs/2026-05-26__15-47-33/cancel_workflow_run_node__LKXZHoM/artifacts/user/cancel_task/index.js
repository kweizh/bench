import KnockMgmt from '@knocklabs/mgmt';
import Knock from '@knocklabs/node';
import dotenv from 'dotenv';

dotenv.config();

// Configuration
const RUN_ID = process.env.ZEALT_RUN_ID;
const GMAIL_USER_NAME = process.env.GMAIL_USER_NAME;
const MAILTRAP_DOMAIN = process.env.MAILTRAP_DOMAIN;
const KNOCK_SERVICE_TOKEN = process.env.KNOCK_SERVICE_TOKEN;
const KNOCK_API_TOKEN = process.env.KNOCK_API_TOKEN;
const KNOCK_ENVIRONMENT = 'development';

if (!RUN_ID) {
  throw new Error('ZEALT_RUN_ID environment variable is required');
}

if (!GMAIL_USER_NAME) {
  throw new Error('GMAIL_USER_NAME environment variable is required');
}

if (!MAILTRAP_DOMAIN) {
  throw new Error('MAILTRAP_DOMAIN environment variable is required');
}

if (!KNOCK_SERVICE_TOKEN) {
  throw new Error('KNOCK_SERVICE_TOKEN environment variable is required');
}

if (!KNOCK_API_TOKEN) {
  throw new Error('KNOCK_API_TOKEN environment variable is required');
}

// Derived values
const WORKFLOW_KEY = `cancel-flow-${RUN_ID}`;
const RECIPIENT_ID = `user-${RUN_ID}`;
const RECIPIENT_EMAIL = `${GMAIL_USER_NAME}+receiver-${RUN_ID}@gmail.com`;
const RECIPIENT_NAME = `User ${RUN_ID}`;
const CANCELLATION_KEY = `cancel-${RUN_ID}`;
const SENDER_EMAIL = `sender-${RUN_ID}@${MAILTRAP_DOMAIN}`;

// Initialize clients
const knockMgmt = new KnockMgmt(KNOCK_SERVICE_TOKEN);
const knock = new Knock(KNOCK_API_TOKEN);

// Helper function to sleep
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Helper function to write to log file
const writeLog = async (content) => {
  const fs = await import('fs');
  fs.appendFileSync('/home/user/cancel_task/output.log', content + '\n');
};

async function main() {
  console.log(`Starting cancel task for run ID: ${RUN_ID}`);
  
  // Clear existing log file
  const fs = await import('fs');
  fs.writeFileSync('/home/user/cancel_task/output.log', '');

  // 1. Upsert workflow with delay and email step
  console.log('Upserting workflow...');
  const workflow = await knockMgmt.workflows.upsert({
    key: WORKFLOW_KEY,
    name: `Cancel Flow ${RUN_ID}`,
    environment: KNOCK_ENVIRONMENT,
    steps: [
      {
        type: 'delay',
        settings: {
          delay_for: {
            unit: 'seconds',
            value: 30
          }
        }
      },
      {
        type: 'channel',
        channel_key: 'mailtrap',
        settings: {
          from_email_address: SENDER_EMAIL,
          subject: 'Test Email for {{recipient.name}}',
          body: '<h1>Hello {{recipient.name}}!</h1><p>This is a test email.</p>'
        }
      }
    ]
  });
  console.log(`Workflow upserted: ${workflow.key}`);

  // 2. Activate the workflow
  console.log('Activating workflow...');
  await knockMgmt.workflows.activate(WORKFLOW_KEY, {
    environment: KNOCK_ENVIRONMENT
  });
  console.log('Workflow activated');

  // 3. Trigger the workflow
  console.log('Triggering workflow...');
  const triggerResult = await knock.workflows.trigger(WORKFLOW_KEY, {
    cancellation_key: CANCELLATION_KEY,
    data: {},
    recipients: [
      {
        id: RECIPIENT_ID,
        email: RECIPIENT_EMAIL,
        name: RECIPIENT_NAME
      }
    ]
  });
  
  const workflowRunId = triggerResult.workflow_run_id;
  console.log(`Workflow triggered with run ID: ${workflowRunId}`);

  // 4. Write log entries
  await writeLog(`Workflow Key: ${WORKFLOW_KEY}`);
  await writeLog(`Workflow Run ID: ${workflowRunId}`);
  await writeLog(`Cancellation Key: ${CANCELLATION_KEY}`);
  await writeLog(`Recipient Email: ${RECIPIENT_EMAIL}`);

  // 5. Wait at least 5 seconds before cancelling
  console.log('Waiting 5 seconds before cancellation...');
  await sleep(5000);

  // 6. Cancel the workflow
  console.log('Cancelling workflow...');
  try {
    await knock.workflows.cancel(WORKFLOW_KEY, {
      cancellation_key: CANCELLATION_KEY
    });
    console.log('Workflow cancelled successfully');
  } catch (error) {
    if (error.response && error.response.status === 204) {
      console.log('Workflow cancelled successfully (204 No Content)');
    } else {
      console.error('Error cancelling workflow:', error);
      throw error;
    }
  }

  console.log('Task completed successfully');
  console.log(`Log file written to: /home/user/cancel_task/output.log`);
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});