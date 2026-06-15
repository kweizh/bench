import Knock from '@knocklabs/node';
import KnockMgmt from '@knocklabs/mgmt';
import fs from 'fs';
import path from 'path';

// Read environment variables
const runId = process.env.ZEALT_RUN_ID;
const gmailUserName = process.env.GMAIL_USER_NAME;
const knockApiKey = process.env.KNOCK_API_KEY;
const knockServiceToken = process.env.KNOCK_SERVICE_TOKEN;

if (!runId || !gmailUserName || !knockApiKey || !knockServiceToken) {
  console.error('Missing required environment variables');
  process.exit(1);
}

// Initialize Knock clients
const knock = new Knock({ apiKey: knockApiKey });
const knockMgmt = new KnockMgmt({ serviceToken: knockServiceToken });

// Workflow configuration
const workflowKey = `branch-flow-${runId}`;
const recipientId = `user-${runId}`;
const recipientEmail = `${gmailUserName}+receiver-${runId}@gmail.com`;
const recipientName = `User ${runId}`;

// Define the workflow with branch step
const workflow = {
  key: workflowKey,
  name: `Branch Workflow ${runId}`,
  trigger_data_json_schema: {
    type: 'object',
    properties: {
      channel_preference: {
        type: 'string',
        enum: ['email', 'in-app']
      }
    },
    required: ['channel_preference']
  },
  steps: [
    {
      id: 'branch-step',
      name: 'Branch on channel preference',
      type: 'branch',
      branches: [
        {
          id: 'email-branch',
          label: 'Email Channel',
          conditions: [
            {
              variable: 'data.channel_preference',
              operator: '==',
              value: 'email'
            }
          ],
          steps: [
            {
              id: 'email-step',
              name: 'Send Email',
              type: 'channel',
              channel_key: 'mailtrap',
              templates: {
                subject: 'Hello {{recipient.name}}',
                body: 'This is an email message for {{recipient.name}}.'
              }
            }
          ],
          terminates: true
        },
        {
          id: 'default-branch',
          label: 'Default In-App',
          default: true,
          steps: [
            {
              id: 'inapp-step',
              name: 'Send In-App',
              type: 'channel',
              channel_key: 'in-app',
              templates: {
                title: 'Hello {{recipient.name}}',
                body: 'This is an in-app message for {{recipient.name}}.'
              }
            }
          ],
          terminates: true
        }
      ]
    }
  ]
};

// Recipient object
const recipient = {
  id: recipientId,
  email: recipientEmail,
  name: recipientName
};

// Log file path
const logFilePath = '/home/user/myproject/output.log';

async function main() {
  try {
    console.log('Starting Knock workflow upsert and trigger...');

    // Step 1: Upsert workflow
    console.log(`Upserting workflow: ${workflowKey}`);
    await knockMgmt.workflows.upsert(workflowKey, { environment: 'development' }, workflow);
    console.log('Workflow upserted successfully');

    // Step 2: Activate workflow
    console.log('Activating workflow in development environment');
    await knockMgmt.workflows.activate(workflowKey, { environment: 'development' });
    console.log('Workflow activated successfully');

    // Step 3: Trigger workflow with email preference
    console.log('Triggering workflow with email preference...');
    const emailTriggerResult = await knock.workflows.trigger(workflowKey, {
      recipients: [recipient],
      data: {
        channel_preference: 'email'
      },
      environment: 'development'
    });
    const emailRunId = emailTriggerResult.workflow_run_id;
    console.log(`Email trigger completed. Run ID: ${emailRunId}`);

    // Step 4: Trigger workflow with in-app preference
    console.log('Triggering workflow with in-app preference...');
    const inAppTriggerResult = await knock.workflows.trigger(workflowKey, {
      recipients: [recipient],
      data: {
        channel_preference: 'in-app'
      },
      environment: 'development'
    });
    const inAppRunId = inAppTriggerResult.workflow_run_id;
    console.log(`In-App trigger completed. Run ID: ${inAppRunId}`);

    // Step 5: Write results to log file
    const logLines = [
      `Workflow Key: ${workflowKey}`,
      `Email Run ID: ${emailRunId}`,
      `InApp Run ID: ${inAppRunId}`
    ];
    
    fs.writeFileSync(logFilePath, logLines.join('\n') + '\n');
    console.log(`Log file written to: ${logFilePath}`);

    console.log('All operations completed successfully!');
    console.log('Log contents:');
    console.log(logLines.join('\n'));

  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();