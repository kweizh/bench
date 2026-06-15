import fs from "node:fs/promises";
import { KnockMgmt } from "@knocklabs/mgmt";
import { Knock } from "@knocklabs/node";

const runId = process.env.ZEALT_RUN_ID;
if (!runId) {
  throw new Error("ZEALT_RUN_ID is required");
}

const serviceToken = process.env.KNOCK_SERVICE_TOKEN;
const apiToken = process.env.KNOCK_API_TOKEN;
const gmailUserName = process.env.GMAIL_USER_NAME;

if (!serviceToken || !apiToken || !gmailUserName) {
  throw new Error("KNOCK_SERVICE_TOKEN, KNOCK_API_TOKEN, and GMAIL_USER_NAME are required");
}

const workflowKey = `branch-flow-${runId}`;
const recipient = {
  id: `user-${runId}`,
  email: `${gmailUserName}+receiver-${runId}@gmail.com`,
  name: `User ${runId}`,
};

const mgmt = new KnockMgmt({
  serviceToken,
  baseURL: "https://control.knock.app",
});

const client = new Knock({
  apiKey: apiToken,
  baseURL: "https://api.knock.app",
  defaultQuery: { environment: "development" },
});

const workflowDefinition = {
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
      ref: "branch_by_channel_preference",
      name: "route-by-channel-preference",
      type: "branch",
      branches: [
        {
          name: "email-branch",
          terminates: true,
          conditions: {
            all: [
              {
                variable: "data.channel_preference",
                operator: "equal_to",
                argument: "email",
              },
            ],
          },
          steps: [
            {
              ref: "send_email",
              name: "send-email",
              type: "channel",
              channel_key: "mailtrap",
              template: {
                settings: {
                  layout_key: "default",
                },
                subject: "Hello from Knock",
                html_body: "<p>Hi {{ recipient.name }}, email branch chosen.</p>",
                text_body: "Hi {{ recipient.name }}, email branch chosen.",
              },
            },
          ],
        },
        {
          name: "noop-continue",
          terminates: false,
          conditions: {
            all: [
              {
                variable: "data.channel_preference",
                operator: "equal_to",
                argument: "__unused__",
              },
            ],
          },
          steps: [
            {
              ref: "noop_delay",
              name: "noop-delay",
              type: "delay",
              settings: {
                delay_for: {
                  unit: "minutes",
                  value: 1,
                },
              },
            },
          ],
        },
        {
          name: "in-app-default",
          terminates: true,
          steps: [
            {
              ref: "send_in_app",
              name: "send-in-app",
              type: "channel",
              channel_key: "in-app",
              template: {
                markdown_body: "Hi {{ recipient.name }}, default in-app branch chosen.",
                action_url: "https://knock.app",
              },
            },
          ],
        },
      ],
    },
  ],
};

const outputLogPath = "/home/user/myproject/output.log";

const run = async () => {
  await mgmt.workflows.upsert(workflowKey, {
    environment: "development",
    workflow: workflowDefinition,
    commit: true,
    commit_message: `Upsert branch workflow ${runId}`,
  });

  await mgmt.workflows.activate(workflowKey, {
    environment: "development",
    status: true,
  });

  const emailTrigger = await client.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: {
      channel_preference: "email",
    },
  });

  const inAppTrigger = await client.workflows.trigger(workflowKey, {
    recipients: [recipient],
    data: {
      channel_preference: "in-app",
    },
  });

  const logLines = [
    `Workflow Key: ${workflowKey}`,
    `Email Run ID: ${emailTrigger.workflow_run_id}`,
    `InApp Run ID: ${inAppTrigger.workflow_run_id}`,
  ];

  await fs.writeFile(outputLogPath, `${logLines.join("\n")}\n`, "utf8");
};

await run();
