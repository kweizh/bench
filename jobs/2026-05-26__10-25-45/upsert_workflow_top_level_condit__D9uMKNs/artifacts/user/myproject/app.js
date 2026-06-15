const fs = require("fs");
const path = require("path");
const { KnockMgmt } = require("@knocklabs/mgmt");
const { Knock } = require("@knocklabs/node");

async function main() {
  const {
    KNOCK_SERVICE_TOKEN,
    KNOCK_API_TOKEN,
    MAILTRAP_DOMAIN,
    GMAIL_USER_NAME,
    ZEALT_RUN_ID,
  } = process.env;

  if (!KNOCK_SERVICE_TOKEN || !KNOCK_API_TOKEN || !MAILTRAP_DOMAIN || !GMAIL_USER_NAME || !ZEALT_RUN_ID) {
    throw new Error("Missing required environment variables.");
  }

  const runId = ZEALT_RUN_ID;
  const workflowKey = `top-level-conditions-${runId}`;

  const adminId = `admin-${runId}`;
  const viewerId = `viewer-${runId}`;

  const adminEmail = `${GMAIL_USER_NAME}+${adminId}@gmail.com`;
  const viewerEmail = `${GMAIL_USER_NAME}+${viewerId}@gmail.com`;

  const mgmt = new KnockMgmt({
    apiKey: KNOCK_SERVICE_TOKEN,
    environment: "development",
  });

  const workflowPayload = {
    name: `Admin security alert ${runId}`,
    key: workflowKey,
    description: "Admin-only security alert",
    conditions: {
      all: [
        {
          variable: "recipient.role",
          operator: "equal_to",
          argument: "admin",
        },
      ],
    },
    steps: [
      {
        name: "Send admin alert",
        type: "channel",
        channel_key: "mailtrap",
        template: {
          subject: `Admin alert ${runId}`,
          html: "<p>Hello {{ recipient.name }},</p><p>This is an admin-only security alert.</p>",
        },
      },
    ],
  };

  await mgmt.workflows.upsert(workflowKey, {
    ...workflowPayload,
    environment: "development",
  });

  await mgmt.workflows.activate(workflowKey, {
    environment: "development",
    status: true,
  });

  const knock = new Knock({
    apiKey: KNOCK_API_TOKEN,
  });

  const triggerResponse = await knock.workflows.trigger(workflowKey, {
    recipients: [
      {
        id: adminId,
        name: "Admin User",
        email: adminEmail,
        role: "admin",
        properties: {
          role: "admin",
        },
      },
      {
        id: viewerId,
        name: "Viewer User",
        email: viewerEmail,
        role: "viewer",
        properties: {
          role: "viewer",
        },
      },
    ],
    data: {
      mailtrap_domain: MAILTRAP_DOMAIN,
    },
  });

  const outputPath = path.join(__dirname, "output.log");
  fs.writeFileSync(outputPath, `Workflow run ID: ${triggerResponse.workflow_run_id}\n`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
