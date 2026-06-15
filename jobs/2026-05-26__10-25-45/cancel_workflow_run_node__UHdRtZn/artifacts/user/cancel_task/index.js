const fs = require("fs");
const path = require("path");
const { Knock: KnockMgmt } = require("@knocklabs/mgmt");
const { Knock } = require("@knocklabs/node");

const REQUIRED_ENV_VARS = [
  "KNOCK_SERVICE_TOKEN",
  "KNOCK_API_TOKEN",
  "MAILTRAP_DOMAIN",
  "GMAIL_USER_NAME",
  "ZEALT_RUN_ID",
];

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const ensureEnv = () => {
  const missing = REQUIRED_ENV_VARS.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(", ")}`);
  }
};

const getWorkflowRunId = (triggerResponse) => {
  if (!triggerResponse) {
    return null;
  }

  if (triggerResponse.workflow_run_id) {
    return triggerResponse.workflow_run_id;
  }

  if (triggerResponse.data && triggerResponse.data.workflow_run_id) {
    return triggerResponse.data.workflow_run_id;
  }

  return null;
};

const main = async () => {
  ensureEnv();

  const runId = process.env.ZEALT_RUN_ID;
  const workflowKey = `cancel-flow-${runId}`;
  const cancellationKey = `cancel-${runId}`;
  const mailtrapDomain = process.env.MAILTRAP_DOMAIN;
  const gmailUser = process.env.GMAIL_USER_NAME;
  const recipientEmail = `${gmailUser}+receiver-${runId}@gmail.com`;
  const recipientId = `user-${runId}`;
  const recipientName = `User ${runId}`;

  const mgmt = new KnockMgmt({ apiKey: process.env.KNOCK_SERVICE_TOKEN });
  const knock = new Knock(process.env.KNOCK_API_TOKEN);

  const workflowSteps = [
    {
      name: "delay-step",
      type: "delay",
      settings: {
        delay_for: {
          unit: "seconds",
          value: 45,
        },
      },
    },
    {
      name: "mailtrap-email",
      type: "channel",
      channel_key: "mailtrap",
      settings: {
        from_email_address: `sender-${runId}@${mailtrapDomain}`,
        subject: `Knock cancel test ${runId} for {{recipient.name}}`,
        html_body: "<p>Hello {{recipient.name}},</p><p>This email should not arrive.</p>",
      },
    },
  ];

  await mgmt.workflows.upsert(workflowKey, {
    name: `Cancel Workflow ${runId}`,
    environment: "development",
    steps: workflowSteps,
  });

  await mgmt.workflows.activate(workflowKey, {
    environment: "development",
  });

  const triggerResponse = await knock.workflows.trigger(workflowKey, {
    cancellation_key: cancellationKey,
    recipients: [
      {
        id: recipientId,
        email: recipientEmail,
        name: recipientName,
      },
    ],
  });

  const workflowRunId = getWorkflowRunId(triggerResponse);
  if (!workflowRunId) {
    throw new Error("Unable to read workflow_run_id from trigger response.");
  }

  await sleep(5000);

  const cancelResponse = await fetch(
    `https://api.knock.app/v1/workflows/${workflowKey}/cancel`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.KNOCK_API_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        cancellation_key: cancellationKey,
      }),
    }
  );

  if (cancelResponse.status !== 204) {
    const body = await cancelResponse.text();
    throw new Error(
      `Cancel request failed with status ${cancelResponse.status}: ${body}`
    );
  }

  const logLines = [
    `Workflow Key: ${workflowKey}`,
    `Workflow Run ID: ${workflowRunId}`,
    `Cancellation Key: ${cancellationKey}`,
    `Recipient Email: ${recipientEmail}`,
  ];

  const logPath = path.join(__dirname, "output.log");
  fs.writeFileSync(logPath, `${logLines.join("\n")}\n`, "utf8");

  console.log("Workflow trigger and cancellation complete.");
  console.log(`Log written to ${logPath}`);
};

main().catch((error) => {
  console.error("Automation failed:", error);
  process.exit(1);
});
