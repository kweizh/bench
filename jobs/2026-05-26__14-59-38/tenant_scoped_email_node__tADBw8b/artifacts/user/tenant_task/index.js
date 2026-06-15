require('dotenv').config();
const { Knock } = require('@knocklabs/node');
const { KnockMgmt } = require('@knocklabs/mgmt');
const fs = require('fs');
const path = require('path');

const runId = process.env.ZEALT_RUN_ID;
const knockApiToken = process.env.KNOCK_API_TOKEN;
const knockServiceToken = process.env.KNOCK_SERVICE_TOKEN;
const mailtrapDomain = process.env.MAILTRAP_DOMAIN;
const gmailUserName = process.env.GMAIL_USER_NAME;

if (!runId || !knockApiToken || !knockServiceToken || !mailtrapDomain || !gmailUserName) {
  console.error('Missing required environment variables');
  process.exit(1);
}

const knock = new Knock({ apiKey: knockApiToken });
const knockMgmt = new KnockMgmt({ bearerToken: knockServiceToken });

const tenantId = `tenant-${runId}`;
const workflowKey = `tenant-welcome-${runId}`;
const recipientId = `user-${runId}`;
const recipientEmail = `${gmailUserName}+receiver-${runId}@gmail.com`;
const fromEmail = `sender-${runId}@${mailtrapDomain}`;

async function run() {
  try {
    // 1. Set a tenant
    console.log(`Setting tenant: ${tenantId}`);
    const tenant = await knock.tenants.set(tenantId, {
      name: `Tenant ${runId}`,
      settings: {
        branding: {
          primary_color: '#3b82f6',
        },
      },
      app_name: `App ${runId}`,
    });

    // 2. Upsert a workflow
    console.log(`Upserting workflow: ${workflowKey}`);
    await knockMgmt.workflows.upsert(workflowKey, {
      workflow: {
        name: `Tenant Welcome Workflow ${runId}`,
        steps: [
          {
            type: 'channel',
            channel_key: 'mailtrap',
            ref: 'email_step',
            settings: {
              from_email_address: fromEmail,
            },
            template: {
              subject: 'Welcome to {{ tenant.app_name }}!',
              html_body: '<p>Hello {{ recipient.name }},</p><p>Welcome to {{ tenant.name }}!</p>',
              settings: {},
            },
          },
        ],
      },
      environment: 'development',
      commit: true,
      commit_message: 'Automatic commit from task',
    });

    // 3. Activate the workflow
    console.log(`Activating workflow: ${workflowKey}`);
    await knockMgmt.workflows.activate(workflowKey, {
      environment: 'development',
      status: true,
    });

    // Wait for activation to propagate
    console.log('Waiting for workflow activation and commit...');
    await new Promise(resolve => setTimeout(resolve, 10000));

    // 4. Trigger the workflow
    console.log(`Triggering workflow: ${workflowKey} for recipient: ${recipientId}`);
    const triggerResponse = await knock.workflows.trigger(workflowKey, {
      recipients: [
        {
          id: recipientId,
          email: recipientEmail,
          name: `User ${runId}`,
        },
      ],
      tenant: tenantId,
    });
    const workflow_run_id = triggerResponse.workflow_run_id;

    // 5. Log output
    const logFilePath = path.join(__dirname, 'output.log');
    const logContent = [
      `Tenant ID: ${tenantId}`,
      `Workflow Key: ${workflowKey}`,
      `Workflow Run ID: ${workflow_run_id}`,
      `Recipient Email: ${recipientEmail}`,
    ].join('\n') + '\n';

    fs.writeFileSync(logFilePath, logContent);
    console.log(`Log written to ${logFilePath}`);

  } catch (error) {
    console.error('Error occurred:', error);
    if (error.error) {
      console.error('Error details:', JSON.stringify(error.error, null, 2));
    }
    process.exit(1);
  }
}

run();
