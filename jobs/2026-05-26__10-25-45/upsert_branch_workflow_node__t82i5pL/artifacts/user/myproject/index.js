const KnockMgmt = require("@knocklabs/mgmt").default;
const { Knock } = require("@knocklabs/node");
const fs = require("fs");

const runId = process.env.ZEALT_RUN_ID || "default-run-id";
const gmailUserName = process.env.GMAIL_USER_NAME || "test";

const knockMgmt = new KnockMgmt(process.env.KNOCK_SERVICE_TOKEN);
const knockNode = new Knock({ apiKey: process.env.KNOCK_API_TOKEN });

async function main() {
  const workflowKey = `branch-flow-${runId}`;

  // 1. & 2. Upsert workflow
  await knockMgmt.workflows.upsert(workflowKey, {
    environment: "development",
    commit: true,
    commit_message: "Upserting workflow",
    workflow: {
      name: `Branch Flow ${runId}`,
      trigger_data_json_schema: {
        type: "object",
        properties: {
          channel_preference: { type: "string" }
        },
        required: ["channel_preference"]
      },
      steps: [
        {
          ref: "branch_step",
          type: "branch",
          name: "Branch on channel preference",
          branches: [
            {
              name: "Email Branch",
              terminates: true,
              conditions: {
                all: [
                  {
                    argument: "email",
                    variable: "data.channel_preference",
                    operator: "equal_to"
                  }
                ]
              },
              steps: [
                {
                  ref: "email_step",
                  type: "channel",
                  channel_key: "mailtrap",
                  template: {
                    subject: "Hello {{ recipient.name }}",
                    html_body: "This is an email for {{ recipient.name }}",
                    settings: {}
                  }
                }
              ]
            },
            {
              name: "Dummy Branch",
              terminates: false,
              conditions: {
                all: [
                  {
                    argument: "dummy",
                    variable: "data.channel_preference",
                    operator: "equal_to"
                  }
                ]
              },
              steps: []
            },
            {
              name: "Default Branch",
              terminates: true,
              default: true,
              steps: [
                {
                  ref: "in_app_step",
                  type: "channel",
                  channel_key: "in-app",
                  template: {
                    markdown_body: "This is an in-app message for {{ recipient.name }}",
                    action_url: "https://example.com"
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  });

  // 3. Activate workflow
  await knockMgmt.workflows.activate(workflowKey, { environment: "development", status: true });

  const recipient = {
    id: `user-${runId}`,
    email: `${gmailUserName}+receiver-${runId}@gmail.com`,
    name: `User ${runId}`
  };

  // 4.1. First trigger with "email"
  const emailTrigger = await knockNode.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: {
      channel_preference: "email"
    }
  });

  // 4.2. Second trigger with "in-app"
  const inAppTrigger = await knockNode.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: {
      channel_preference: "in-app"
    }
  });

  // 6. Log to output.log
  const logContent = [
    `Workflow Key: ${workflowKey}`,
    `Email Run ID: ${emailTrigger.workflow_run_id}`,
    `InApp Run ID: ${inAppTrigger.workflow_run_id}`
  ].join("\n") + "\n";

  fs.writeFileSync("/home/user/myproject/output.log", logContent);
  console.log("Done");
}

main().catch(err => {
  console.error("Error:", err.error || err);
  process.exit(1);
});
