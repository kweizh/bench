const Knock = require('@knocklabs/node');
const KnockMgmt = require('@knocklabs/mgmt');
const fs = require('fs');
const path = require('path');

// Read environment variables
const KNOCK_API_TOKEN = process.env.KNOCK_API_TOKEN;
const KNOCK_SERVICE_TOKEN = process.env.KNOCK_SERVICE_TOKEN;
const ZEALT_RUN_ID = process.env.ZEALT_RUN_ID || Date.now().toString();
const GMAIL_USER_NAME = process.env.GMAIL_USER_NAME;
const MAILTRAP_DOMAIN = process.env.MAILTRAP_DOMAIN || 'mailtrap.io';

// Validate required environment variables
if (!KNOCK_API_TOKEN) {
  throw new Error('KNOCK_API_TOKEN is required');
}
if (!KNOCK_SERVICE_TOKEN) {
  throw new Error('KNOCK_SERVICE_TOKEN is required');
}
if (!GMAIL_USER_NAME) {
  throw new Error('GMAIL_USER_NAME is required');
}

// Generate unique identifiers with run-id suffix
const tenantId = `tenant-${ZEALT_RUN_ID}`;
const workflowKey = `tenant-welcome-${ZEALT_RUN_ID}`;
const recipientId = `user-${ZEALT_RUN_ID}`;
const recipientEmail = `${GMAIL_USER_NAME}+receiver-${ZEALT_RUN_ID}@gmail.com`;
const fromEmailAddress = `sender-${ZEALT_RUN_ID}@${MAILTRAP_DOMAIN}`;

// Initialize Knock clients
const knock = new Knock(KNOCK_API_TOKEN);
const knockMgmt = new KnockMgmt.KnockClient({
  apiKey: KNOCK_SERVICE_TOKEN,
});

async function main() {
  console.log(`Starting tenant-scoped Knock workflow automation with run-id: ${ZEALT_RUN_ID}`);

  // Step 1: Set tenant with custom properties
  console.log(`Setting tenant: ${tenantId}`);
  const tenant = await knock.tenants.set(tenantId, {
    name: `Tenant ${ZEALT_RUN_ID}`,
    settings: {
      branding: {
        primary_color: '#3b82f6'
      }
    },
    app_name: 'MyApp'
  });
  console.log('Tenant created successfully');

  // Step 2: Upsert workflow with email step
  console.log(`Upserting workflow: ${workflowKey}`);
  const workflow = await knockMgmt.workflows.upsert({
    key: workflowKey,
    name: `Tenant Welcome Workflow ${ZEALT_RUN_ID}`,
    environment: 'development',
    steps: [
      {
        key: 'email-step',
        type: 'channel',
        channel_key: 'mailtrap',
        recipients: [
          {
            key: 'primary',
            recipient: {
              email: '{{ recipient.email }}',
              name: '{{ recipient.name }}'
            }
          }
        ],
        settings: {
          from_email_address: fromEmailAddress,
          subject: 'Welcome to {{ tenant.app_name }}!',
          html: `
            <h1>Hello {{ recipient.name }}!</h1>
            <p>Welcome to <strong>{{ tenant.name }}</strong>.</p>
            <p>We're excited to have you on board!</p>
          `
        }
      }
    ]
  });
  console.log('Workflow upserted successfully');

  // Step 3: Activate the workflow
  console.log(`Activating workflow: ${workflowKey}`);
  await knockMgmt.workflows.activate({
    key: workflowKey,
    environment: 'development'
  });
  console.log('Workflow activated successfully');

  // Step 4: Trigger the workflow with tenant-scoped recipient
  console.log(`Triggering workflow for recipient: ${recipientEmail}`);
  const triggerResult = await knock.workflows.trigger(workflowKey, {
    tenant: tenantId,
    recipients: [
      {
        id: recipientId,
        email: recipientEmail,
        name: `User ${ZEALT_RUN_ID}`
      }
    ]
  });
  const workflowRunId = triggerResult.workflow_run_id;
  console.log(`Workflow triggered successfully. Run ID: ${workflowRunId}`);

  // Step 5: Write to log file
  const logFilePath = path.join(__dirname, 'output.log');
  const logContent = [
    `Tenant ID: ${tenantId}`,
    `Workflow Key: ${workflowKey}`,
    `Workflow Run ID: ${workflowRunId}`,
    `Recipient Email: ${recipientEmail}`
  ].join('\n');

  fs.writeFileSync(logFilePath, logContent);
  console.log(`Log file written to: ${logFilePath}`);

  console.log('Tenant-scoped Knock workflow automation completed successfully!');
}

main().catch(error => {
  console.error('Error:', error);
  process.exit(1);
});