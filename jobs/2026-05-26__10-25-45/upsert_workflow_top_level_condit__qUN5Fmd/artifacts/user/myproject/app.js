const { KnockMgmt } = require('@knocklabs/mgmt');
const { Knock } = require('@knocklabs/node');
const fs = require('fs');

async function main() {
  const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
  const apiToken = process.env.KNOCK_API_TOKEN;
  const gmailUserName = process.env.GMAIL_USER_NAME;
  const runId = process.env.ZEALT_RUN_ID;

  if (!serviceToken || !apiToken || !gmailUserName || !runId) {
    throw new Error("Missing required environment variables");
  }

  const mgmtClient = new KnockMgmt({ serviceToken });
  const knockClient = new Knock({ apiKey: apiToken });

  const workflowKey = `top-level-conditions-${runId}`;

  // Upsert the workflow
  console.log(`Upserting workflow ${workflowKey}...`);
  await mgmtClient.workflows.upsert(workflowKey, {
    environment: 'development',
    commit: true,
    workflow: {
      name: `Top Level Conditions ${runId}`,
      conditions: {
        all: [
          {
            variable: "recipient.role",
            operator: "equal_to",
            argument: "admin"
          }
        ]
      },
      steps: [
        {
          ref: "step_1",
          type: "channel",
          channel_key: "mailtrap",
          template: {
            settings: {},
            subject: `Admin alert ${runId}`,
            html_body: `<p>Hello {{ recipient.name }},</p>`,
          }
        }
      ]
    }
  });

  // Activate the workflow
  console.log(`Activating workflow ${workflowKey}...`);
  await mgmtClient.workflows.activate(workflowKey, {
    environment: 'development',
    status: true
  });

  // Trigger the workflow
  console.log(`Triggering workflow ${workflowKey}...`);
  const adminId = `admin-${runId}`;
  const viewerId = `viewer-${runId}`;

  const adminEmail = `${gmailUserName}+${adminId}@gmail.com`;
  const viewerEmail = `${gmailUserName}+${viewerId}@gmail.com`;

  const triggerResponse = await knockClient.workflows.trigger(workflowKey, {
    recipients: [
      {
        id: adminId,
        name: "Admin User",
        email: adminEmail,
        role: "admin"
      },
      {
        id: viewerId,
        name: "Viewer User",
        email: viewerEmail,
        role: "viewer"
      }
    ]
  });

  console.log("Trigger response:", triggerResponse);

  const logLine = `Workflow run ID: ${triggerResponse.workflow_run_id}\n`;
  fs.writeFileSync('/home/user/myproject/output.log', logLine);
  console.log("Done.");
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
