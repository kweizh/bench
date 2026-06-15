const { KnockMgmt } = require("@knocklabs/mgmt");
const { Knock } = require("@knocklabs/node");
const fs = require("fs");

const KNOCK_SERVICE_TOKEN = process.env.KNOCK_SERVICE_TOKEN;
const KNOCK_API_TOKEN = process.env.KNOCK_API_TOKEN;
const GMAIL_USER_NAME = process.env.GMAIL_USER_NAME;
const ZEALT_RUN_ID = process.env.ZEALT_RUN_ID;

const workflowKey = `top-level-conditions-${ZEALT_RUN_ID}`;
const adminId = `admin-${ZEALT_RUN_ID}`;
const viewerId = `viewer-${ZEALT_RUN_ID}`;

const mgmtClient = new KnockMgmt({ apiKey: KNOCK_SERVICE_TOKEN });
const knockClient = new Knock({ apiKey: KNOCK_API_TOKEN });

async function run() {
  try {
    console.log(`Upserting workflow: ${workflowKey}`);
    
    // 1. Upsert the workflow in development
    await mgmtClient.workflows.upsert(workflowKey, {
      environment: "development",
      commit: true,
      workflow: {
        name: `Admin Alert Workflow ${ZEALT_RUN_ID}`,
        active: true,
        trigger_conditions: {
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
            type: "channel",
            channel_key: "mailtrap",
            ref: "mailtrap_step",
            template: {
              subject: `Admin alert ${ZEALT_RUN_ID}`,
              html_body: "<html><body><h1>Hello {{ recipient.name }}</h1><p>This is a security alert for admins only.</p></body></html>",
              settings: {}
            },
          },
        ],
      }
    });

    console.log(`Triggering workflow: ${workflowKey}`);
    // 2. Trigger the workflow
    const response = await knockClient.workflows.trigger(workflowKey, {
      recipients: [
        {
          id: adminId,
          name: "Admin User",
          email: `${GMAIL_USER_NAME}+${adminId}@gmail.com`,
          role: "admin",
        },
        {
          id: viewerId,
          name: "Viewer User",
          email: `${GMAIL_USER_NAME}+${viewerId}@gmail.com`,
          role: "viewer",
        },
      ],
    });

    const workflowRunId = response.workflow_run_id;
    console.log(`Workflow run ID: ${workflowRunId}`);

    // 3. Write to log file
    const logPath = "/home/user/myproject/output.log";
    fs.writeFileSync(logPath, `Workflow run ID: ${workflowRunId}\n`);
    
  } catch (error) {
    if (error.error && error.error.errors) {
        console.error("Error details:", JSON.stringify(error.error.errors, null, 2));
    }
    console.error("Error:", error);
    process.exit(1);
  }
}

run();
