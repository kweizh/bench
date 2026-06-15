const fs = require("fs");
const path = require("path");
const { KnockMgmt } = require("@knocklabs/mgmt");
const { Knock } = require("@knocklabs/node");

const REQUIRED_ENV_VARS = [
  "ZEALT_RUN_ID",
  "KNOCK_SERVICE_TOKEN",
  "KNOCK_API_TOKEN",
  "GMAIL_USER_NAME",
  "MAILTRAP_DOMAIN",
];

const missingVars = REQUIRED_ENV_VARS.filter((key) => !process.env[key]);
if (missingVars.length > 0) {
  throw new Error(`Missing required environment variables: ${missingVars.join(", ")}`);
}

const runId = process.env.ZEALT_RUN_ID;
const gmailUserName = process.env.GMAIL_USER_NAME;
const mailtrapDomain = process.env.MAILTRAP_DOMAIN;

const workflowKey = `dedup-test-${runId}`;
const recipientId = `dedup-recipient-${runId}`;
const recipientEmail = `${gmailUserName}+receiver-${runId}@gmail.com`;
const logPath = path.join(__dirname, "output.log");

const formatRunId = (runIdValue) => (runIdValue ? runIdValue : "null");

const main = async () => {
  const mgmtClient = new KnockMgmt({ serviceToken: process.env.KNOCK_SERVICE_TOKEN });

  await mgmtClient.workflows.upsert(workflowKey, {
    environment: "development",
    commit: true,
    commit_message: `Initialize ${workflowKey}`,
    workflow: {
      name: `Dedup Test ${runId}`,
      trigger_frequency: "once_per_recipient",
      steps: [
        {
          ref: "email_step",
          type: "channel",
          channel_key: "mailtrap",
          channel_type: "email",
          channel_overrides: {
            from_address: `dedup-${runId}@${mailtrapDomain}`,
            from_name: `Dedup ${runId}`,
          },
          template: {
            settings: {
              layout_key: "default",
            },
            subject: `dedup-test-${runId} welcome`,
            html_body: `<!doctype html><html><body><h1>Dedup test ${runId}</h1><p>Hello {{ recipient.name }}!</p></body></html>`,
            text_body: `Dedup test ${runId} - Hello {{ recipient.name }}!`,
          },
        },
      ],
    },
  });

  await mgmtClient.workflows.activate(workflowKey, {
    environment: "development",
    status: true,
  });

  const apiClient = new Knock({ apiKey: process.env.KNOCK_API_TOKEN });
  const inlineRecipient = {
    id: recipientId,
    email: recipientEmail,
    name: `Recipient ${runId}`,
  };

  fs.writeFileSync(logPath, "");

  const firstTrigger = await apiClient.workflows.trigger(workflowKey, {
    recipients: [inlineRecipient],
  });

  fs.appendFileSync(
    logPath,
    `First trigger workflow_run_id: ${formatRunId(firstTrigger?.workflow_run_id)}\n`,
  );

  const secondTrigger = await apiClient.workflows.trigger(workflowKey, {
    recipients: [inlineRecipient],
  });

  fs.appendFileSync(
    logPath,
    `Second trigger workflow_run_id: ${formatRunId(secondTrigger?.workflow_run_id)}\n`,
  );
};

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
