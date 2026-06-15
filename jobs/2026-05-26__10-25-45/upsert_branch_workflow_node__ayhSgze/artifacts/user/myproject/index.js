'use strict';

const fs = require('fs');
const path = require('path');

// ── Environment variables ──────────────────────────────────────────────────
const KNOCK_SERVICE_TOKEN = process.env.KNOCK_SERVICE_TOKEN;
const KNOCK_API_TOKEN     = process.env.KNOCK_API_TOKEN;
const ZEALT_RUN_ID        = process.env.ZEALT_RUN_ID;
const GMAIL_USER_NAME     = process.env.GMAIL_USER_NAME;

if (!KNOCK_SERVICE_TOKEN) throw new Error('Missing KNOCK_SERVICE_TOKEN');
if (!KNOCK_API_TOKEN)     throw new Error('Missing KNOCK_API_TOKEN');
if (!ZEALT_RUN_ID)        throw new Error('Missing ZEALT_RUN_ID');
if (!GMAIL_USER_NAME)     throw new Error('Missing GMAIL_USER_NAME');

// ── Derived identifiers ────────────────────────────────────────────────────
const runId        = ZEALT_RUN_ID;
const workflowKey  = `branch-flow-${runId}`;
const recipientId  = `user-${runId}`;
const recipientEmail = `${GMAIL_USER_NAME}+receiver-${runId}@gmail.com`;
const recipientName  = `User ${runId}`;
const logFile      = path.join(__dirname, 'output.log');
const ENV          = 'development';

// ── SDK clients ────────────────────────────────────────────────────────────
const KnockMgmt = require('@knocklabs/mgmt');
const Knock     = require('@knocklabs/node');

const mgmtClient = new KnockMgmt.default({
  serviceToken: KNOCK_SERVICE_TOKEN,
});

const apiClient = new Knock.default({
  apiKey: KNOCK_API_TOKEN,
});

// ── Inline recipient object ────────────────────────────────────────────────
const recipient = {
  id:    recipientId,
  email: recipientEmail,
  name:  recipientName,
};

async function main() {
  // ── Step 1: Upsert the workflow ──────────────────────────────────────────
  console.log(`Upserting workflow: ${workflowKey} …`);

  await mgmtClient.workflows.upsert(workflowKey, {
    environment: ENV,
    commit: true,
    commit_message: `Auto-commit workflow ${workflowKey}`,
    workflow: {
      name: workflowKey,
      trigger_data_json_schema: {
        type: 'object',
        properties: {
          channel_preference: { type: 'string' },
        },
        required: ['channel_preference'],
      },
      steps: [
        {
          ref:  'branch_1',
          type: 'branch',
          branches: [
            // Non-default branch: fires when data.channel_preference == "email"
            {
              name: 'Email branch',
              terminates: true,
              conditions: {
                all: [
                  {
                    variable: 'data.channel_preference',
                    operator: 'equal_to',
                    argument: 'email',
                  },
                ],
              },
              steps: [
                {
                  ref:         'email_step',
                  type:        'channel',
                  channel_key: 'mailtrap',
                  template: {
                    subject:   `Hello {{ recipient.name }}`,
                    html_body: `<p>Hello {{ recipient.name }}, this is your email notification.</p>`,
                    text_body: `Hello {{ recipient.name }}, this is your email notification.`,
                    settings:  { layout_key: 'default' },
                  },
                },
              ],
            },
            // Default branch: fallback → in-app (terminates naturally as last branch)
            {
              name:       'In-app branch',
              terminates: false,
              // No conditions ⟹ default branch
              steps: [
                {
                  ref:         'in_app_step',
                  type:        'channel',
                  channel_key: 'in-app',
                  template: {
                    markdown_body: `Hello **{{ recipient.name }}**, this is your in-app notification.`,
                    action_url:    `https://knock.app`,
                  },
                },
              ],
            },
          ],
        },
      ],
    },
  });

  console.log('Workflow upserted.');

  // ── Step 2: Activate the workflow ────────────────────────────────────────
  console.log('Activating workflow …');
  await mgmtClient.workflows.activate(workflowKey, {
    environment: ENV,
    status: true,
  });
  console.log('Workflow activated.');

  // ── Step 3: Trigger #1 — email branch ───────────────────────────────────
  console.log('Triggering workflow (email) …');
  const emailTrigger = await apiClient.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: { channel_preference: 'email' },
  });
  const emailRunId = emailTrigger.workflow_run_id;
  console.log(`Email trigger run ID: ${emailRunId}`);

  // ── Step 4: Trigger #2 — in-app branch ──────────────────────────────────
  console.log('Triggering workflow (in-app) …');
  const inAppTrigger = await apiClient.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: { channel_preference: 'in-app' },
  });
  const inAppRunId = inAppTrigger.workflow_run_id;
  console.log(`In-app trigger run ID: ${inAppRunId}`);

  // ── Step 5: Write log file ───────────────────────────────────────────────
  const logLines = [
    `Workflow Key: ${workflowKey}`,
    `Email Run ID: ${emailRunId}`,
    `InApp Run ID: ${inAppRunId}`,
  ].join('\n') + '\n';

  fs.writeFileSync(logFile, logLines, 'utf8');
  console.log(`\nLog written to ${logFile}:`);
  console.log(logLines);
}

main().catch((err) => {
  console.error('Fatal error:', err);
  if (err && err.error) {
    console.error('API errors:', JSON.stringify(err.error, null, 2));
  }
  process.exit(1);
});
