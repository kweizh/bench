const { KnockMgmt } = require("@knocklabs/mgmt");
const { Knock } = require("@knocklabs/node");
const fs = require("fs");
const path = require("path");

async function main() {
  const runId = process.env.ZEALT_RUN_ID;
  const gmailUserName = process.env.GMAIL_USER_NAME;
  const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
  const apiToken = process.env.KNOCK_API_TOKEN;

  if (!runId || !gmailUserName || !serviceToken || !apiToken) {
    console.error("Missing required environment variables.");
    process.exit(1);
  }

  const workflowKey = `branch-flow-${runId}`;
  const mgmtClient = new KnockMgmt({ bearerToken: serviceToken });
  const nodeClient = new Knock(apiToken);

  console.log(`Upserting workflow: ${workflowKey}`);

  try {
    // 1. Upsert the workflow
    await mgmtClient.workflows.upsert(workflowKey, {
      environment: "development",
      workflow: {
        name: `Branch Flow ${runId}`,
        trigger_data_json_schema: {
          type: "object",
          properties: {
            channel_preference: { type: "string" },
          },
          required: ["channel_preference"],
        },
        steps: [
          {
            type: "branch",
            ref: "branch_step",
            branches: [
              {
                name: "Email Branch",
                terminates: true,
                conditions: {
                  all: [
                    {
                      variable: "data.channel_preference",
                      argument: "data.channel_preference",
                      operator: "equal_to",
                      value: "email",
                    },
                  ],
                },
                steps: [
                  {
                    type: "channel",
                    channel_key: "mailtrap",
                    ref: "email_step",
                    template: {
                      subject: "Hello {{ recipient.name }}!",
                      html_body: "This is an email for {{ recipient.name }}.",
                      settings: {},
                    },
                  },
                ],
              },
              {
                name: "Sentinel Branch",
                terminates: false,
                conditions: {
                  all: [
                    {
                      variable: "data.sentinel",
                      argument: "data.sentinel",
                      operator: "equal_to",
                      value: "true",
                    },
                  ],
                },
                steps: [],
              },
              {
                name: "Default Branch",
                terminates: true,
                default: true,
                steps: [
                  {
                    type: "channel",
                    channel_key: "in-app",
                    ref: "in_app_step",
                    template: {
                      markdown_body: "Hello {{ recipient.name }}! This is an in-app message.",
                      action_url: "https://knock.app",
                    },
                  },
                ],
              },
            ],
          },
        ],
      },
    });
  } catch (err) {
    if (err.error && err.error.errors) {
      console.error("Validation Errors:", JSON.stringify(err.error.errors, null, 2));
    }
    throw err;
  }

  // 2. Activate the workflow
  console.log(`Activating workflow: ${workflowKey}`);
  await mgmtClient.workflows.activate(workflowKey, { environment: "development" });

  // Commit the changes
  console.log(`Committing changes...`);
  await mgmtClient.commits.commitAll({
    environment: "development",
    message: `Upserting branch-flow-${runId}`,
  });

  // Wait for propagation
  console.log("Waiting 5 seconds for workflow propagation...");
  await new Promise(resolve => setTimeout(resolve, 5000));

  const recipient = {
    id: `user-${runId}`,
    email: `${gmailUserName}+receiver-${runId}@gmail.com`,
    name: `User ${runId}`,
  };

  // 3. Trigger for Email
  console.log(`Triggering email branch for: ${workflowKey}`);
  const emailTrigger = await nodeClient.workflows.trigger(workflowKey, {
    data: { channel_preference: "email" },
    recipients: [recipient],
  });

  // 4. Trigger for In-App
  console.log(`Triggering in-app branch for: ${workflowKey}`);
  const inAppTrigger = await nodeClient.workflows.trigger(workflowKey, {
    data: { channel_preference: "in-app" },
    recipients: [recipient],
  });

  // 5. Log the results
  const logContent = [
    `Workflow Key: ${workflowKey}`,
    `Email Run ID: ${emailTrigger.workflow_run_id}`,
    `InApp Run ID: ${inAppTrigger.workflow_run_id}`,
  ].join("\n") + "\n";

  const logPath = path.join(__dirname, "output.log");
  fs.writeFileSync(logPath, logContent);
  console.log(`Results logged to ${logPath}`);
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
