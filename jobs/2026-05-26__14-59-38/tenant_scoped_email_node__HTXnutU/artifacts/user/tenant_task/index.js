const fs = require("fs/promises");
const Knock = require("@knocklabs/node");
const KnockMgmt = require("@knocklabs/mgmt");

const REQUIRED_ENV_VARS = [
  "KNOCK_API_TOKEN",
  "KNOCK_SERVICE_TOKEN",
  "ZEALT_RUN_ID",
  "MAILTRAP_DOMAIN",
  "GMAIL_USER_NAME",
];

const ensureEnvVars = () => {
  const missing = REQUIRED_ENV_VARS.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(", ")}`
    );
  }
};

const buildWorkflowPayload = ({ runId, fromEmail }) => ({
  name: `Tenant welcome workflow ${runId}`,
  steps: [
    {
      ref: `email-step-${runId}`,
      name: `Tenant welcome email ${runId}`,
      type: "channel",
      channel_key: "mailtrap",
      channel_type: "email",
      template: {
        subject: `Welcome to {{ tenant.app_name }} (${runId})`,
        html_body:
          `<html><body>` +
          `<p>Hello {{ recipient.name }},</p>` +
          `<p>Welcome to {{ tenant.name }}!</p>` +
          `</body></html>`,
        settings: {
          from_email_address: fromEmail,
        },
      },
      channel_overrides: {
        from_address: fromEmail,
      },
    },
  ],
});

const appendLog = async ({ logPath, tenantId, workflowKey, runId, recipientEmail, workflowRunId }) => {
  const lines = [
    `Tenant ID: ${tenantId}`,
    `Workflow Key: ${workflowKey}`,
    `Workflow Run ID: ${workflowRunId}`,
    `Recipient Email: ${recipientEmail}`,
  ];
  await fs.appendFile(logPath, `${lines.join("\n")}\n`);
};

const main = async () => {
  ensureEnvVars();

  const runId = process.env.ZEALT_RUN_ID;
  const knockApiToken = process.env.KNOCK_API_TOKEN;
  const knockServiceToken = process.env.KNOCK_SERVICE_TOKEN;
  const mailtrapDomain = process.env.MAILTRAP_DOMAIN;
  const gmailUserName = process.env.GMAIL_USER_NAME;

  const tenantId = `tenant-${runId}`;
  const workflowKey = `tenant-welcome-${runId}`;
  const recipientId = `user-${runId}`;
  const recipientEmail = `${gmailUserName}+receiver-${runId}@gmail.com`;
  const recipientName = `Recipient ${runId}`;
  const tenantAppName = `App ${runId}`;
  const fromEmail = `sender-${runId}@${mailtrapDomain}`;

  const knockClient = new Knock({
    apiKey: knockApiToken,
    defaultHeaders: {
      "X-Knock-Environment": "development",
    },
    defaultQuery: {
      environment: "development",
    },
  });
  const knockMgmtClient = new KnockMgmt({ serviceToken: knockServiceToken });

  await knockClient.tenants.set(tenantId, {
    name: `Tenant ${runId}`,
    settings: {
      branding: {
        primary_color: "#2F80ED",
      },
    },
    app_name: tenantAppName,
  });

  await knockMgmtClient.workflows.upsert(workflowKey, {
    environment: "development",
    commit: true,
    commit_message: `Add tenant workflow ${runId}`,
    workflow: buildWorkflowPayload({ runId, fromEmail }),
  });

  await knockMgmtClient.workflows.activate(workflowKey, {
    environment: "development",
    status: true,
  });

  const triggerResponse = await knockClient.workflows.trigger(
    workflowKey,
    {
      recipients: [
        {
          id: recipientId,
          email: recipientEmail,
          name: recipientName,
        },
      ],
      tenant: tenantId,
    },
    {
      headers: {
        "X-Knock-Environment": "development",
      },
      query: {
        environment: "development",
      },
    }
  );

  await appendLog({
    logPath: "/home/user/tenant_task/output.log",
    tenantId,
    workflowKey,
    runId,
    recipientEmail,
    workflowRunId: triggerResponse.workflow_run_id,
  });

  console.log("Workflow triggered:", triggerResponse.workflow_run_id);
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
