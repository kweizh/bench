import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import Knock from "@knocklabs/node";
import KnockMgmt from "@knocklabs/mgmt";

// ---------------------------------------------------------------------------
// Environment variable validation
// ---------------------------------------------------------------------------
const required = [
  "KNOCK_API_TOKEN",
  "KNOCK_SERVICE_TOKEN",
  "ZEALT_RUN_ID",
  "GMAIL_USER_NAME",
  "MAILTRAP_DOMAIN",
];

for (const key of required) {
  if (!process.env[key]) {
    console.error(`Missing required environment variable: ${key}`);
    process.exit(1);
  }
}

const RUN_ID = process.env.ZEALT_RUN_ID;
const GMAIL_USER_NAME = process.env.GMAIL_USER_NAME;
const MAILTRAP_DOMAIN = process.env.MAILTRAP_DOMAIN;
const KNOCK_API_TOKEN = process.env.KNOCK_API_TOKEN;
const KNOCK_SERVICE_TOKEN = process.env.KNOCK_SERVICE_TOKEN;

// ---------------------------------------------------------------------------
// Derived identifiers (all suffixed with run-id to avoid collisions)
// ---------------------------------------------------------------------------
const tenantId = `tenant-${RUN_ID}`;
const workflowKey = `tenant-welcome-${RUN_ID}`;
const recipientId = `user-${RUN_ID}`;
const recipientEmail = `${GMAIL_USER_NAME}+receiver-${RUN_ID}@gmail.com`;
const recipientName = `Test User ${RUN_ID}`;
const fromEmail = `sender-${RUN_ID}@${MAILTRAP_DOMAIN}`;
const appName = `MyApp-${RUN_ID}`;

// ---------------------------------------------------------------------------
// Log file path
// ---------------------------------------------------------------------------
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LOG_FILE = path.join(__dirname, "output.log");

function appendLog(line) {
  fs.appendFileSync(LOG_FILE, line + "\n", "utf8");
  console.log(line);
}

async function main() {
  // -------------------------------------------------------------------------
  // 1. Set the tenant via the Knock Node SDK
  // -------------------------------------------------------------------------
  console.log(`\n[1] Setting tenant: ${tenantId}`);
  const knock = new Knock({ apiKey: KNOCK_API_TOKEN });

  await knock.tenants.set(tenantId, {
    name: `Tenant ${RUN_ID}`,
    settings: {
      branding: {
        primary_color: "#4F46E5",
      },
    },
    app_name: appName,
  });

  console.log(`    ✓ Tenant "${tenantId}" set successfully`);

  // -------------------------------------------------------------------------
  // 2. Upsert the workflow via the Knock Management API
  // -------------------------------------------------------------------------
  console.log(`\n[2] Upserting workflow: ${workflowKey}`);
  const mgmt = new KnockMgmt({ serviceToken: KNOCK_SERVICE_TOKEN });

  await mgmt.workflows.upsert(workflowKey, {
    environment: "development",
    commit: true,
    commit_message: `Upsert workflow ${workflowKey}`,
    workflow: {
      name: `Tenant Welcome ${RUN_ID}`,
      steps: [
        {
          ref: "email-step",
          type: "channel",
          channel_key: "mailtrap",
          channel_type: "email",
          template: {
            subject: "Welcome to {{ tenant.app_name }}",
            html_body: `<p>Hello {{ recipient.name }},</p>
<p>Welcome to the tenant: <strong>{{ tenant.name }}</strong>.</p>
<p>We are glad to have you on board!</p>`,
            settings: {},
          },
          channel_overrides: {
            from_address: fromEmail,
          },
        },
      ],
    },
  });

  console.log(`    ✓ Workflow "${workflowKey}" upserted successfully`);

  // -------------------------------------------------------------------------
  // 3. Activate the workflow in the development environment
  // -------------------------------------------------------------------------
  console.log(`\n[3] Activating workflow: ${workflowKey}`);

  await mgmt.workflows.activate(workflowKey, {
    environment: "development",
    status: true,
  });

  console.log(`    ✓ Workflow "${workflowKey}" activated successfully`);

  // -------------------------------------------------------------------------
  // 4. Trigger the workflow with a single recipient scoped to the tenant
  // -------------------------------------------------------------------------
  console.log(`\n[4] Triggering workflow: ${workflowKey}`);

  const triggerResponse = await knock.workflows.trigger(workflowKey, {
    recipients: [
      {
        id: recipientId,
        email: recipientEmail,
        name: recipientName,
      },
    ],
    tenant: tenantId,
  });

  const workflowRunId = triggerResponse.workflow_run_id;
  console.log(`    ✓ Workflow triggered. Run ID: ${workflowRunId}`);

  // -------------------------------------------------------------------------
  // 5. Write log file
  // -------------------------------------------------------------------------
  console.log(`\n[5] Writing output log: ${LOG_FILE}`);

  // Clear log file if it exists, then write fresh lines
  if (fs.existsSync(LOG_FILE)) {
    fs.unlinkSync(LOG_FILE);
  }

  appendLog(`Tenant ID: ${tenantId}`);
  appendLog(`Workflow Key: ${workflowKey}`);
  appendLog(`Workflow Run ID: ${workflowRunId}`);
  appendLog(`Recipient Email: ${recipientEmail}`);

  console.log("\n✅ All steps completed successfully.");
}

main().catch((err) => {
  console.error("Error:", err.message || err);
  if (err.status) {
    console.error("HTTP status:", err.status);
  }
  if (err.error) {
    console.error("API error:", JSON.stringify(err.error, null, 2));
  }
  process.exit(1);
});
