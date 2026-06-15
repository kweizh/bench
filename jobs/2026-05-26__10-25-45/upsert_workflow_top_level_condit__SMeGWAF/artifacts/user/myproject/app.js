import KnockMgmt from '@knocklabs/mgmt';
import Knock from '@knocklabs/node';
import fs from 'fs';
import path from 'path';

// ── Read environment variables ─────────────────────────────────────────────
const KNOCK_SERVICE_TOKEN = process.env.KNOCK_SERVICE_TOKEN;
const KNOCK_API_TOKEN     = process.env.KNOCK_API_TOKEN;
const MAILTRAP_DOMAIN     = process.env.MAILTRAP_DOMAIN;
const GMAIL_USER_NAME     = process.env.GMAIL_USER_NAME;
const RUN_ID              = process.env.ZEALT_RUN_ID;

if (!KNOCK_SERVICE_TOKEN) throw new Error('Missing KNOCK_SERVICE_TOKEN');
if (!KNOCK_API_TOKEN)     throw new Error('Missing KNOCK_API_TOKEN');
if (!GMAIL_USER_NAME)     throw new Error('Missing GMAIL_USER_NAME');
if (!RUN_ID)              throw new Error('Missing ZEALT_RUN_ID');

// ── Derived identifiers (run-id suffix makes them concurrency-safe) ─────────
const WORKFLOW_KEY   = `top-level-conditions-${RUN_ID}`;
const ADMIN_ID       = `admin-${RUN_ID}`;
const VIEWER_ID      = `viewer-${RUN_ID}`;
const EMAIL_SUBJECT  = `Admin alert ${RUN_ID}`;

// ── Clients ─────────────────────────────────────────────────────────────────
const mgmtClient = new KnockMgmt({ serviceToken: KNOCK_SERVICE_TOKEN });
const knockClient = new Knock({ apiKey: KNOCK_API_TOKEN });

async function main() {
  // ── 1. Upsert the workflow ───────────────────────────────────────────────
  console.log(`Upserting workflow: ${WORKFLOW_KEY}`);

  await mgmtClient.workflows.upsert(WORKFLOW_KEY, {
    environment: 'development',
    commit: true,
    commit_message: `Upsert admin-only alert workflow (run ${RUN_ID})`,
    workflow: {
      name: 'Admin-only Security Alert',
      description: 'Sends a security alert email only to users with role=admin.',

      // Top-level condition gate: only run for recipients whose role == "admin"
      conditions: {
        all: [
          {
            variable: 'recipient.role',
            operator: 'equal_to',
            argument:  'admin',
          },
        ],
      },

      steps: [
        {
          ref:         'email-alert',
          type:        'channel',
          channel_key: 'mailtrap',
          template: {
            settings: {
              layout_key: null,
            },
            subject:   EMAIL_SUBJECT,
            html_body: `<html><body><p>Hello {{ recipient.name }},</p><p>This is a security alert. Please review your account activity immediately.</p></body></html>`,
          },
        },
      ],
    },
  });

  console.log('Workflow upserted successfully.');

  // ── 2. Activate the workflow in development ──────────────────────────────
  console.log(`Activating workflow: ${WORKFLOW_KEY}`);

  await mgmtClient.workflows.activate(WORKFLOW_KEY, {
    environment: 'development',
    status: true,
  });

  console.log('Workflow activated successfully.');

  // ── 3. Trigger the workflow with inline recipient identification ──────────
  console.log(`Triggering workflow: ${WORKFLOW_KEY}`);

  const triggerResponse = await knockClient.workflows.trigger(WORKFLOW_KEY, {
    recipients: [
      // Admin user – will pass the top-level conditions gate
      {
        id:    ADMIN_ID,
        name:  `Admin User ${RUN_ID}`,
        email: `${GMAIL_USER_NAME}+${ADMIN_ID}@gmail.com`,
        role:  'admin',
      },
      // Viewer user – will be blocked by the top-level conditions gate
      {
        id:    VIEWER_ID,
        name:  `Viewer User ${RUN_ID}`,
        email: `${GMAIL_USER_NAME}+${VIEWER_ID}@gmail.com`,
        role:  'viewer',
      },
    ],
  });

  const workflowRunId = triggerResponse.workflow_run_id;
  console.log(`Workflow triggered. Run ID: ${workflowRunId}`);

  // ── 4. Write the run ID to the log file ─────────────────────────────────
  const logPath = path.join(import.meta.dirname, 'output.log');
  fs.writeFileSync(logPath, `Workflow run ID: ${workflowRunId}\n`);
  console.log(`Written to ${logPath}`);
}

main().catch((err) => {
  console.error('Error:', err);
  process.exit(1);
});
