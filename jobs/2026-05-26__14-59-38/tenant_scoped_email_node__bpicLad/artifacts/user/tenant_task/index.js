const { KnockMgmt } = require('@knocklabs/mgmt');
const { Knock } = require('@knocklabs/node');
const fs = require('fs');
require('dotenv').config();

async function run() {
  try {
    const runId = process.env.ZEALT_RUN_ID || 'test';
    const gmailUser = process.env.GMAIL_USER_NAME || 'test';
    const mailtrapDomain = process.env.MAILTRAP_DOMAIN || 'example.com';
    const tenantId = `tenant-${runId}`;
    const workflowKey = `tenant-welcome-${runId}`;
    const recipientId = `user-${runId}`;
    const recipientEmail = `${gmailUser}+receiver-${runId}@gmail.com`;

    const knockMgmt = new KnockMgmt({ serviceToken: process.env.KNOCK_SERVICE_TOKEN });
    const knockNode = new Knock({ apiKey: process.env.KNOCK_API_TOKEN });

    // 1. Set a tenant
    console.log('Setting tenant...');
    await knockNode.tenants.set(tenantId, {
      name: `Tenant ${runId}`,
      settings: {
        branding: {
          primary_color: '#ff0000'
        }
      },
      app_name: 'My Cool App'
    });

    // 2. Upsert workflow
    console.log('Upserting workflow...');
    await knockMgmt.workflows.upsert(workflowKey, {
      environment: 'development',
      commit: true,
      workflow: {
        name: `Welcome Workflow ${runId}`,
        steps: [
          {
            ref: 'email-step-1',
            type: 'channel',
            channel_key: 'mailtrap',
            settings: {
              from_email_address: `sender-${runId}@${mailtrapDomain}`
            },
            channel_overrides: {
              from_address: `sender-${runId}@${mailtrapDomain}`
            },
            template: {
              subject: 'Welcome to {{ tenant.app_name }}',
              html_body: 'Hi {{ recipient.name }}, welcome to {{ tenant.name }}',
              settings: {
                layout_key: null
              }
            }
          }
        ]
      }
    });

    // 3. Activate workflow
    console.log('Activating workflow...');
    await knockMgmt.workflows.activate(workflowKey, {
      environment: 'development',
      status: true
    });

    // 4. Trigger workflow
    console.log('Triggering workflow...');
    const triggerResult = await knockNode.workflows.trigger(workflowKey, {
      tenant: tenantId,
      recipients: [
        {
          id: recipientId,
          email: recipientEmail,
          name: `User ${runId}`
        }
      ]
    });

    console.log('Trigger result:', triggerResult);

    // 5. Write to log
    const logContent = [
      `Tenant ID: ${tenantId}`,
      `Workflow Key: ${workflowKey}`,
      `Workflow Run ID: ${triggerResult.workflow_run_id}`,
      `Recipient Email: ${recipientEmail}`
    ].join('\n');

    fs.writeFileSync('/home/user/tenant_task/output.log', logContent + '\n');
    console.log('Done.');

  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

run();
